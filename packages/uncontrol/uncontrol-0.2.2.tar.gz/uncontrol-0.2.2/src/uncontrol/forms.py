from base64 import b64encode, b64decode

from django import forms
from django.contrib.auth.hashers import check_password

from .exceptions import CryptoError
from .gpg import TemporaryGPG
from .models import PrivateKey, PublicKey, GpgUid


class BaseForm(forms.Form):
    action: str | None = None
    method: str = "post"


class PublicKeyImportForm(BaseForm, forms.ModelForm):
    class Meta:
        model = PublicKey
        fields = ["content"]
        widgets = {
            "content": forms.Textarea(attrs={"rows": 10, "cols": 70}),
        }
        labels = {
            "content": "Public Key",
        }
        help_texts = {
            "content": "Enter your public key in PEM format.",
        }

    def __init__(self, group, profile, *args, **kwargs):
        self.group = group
        self.profile = profile
        super().__init__(*args, **kwargs)

    def clean(self):
        public_key = PublicKey(
            content=self.cleaned_data["content"],
            creator=self.profile,
        )
        try:
            gpg = TemporaryGPG([], [public_key])
        except CryptoError as err:
            raise forms.ValidationError(f"Invalid public key: {err}") from err
        return {
            **super().clean(),
            "fingerprint": gpg.list_keys()[0]["fingerprint"],
            "creator": self.profile,
            "uids": gpg.list_keys()[0]["uids"],
        }

    def save(self, **kwargs) -> PublicKey:
        uids = [GpgUid.objects.get_or_create(raw=uid)[0] for uid in self.cleaned_data.pop("uids")]
        instance = PublicKey.objects.update_or_create(
            fingerprint=self.cleaned_data.pop("fingerprint"),
            defaults=self.cleaned_data,
        )[0]
        instance.uids.set(uids)
        self.group.public_keys.add(instance)
        return instance


class PrivateKeyImportForm(BaseForm):
    user_password = forms.CharField(
        widget=forms.PasswordInput(),
        label="User Password",
        help_text="Enter your User passphrase to encrypt your private key.",
        required=True,
    )
    content = forms.CharField(
        widget=forms.Textarea(attrs={"rows": 10, "class": "w-100"}),
        label="Private Key",
        help_text="Enter your private key in PEM format.",
    )
    passphrase = forms.CharField(
        widget=forms.PasswordInput(),
        label="Private Key Passphrase",
        help_text="Enter the passphrase for your private key, if any.",
        required=False,
    )

    def __init__(self, profile, *args, **kwargs):
        self.profile = profile
        super().__init__(*args, **kwargs)

    def clean_user_password(self) -> str:
        user_password = self.cleaned_data["user_password"]
        if not check_password(user_password, self.profile.user.password):
            raise forms.ValidationError("Das eingegebene Passwort ist falsch.")
        return user_password

    def clean(self):
        cleaned_data = super().clean()
        if "user_password" not in cleaned_data:
            raise forms.ValidationError("User password is required.")
        private_key = PrivateKey(
            content=cleaned_data["content"],
            passphrase=cleaned_data["passphrase"],
            user_password=cleaned_data["user_password"],
        )
        gpg = TemporaryGPG([private_key], [])
        return {
            "owner": self.profile,
            "encrypted_content": private_key.encrypted_content,
            "encrypted_passphrase": private_key.encrypted_passphrase,
            "fingerprint": gpg.list_keys(secret=True)[0]["fingerprint"],
            "uids": gpg.list_keys()[0]["uids"],
        }

    def save(self, commit=True) -> PrivateKey:
        uids = [GpgUid.objects.get_or_create(raw=uid)[0] for uid in self.cleaned_data.pop("uids")]
        instance = PrivateKey.objects.update_or_create(
            fingerprint=self.cleaned_data.pop("fingerprint"),
            defaults=self.cleaned_data,
        )[0]
        instance.uids.set(uids)
        return instance


class EncryptionGroupEncryptForm(forms.Form):
    message = forms.CharField(
        widget=forms.Textarea(attrs={"rows": 10, "class": "w-100"}),
        label="Plaintext",
        help_text="Enter the plaintext to be encrypted.",
    )
    processed_message = None

    def __init__(self, group, profile, *args, **kwargs):
        self.group = group
        self.profile = profile
        super().__init__(*args, **kwargs)

    def encrypt(self) -> str:
        gpg = TemporaryGPG([], self.group.public_keys.all())
        encrypted_message = gpg.encrypt(self.cleaned_data["message"])
        return b64encode(encrypted_message.encode()).decode()

    def save(self):
        if not self.processed_message:
            self.processed_message = self.encrypt()
        return self.processed_message


class DecryptMessageForm(forms.Form):
    user_password = forms.CharField(
        widget=forms.PasswordInput(),
        label="User Password",
        help_text="Enter your User passphrase to decrypt your private key.",
        required=True,
    )
    encrypted_message = forms.CharField(
        widget=forms.Textarea(attrs={"rows": 10, "class": "w-100"}),
        label="Encrypted Message",
        help_text="Enter the encrypted message (Base64 encoded).",
    )
    processed_message = None

    def __init__(self, profile, *args, **kwargs):
        self.profile = profile
        super().__init__(*args, **kwargs)

    def clean_user_password(self) -> str:
        user_password = self.cleaned_data["user_password"]
        if not check_password(user_password, self.profile.user.password):
            raise forms.ValidationError("Das eingegebene Passwort ist falsch.")
        return user_password

    def clean_encrypted_message(self) -> str:
        encrypted_message = self.cleaned_data["encrypted_message"]
        try:
            encrypted_message = b64decode(encrypted_message).decode()
        except UnicodeDecodeError:
            pass
        return encrypted_message

    def decrypt(self):
        private_keys = [*self.profile.private_keys.all()]
        for private_key in private_keys:
            private_key.set_user_password(self.cleaned_data["user_password"])
        gpg = TemporaryGPG(private_keys, [])
        try:
            decrypted_message = gpg.decrypt(self.cleaned_data["encrypted_message"])
        except CryptoError as err:
            raise forms.ValidationError(f"Decryption failed: {err}") from err
        return decrypted_message

    def save(self) -> str:
        if not self.processed_message:
            self.processed_message = self.decrypt()
        return self.processed_message
