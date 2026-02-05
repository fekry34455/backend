"""
Tests for Comments app
Coverage: Models, Serializers, Views
"""
import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from comments.models import Comment

User = get_user_model()


@pytest.mark.django_db
class TestCommentModel:
    """Test Comment model"""
    
    def test_create_comment(self, create_user, create_post):
        """Test creating a comment"""
        user = create_user()
        post = create_post()
        
        comment = Comment.objects.create(
            text='Test comment',
            creator=user,
            post=post,
            community=post.community
        )
        
        assert comment.text == 'Test comment'
        assert comment.creator == user
        assert comment.post == post
        
    def test_comment_str_method(self, create_comment):
        """Test comment string representation"""
        comment = create_comment(text='My comment')
        assert 'Comment by' in str(comment)


@pytest.mark.django_db
class TestCommentList:
    """Test comment list endpoint"""
    
    def test_list_comments(self, api_client, create_comment):
        """Test listing comments"""
        create_comment(text='Comment 1')
        create_comment(text='Comment 2')
        
        url = reverse('comments:comment-list')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 2
        
    def test_list_comments_by_post(self, api_client, create_post, create_comment):
        """Test listing comments filtered by post"""
        post1 = create_post(title='Post 1')
        post2 = create_post(title='Post 2')
        
        create_comment(post=post1, text='Comment on post 1')
        create_comment(post=post1, text='Another comment on post 1')
        create_comment(post=post2, text='Comment on post 2')
        
        url = reverse('comments:comment-list')
        response = api_client.get(url, {'post': post1.id})
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 2
        
    def test_comment_includes_creator_info(self, api_client, create_comment):
        """Test that comments include creator information"""
        create_comment()
        
        url = reverse('comments:comment-list')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert 'creatorDisplayText' in response.data['results'][0]


@pytest.mark.django_db
class TestCommentCreate:
    """Test comment creation endpoint"""
    
    def test_create_comment_authenticated(self, authenticated_client, create_post):
        """Test creating comment as authenticated user"""
        post = create_post()
        
        url = reverse('comments:comment-create')
        data = {
            'text': 'New comment',
            'post': post.id
        }
        response = authenticated_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert Comment.objects.filter(text='New comment').exists()
        
    def test_create_comment_unauthenticated(self, api_client, create_post):
        """Test creating comment without authentication"""
        post = create_post()
        
        url = reverse('comments:comment-create')
        data = {
            'text': 'New comment',
            'post': post.id
        }
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        
    def test_create_comment_missing_text(self, authenticated_client, create_post):
        """Test creating comment without text"""
        post = create_post()
        
        url = reverse('comments:comment-create')
        data = {
            'post': post.id
        }
        response = authenticated_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        
    def test_create_comment_missing_post(self, authenticated_client):
        """Test creating comment without post"""
        url = reverse('comments:comment-create')
        data = {
            'text': 'New comment'
        }
        response = authenticated_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        
    def test_create_comment_invalid_post(self, authenticated_client):
        """Test creating comment with invalid post ID"""
        url = reverse('comments:comment-create')
        data = {
            'text': 'New comment',
            'post': 99999
        }
        response = authenticated_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestCommentDelete:
    """Test comment deletion endpoint"""
    
    def test_delete_comment_as_creator(self, authenticated_client, create_comment):
        """Test deleting comment as creator"""
        comment = create_comment(creator=authenticated_client.user)
        
        url = reverse('comments:comment-delete', kwargs={'pk': comment.id})
        response = authenticated_client.delete(url)
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Comment.objects.filter(id=comment.id).exists()
        
    def test_delete_comment_as_non_creator(self, authenticated_client, create_comment, create_user):
        """Test deleting comment as non-creator"""
        other_user = create_user(username='other', email='other@example.com')
        comment = create_comment(creator=other_user)
        
        url = reverse('comments:comment-delete', kwargs={'pk': comment.id})
        response = authenticated_client.delete(url)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
        
    def test_delete_comment_unauthenticated(self, api_client, create_comment):
        """Test deleting comment without authentication"""
        comment = create_comment()
        
        url = reverse('comments:comment-delete', kwargs={'pk': comment.id})
        response = api_client.delete(url)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        
    def test_delete_nonexistent_comment(self, authenticated_client):
        """Test deleting non-existent comment"""
        url = reverse('comments:comment-delete', kwargs={'pk': 99999})
        response = authenticated_client.delete(url)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
class TestCommentPermissions:
    """Test comment permissions"""
    
    def test_creator_can_delete_own_comment(self, authenticated_client, create_comment):
        """Test that creator can delete their own comment"""
        comment = create_comment(creator=authenticated_client.user)
        
        url = reverse('comments:comment-delete', kwargs={'pk': comment.id})
        response = authenticated_client.delete(url)
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        
    def test_other_user_cannot_delete_comment(self, api_client, create_user, create_comment):
        """Test that other users cannot delete comments"""
        creator = create_user(username='creator', email='creator@example.com')
        other_user = create_user(username='other', email='other@example.com')
        
        comment = create_comment(creator=creator)
        
        refresh = RefreshToken.for_user(other_user)
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        url = reverse('comments:comment-delete', kwargs={'pk': comment.id})
        response = api_client.delete(url)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestCommentNesting:
    """Test comment nesting and relationships"""
    
    def test_comments_belong_to_post(self, create_post, create_comment):
        """Test that comments are correctly linked to posts"""
        post = create_post()
        comment1 = create_comment(post=post)
        comment2 = create_comment(post=post)
        
        post_comments = Comment.objects.filter(post=post)
        assert post_comments.count() == 2
        assert comment1 in post_comments
        assert comment2 in post_comments
