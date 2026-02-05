from rest_framework import serializers
from .models import Comment
from django.contrib.auth import get_user_model

User = get_user_model()


class CommentSerializer(serializers.ModelSerializer):
    """Serializer for Comment model"""
    creator = serializers.IntegerField(source='creator.id', read_only=True)
    creatorId = serializers.IntegerField(source='creator.id', read_only=True)
    creatorDisplayText = serializers.CharField(source='creator.display_name', read_only=True)
    creatorPhotoURL = serializers.URLField(source='creator.photo_url', read_only=True, allow_null=True)
    post = serializers.IntegerField(write_only=True, required=False)
    postId = serializers.IntegerField(source='post.id', read_only=True)
    community = serializers.CharField(source='community.id', read_only=True)
    communityId = serializers.CharField(source='community.id', read_only=True)
    createdAt = serializers.DateTimeField(source='created_at', read_only=True)
    
    class Meta:
        model = Comment
        fields = [
            'id', 'post', 'postId', 'creator', 'creatorId', 
            'creatorDisplayText', 'creatorPhotoURL', 
            'community', 'communityId', 'text', 'createdAt'
        ]
        read_only_fields = ['id', 'createdAt']
