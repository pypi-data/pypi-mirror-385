from django.urls import path

from .views import DashboardView, PrivateKeyImportView, PublicKeyImportView, \
    EncryptionGroupUpdateView, EncryptionGroupCreateView, EncryptionGroupDeleteView, EncryptionGroupRemovePublicKeyView, \
    EncryptionGroupEncryptView, DecryptMessageView

urlpatterns = [
    path('', DashboardView.as_view(), name='dashboard'),
    path('group/<int:group_id>/public-key/create/', PublicKeyImportView.as_view(), name='create-public-key'),
    path('group/<int:group_id>/public-key/<int:pk>/remove/', EncryptionGroupRemovePublicKeyView.as_view(),
         name='group-remove-public-key'),
    path('private-key/create/', PrivateKeyImportView.as_view(), name='create-private-key'),
    path('private-key/<int:pk>/delete/', PrivateKeyImportView.as_view(), name='delete-private-key'),
    path('group/create/', EncryptionGroupCreateView.as_view(), name='create-encryption-group'),
    path('group/<int:pk>/update/', EncryptionGroupUpdateView.as_view(),
         name="update-encryption-group"),
    path('group/<int:pk>/delete/', EncryptionGroupDeleteView.as_view(),
         name='delete-encryption-group'),
    path('group/<int:pk>/encrypt/', EncryptionGroupEncryptView.as_view(),
         name='encryption-group-encrypt'),
    path('decrypt-message/', DecryptMessageView.as_view(), name='decrypt-message'),
]
