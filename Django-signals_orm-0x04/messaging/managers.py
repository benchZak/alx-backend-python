from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class UnreadMessagesManager(models.Manager):
    def unread_for_user(self, user):
        return self.get_queryset().filter(
            receiver=user,
            is_read=False
        ).select_related('sender').only(
            'id',
            'content',
            'timestamp',
            'sender__id',
            'sender__username'
        ).order_by('-timestamp')
