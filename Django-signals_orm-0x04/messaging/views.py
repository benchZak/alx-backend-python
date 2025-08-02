from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Message

@login_required
def inbox_unread(request):
    # Using the exact required keywords in the query
    unread_messages = Message.objects.filter(
        receiver=request.user,
        is_read=False
    ).select_related('sender').only(
        'id',
        'content',
        'timestamp',
        'sender__id',
        'sender__username'
    ).order_by('-timestamp')
    
    unread_count = unread_messages.count()
    
    return render(request, 'messaging/inbox_unread.html', {
        'unread_messages': unread_messages,
        'unread_count': unread_count
    })
