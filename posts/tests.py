"""
Tests for Posts app
Coverage: Models, Serializers, Views, Voting
"""
import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from posts.models import Post, PostVote

User = get_user_model()


@pytest.mark.django_db
class TestPostModel:
    """Test Post model"""
    
    def test_create_post(self, create_user, create_community):
        """Test creating a post"""
        user = create_user()
        community = create_community()
        
        post = Post.objects.create(
            title='Test Post',
            body='Test content',
            creator=user,
            community=community
        )
        
        assert post.title == 'Test Post'
        assert post.body == 'Test content'
        assert post.creator == user
        assert post.community == community
        assert post.vote_status == 0
        
    def test_post_str_method(self, create_post):
        """Test post string representation"""
        post = create_post(title='My Post')
        assert str(post) == 'My Post'


@pytest.mark.django_db
class TestPostVoteModel:
    """Test PostVote model"""
    
    def test_create_vote(self, create_user, create_post):
        """Test creating a vote"""
        user = create_user()
        post = create_post()
        
        vote = PostVote.objects.create(
            user=user,
            post=post,
            community=post.community,
            vote_value=1
        )
        
        assert vote.user == user
        assert vote.post == post
        assert vote.vote_value == 1
        
    def test_unique_vote_constraint(self, create_user, create_post):
        """Test unique constraint on user-post vote"""
        user = create_user()
        post = create_post()
        
        PostVote.objects.create(user=user, post=post, community=post.community, vote_value=1)
        
        with pytest.raises(Exception):
            PostVote.objects.create(user=user, post=post, community=post.community, vote_value=-1)


@pytest.mark.django_db
class TestPostList:
    """Test post list endpoint"""
    
    def test_list_posts(self, api_client, create_post):
        """Test listing posts"""
        # Clear any existing posts first
        Post.objects.all().delete()
        
        create_post(title='Post 1')
        create_post(title='Post 2')
        
        url = reverse('posts:post-list')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2
        
    def test_list_posts_with_limit(self, api_client, create_post):
        """Test listing posts with limit parameter"""
        for i in range(5):
            create_post(title=f'Post {i}')
        
        url = reverse('posts:post-list')
        response = api_client.get(url, {'limit': 3})
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 3
        
    def test_list_posts_by_community(self, api_client, create_post, create_community):
        """Test listing posts filtered by community"""
        comm1 = create_community(id='comm1')
        comm2 = create_community(id='comm2')
        
        create_post(community=comm1, title='Post 1')
        create_post(community=comm1, title='Post 2')
        create_post(community=comm2, title='Post 3')
        
        url = reverse('posts:post-list')
        response = api_client.get(url, {'community_id': 'comm1'})
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2
        
    def test_posts_include_community_image_url(self, api_client, create_post):
        """Test that posts include communityImageURL"""
        create_post()
        
        url = reverse('posts:post-list')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert 'communityImageURL' in response.data[0]


