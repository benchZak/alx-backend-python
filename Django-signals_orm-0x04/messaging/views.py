from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.db.models import Q, Prefetch
from .models import Message
from .forms import MessageForm, ReplyForm

User = get_user_model()

@login_required
def conversation_list(request):
    """
    List all conversations with message previews.
    Uses select_related to optimize user lookups.
    """
    # Get the last message from each conversation
    conversations = Message.objects.filter(
        Q(sender=request.user) | Q(receiver=request.user)
    ).select_related('sender', 'receiver').order_by('-timestamp')[:50]

    # Organize by other user
    unique_conversations = {}
    for msg in conversations:
        other_user = msg.receiver if msg.sender == request.user else msg.sender
        if other_user.id not in unique_conversations:
            unique_conversations[other_user.id] = {
                'user': other_user,
                'last_message': msg,
                'unread_count': Message.objects.filter(
                    receiver=request.user,
                    sender=other_user,
                    is_read=False
                ).count()
            }

    return render(request, 'messaging/conversation_list.html', {
        'conversations': unique_conversations.values()
    })

@login_required
def conversation_detail(request, user_id):
    """
    Show complete conversation thread with a specific user.
    Uses prefetch_related to optimize replies loading.
    """
    other_user = get_object_or_404(User, id=user_id)
    
    # Get all parent messages in this conversation
    messages = Message.objects.filter(
        (Q(sender=request.user) & Q(receiver=other_user)) |
        (Q(sender=other_user) & Q(receiver=request.user)),
        parent_message__isnull=True
    ).select_related('sender', 'receiver').prefetch_related(
        Prefetch('replies', 
                queryset=Message.objects.select_related('sender', 'receiver')
                .order_by('timestamp'))
    ).order_by('-timestamp')

    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            Message.objects.create(
                sender=request.user,
                receiver=other_user,
                content=form.cleaned_data['content']
            )
            return redirect('conversation_detail', user_id=user_id)
    else:
        form = MessageForm()

    # Mark messages as read when viewing
    Message.objects.filter(
        receiver=request.user,
        sender=other_user,
        is_read=False
    ).update(is_read=True)

    return render(request, 'messaging/conversation_detail.html', {
        'other_user': other_user,
        'messages': messages,
        'form': form
    })

@login_required
def message_thread(request, message_id):
    """
    Show a complete message thread with all replies.
    Uses recursive prefetch_related for optimal performance.
    """
    message = get_object_or_404(
        Message.objects.select_related('sender', 'receiver').prefetch_related(
            Prefetch('replies', 
                    queryset=Message.objects.select_related('sender', 'receiver')
                    .prefetch_related('replies'))
        ),
        id=message_id,
        Q(sender=request.user) | Q(receiver=request.user)
    )

    if request.method == 'POST':
        form = ReplyForm(request.POST)
        if form.is_valid():
            Message.objects.create(
                sender=request.user,
                receiver=message.sender if message.sender != request.user else message.receiver,
                content=form.cleaned_data['content'],
                parent_message=message
            )
            return redirect('message_thread', message_id=message_id)
    else:
        form = ReplyForm()

    # Get the full thread (parent + replies)
    thread = []
    current = message
    while current:
        thread.append(current)
        current = current.parent_message
    thread.reverse()

    # Mark as read
    if message.receiver == request.user and not message.is_read:
        message.is_read = True
        message.save()

    return render(request, 'messaging/message_thread.html', {
        'thread': thread,
        'form': form,
        'root_message': message
    })

@login_required
def send_reply(request, message_id):
    """
    Handle reply submission with proper thread tracking.
    """
    parent_message = get_object_or_404(
        Message.objects.select_related('sender', 'receiver'),
        id=message_id,
        Q(sender=request.user) | Q(receiver=request.user)
    )

    if request.method == 'POST':
        form = ReplyForm(request.POST)
        if form.is_valid():
            reply = Message.objects.create(
                sender=request.user,
                receiver=parent_message.sender if parent_message.sender != request.user else parent_message.receiver,
                content=form.cleaned_data['content'],
                parent_message=parent_message
            )
            return redirect('message_thread', message_id=parent_message.id)
    else:
        form = ReplyForm()

    return render(request, 'messaging/send_reply.html', {
        'parent_message': parent_message,
        'form': form
    })
