from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from django.db import transaction
from django.shortcuts import get_object_or_404
from .models import Post, PostVote
from communities.models import Community
from .serializers import PostSerializer, PostVoteSerializer


class PostListView(generics.ListAPIView):
    """List all posts or posts by community"""
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = None  # Disable pagination for posts list
    
    def get_queryset(self):
        queryset = Post.objects.all()
        community_id = self.request.query_params.get('community_id')
        limit = self.request.query_params.get('limit')
        
        if community_id:
            queryset = queryset.filter(community_id=community_id)
        
        queryset = queryset.select_related('creator', 'community').order_by('-created_at')
        
        # Apply limit if provided
        if limit:
            try:
                queryset = queryset[:int(limit)]
            except (ValueError, TypeError):
                pass  # Ignore invalid limit values
        
        return queryset


class PostCreateView(generics.CreateAPIView):
    """Create a new post"""
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]
    
    def perform_create(self, serializer):
        community_id = self.request.data.get('community_id')
        if not community_id:
            from rest_framework.exceptions import ValidationError
            raise ValidationError({'community_id': 'This field is required.'})
        try:
            community = Community.objects.get(id=community_id)
        except Community.DoesNotExist:
            from rest_framework.exceptions import ValidationError
            raise ValidationError({'community_id': 'Community does not exist.'})
        serializer.save(creator=self.request.user, community=community)


class PostDetailView(generics.RetrieveDestroyAPIView):
    """Get or delete a post"""
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    def perform_destroy(self, instance):
        # Only creator can delete
        if instance.creator != self.request.user:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied('Not authorized')
        instance.delete()


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def vote_post(request, post_id):
    """Vote on a post (upvote/downvote)"""
    post = get_object_or_404(Post, id=post_id)
    vote_value = request.data.get('vote_value')  # 1 or -1
    
    if vote_value not in [1, -1]:
        return Response(
            {'error': 'Invalid vote value'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    with transaction.atomic():
        # Check existing vote
        existing_vote = PostVote.objects.filter(
            user=request.user,
            post=post
        ).first()
        
        if existing_vote:
            if existing_vote.vote_value == vote_value:
                # Remove vote
                post.vote_status -= vote_value
                post.save()
                existing_vote.delete()
                return Response({
                    'message': 'Vote removed',
                    'vote_status': post.vote_status,
                    'removed': True
                })
            else:
                # Change vote
                post.vote_status += (2 * vote_value)
                post.save()
                existing_vote.vote_value = vote_value
                existing_vote.save()
                serializer = PostVoteSerializer(existing_vote)
                return Response({
                    'message': 'Vote changed',
                    'vote_status': post.vote_status,
                    'id': existing_vote.id,
                    **serializer.data
                })
        else:
            # New vote
            new_vote = PostVote.objects.create(
                user=request.user,
                post=post,
                community=post.community,
                vote_value=vote_value
            )
            post.vote_status += vote_value
            post.save()
            serializer = PostVoteSerializer(new_vote)
            return Response({
                'message': 'Vote added',
                'vote_status': post.vote_status,
                'id': new_vote.id,
                **serializer.data
            })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_post_votes(request):
    """Get user's post votes for a community"""
    community_id = request.query_params.get('community_id')
    
    # If no community_id provided, return empty list instead of error
    if not community_id:
        return Response([])
    
    votes = PostVote.objects.filter(
        user=request.user,
        community_id=community_id
    )
    
    serializer = PostVoteSerializer(votes, many=True)
    return Response(serializer.data)
