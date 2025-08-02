from django.urls import path
from .views import DeleteAccountView, delete_account, inbox_unread

urlpatterns = [
    # Other URLs...
    path('delete-account/', DeleteAccountView.as_view(), name='delete_account'),
    path('inbox/unread/', inbox_unread, name='inbox_unread'),
    # Or using the function-based view:
    # path('delete-account/', delete_account, name='delete_account'),
]
