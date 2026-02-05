from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from django.shortcuts import get_object_or_404
from .models import Comment
from posts.models import Post
from .serializers import CommentSerializer


class CommentListView(generics.ListAPIView):
    """List comments for a post"""
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        post_id = self.request.query_params.get('post')
        if post_id:
            return Comment.objects.filter(post_id=post_id).select_related('creator', 'post')
        return Comment.objects.all().select_related('creator', 'post')


class CommentCreateView(generics.CreateAPIView):
    """Create a comment"""
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]
    
    def perform_create(self, serializer):
        post_id = self.request.data.get('post')
        if not post_id:
            from rest_framework.exceptions import ValidationError
            raise ValidationError({'post': 'This field is required.'})
        
        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            from rest_framework.exceptions import ValidationError
            raise ValidationError({'post': 'Invalid post ID.'})
        
        # Increment comment count
        post.number_of_comments += 1
        post.save()
        
        serializer.save(
            creator=self.request.user,
            post=post,
            community=post.community,
            creator_photo_url=self.request.user.photo_url
        )


class CommentDeleteView(generics.DestroyAPIView):
    """Delete a comment"""
    queryset = Comment.objects.all()
    permission_classes = [IsAuthenticated]
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        
        # Only creator can delete
        if instance.creator != request.user:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied('Not authorized')
        
        # Decrement comment count
        post = instance.post
        post.number_of_comments -= 1
        post.save()
        
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
