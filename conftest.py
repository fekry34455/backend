"""
Pytest configuration and shared fixtures
"""
import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from faker import Faker

User = get_user_model()
fake = Faker()


@pytest.fixture(scope='session')
def django_db_setup():
    """Configure test database"""
    from django.conf import settings
    settings.DATABASES['default'] = {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
        'ATOMIC_REQUESTS': False,
        'AUTOCOMMIT': True,
        'CONN_MAX_AGE': 0,
        'OPTIONS': {},
        'TIME_ZONE': None,
        'USER': '',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
        'TEST': {
            'CHARSET': None,
            'COLLATION': None,
            'NAME': None,
            'MIRROR': None,
        },
    }


@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    """Enable database access for all tests"""
    pass


@pytest.fixture
def api_client():
    """Return API client"""
    return APIClient()


@pytest.fixture
def create_user():
    """Factory to create unique users"""
    def _create_user(**kwargs):
        defaults = {
            'username': fake.user_name() + fake.uuid4()[:8],
            'email': fake.email(),
            'password': 'testpass123'
        }
        defaults.update(kwargs)
        password = defaults.pop('password')
        user = User.objects.create(**defaults)
        user.set_password(password)
        user.save()
        return user
    return _create_user


@pytest.fixture
def authenticated_client(api_client, create_user):
    """Return authenticated API client"""
    user = create_user()
    refresh = RefreshToken.for_user(user)
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    api_client.user = user
    return api_client


@pytest.fixture
def create_community(create_user):
    """Factory to create unique communities"""
    def _create_community(**kwargs):
        if 'creator' not in kwargs:
            kwargs['creator'] = create_user()
        defaults = {
            'id': fake.slug() + fake.uuid4()[:8],
            'privacy_type': 'public'
        }
        defaults.update(kwargs)
        from communities.models import Community
        return Community.objects.create(**defaults)
    return _create_community


@pytest.fixture
def create_post(create_user, create_community):
    """Factory to create posts"""
    def _create_post(**kwargs):
        if 'creator' not in kwargs:
            kwargs['creator'] = create_user()
        if 'community' not in kwargs:
            kwargs['community'] = create_community()
        defaults = {
            'title': fake.sentence(),
            'body': fake.text()
        }
        defaults.update(kwargs)
        from posts.models import Post
        return Post.objects.create(**defaults)
    return _create_post


@pytest.fixture
def create_comment(create_user, create_post):
    """Factory to create comments"""
    def _create_comment(**kwargs):
        if 'creator' not in kwargs:
            kwargs['creator'] = create_user()
        if 'post' not in kwargs:
            kwargs['post'] = create_post()
        if 'community' not in kwargs:
            kwargs['community'] = kwargs.get('post').community
        defaults = {
            'text': fake.sentence()
        }
        defaults.update(kwargs)
        from comments.models import Comment
        return Comment.objects.create(**defaults)
    return _create_comment
