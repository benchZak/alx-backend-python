from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

User = get_user_model()

class Message(models.Model):
    """
    Represents a message sent between users.
    Includes tracking for edits and read status.
    """
    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sent_messages',
        verbose_name=_('sender'),
        help_text=_('User who sent the message')
    )
    receiver = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='received_messages',
        verbose_name=_('receiver'),
        help_text=_('User who received the message')
    )
    content = models.TextField(
        verbose_name=_('content'),
        help_text=_('The message content')
    )
    timestamp = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('sent at'),
        help_text=_('When the message was sent')
    )
    is_read = models.BooleanField(
        default=False,
        verbose_name=_('is read'),
        help_text=_('Has the message been read by the recipient')
    )
    edited = models.BooleanField(
        default=False,
        verbose_name=_('edited'),
        help_text=_('Has the message been edited')
    )
    last_edited = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('last edited at'),
        help_text=_('When the message was last edited')
    )

    class Meta:
        ordering = ['-timestamp']
        verbose_name = _('message')
        verbose_name_plural = _('messages')
        indexes = [
            models.Index(fields=['sender', 'receiver']),
            models.Index(fields=['timestamp']),
            models.Index(fields=['is_read']),
            models.Index(fields=['edited']),
        ]
        constraints = [
            models.CheckConstraint(
                check=~models.Q(sender=models.F('receiver')),
                name='no_self_messages'
            )
        ]

    def __str__(self):
        return _('Message from %(sender)s to %(receiver)s') % {
            'sender': self.sender,
            'receiver': self.receiver
        }

    def clean(self):
        """Validate that sender and receiver are different."""
        if self.sender == self.receiver:
            raise ValidationError(_('Users cannot send messages to themselves.'))
        super().clean()

    def mark_as_read(self):
        """Mark the message as read and save."""
        if not self.is_read:
            self.is_read = True
            self.save(update_fields=['is_read'])


class MessageHistory(models.Model):
    """
    Tracks historical versions of edited messages.
    """
    message = models.ForeignKey(
        Message,
        on_delete=models.CASCADE,
        related_name='history',
        verbose_name=_('message'),
        help_text=_('The message this history belongs to')
    )
    old_content = models.TextField(
        verbose_name=_('old content'),
        help_text=_('The previous content of the message')
    )
    edited_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('edited at'),
        help_text=_('When this edit was made')
    )
    edited_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_('edited by'),
        help_text=_('User who made this edit')
    )

    class Meta:
        ordering = ['-edited_at']
        verbose_name = _('message history')
        verbose_name_plural = _('message histories')
        indexes = [
            models.Index(fields=['message', 'edited_at']),
        ]
        get_latest_by = 'edited_at'

    def __str__(self):
        return _('History for message %(message_id)s edited at %(edited_at)s') % {
            'message_id': self.message_id,
            'edited_at': self.edited_at.strftime('%Y-%m-%d %H:%M')
        }


class Notification(models.Model):
    """
    Represents a notification for a user about a new message.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name=_('user'),
        help_text=_('User who receives the notification')
    )
    message = models.ForeignKey(
        Message,
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name=_('message'),
        help_text=_('The message this notification is about')
    )
    is_read = models.BooleanField(
        default=False,
        verbose_name=_('is read'),
        help_text=_('Has the notification been read by the user')
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('created at'),
        help_text=_('When the notification was created')
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = _('notification')
        verbose_name_plural = _('notifications')
        indexes = [
            models.Index(fields=['user', 'is_read']),
            models.Index(fields=['created_at']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'message'],
                name='unique_user_message_notification'
            )
        ]

    def __str__(self):
        return _('Notification for %(user)s about message %(message_id)s') % {
            'user': self.user,
            'message_id': self.message_id
        }

    def mark_as_read(self):
        """Mark the notification as read and save."""
        if not self.is_read:
            self.is_read = True
            self.save(update_fields=['is_read'])


class UserProfile(models.Model):
    """
    Extended profile information for users.
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile',
        verbose_name=_('user')
    )
    message_notifications_enabled = models.BooleanField(
        default=True,
        verbose_name=_('message notifications enabled'),
        help_text=_('Enable notifications for new messages')
    )
    message_edit_notifications_enabled = models.BooleanField(
        default=True,
        verbose_name=_('edit notifications enabled'),
        help_text=_('Enable notifications for message edits')
    )
    last_activity = models.DateTimeField(
        auto_now=True,
        verbose_name=_('last activity'),
        help_text=_('When the user was last active')
    )

    class Meta:
        verbose_name = _('user profile')
        verbose_name_plural = _('user profiles')

    def __str__(self):
        return _('Profile for %(username)s') % {'username': self.user.username}
