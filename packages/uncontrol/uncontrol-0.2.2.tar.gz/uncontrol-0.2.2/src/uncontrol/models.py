from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _
from gnupg import GPG

from .gpg import encrypt_symmetric, decrypt_symmetric

User = get_user_model()


def get_user_profile(user: User) -> "UncontrolProfile":
    return UncontrolProfile.objects.get_or_create(user=user)[0]


class BaseModel(models.Model):
    # id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class BaseKey(BaseModel):
    fingerprint = models.CharField(max_length=40, unique=True)
    uids = models.ManyToManyField("GpgUid")

    class Meta(BaseModel.Meta):
        abstract = True
        ordering = ("-created_at",)

    def __str__(self):
        return ", ".join((str(uid) for uid in self.uids.all()))


class UncontrolProfile(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="uncontrol_profile")

    class Meta(BaseModel.Meta):
        verbose_name = _("Chat Fortress User")
        verbose_name_plural = _("Chat Fortress User")

    def __str__(self):
        return str(self.user)


class GpgUid(BaseModel):
    raw = models.CharField(max_length=512, unique=True)

    class Meta(BaseModel.Meta):
        verbose_name = _("GPG UID")
        verbose_name_plural = _("GPG UIDs")

    def __str__(self):
        return self.raw


class PublicKey(BaseKey):
    creator = models.ForeignKey(UncontrolProfile, on_delete=models.CASCADE, related_name="public_keys")
    content = models.TextField()

    class Meta(BaseKey.Meta):
        verbose_name = _("GPG Public Key")
        verbose_name_plural = _("GPG PublicKeys")


class PrivateKey(BaseKey):
    owner = models.ForeignKey(UncontrolProfile, on_delete=models.CASCADE, related_name="private_keys")
    encrypted_content = models.TextField()
    encrypted_passphrase = models.CharField(blank=True, null=True)
    _user_password: str

    class Meta(BaseKey.Meta):
        verbose_name = _("GPG Private Key")
        verbose_name_plural = _("GPG Private Keys")

    def __init__(self, *args, **kwargs):
        if "user_password" in kwargs:
            self.set_user_password(kwargs.pop("user_password"))
        super().__init__(*args, **kwargs)

    @property
    def user_password(self) -> str:
        if not hasattr(self, "_user_password"):
            raise ValueError("User password is not set")
        return self._user_password

    @property
    def content(self) -> str:
        return self.decrypt(self.encrypted_content)

    @content.setter
    def content(self, value: str) -> None:
        self.encrypted_content = self.encrypt(value)

    @property
    def passphrase(self) -> str | None:
        return self.decrypt(self.encrypted_passphrase) if self.encrypted_passphrase else None

    @passphrase.setter
    def passphrase(self, value: str | None) -> None:
        self.encrypted_passphrase = self.encrypt(value) if value else None

    def set_user_password(self, password: str) -> None:
        self._user_password = password

    def decrypt(self, message: str) -> str:
        return decrypt_symmetric(message, self.user_password)

    def encrypt(self, message: str) -> str:
        return encrypt_symmetric(message, self.user_password)


class Membership(BaseModel):
    member = models.ForeignKey(
        UncontrolProfile, on_delete=models.CASCADE, related_name="encryption_group_memberships",
    )
    encryption_group = models.ForeignKey(
        "EncryptionGroup",
        on_delete=models.CASCADE,
        related_name="encryption_group_memberships",
    )
    is_manager = models.BooleanField(_("Is Group Manager"), default=False)

    class Meta(BaseModel.Meta):
        verbose_name = _("Membership")
        verbose_name_plural = _("Memberships")
        unique_together = ("member", "encryption_group")


class EncryptionGroup(BaseModel):
    name = models.CharField(max_length=255)
    members = models.ManyToManyField(
        UncontrolProfile, through=Membership, related_name="encryption_groups"
    )
    public_keys = models.ManyToManyField(PublicKey)

    class Meta(BaseModel.Meta):
        verbose_name = _("Encryption Group")
        verbose_name_plural = _("Encryption Groups")

    def __str__(self):
        return self.name

    def encrypt(self, message: str) -> str:
        breakpoint()
        recipient_keys = [key.content for key in self.public_keys.all()]
        encrypted_data = GPG().encrypt(
            data=message,
            recipients=recipient_keys,
            always_trust=True,
            armor=True,
        )
        if not encrypted_data.ok:
            raise ValueError(f"Verschlüsselung fehlgeschlagen: {encrypted_data.status}")
        return str(encrypted_data)
