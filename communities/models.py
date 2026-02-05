from django.db import models
from django.conf import settings


class Community(models.Model):
    """Community model - equivalent to Firebase communities collection"""
    
    PRIVACY_CHOICES = [
        ('public', 'Public'),
        ('restricted', 'Restricted'),
        ('private', 'Private'),
    ]
    
    id = models.CharField(max_length=21, primary_key=True)  # Community name as ID
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_communities'
    )
    privacy_type = models.CharField(
        max_length=20,
        choices=PRIVACY_CHOICES,
        default='public'
    )
    number_of_members = models.IntegerField(default=1)
    image_url = models.TextField(blank=True, null=True)  # Legacy: base64 or URL strings
    image = models.ImageField(upload_to='communities/', blank=True, null=True)  # New: proper image storage for S3
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def get_image_url(self):
        """Return full URL for image - supports both ImageField and legacy image_url"""
        # Priority 1: ImageField (new S3-compatible storage)
        if self.image:
            return self.image.url
        # Priority 2: Legacy image_url field (base64 or URL strings)
        if self.image_url:
            return self.image_url
        return None
    
    def __str__(self):
        return f"r/{self.id}"
    
    class Meta:
        db_table = 'communities'
        ordering = ['-created_at']


class CommunityMember(models.Model):
    """Community membership - equivalent to Firebase communitySnippets subcollection"""
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='community_memberships'
    )
    community = models.ForeignKey(
        Community,
        on_delete=models.CASCADE,
        related_name='members'
    )
    is_moderator = models.BooleanField(default=False)
    joined_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'community_members'
        unique_together = ['user', 'community']
        ordering = ['-joined_at']
    
    def __str__(self):
        return f"{self.user.username} in r/{self.community.id}"
