from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class UnreadMessagesManager(models.Manager):
    """
    Custom manager for unread messages with optimized queries.
    """
    def unread_for_user(self, user):
        """
        Returns unread messages for a specific user with optimized queries.
        Uses select_related and only to fetch only necessary fields.
        """
        return self.get_queryset().filter(
            receiver=user,
            is_read=False
        ).select_related(
            'sender'
        ).only(
            'id',
            'content',
            'timestamp',
            'is_read',
            'sender__id',
            'sender__username'
        ).order_by('-timestamp')

    def unread_count_for_user(self, user):
        """
        Returns count of unread messages for a specific user.
        """
        return self.unread_for_user(user).count()
