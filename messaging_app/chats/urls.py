# messaging_app/chats/urls.py
from rest_framework_nested import routers
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ConversationViewSet, MessageViewSet

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

router = routers.DefaultRouter()  # <-- exactly routers.DefaultRouter()
router.register(r'conversations', ConversationViewSet, basename='conversation')

# Nested messages inside conversations
convo_router = routers.NestedDefaultRouter(router, r'conversations', lookup='conversation')

router.register(r'messages', MessageViewSet, basename='message')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(convo_router.urls)),

    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/', include('messaging_app.chats.urls')),  # your app's routes
]

