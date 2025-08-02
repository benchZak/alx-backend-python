from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

User = get_user_model()

class UnreadMessagesManager(models.Manager):
    """
    Custom manager for unread messages with optimized queries.
    """
    def for_user(self, user):
        """
        Returns unread messages for a specific user.
        Uses only() to fetch only necessary fields.
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
            'sender__id',
            'sender__username',
            'sender__email'
        ).order_by('-timestamp')

    def count_for_user(self, user):
        """
        Optimized count of unread messages for a user.
        """
        return self.get_queryset().filter(
            receiver=user,
            is_read=False
        ).count()

class Message(models.Model):
    """
    Message model with read status tracking and custom managers.
    """
    # Standard manager
    objects = models.Manager()
    
    # Custom manager for unread messages
    unread = UnreadMessagesManager()

    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sent_messages',
        verbose_name=_('sender')
    )
    receiver = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='received_messages',
        verbose_name=_('receiver')
    )
    content = models.TextField(verbose_name=_('content'))
    timestamp = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('sent at'))
    is_read = models.BooleanField(
        default=False,
        verbose_name=_('is read'),
        help_text=_('Designates whether the message has been read.'))
    parent_message = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='replies',
        verbose_name=_('parent message'))
    edited = models.BooleanField(
        default=False,
        verbose_name=_('edited'))
    last_edited = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('last edited at'))

    class Meta:
        ordering = ['-timestamp']
        verbose_name = _('message')
        verbose_name_plural = _('messages')
        indexes = [
            models.Index(fields=['receiver', 'is_read']),
            models.Index(fields=['sender', 'receiver']),
            models.Index(fields=['timestamp']),
        ]
        constraints = [
            models.CheckConstraint(
                check=~models.Q(sender=models.F('receiver')),
                name='no_self_messages'
            )
        ]

    def __str__(self):
        return _('Message #{id} from {sender} to {receiver}').format(
            id=self.id,
            sender=self.sender,
            receiver=self.receiver
        )

    def mark_as_read(self):
        """
        Mark message as read and save.
        """
        if not self.is_read:
            self.is_read = True
            self.save(update_fields=['is_read'])

    def mark_as_unread(self):
        """
        Mark message as unread and save.
        """
        if self.is_read:
            self.is_read = False
            self.save(update_fields=['is_read'])

    def clean(self):
        """Validate message relationships."""
        if self.sender == self.receiver:
            raise ValidationError(_('Users cannot send messages to themselves.'))
        super().clean()


class Notification(models.Model):
    """
    Notification model that works with the messaging system.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name=_('user'))
    message = models.ForeignKey(
        Message,
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name=_('message'))
    is_read = models.BooleanField(
        default=False,
        verbose_name=_('is read'))
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('created at'))

    class Meta:
        ordering = ['-created_at']
        verbose_name = _('notification')
        verbose_name_plural = _('notifications')
        indexes = [
            models.Index(fields=['user', 'is_read']),
        ]

    def __str__(self):
        return _('Notification for %(user)s') % {'user': self.user}

    def mark_as_read(self):
        """Mark notification as read and save."""
        if not self.is_read:
            self.is_read = True
            self.save(update_fields=['is_read'])
