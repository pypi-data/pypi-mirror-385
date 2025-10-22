from functools import update_wrapper
from typing import Optional, Tuple, Union, List, Any

from django import forms
from django.contrib.admin import ModelAdmin as BaseModelAdmin
from django.contrib.admin import StackedInline as BaseStackedInline
from django.contrib.admin import TabularInline as BaseTabularInline
from django.contrib.admin import display, helpers
from django.contrib.admin.options import InlineModelAdmin
from django.contrib.admin.views import main
from django.contrib.admin.views.main import IGNORED_PARAMS
from django.contrib.contenttypes.admin import (
    GenericStackedInline as BaseGenericStackedInline,
)
from django.contrib.contenttypes.admin import (
    GenericTabularInline as BaseGenericTabularInline,
)
from django.db.models import BLANK_CHOICE_DASH, Model
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.urls import URLPattern, path
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from django.views import View

from unfold.checks import UnfoldModelAdminChecks
from unfold.datasets import BaseDataset
from unfold.forms import (
    ActionForm,
    PaginationGenericInlineFormSet,
    PaginationInlineFormSet,
)
from unfold.mixins import ActionModelAdminMixin, BaseModelAdminMixin
from unfold.overrides import FORMFIELD_OVERRIDES_INLINE
from unfold.typing import FieldsetsType
from unfold.views import ChangeList
from unfold.widgets import UnfoldBooleanWidget

from unfold.dataclasses import UnfoldAction

checkbox = UnfoldBooleanWidget(
    {
        "class": "action-select",
        "aria-label": _("Select record"),
    },
    lambda value: False,
)


