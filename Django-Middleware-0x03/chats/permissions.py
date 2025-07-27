# messaging_app/chats/permissions.py

from rest_framework import permissions 
from rest_framework.permissions import BasePermission

class IsOwner(BasePermission):
    """
    Allows access only to objects owned by the requesting user.
    """
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user  # adjust field name to your model

class IsParticipantOfConversation(permissions.BasePermission):
    """
    Allows access only to users who are participants in the conversation.
    """
    def has_permission(self, request, view):
        # Allow only authenticated users
        return request.user and request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        # Allow only participants of the conversation to access messages
        if request.method in ["GET", "POST", "PUT", "PATCH", "DELETE"]:
            return request.user in obj.conversation.participants.all()
        return False