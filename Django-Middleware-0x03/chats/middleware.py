# chats/middleware.py
from datetime import datetime, timedelta
from django.http import JsonResponse

class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        user = request.user.username if request.user.is_authenticated else "Anonymous"
        log_entry = f"{datetime.now()} - User: {user} - Path: {request.path}\n"
        
        with open("requests.log", "a") as log_file:
            log_file.write(log_entry)
        
        response = self.get_response(request)
        return response

class OffensiveLanguageMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.ip_requests = {}
        self.limit = 5  # 5 messages
        self.time_window = 60  # 60 seconds (1 minute)

    def __call__(self, request):
        if request.method == 'POST' and ('/messages/' in request.path or '/send/' in request.path):
            ip_address = self.get_client_ip(request)
            current_time = datetime.now()

            if ip_address not in self.ip_requests:
                self.ip_requests[ip_address] = {
                    'count': 1,
                    'first_request_time': current_time
                }
            else:
                time_elapsed = (current_time - self.ip_requests[ip_address]['first_request_time']).total_seconds()
                
                if time_elapsed > self.time_window:
                    self.ip_requests[ip_address] = {
                        'count': 1,
                        'first_request_time': current_time
                    }
                else:
                    self.ip_requests[ip_address]['count'] += 1
                    if self.ip_requests[ip_address]['count'] > self.limit:
                        return JsonResponse(
                            {'error': 'Rate limit exceeded. Please wait 1 minute before sending more messages.'},
                            status=429
                        )

        response = self.get_response(request)
        return response

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
