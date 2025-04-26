"""Custom middleware to handle user authentication and redirection."""
import re
from django.shortcuts import redirect

class AuthenticationMiddleware:
    """
    Middleware to check if a user is authenticated and redirect to login if not.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Get current URL path
        path = request.path_info

        # Define public paths that don't require authentication
        public_paths = [
            r'^/$',                      # Home page
            r'^/home/$',                 # Home page with '/home/' path
            r'^/about_us/$',             # About us page
            r'^/login/$',                # Login page
            r'^/register/$',             # Register page
            r'^/admin/.*$'              # Admin pages
        ]

        # Check if the current path matches any public path
        is_public_path = any(re.match(pattern, path) for pattern in public_paths)

        # If user is not authenticated and path is not public, redirect to login
        if not request.user.is_authenticated and not is_public_path:
            if not path.startswith('/login/'):  # Prevent redirect loop
                return redirect('/login/')

        response = self.get_response(request)
        return response
