import os
from django.conf import settings
from django.http import HttpResponse, FileResponse

class MediaFileMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Check if the request is for a media file
        if request.path.startswith('/media/'):
            # Get the relative path within media folder
            path = request.path.replace('/media/', '')
            full_path = os.path.join(settings.MEDIA_ROOT, path)
            
            # Check if the file exists
            if os.path.exists(full_path) and os.path.isfile(full_path):
                try:
                    # Serve the file
                    response = FileResponse(open(full_path, 'rb'))
                    # Set appropriate content type based on file extension
                    if full_path.endswith('.jpg') or full_path.endswith('.jpeg'):
                        response['Content-Type'] = 'image/jpeg'
                    elif full_path.endswith('.png'):
                        response['Content-Type'] = 'image/png'
                    elif full_path.endswith('.gif'):
                        response['Content-Type'] = 'image/gif'
                    elif full_path.endswith('.webp'):
                        response['Content-Type'] = 'image/webp'
                    
                    # Add cache control headers for better performance
                    response['Cache-Control'] = 'public, max-age=31536000'
                    return response
                except Exception as e:
                    # Log the error
                    print(f"Error serving media file {full_path}: {str(e)}")
        
        # If not a media file or not found, continue with the normal request
        return self.get_response(request)
