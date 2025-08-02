from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class UnreadMessagesManager(models.Manager):
    """
    Custom manager for unread messages with optimized queries.
    """
    def get_queryset(self):
        return super().get_queryset().select_related('sender', 'receiver')

    def unread_for_user(self, user):
        """
        Returns unread messages for a specific user with optimized queries.
        """
        return self.filter(
            receiver=user,
            is_read=False
        ).only(
            'id',
            'content',
            'timestamp',
            'is_read',
            'sender__id',
            'sender__username',
            'receiver__id'
        ).order_by('-timestamp')
