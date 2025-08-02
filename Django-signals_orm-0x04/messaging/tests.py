from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from .models import Message, Notification, MessageHistory

User = get_user_model()

class MessagingSignalTests(TestCase):
    def setUp(self):
        self.sender = User.objects.create_user(
            username='sender',
            email='sender@example.com',
            password='testpass123'
        )
        self.receiver = User.objects.create_user(
            username='receiver',
            email='receiver@example.com',
            password='testpass123'
        )

    def test_notification_created_on_message_save(self):
        self.assertEqual(Notification.objects.count(), 0)
        
        message = Message.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            content="Hello there!"
        )
        
        self.assertEqual(Notification.objects.count(), 1)
        
        notification = Notification.objects.first()
        self.assertEqual(notification.user, self.receiver)
        self.assertEqual(notification.message, message)
        self.assertFalse(notification.is_read)

    def test_notification_not_created_on_message_update(self):
        message = Message.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            content="Initial message"
        )
        
        Notification.objects.all().delete()
        
        message.content = "Updated message"
        message.save()
        
        self.assertEqual(Notification.objects.count(), 0)

class MessageEditTrackingTests(TestCase):
    def setUp(self):
        self.sender = User.objects.create_user(
            username='sender',
            email='sender@example.com',
            password='testpass123'
        )
        self.receiver = User.objects.create_user(
            username='receiver',
            email='receiver@example.com',
            password='testpass123'
        )
        self.message = Message.objects.create(
            sender=self.sender,
            receiver=self.receiver,
            content="Original content"
        )

    def test_message_edit_history_created(self):
        # Initial state
        self.assertEqual(MessageHistory.objects.count(), 0)
        self.assertFalse(self.message.edited)
        self.assertIsNone(self.message.last_edited)

        # Edit the message
        self.message.content = "Edited content"
        self.message.save()

        # Refresh from db
        self.message.refresh_from_db()

        # Verify history was created
        self.assertEqual(MessageHistory.objects.count(), 1)
        history = MessageHistory.objects.first()
        self.assertEqual(history.message, self.message)
        self.assertEqual(history.old_content, "Original content")
        self.assertEqual(history.edited_by, self.sender)

        # Verify message flags were updated
        self.assertTrue(self.message.edited)
        self.assertIsNotNone(self.message.last_edited)

    def test_no_history_for_new_messages(self):
        new_message = Message(
            sender=self.sender,
            receiver=self.receiver,
            content="New message"
        )
        new_message.save()

        self.assertEqual(MessageHistory.objects.count(), 0)

    def test_no_history_when_content_unchanged(self):
        # Initial edit to set edited flag
        self.message.content = "First edit"
        self.message.save()

        # Clear history for this test
        MessageHistory.objects.all().delete()

        # Edit without changing content
        self.message.content = "First edit"  # Same content
        self.message.save()

        # No new history should be created
        self.assertEqual(MessageHistory.objects.count(), 0)
