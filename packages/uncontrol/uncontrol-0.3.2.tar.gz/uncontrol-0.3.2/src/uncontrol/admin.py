from django.contrib import admin

from .models import UncontrolProfile, PublicKey, PrivateKey, Membership, EncryptionGroup


@admin.register(UncontrolProfile)
class UncontrolProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "id", "created_at", "updated_at")
    search_fields = ("user__username", "user__email")
    list_filter = ("created_at", "updated_at")
    readonly_fields = ("id", "created_at", "updated_at")
    ordering = ("-created_at",)


@admin.register(PublicKey)
class PublicKeyAdmin(admin.ModelAdmin):
    list_display = ("id", "fingerprint", "creator", "created_at", "updated_at")
    search_fields = ("fingerprint", "creator__user__username", "content")
    list_filter = ("created_at", "updated_at")
    readonly_fields = ("id", "uids", "created_at", "updated_at")
    raw_id_fields = ("creator",)
    ordering = ("-created_at",)


@admin.register(PrivateKey)
class PrivateKeyAdmin(admin.ModelAdmin):
    list_display = ("id", "fingerprint", "owner", "created_at", "updated_at")
    search_fields = ("fingerprint", "owner__user__username",)
    list_filter = ("created_at", "updated_at")
    readonly_fields = ("id", "created_at", "updated_at")
    raw_id_fields = ("owner",)
    ordering = ("-created_at",)

    def formfield_for_dbfield(self, db_field, **kwargs):
        if db_field.name == "password":
            kwargs["widget"] = admin.widgets.AdminTextInputWidget()
        return super().formfield_for_dbfield(db_field, **kwargs)


@admin.register(Membership)
class MembershipAdmin(admin.ModelAdmin):
    list_display = ("member", "encryption_group", "is_manager", "created_at", "updated_at")
    search_fields = ("member__user__username", "encryption_group__id")
    list_filter = ("is_manager", "created_at", "updated_at")
    readonly_fields = ("id", "created_at", "updated_at")
    raw_id_fields = ("member", "encryption_group")
    ordering = ("-created_at",)


class EncryptionGroupPublicKeysInline(admin.TabularInline):
    model = EncryptionGroup.public_keys.through
    extra = 0
    verbose_name = "Public Key"
    verbose_name_plural = "Public Keys"
    raw_id_fields = ("publickey",)


@admin.register(EncryptionGroup)
class EncryptionGroupAdmin(admin.ModelAdmin):
    list_display = ("id", "created_at", "updated_at")
    search_fields = ("id",)
    list_filter = ("created_at", "updated_at")
    readonly_fields = ("id", "created_at", "updated_at")
    # filter_horizontal = ("users", "public_keys")
    ordering = ("-created_at",)
    inlines = [EncryptionGroupPublicKeysInline]

    """
    def get_users(self, obj):
        return ", ".join([user.user.username for user in obj.users.all()])

    get_users.short_description = _("Users")

    def get_public_keys_count(self, obj):
        return obj.public_keys.count()

    get_public_keys_count.short_description = _("Public Keys Count")
    """
