import os

# Media files configuration
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Ensure media files are properly served in production
if not DEBUG:
    # Configure for production environment
    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
    
    # If you're using AWS S3 for storage
    # AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
    # AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
    # AWS_STORAGE_BUCKET_NAME = os.environ.get('AWS_STORAGE_BUCKET_NAME')
    # AWS_S3_REGION_NAME = os.environ.get('AWS_S3_REGION_NAME', 'eu-central-1')
    # AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com'
    # AWS_DEFAULT_ACL = 'public-read'
    # AWS_S3_OBJECT_PARAMETERS = {'CacheControl': 'max-age=86400'}