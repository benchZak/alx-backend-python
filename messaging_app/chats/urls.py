from rest_framework_nested import routers
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ConversationViewSet, MessageViewSet
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

router = DefaultRouter()
router.register(r'conversations', ConversationViewSet, basename='conversation')

convo_router = routers.NestedDefaultRouter(router, r'conversations', lookup='conversation')
convo_router.register(r'messages', MessageViewSet, basename='conversation-messages')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(convo_router.urls)),
    # JWT endpoints here only if you're calling them from /api/chats/token/
    # Otherwise, leave JWT only in project-level urls.py
]
