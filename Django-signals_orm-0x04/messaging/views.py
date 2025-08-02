from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.views.decorators.cache import cache_page
from .models import Message, User, Notification

@login_required
def delete_user(request):
    if request.method == 'POST':
        request.user.delete()
        return redirect('home')
    return render(request, 'messaging/delete_confirm.html')

@login_required
@cache_page(60)
def conversation_thread(request, user_id):
    other_user = get_object_or_404(User, id=user_id)
    messages = Message.objects.filter(
        (Q(sender=request.user) & Q(receiver=other_user)) |
        (Q(sender=other_user) & Q(receiver=request.user))
    ).select_related('sender', 'receiver').prefetch_related('replies').order_by('-timestamp')
    
    return render(request, 'messaging/conversation.html', {
        'messages': messages,
        'other_user': other_user
    })

@login_required
def inbox(request):
    unread_messages = Message.objects.filter(
        receiver=request.user,
        is_read=False
    ).select_related('sender').only(
        'id', 'content', 'timestamp', 'sender__username'
    ).order_by('-timestamp')
    
    return render(request, 'messaging/inbox.html', {
        'unread_messages': unread_messages
    })
