from rest_framework import serializers
from .models import Community, CommunityMember
from django.contrib.auth import get_user_model

User = get_user_model()


class CommunitySerializer(serializers.ModelSerializer):
    """Serializer for Community model"""
    communityId = serializers.CharField(source='id', read_only=True)  # Added for frontend compatibility
    creatorId = serializers.IntegerField(source='creator.id', read_only=True)
    numberOfMembers = serializers.IntegerField(source='number_of_members', read_only=True)
    privacyType = serializers.CharField(source='privacy_type')
    imageURL = serializers.SerializerMethodField()
    image = serializers.ImageField(write_only=True, required=False, allow_null=True)
    image_url = serializers.CharField(write_only=True, required=False, allow_blank=True)
    createdAt = serializers.DateTimeField(source='created_at', read_only=True)
    
    def get_imageURL(self, obj):
        """Return full URL for image - supports both ImageField and legacy image_url"""
        image_url = obj.get_image_url()
        if image_url and not image_url.startswith(('http://', 'https://', 'data:')):
            # Build absolute URL for local media files
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(image_url)
        return image_url
    
    class Meta:
        model = Community
        fields = [
            'id', 'communityId', 'creatorId', 'privacyType', 'numberOfMembers',
            'image', 'image_url', 'imageURL', 'createdAt'
        ]
        read_only_fields = ['numberOfMembers', 'createdAt']
    
    def create(self, validated_data):
        # Creator is set from the request user
        user = self.context['request'].user
        community = Community.objects.create(
            creator=user,
            **validated_data
        )
        # Automatically add creator as a member and moderator
        CommunityMember.objects.create(
            user=user,
            community=community,
            is_moderator=True
        )
        return community


class CommunitySnippetSerializer(serializers.ModelSerializer):
    """Serializer for community snippets (user's joined communities)"""
    id = serializers.CharField(source='community.id', read_only=True)
    communityId = serializers.CharField(source='community.id', read_only=True)
    imageURL = serializers.SerializerMethodField()
    isModerator = serializers.BooleanField(source='is_moderator', read_only=True)
    
    def get_imageURL(self, obj):
        """Return full URL for community image - supports both ImageField and legacy image_url"""
        image_url = obj.community.get_image_url()
        if image_url and not image_url.startswith(('http://', 'https://', 'data:')):
            # Build absolute URL for local media files
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(image_url)
        return image_url
    
    class Meta:
        model = CommunityMember
        fields = ['id', 'communityId', 'imageURL', 'isModerator']


class CommunityMemberSerializer(serializers.ModelSerializer):
    """Serializer for community membership"""
    
    class Meta:
        model = CommunityMember
        fields = ['id', 'user', 'community', 'is_moderator', 'joined_at']
        read_only_fields = ['id', 'joined_at']
