from django.db import models
from django.conf import settings
from posts.models import Post
from communities.models import Community


class Comment(models.Model):
    """Comment model - equivalent to Firebase comments collection"""
    
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    community = models.ForeignKey(
        Community,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    text = models.TextField()
    creator_photo_url = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    @property
    def creator_display_text(self):
        return self.creator.display_name
    
    @property
    def creator_id(self):
        return str(self.creator.id)
    
    @property
    def post_id(self):
        return str(self.post.id)
    
    @property
    def post_title(self):
        return self.post.title
    
    @property
    def community_id(self):
        return self.community.id
    
    def __str__(self):
        return f"Comment by {self.creator.username} on {self.post.title}"
    
    class Meta:
        db_table = 'comments'
        ordering = ['-created_at']
