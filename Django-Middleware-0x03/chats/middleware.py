# chats/middleware.py
from datetime import datetime

class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called
        
        # Get the user (or 'Anonymous' if not authenticated)
        user = request.user.username if request.user.is_authenticated else "Anonymous"
        
        # Log the request information
        log_entry = f"{datetime.now()} - User: {user} - Path: {request.path}\n"
        
        # Write to the log file
        with open("requests.log", "a") as log_file:
            log_file.write(log_entry)
        
        response = self.get_response(request)
        
        # Code to be executed for each request/response after
        # the view is called
        
        return response
