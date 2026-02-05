from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.db import transaction
from django.shortcuts import get_object_or_404
from .models import Community, CommunityMember
from .serializers import (
    CommunitySerializer,
    CommunitySnippetSerializer,
    CommunityMemberSerializer
)


class CommunityListCreateView(generics.ListCreateAPIView):
    """List all communities or create a new one"""
    queryset = Community.objects.all().order_by('-number_of_members')
    serializer_class = CommunitySerializer
    pagination_class = None  # Disable pagination for communities list
    
    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated()]
        return [AllowAny()]


class CommunityDetailView(generics.RetrieveUpdateAPIView):
    """Get or update community details"""
    queryset = Community.objects.all()
    serializer_class = CommunitySerializer
    lookup_field = 'id'
    
    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH']:
            return [IsAuthenticated()]
        return [AllowAny()]
    
    def perform_update(self, serializer):
        """Only allow creator or moderator to update community"""
        community = self.get_object()
        user = self.request.user
        
        # Check if user is creator or moderator
        is_creator = community.creator_id == user.id
        is_moderator = CommunityMember.objects.filter(
            user=user,
            community=community,
            is_moderator=True
        ).exists()
        
        if not (is_creator or is_moderator):
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("Only moderators can update community details")
        
        serializer.save()


class UserCommunitiesView(generics.ListAPIView):
    """Get user's joined communities (snippets)"""
    serializer_class = CommunitySnippetSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None  # Disable pagination - frontend expects plain array
    
    def get_queryset(self):
        return CommunityMember.objects.filter(user=self.request.user)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def join_community(request, community_id):
    """Join a community"""
    community = get_object_or_404(Community, id=community_id)
    
    # Check if already a member
    existing_membership = CommunityMember.objects.filter(user=request.user, community=community).first()
    if existing_membership:
        # Return success if already member (idempotent operation)
        return Response({
            'message': 'Already a member',
            'is_moderator': existing_membership.is_moderator
        })
    
    with transaction.atomic():
        # Create membership
        CommunityMember.objects.create(
            user=request.user,
            community=community
        )
        # Increment member count
        community.number_of_members += 1
        community.save()
    
    return Response({'message': 'Successfully joined community'})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def leave_community(request, community_id):
    """Leave a community"""
    community = get_object_or_404(Community, id=community_id)
    
    # Get membership
    membership = CommunityMember.objects.filter(
        user=request.user,
        community=community
    ).first()
    
    if not membership:
        return Response(
            {'error': 'Not a member'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    with transaction.atomic():
        # Delete membership
        membership.delete()
        # Decrement member count
        community.number_of_members -= 1
        community.save()
    
    return Response({'message': 'Successfully left community'})

