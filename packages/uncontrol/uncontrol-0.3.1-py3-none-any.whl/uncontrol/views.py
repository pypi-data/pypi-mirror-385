from django import forms
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import TemplateView, UpdateView, CreateView, DeleteView
from htmx_components.views import Modal
from htmx_components.views import ModalFormView

from .forms import PrivateKeyImportForm, PublicKeyImportForm, EncryptionGroupEncryptForm, DecryptMessageForm
from .models import EncryptionGroup, UncontrolProfile, get_user_profile, Membership


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "uncontrol/dashboard.html"
    profile: UncontrolProfile

    def dispatch(self, request, *args, **kwargs):
        self.profile = get_user_profile(request.user)
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        profile = get_user_profile(self.request.user)
        return {
            **super().get_context_data(**kwargs),
            "private_keys": profile.private_keys.all(),
            "encryption_groups": self.get_encryption_groups_qs(profile),
        }

    def get_encryption_groups_qs(self, profile: UncontrolProfile):
        # breakpoint()
        qs = EncryptionGroup.objects.filter(members=profile)
        return qs


class KeyImportView(LoginRequiredMixin, ModalFormView):
    form_class: forms.Form

    # success_url = reverse_lazy("dashboard")

    def get_form_kwargs(self):
        return {
            **super().get_form_kwargs(),
            "profile": get_user_profile(self.request.user),
        }


class PublicKeyImportView(KeyImportView):
    form_class = PublicKeyImportForm
    group: EncryptionGroup

    def dispatch(self, request, *args, **kwargs):
        self.group = EncryptionGroup.objects.get(id=kwargs.pop("group_id"))
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        return {
            **super().get_form_kwargs(),
            "group": self.group,
        }


class PrivateKeyImportView(KeyImportView):
    form_class = PrivateKeyImportForm


class EncryptionGroupCreateView(LoginRequiredMixin, CreateView):
    model = EncryptionGroup
    fields = ["name"]
    template_name = "htmx_components/form.html"
    success_url = reverse_lazy("dashboard")

    def form_valid(self, form):
        form.instance.save()
        Membership.objects.create(
            member=self.request.user.uncontrol_profile,
            encryption_group=form.instance,
            is_manager=True,
        )
        return super().form_valid(form)


class EncryptionGroupUpdateView(LoginRequiredMixin, ModalFormView, UpdateView):
    model = EncryptionGroup
    fields = ["name", "members", "public_keys"]
    template_name = "htmx_components/form.html"
    success_url = reverse_lazy("dashboard")

    def get_form_class(self):
        form_class = super().get_form_class()
        form_class.method = "post"
        return form_class

    def form_valid(self, form):
        response = super().form_valid(form)
        return response


class EncryptionGroupDeleteView(LoginRequiredMixin, DeleteView):
    template_name = "htmx_components/form.html"
    success_url = reverse_lazy("dashboard")
    model = EncryptionGroup

    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.filter(encryption_group_memberships__member=self.request.user.uncontrol_profile,
                       encryption_group_memberships__is_manager=True)
        return qs


class EncryptionGroupRemovePublicKeyView(LoginRequiredMixin, DeleteView):
    template_name = "htmx_components/form.html"
    success_url = reverse_lazy("dashboard")
    model = EncryptionGroup

    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.filter(encryption_group_memberships__member=self.request.user.uncontrol_profile,
                       encryption_group_memberships__is_manager=True)
        return qs

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        public_key_id = self.kwargs.get("pk")
        self.object.public_keys.remove(public_key_id)
        return super().delete(request, *args, **kwargs)


class CryptoOperationView(LoginRequiredMixin, ModalFormView):
    modal = Modal(size="xl")
    template_name = "uncontrol/form_with_result.html"

    def get_form_kwargs(self):
        return {
            **super().get_form_kwargs(),
            "profile": get_user_profile(self.request.user),
        }


class EncryptionGroupEncryptView(CryptoOperationView):
    form_class = EncryptionGroupEncryptForm

    def get_form_kwargs(self):
        return {
            **super().get_form_kwargs(),
            "group": EncryptionGroup.objects.get(id=self.kwargs.get("pk")),
        }


class DecryptMessageView(CryptoOperationView):
    form_class = DecryptMessageForm
