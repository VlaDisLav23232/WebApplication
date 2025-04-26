document.addEventListener('DOMContentLoaded', function() {
    // Handle all img tags
    handleImageErrors();
    
    // Handle all div elements with background images (like card-image)
    handleBackgroundImages();
});

function handleImageErrors() {
    document.querySelectorAll('img').forEach(img => {
        // Skip images that already have error handlers
        if (!img.hasAttribute('data-error-handled')) {
            img.setAttribute('data-error-handled', 'true');
            
            // Save the original error handler if one exists
            const originalOnError = img.onerror;
            
            img.onerror = function(e) {
                // Prevent infinite loops
                this.onerror = null;
                
                // Determine the appropriate fallback image
                let fallbackImage = '/static/pictures/fundraisings/default_image.jpg';
                
                // If it's a profile/avatar image
                if (
                    this.classList.contains('avatar-preview') || 
                    this.src.includes('avatar') || 
                    this.classList.contains('profile-pic') ||
                    this.parentElement && this.parentElement.classList.contains('profile-pic')
                ) {
                    fallbackImage = '/static/pictures/profile_page/default.png';
                }
                
                console.log('Image failed to load, using fallback:', this.src, '→', fallbackImage);
                this.src = fallbackImage;
                
                // Call the original error handler if it existed
                if (typeof originalOnError === 'function') {
                    originalOnError.call(this, e);
                }
            };
        }
    });
}

function handleBackgroundImages() {
    // Add a style for background images in case they fail to load
    const style = document.createElement('style');
    style.textContent = `
        .card-image {
            background-color: #e0e0e0;
        }
        .card-image.error-loading {
            background-image: url('/static/pictures/fundraisings/default_image.jpg') !important;
        }
    `;
    document.head.appendChild(style);
    
    // Handle all elements with background-image style
    document.querySelectorAll('[style*="background-image"]').forEach(element => {
        if (!element.hasAttribute('data-bg-handled')) {
            element.setAttribute('data-bg-handled', 'true');
            
            try {
                const url = element.style.backgroundImage.replace(/url\(['"]?(.*?)['"]?\)/i, '$1');
                
                if (url && url !== 'none') {
                    const testImage = new Image();
                    testImage.onerror = function() {
                        console.log('Background image failed to load:', url);
                        element.classList.add('error-loading');
                        element.style.backgroundImage = "url('/static/pictures/fundraisings/default_image.jpg')";
                    };
                    testImage.src = url;
                }
            } catch (e) {
                console.error('Error handling background image:', e);
            }
        }
    });
}
