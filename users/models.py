from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Custom User model with additional fields"""
    email = models.EmailField(unique=True)
    photo_url_legacy = models.TextField(blank=True, null=True)  # Legacy: base64 or URL strings
    photo = models.ImageField(upload_to='users/', blank=True, null=True)  # New: proper image storage for S3
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    @property
    def photo_url(self):
        """Return full URL for photo - supports both ImageField and legacy photo_url_legacy"""
        # Priority 1: ImageField (new S3-compatible storage)
        if self.photo:
            return self.photo.url
        # Priority 2: Legacy photo_url_legacy field (base64 or URL strings)
        if self.photo_url_legacy:
            return self.photo_url_legacy
        return None
    
    # Display name is extracted from email or can be set separately
    @property
    def display_name(self):
        return self.username or self.email.split('@')[0]
    
    def __str__(self):
        return self.email

    class Meta:
        db_table = 'users'
        ordering = ['-created_at']