class ModelAdmin(BaseModelAdminMixin, ActionModelAdminMixin, BaseModelAdmin):
    action_form = ActionForm
    custom_urls = ()
    add_fieldsets = ()
    ordering_field = None
    hide_ordering_field = False
    list_horizontal_scrollbar_top = False
    list_filter_submit = False
    list_filter_sheet = True
    list_fullwidth = False
    list_disable_select_all = False
    list_before_template = None
    list_after_template = None
    change_form_before_template = None
    change_form_after_template = None
    change_form_outer_before_template = None
    change_form_outer_after_template = None
    change_form_datasets = ()
    compressed_fields = False
    readonly_preprocess_fields = {}
    warn_unsaved_form = False
    checks_class = UnfoldModelAdminChecks

    @property
    def media(self):
        if not hasattr(self, "request"):
            return super().media

        media = super().media

        for filter in self.get_list_filter(self.request):
            if (
                isinstance(filter, tuple | list)
                and hasattr(filter[1], "form_class")
                and hasattr(filter[1].form_class, "Media")
            ):
                media += forms.Media(filter[1].form_class.Media)
            elif hasattr(filter, "form_class") and hasattr(filter.form_class, "Media"):
                media += forms.Media(filter.form_class.Media)

        return media

    def changelist_view(
        self, request: HttpRequest, extra_context: dict[str, str] | None = None
    ) -> TemplateResponse:
        self.request = request

        if self.ordering_field and self.ordering_field not in self.list_editable:
            list_editable = list(getattr(self, "list_editable", []))
            list_editable.append(self.ordering_field)
            self.list_editable = list_editable

        return super().changelist_view(request, extra_context)

    def changeform_view(
        self,
        request: HttpRequest,
        object_id: str | None = None,
        form_url: str = "",
        extra_context: dict[str, Any] | None = None,
    ) -> TemplateResponse:
        self.request = request
        extra_context = extra_context or {}
        datasets = self.get_changeform_datasets(request)

        # Monkeypatch IGNORED_PARAMS to add dataset page and search arguments into ignored params
        ignored_params = []
        for dataset in datasets:
            ignored_params.append(f"{dataset.model._meta.model_name}-q")
            ignored_params.append(f"{dataset.model._meta.model_name}-p")

        main.IGNORED_PARAMS = (*IGNORED_PARAMS, *ignored_params)

        rendered_datasets = []
        for dataset in datasets:
            rendered_datasets.append(
                dataset(
                    request=request,
                    extra_context={
                        "object": object_id,
                    },
                )
            )

        extra_context["datasets"] = rendered_datasets
        return super().changeform_view(request, object_id, form_url, extra_context)

    def get_list_display(self, request: HttpRequest) -> list[str]:
        list_display = super().get_list_display(request)

        if self.ordering_field and self.ordering_field not in list_display:
            list_display.append(self.ordering_field)

        return list_display

    def get_fieldsets(
        self, request: HttpRequest, obj: Model | None = None
    ) -> FieldsetsType:
        if not obj and self.add_fieldsets:
            return self.add_fieldsets
        return super().get_fieldsets(request, obj)

    def getLogMessage(self, form, add=False, formsetObj=None):
        """
        Return a list of messages describing the changes from the admin form.
        """
        changed_data = {} if form is None else form.changed_data
        data = {}
        change_message = []

        if formsetObj is not None:
            data = {
                "name": str(formsetObj._meta.verbose_name_plural),
                "object": f"{str(formsetObj)}({formsetObj.pk})",
            }
        if add:
            change_message.append({"added": data})
        elif form.changed_data:
            message = []
            for field in changed_data:
                initial = form.initial[field]
                cleaned_data = form.cleaned_data[field]

                message.append(
                    f"""[{form.fields[field].label}] "{str(initial)}" => "{str(cleaned_data)}" """
                )
            data["fields"] = message
            change_message.append({"changed": data})
        return change_message

    def construct_change_message(self, request, form, formsets, add=False):
        """
        Construct a JSON structure describing change details from a changed object and append it to change_messge in django_admin_log.
        """
        change_message = self.getLogMessage(form, add)

        if formsets:
            for formset in formsets:
                formList = {}

                pkName = ""
                if formset.__len__() > 0:
                    pkName = formset.forms[0]._meta.model._meta.pk.name

                for singleform in formset.forms:
                    try:
                        obj = singleform.cleaned_data[pkName]

                        if obj is None:
                            obj = singleform.initial.get(pkName)

                        if obj is not None:
                            formList[getattr(obj, pkName)] = singleform
                    except Exception as e:
                        print(e)

                for added_object in formset.new_objects:
                    message = self.getLogMessage(None, True, formsetObj=added_object)
                    change_message += message

                for changed_object, changed_fields in formset.changed_objects:
                    singleForm = formList[changed_object.pk]
                    message = self.getLogMessage(
                        singleForm, False, formsetObj=changed_object
                    )
                    change_message += message

                    self.log_change(
                        request, changed_object, self.getLogMessage(singleForm, False)
                    )

                for deleted_object in formset.deleted_objects:
                    change_message.append(
                        {
                            "deleted": {
                                "name": str(deleted_object._meta.verbose_name_plural),
                                "object": str(deleted_object),
                            }
                        }
                    )
        return change_message

    def _filter_unfold_actions_by_permissions(
        self,
        request: HttpRequest,
        actions: List[UnfoldAction],
        object_id: Optional[Union[int, str]] = None,
    ) -> List[UnfoldAction]:
        """Filter out any Unfold actions that the user doesn't have access to."""
        filtered_actions = []
        for action in actions:
            if not hasattr(action.method, "allowed_permissions"):
                filtered_actions.append(action)
                continue

            permission_checks = (
                getattr(self, f"has_{permission}_permission")
                for permission in action.method.allowed_permissions
            )

            if object_id:
                if any(
                    has_permission(request, object_id)
                    for has_permission in permission_checks
                ):
                    filtered_actions.append(action)
            else:
                if any(has_permission(request) for has_permission in permission_checks):
                    filtered_actions.append(action)

        return filtered_actions

    def get_actions_list(self, request: HttpRequest) -> List[UnfoldAction]:
        return self._filter_unfold_actions_by_permissions(
            request, self._get_base_actions_list()
        )

    def _get_base_actions_list(self) -> List[UnfoldAction]:
        """
        Returns all available list global actions, prior to any filtering
        """
        return [self.get_unfold_action(action) for action in self.actions_list or []]

    def get_actions_detail(
        self, request: HttpRequest, object_id: int
    ) -> List[UnfoldAction]:
        return self._filter_unfold_actions_by_permissions(
            request, self._get_base_actions_detail(), object_id
        )

    def _get_base_actions_detail(self) -> List[UnfoldAction]:
        """
        Returns all available detail actions, prior to any filtering
        """
        return [self.get_unfold_action(action) for action in self.actions_detail or []]

    def get_actions_row(self, request: HttpRequest) -> List[UnfoldAction]:
        return self._filter_unfold_actions_by_permissions(
            request, self._get_base_actions_row()
        )

    def _get_base_actions_row(self) -> List[UnfoldAction]:
        """
        Returns all available row actions, prior to any filtering
        """
        return [self.get_unfold_action(action) for action in self.actions_row or []]

    def get_actions_submit_line(
        self, request: HttpRequest, object_id: int
    ) -> List[UnfoldAction]:
        return self._filter_unfold_actions_by_permissions(
            request, self._get_base_actions_submit_line(), object_id
        )

    def _get_base_actions_submit_line(self) -> List[UnfoldAction]:
        """
        Returns all available submit row actions, prior to any filtering
        """
        return [
            self.get_unfold_action(action) for action in self.actions_submit_line or []
        ]

    def get_custom_urls(self) -> Tuple[Tuple[str, str, View], ...]:
        """
        Method to get custom views for ModelAdmin with their urls

        Format of custom_urls item:
            ("path_to_view", "name_of_view", view_itself)
        """
        return () if self.custom_urls is None else self.custom_urls

    def get_urls(self) -> list[URLPattern]:
        urls = super().get_urls()

        def wrap(view):
            def wrapper(*args, **kwargs):
                return self.admin_site.admin_view(view)(*args, **kwargs)

            wrapper.model_admin = self
            return update_wrapper(wrapper, view)

        custom_urls = [
            self._path_from_custom_url(custom_url)
            for custom_url in self.get_custom_urls()
        ]

        actions_list_urls = [
            path(
                f"{action.path.removesuffix('/')}/",
                wrap(action.method),
                name=action.action_name,
            )
            for action in self._get_base_actions_list()
        ]

        action_detail_urls = [
            path(
                f"<path:object_id>/{action.path.removesuffix('/')}/",
                wrap(action.method),
                name=action.action_name,
            )
            for action in self._get_base_actions_detail()
        ]

        action_row_urls = [
            path(
                f"<path:object_id>/{action.path.removesuffix('/')}/",
                wrap(action.method),
                name=action.action_name,
            )
            for action in self._get_base_actions_row()
        ]

        return (
            custom_urls
            + action_row_urls
            + actions_list_urls
            + action_detail_urls
            + urls
        )

    def _path_from_custom_url(self, custom_url: tuple[str, str, View]) -> URLPattern:
        return path(
            custom_url[0],
            self.admin_site.admin_view(custom_url[2]),
            {"model_admin": self},
            name=custom_url[1],
        )

    def get_action_choices(
        self,
        request: HttpRequest,
        default_choices: list[tuple[str, str]] = BLANK_CHOICE_DASH,
    ) -> list[tuple[str, str]]:
        default_choices = [("", _("Select action"))]
        return super().get_action_choices(request, default_choices)

    @display(description=mark_safe(checkbox.render("action_toggle_all", 1)))
    def action_checkbox(self, obj: Model) -> str:
        return checkbox.render(helpers.ACTION_CHECKBOX_NAME, str(obj.pk))

    def response_change(self, request: HttpRequest, obj: Model) -> HttpResponse:
        res = super().response_change(request, obj)
        if "next" in request.GET:
            return redirect(request.GET["next"])
        return res

    def response_add(
        self, request: HttpRequest, obj: Model, post_url_continue: str | None = None
    ) -> HttpResponse:
        res = super().response_add(request, obj, post_url_continue)
        if "next" in request.GET:
            return redirect(request.GET["next"])
        return res

    def get_changelist(self, request: HttpRequest, **kwargs: Any) -> ChangeList:
        return ChangeList

    def get_formset_kwargs(
        self, request: HttpRequest, obj: Model, inline: InlineModelAdmin, prefix: str
    ) -> dict[str, Any]:
        formset_kwargs = super().get_formset_kwargs(request, obj, inline, prefix)

        if hasattr(inline, "per_page") and inline.per_page:
            formset_kwargs["request"] = request
            formset_kwargs["per_page"] = inline.per_page

        return formset_kwargs

    def get_changeform_datasets(self, request: HttpRequest) -> list[type[BaseDataset]]:
        return self.change_form_datasets


class BaseInlineMixin:
    formfield_overrides = FORMFIELD_OVERRIDES_INLINE
    readonly_preprocess_fields = {}
    ordering_field = None
    per_page = None
    hide_ordering_field = False
    collapsible = False


class TabularInline(BaseInlineMixin, BaseModelAdminMixin, BaseTabularInline):
    formset = PaginationInlineFormSet


class StackedInline(BaseInlineMixin, BaseModelAdminMixin, BaseStackedInline):
    formset = PaginationInlineFormSet


class GenericStackedInline(
    BaseInlineMixin, BaseModelAdminMixin, BaseGenericStackedInline
):
    formset = PaginationGenericInlineFormSet


class GenericTabularInline(
    BaseInlineMixin, BaseModelAdminMixin, BaseGenericTabularInline
):
    formset = PaginationGenericInlineFormSet
