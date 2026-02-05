from django.db import models
from django.conf import settings
from communities.models import Community


class Post(models.Model):
    """Post model - equivalent to Firebase posts collection"""
    
    community = models.ForeignKey(
        Community,
        on_delete=models.CASCADE,
        related_name='posts'
    )
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='posts'
    )
    title = models.CharField(max_length=300)
    body = models.TextField(blank=True)
    image_url = models.TextField(blank=True, null=True)  # Legacy: base64 or URL strings
    image = models.ImageField(upload_to='posts/', blank=True, null=True)  # New: proper image storage for S3
    number_of_comments = models.IntegerField(default=0)
    vote_status = models.IntegerField(default=0)  # Sum of all votes
    created_at = models.DateTimeField(auto_now_add=True)
    edited_at = models.DateTimeField(auto_now=True)
    
    @property
    def community_id(self):
        return self.community.id
    
    @property
    def community_image_url(self):
        return self.community.image_url
    
    @property
    def user_display_text(self):
        return self.creator.display_name
    
    @property
    def creator_id(self):
        return str(self.creator.id)
    
    def __str__(self):
        return self.title
    
    class Meta:
        db_table = 'posts'
        ordering = ['-created_at']


class PostVote(models.Model):
    """Post vote model - equivalent to Firebase postVotes subcollection"""
    
    VOTE_CHOICES = [
        (1, 'Upvote'),
        (-1, 'Downvote'),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='post_votes'
    )
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='votes'
    )
    community = models.ForeignKey(
        Community,
        on_delete=models.CASCADE,
        related_name='post_votes'
    )
    vote_value = models.IntegerField(choices=VOTE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'post_votes'
        unique_together = ['user', 'post']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} voted {self.vote_value} on {self.post.title}"
