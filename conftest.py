import pytest
import django
from django.conf import settings

# Configure Django settings before importing models
if not settings.configured:
    django.setup()

from django.contrib.auth.models import User
from rest_framework.test import APIClient
from posts.models import Author, Post, Comment


@pytest.fixture
def api_client():
    """Fixture for API client."""
    return APIClient()


@pytest.fixture
def user():
    """Fixture for creating a test user."""
    return User.objects.create_user(
        username='testuser',
        email='testuser@example.com',
        password='testpass123'
    )


@pytest.fixture
def author_user():
    """Fixture for creating a test user with author profile."""
    user = User.objects.create_user(
        username='authoruser',
        email='author@example.com',
        password='testpass123'
    )
    author = Author.objects.create(
        name='Test Author',
        email='author@example.com',
        user=user
    )
    return user


@pytest.fixture
def author(author_user):
    """Fixture for getting the author profile."""
    return author_user.author_profile.first()


@pytest.fixture
def another_user():
    """Fixture for creating another test user."""
    return User.objects.create_user(
        username='anotheruser',
        email='another@example.com',
        password='testpass123'
    )


@pytest.fixture
def active_post(author):
    """Fixture for creating an active post."""
    return Post.objects.create(
        title='Test Active Post',
        content='This is test content for an active post.',
        author=author,
        status=Post.StatusChoices.PUBLISHED,
        active=True
    )


@pytest.fixture
def inactive_post(author):
    """Fixture for creating an inactive post."""
    return Post.objects.create(
        title='Test Inactive Post',
        content='This is test content for an inactive post.',
        author=author,
        status=Post.StatusChoices.PUBLISHED,
        active=False
    )


@pytest.fixture
def draft_post(author):
    """Fixture for creating a draft post."""
    return Post.objects.create(
        title='Test Draft Post',
        content='This is test content for a draft post.',
        author=author,
        status=Post.StatusChoices.DRAFT,
        active=True
    )


@pytest.fixture
def comment_on_active_post(active_post, user):
    """Fixture for creating a comment on an active post."""
    return Comment.objects.create(
        post=active_post,
        content='This is a test comment.',
        user=user
    )


@pytest.fixture
def anonymous_comment(active_post):
    """Fixture for creating an anonymous comment."""
    return Comment.objects.create(
        post=active_post,
        content='This is an anonymous comment.',
        user=None
    )
