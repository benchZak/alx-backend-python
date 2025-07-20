# messaging_app/chats/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ConversationViewSet, MessageViewSet

router = routers.DefaultRouter()  # <-- exactly routers.DefaultRouter()
router.register(r'conversations', ConversationViewSet, basename='conversation')

# Nested messages inside conversations
convo_router = routers.NestedDefaultRouter(router, r'conversations', lookup='conversation')

router.register(r'messages', MessageViewSet, basename='message')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(convo_router.urls)),
]