@pytest.mark.django_db
class TestPostCreate:
    """Test post creation endpoint"""
    
    def test_create_post_authenticated(self, authenticated_client, create_community):
        """Test creating post as authenticated user"""
        community = create_community(id='testcomm')
        
        url = reverse('posts:post-create')
        data = {
            'title': 'New Post',
            'body': 'Post content',
            'community_id': 'testcomm'
        }
        response = authenticated_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert Post.objects.filter(title='New Post').exists()
        
    def test_create_post_unauthenticated(self, api_client, create_community):
        """Test creating post without authentication"""
        create_community(id='testcomm')
        
        url = reverse('posts:post-create')
        data = {
            'title': 'New Post',
            'body': 'Post content',
            'community_id': 'testcomm'
        }
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        
    def test_create_post_invalid_community(self, authenticated_client):
        """Test creating post with invalid community"""
        url = reverse('posts:post-create')
        data = {
            'title': 'New Post',
            'body': 'Post content',
            'community_id': 'nonexistent'
        }
        response = authenticated_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestPostDetail:
    """Test post detail endpoint"""
    
    def test_get_post_detail(self, api_client, create_post):
        """Test getting post details"""
        post = create_post(title='Test Post')
        
        url = reverse('posts:post-detail', kwargs={'pk': post.id})
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['title'] == 'Test Post'
        assert 'communityImageURL' in response.data
        
    def test_get_nonexistent_post(self, api_client):
        """Test getting non-existent post"""
        url = reverse('posts:post-detail', kwargs={'pk': 99999})
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        
    def test_delete_post_as_creator(self, authenticated_client, create_post):
        """Test deleting post as creator"""
        post = create_post(creator=authenticated_client.user)
        
        url = reverse('posts:post-detail', kwargs={'pk': post.id})
        response = authenticated_client.delete(url)
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Post.objects.filter(id=post.id).exists()
        
    def test_delete_post_as_non_creator(self, authenticated_client, create_post, create_user):
        """Test deleting post as non-creator"""
        other_user = create_user(username='other', email='other@example.com')
        post = create_post(creator=other_user)
        
        url = reverse('posts:post-detail', kwargs={'pk': post.id})
        response = authenticated_client.delete(url)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestPostVoting:
    """Test post voting endpoints"""
    
    def test_upvote_post(self, authenticated_client, create_post):
        """Test upvoting a post"""
        post = create_post()
        
        url = reverse('posts:vote-post', kwargs={'post_id': post.id})
        response = authenticated_client.post(url, {
            'vote_value': 1,
            'community_id': post.community.id
        }, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert PostVote.objects.filter(
            user=authenticated_client.user,
            post=post,
            vote_value=1
        ).exists()
        
    def test_downvote_post(self, authenticated_client, create_post):
        """Test downvoting a post"""
        post = create_post()
        
        url = reverse('posts:vote-post', kwargs={'post_id': post.id})
        response = authenticated_client.post(url, {
            'vote_value': -1,
            'community_id': post.community.id
        }, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert PostVote.objects.filter(
            user=authenticated_client.user,
            post=post,
            vote_value=-1
        ).exists()
        
    def test_change_vote(self, authenticated_client, create_post):
        """Test changing a vote"""
        post = create_post()
        PostVote.objects.create(
            user=authenticated_client.user,
            post=post,            community=post.community,            vote_value=1
        )
        
        url = reverse('posts:vote-post', kwargs={'post_id': post.id})
        response = authenticated_client.post(url, {
            'vote_value': -1,
            'community_id': post.community.id
        }, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        vote = PostVote.objects.get(user=authenticated_client.user, post=post)
        assert vote.vote_value == -1
        
    def test_remove_vote(self, authenticated_client, create_post):
        """Test removing a vote"""
        post = create_post()
        PostVote.objects.create(
            user=authenticated_client.user,
            post=post,
            community=post.community,
            vote_value=1
        )
        
        # Click the same vote value again to remove it
        url = reverse('posts:vote-post', kwargs={'post_id': post.id})
        response = authenticated_client.post(url, {
            'vote_value': 1,
            'community_id': post.community.id
        }, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert not PostVote.objects.filter(
            user=authenticated_client.user,
            post=post
        ).exists()
        
    def test_vote_unauthenticated(self, api_client, create_post):
        """Test voting without authentication"""
        post = create_post()
        
        url = reverse('posts:vote-post', kwargs={'post_id': post.id})
        response = api_client.post(url, {
            'vote_value': 1,
            'community_id': post.community.id
        }, format='json')
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestUserPostVotes:
    """Test user post votes endpoint"""
    
    def test_get_user_votes(self, authenticated_client, create_post):
        """Test getting user's votes"""
        post1 = create_post(title='Post 1')
        post2 = create_post(title='Post 2')
        
        PostVote.objects.create(
            user=authenticated_client.user,
            post=post1,
            community=post1.community,
            vote_value=1
        )
        PostVote.objects.create(
            user=authenticated_client.user,
            post=post2,
            community=post2.community,
            vote_value=-1
        )
        
        url = reverse('posts:user-post-votes')
        response = authenticated_client.get(url, {'community_id': post1.community.id})
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1  # At least one vote for the queried community
