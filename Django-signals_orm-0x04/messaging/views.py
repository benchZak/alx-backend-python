from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_page
from django.db.models import Q
from django.contrib import messages
from .models import Message, User

@login_required
def delete_user(request):
    if request.method == 'POST':
        request.user.delete()
        messages.success(request, 'Your account has been deleted.')
        return redirect('home')
    return render(request, 'messaging/delete_confirm.html')

@login_required
@cache_page(60)
def conversation_thread(request, user_id):
    other_user = get_object_or_404(User, id=user_id)
    messages = Message.objects.filter(
        (Q(sender=request.user) & Q(receiver=other_user)) |
        (Q(sender=other_user) & Q(receiver=request.user))
    ).select_related('sender', 'receiver').order_by('-timestamp')
    return render(request, 'messaging/conversation.html', {
        'messages': messages,
        'other_user': other_user
    })

@login_required
def inbox_unread(request):
    unread_messages = Message.unread.unread_for_user(request.user)
    return render(request, 'messaging/inbox_unread.html', {
        'unread_messages': unread_messages
    })
