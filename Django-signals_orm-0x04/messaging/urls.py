from django.urls import path
from .views import DeleteAccountView, delete_account

urlpatterns = [
    # Other URLs...
    path('delete-account/', DeleteAccountView.as_view(), name='delete_account'),
    # Or using the function-based view:
    # path('delete-account/', delete_account, name='delete_account'),
]
