from rest_framework import viewsets, status, filters
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Conversation, Message, User
from .serializers import ConversationSerializer, MessageSerializer
from .permissions import IsOwner
from .permissions import IsParticipantOfConversation
from rest_framework.exceptions import PermissionDenied
from rest_framework.status import HTTP_403_FORBIDDEN


class ConversationViewSet(viewsets.ModelViewSet):
    queryset = Conversation.objects.all()
    serializer_class = ConversationSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['participants__username', 'participants__email']

    def create(self, request, *args, **kwargs):
        # Expecting participant user_ids in the request to create conversation
        participant_ids = request.data.get('participant_ids', [])
        if not participant_ids or not isinstance(participant_ids, list):
            return Response({"error": "participant_ids list is required."}, status=status.HTTP_400_BAD_REQUEST)
        
        # Get User objects
        participants = User.objects.filter(user_id__in=participant_ids)
        if participants.count() != len(participant_ids):
            return Response({"error": "Some participant_ids are invalid."}, status=status.HTTP_400_BAD_REQUEST)

        conversation = Conversation.objects.create()
        conversation.participants.set(participants)
        conversation.save()

        serializer = self.get_serializer(conversation)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def get_queryset(self):
        user = self.request.user
        return Conversation.objects.filter(participants=user)


class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated, IsParticipantOfConversation]
    filter_backends = [filters.SearchFilter]
    search_fields = ['sender__username', 'conversation__conversation_id']

    def create(self, request, *args, **kwargs):
        sender_id = request.data.get('sender_id')
        conversation_id = request.data.get('conversation_id')
        message_body = request.data.get('message_body', '').strip()

        if not sender_id or not conversation_id or not message_body:
            return Response({"error": "sender_id, conversation_id and message_body are required."},
                            status=status.HTTP_400_BAD_REQUEST)

        # Validate sender and conversation exist
        try:
            sender = User.objects.get(user_id=sender_id)
        except User.DoesNotExist:
            return Response({"error": "Invalid sender_id."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            conversation = Conversation.objects.get(conversation_id=conversation_id)
        except Conversation.DoesNotExist:
            return Response({"error": "Invalid conversation_id."}, status=status.HTTP_400_BAD_REQUEST)

        message = Message.objects.create(sender=sender, conversation=conversation, message_body=message_body)
        serializer = self.get_serializer(message)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    def get_queryset(self):
        """
        Return messages in conversations where the user is a participant
        """
        return Message.objects.filter(
            conversation__participants=self.request.user
        )

    def perform_create(self, serializer):
        conversation = serializer.validated_data.get("conversation")
        if self.request.user not in conversation.participants.all():
            return Response(
                {"detail": "You are not a participant of this conversation."},
                status=HTTP_403_FORBIDDEN
            )
        serializer.save(sender=self.request.user)