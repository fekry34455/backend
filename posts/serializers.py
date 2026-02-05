from rest_framework import serializers
from .models import Post, PostVote
from django.contrib.auth import get_user_model

User = get_user_model()


class PostSerializer(serializers.ModelSerializer):
    """Serializer for Post model"""
    communityId = serializers.CharField(source='community.id', read_only=True)
    communityImageURL = serializers.SerializerMethodField()
    creatorId = serializers.CharField(source='creator.id', read_only=True)
    creatorDisplayText = serializers.CharField(source='creator.display_name', read_only=True)
    numberOfComments = serializers.IntegerField(source='number_of_comments', read_only=True)
    voteStatus = serializers.IntegerField(source='vote_status', read_only=True)
    imageURL = serializers.SerializerMethodField()
    image = serializers.ImageField(write_only=True, required=False, allow_null=True)
    image_url = serializers.CharField(write_only=True, required=False, allow_blank=True, allow_null=True)  # Legacy base64 support
    createdAt = serializers.DateTimeField(source='created_at', read_only=True)
    
    def get_imageURL(self, obj):
        """Return full URL for image - supports both ImageField and legacy image_url"""
        # Priority 1: ImageField (new S3-compatible storage)
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        # Priority 2: Legacy image_url field (base64 or URL strings)
        if obj.image_url:
            return obj.image_url
        return None
    
    def get_communityImageURL(self, obj):
        """Return community image URL for post header display"""
        if obj.community:
            image_url = obj.community.get_image_url()
            if image_url and not image_url.startswith(('http://', 'https://', 'data:')):
                # Build absolute URL for local media files
                request = self.context.get('request')
                if request:
                    return request.build_absolute_uri(image_url)
            return image_url
        return None
    
    class Meta:
        model = Post
        fields = [
            'id', 'communityId', 'communityImageURL', 'creatorId', 'creatorDisplayText',
            'title', 'body', 'image', 'image_url', 'imageURL', 'numberOfComments',
            'voteStatus', 'createdAt'
        ]
        read_only_fields = ['id', 'numberOfComments', 'voteStatus', 'createdAt']


class PostVoteSerializer(serializers.ModelSerializer):
    """Serializer for PostVote model"""
    postId = serializers.IntegerField(source='post.id', read_only=True)
    communityId = serializers.CharField(source='community.id', read_only=True)
    voteValue = serializers.IntegerField(source='vote_value', read_only=True)
    
    class Meta:
        model = PostVote
        fields = ['id', 'postId', 'communityId', 'voteValue']
        read_only_fields = ['id']
