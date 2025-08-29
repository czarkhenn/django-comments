import pytest
from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APIClient
from datetime import datetime, timedelta
from django.utils import timezone

from posts.models import Post, Comment, Author


@pytest.mark.django_db
class TestPostListAPI:
    """Test cases for Post List API (requirement 2.1)."""
    
    def test_post_list_shows_only_active_posts(self, api_client, user, active_post, inactive_post):
        """
        REQUIREMENT 2.1: Test that post list is working properly and only shows Post.active=True
        
        Test that post list API only shows active posts.
        """
        api_client.force_authenticate(user=user)
        url = reverse('posts:post_list')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1
        assert response.data['results'][0]['id'] == active_post.id
        assert response.data['results'][0]['title'] == active_post.title
        assert response.data['results'][0]['active'] == active_post.active

    def test_post_list_includes_required_fields(self, api_client, user, active_post):
        """Test that post list includes title, content, published_date, and author_name."""
        api_client.force_authenticate(user=user)
        url = reverse('posts:post_list')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        post_data = response.data['results'][0]
        
        required_fields = ['title', 'content', 'published_date', 'author_name']
        for field in required_fields:
            assert field in post_data
            
        assert post_data['author_name'] == active_post.author.name
        
    def test_post_list_filter_by_title(self, api_client, user, author):
        """Test filtering posts by title."""
        api_client.force_authenticate(user=user)
        post1 = Post.objects.create(
            title='Django Tutorial',
            content='Content 1',
            author=author,
            active=True
        )
        post2 = Post.objects.create(
            title='Python Guide',
            content='Content 2',
            author=author,
            active=True
        )
        
        url = reverse('posts:post_list')
        response = api_client.get(url, {'title': 'Django'})
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1
        assert response.data['results'][0]['id'] == post1.id
        
    def test_post_list_filter_by_author_name(self, api_client):
        """Test filtering posts by author name."""
        # Create two authors
        user1 = User.objects.create_user(username='user1', email='user1@test.com')
        author1 = Author.objects.create(name='John Doe', email='john@test.com', user=user1)
        
        user2 = User.objects.create_user(username='user2', email='user2@test.com')
        author2 = Author.objects.create(name='Jane Smith', email='jane@test.com', user=user2)
        
        post1 = Post.objects.create(
            title='Post by John',
            content='Content 1',
            author=author1,
            active=True
        )
        post2 = Post.objects.create(
            title='Post by Jane',
            content='Content 2',
            author=author2,
            active=True
        )
        
        api_client.force_authenticate(user=user1)
        url = reverse('posts:post_list')
        response = api_client.get(url, {'author_name': 'John'})
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1
        assert response.data['results'][0]['id'] == post1.id
        
    def test_post_list_filter_by_published_date_range(self, api_client, user, author):
        """
        REQUIREMENT 2.1: Test that post list with filter is working properly (filtering by published_date should be range of date)
        
        Test filtering posts by published date range.
        """
        api_client.force_authenticate(user=user)
        # Create posts with different dates
        old_date = timezone.now() - timedelta(days=10)
        recent_date = timezone.now() - timedelta(days=2)
        
        old_post = Post.objects.create(
            title='Old Post',
            content='Old content',
            author=author,
            active=True
        )
        old_post.published_date = old_date
        old_post.save()
        
        recent_post = Post.objects.create(
            title='Recent Post',
            content='Recent content',
            author=author,
            active=True
        )
        recent_post.published_date = recent_date
        recent_post.save()
        
        url = reverse('posts:post_list')
        
        # Filter for posts from last 5 days
        date_from = (timezone.now() - timedelta(days=5)).strftime('%Y-%m-%d')
        response = api_client.get(url, {'published_date_from': date_from})
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1
        assert response.data['results'][0]['id'] == recent_post.id

    def test_post_list_filter_by_exact_published_date(self, api_client, user, author):
        """Test filtering posts by exact published date."""
        api_client.force_authenticate(user=user)
        target_date = timezone.now().replace(hour=10, minute=0, second=0, microsecond=0)
        other_date = target_date + timedelta(days=1)
        
        target_post = Post.objects.create(
            title='Target Post',
            content='Target content',
            author=author,
            active=True
        )
        target_post.published_date = target_date
        target_post.save()
        
        other_post = Post.objects.create(
            title='Other Post',
            content='Other content',
            author=author,
            active=True
        )
        other_post.published_date = other_date
        other_post.save()
        
        url = reverse('posts:post_list')
        date_str = target_date.strftime('%Y-%m-%d')
        response = api_client.get(url, {'published_date': date_str})
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1
        assert response.data['results'][0]['id'] == target_post.id

    def test_post_list_search_functionality(self, api_client):
        """Test search functionality across title and author name."""
        user1 = User.objects.create_user(username='user1', email='user1@test.com')
        author1 = Author.objects.create(name='Django Expert', email='django@test.com', user=user1)
        
        user2 = User.objects.create_user(username='user2', email='user2@test.com')
        author2 = Author.objects.create(name='Python Guru', email='python@test.com', user=user2)
        
        post1 = Post.objects.create(
            title='Advanced Django Techniques',
            content='Content about Django',
            author=author1,
            active=True
        )
        post2 = Post.objects.create(
            title='Python Best Practices',
            content='Content about Python',
            author=author2,
            active=True
        )
        post3 = Post.objects.create(
            title='Web Development with Django',
            content='More Django content',
            author=author2,
            active=True
        )
        
        api_client.force_authenticate(user=user1)
        url = reverse('posts:post_list')
        
        # Search should find posts with "Django" in title or author name
        response = api_client.get(url, {'search': 'Django'})
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 2  # 2 posts with "Django" in title
        
        # Search for "Expert" should find post by author name
        response = api_client.get(url, {'search': 'Expert'})
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1
        assert response.data['results'][0]['id'] == post1.id

    def test_post_list_combined_filters(self, api_client):
        """Test combining multiple filters."""
        user1 = User.objects.create_user(username='user1', email='user1@test.com')
        author1 = Author.objects.create(name='John Smith', email='john@test.com', user=user1)
        
        user2 = User.objects.create_user(username='user2', email='user2@test.com')
        author2 = Author.objects.create(name='Jane Doe', email='jane@test.com', user=user2)
        
        # Create posts with different dates
        old_date = timezone.now() - timedelta(days=10)
        recent_date = timezone.now() - timedelta(days=2)
        
        post1 = Post.objects.create(
            title='Django Tutorial by John',
            content='Content 1',
            author=author1,
            active=True
        )
        post1.published_date = recent_date
        post1.save()
        
        post2 = Post.objects.create(
            title='Django Guide by Jane',
            content='Content 2',
            author=author2,
            active=True
        )
        post2.published_date = old_date
        post2.save()
        
        post3 = Post.objects.create(
            title='Python Tutorial by John',
            content='Content 3',
            author=author1,
            active=True
        )
        post3.published_date = recent_date
        post3.save()
        
        api_client.force_authenticate(user=user1)
        url = reverse('posts:post_list')
        
        # Filter by title and author_name
        response = api_client.get(url, {'title': 'Django', 'author_name': 'John'})
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1
        assert response.data['results'][0]['id'] == post1.id
        
        # Filter by author_name and date range
        date_from = (timezone.now() - timedelta(days=5)).strftime('%Y-%m-%d')
        response = api_client.get(url, {'author_name': 'John', 'published_date_from': date_from})
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 2


@pytest.mark.django_db
class TestPostDetailAPI:
    """Test cases for Post Detail API."""
    
    def test_post_detail_with_comments(self, api_client, user, active_post, comment_on_active_post, anonymous_comment):
        """Test post detail shows post with nested comments."""
        api_client.force_authenticate(user=user)
        url = reverse('posts:post_detail', kwargs={'pk': active_post.pk})
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == active_post.id
        assert response.data['title'] == active_post.title
        assert 'comments' in response.data
        assert len(response.data['comments']) == 2
        
        # Check that comments have user field instead of author_name
        for comment in response.data['comments']:
            assert 'user' in comment
        
    def test_post_detail_inactive_post_not_accessible(self, api_client, user, inactive_post):
        """Test that inactive posts are not accessible via detail API."""
        api_client.force_authenticate(user=user)
        url = reverse('posts:post_detail', kwargs={'pk': inactive_post.pk})
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        
    def test_post_detail_returns_full_user_object_when_author_has_user(self, api_client, user, active_post):
        """Test that post detail returns full author object with nested user when author has associated user."""
        api_client.force_authenticate(user=user)
        url = reverse('posts:post_detail', kwargs={'pk': active_post.pk})
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert 'author' in response.data
        
        # Verify author object is returned with expected fields
        author_data = response.data['author']
        assert author_data is not None
        assert 'id' in author_data
        assert 'name' in author_data
        assert 'email' in author_data
        assert 'user' in author_data
        assert 'created_at' in author_data
        assert 'updated_at' in author_data
        
        # Verify nested user object has expected fields
        user_data = author_data['user']
        assert user_data is not None
        assert 'id' in user_data
        assert 'username' in user_data
        assert 'email' in user_data
        assert 'first_name' in user_data
        assert 'last_name' in user_data
        assert 'date_joined' in user_data
        
        # Verify the data matches the actual author and user
        expected_author = active_post.author
        expected_user = active_post.author.user
        assert author_data['id'] == expected_author.id
        assert author_data['name'] == expected_author.name
        assert author_data['email'] == expected_author.email
        assert user_data['id'] == expected_user.id
        assert user_data['username'] == expected_user.username
        assert user_data['email'] == expected_user.email
        
    def test_post_detail_returns_null_user_when_author_has_no_user(self, api_client, user):
        """Test that post detail returns author object with null user when author has no associated user."""
        api_client.force_authenticate(user=user)
        # Create an author without an associated user
        author_without_user = Author.objects.create(
            name='Orphaned Author',
            email='orphaned@test.com',
            user=None  # No associated user
        )
        
        # Create a post with this author
        post_without_user = Post.objects.create(
            title='Post by Orphaned Author',
            content='This post has an author with no user.',
            author=author_without_user,
            active=True
        )
        
        url = reverse('posts:post_detail', kwargs={'pk': post_without_user.pk})
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert 'author' in response.data
        
        # Verify author object is returned with expected fields
        author_data = response.data['author']
        assert author_data is not None
        assert 'id' in author_data
        assert 'name' in author_data
        assert 'email' in author_data
        assert 'user' in author_data
        assert 'created_at' in author_data
        assert 'updated_at' in author_data
        
        # Verify the user field is null since author has no associated user
        assert author_data['user'] is None
        assert author_data['name'] == 'Orphaned Author'
        assert author_data['email'] == 'orphaned@test.com'
        
        # Verify other fields are still present
        assert response.data['title'] == 'Post by Orphaned Author'


@pytest.mark.django_db
class TestPostCreateAPI:
    """Test cases for Post Create API (requirement 3.4)."""
    
    def test_create_post_as_authenticated_author(self, api_client, author_user):
        """
        REQUIREMENT 3.4: Test that you can create a Post as an author using the api
        
        Test that authenticated users can create posts.
        """
        api_client.force_authenticate(user=author_user)
        
        url = reverse('posts:post_create')
        data = {
            'title': 'New Test Post',
            'content': 'This is new test content.',
            'status': 'published'
        }
        
        response = api_client.post(url, data)
        
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['title'] == data['title']
        assert response.data['content'] == data['content']
        assert 'author_name' in response.data
        
        # Verify post was created in database
        post = Post.objects.get(id=response.data['id'])
        assert post.title == data['title']
        assert post.author.user == author_user
        
    def test_create_post_unauthenticated_fails(self, api_client):
        """Test that unauthenticated users cannot create posts."""
        url = reverse('posts:post_create')
        data = {
            'title': 'New Test Post',
            'content': 'This is new test content.',
            'status': 'published'
        }
        
        response = api_client.post(url, data)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestPostUpdateAPI:
    """Test cases for Post Update API (requirement 3.5)."""
    
    def test_update_post_as_owner(self, api_client, author_user, active_post):
        """
        REQUIREMENT 3.5: Test that you can edit a Post as an author using the api
        
        Test that post owners can edit their posts.
        """
        api_client.force_authenticate(user=author_user)
        
        url = reverse('posts:post_update', kwargs={'pk': active_post.pk})
        data = {
            'title': 'Updated Title',
            'content': 'Updated content.',
            'active': False
        }
        
        response = api_client.put(url, data)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['title'] == data['title']
        assert response.data['content'] == data['content']
        assert response.data['active'] == data['active']
        
        # Verify changes in database
        active_post.refresh_from_db()
        assert active_post.title == data['title']
        assert active_post.content == data['content']
        assert active_post.active == data['active']
        
    def test_update_post_as_non_owner_fails(self, api_client, another_user, active_post):
        """Test that non-owners cannot edit posts."""
        api_client.force_authenticate(user=another_user)
        
        url = reverse('posts:post_update', kwargs={'pk': active_post.pk})
        data = {
            'title': 'Hacked Title',
            'content': 'Hacked content.',
            'active': False
        }
        
        response = api_client.put(url, data)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        
    def test_update_post_unauthenticated_fails(self, api_client, active_post):
        """Test that unauthenticated users cannot edit posts."""
        url = reverse('posts:post_update', kwargs={'pk': active_post.pk})
        data = {
            'title': 'Hacked Title',
            'content': 'Hacked content.',
            'active': False
        }
        
        response = api_client.put(url, data)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestPostDeleteAPI:
    """Test cases for Post Delete API (requirement 3.6)."""
    
    def test_delete_post_as_owner(self, api_client, author_user, active_post):
        """
        REQUIREMENT 3.6: Test that you can delete a Post an author using the api
        
        Test that post owners can delete their posts.
        """
        api_client.force_authenticate(user=author_user)
        post_id = active_post.id
        
        url = reverse('posts:post_delete', kwargs={'pk': active_post.pk})
        response = api_client.delete(url)
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        
        # Verify post was deleted
        assert not Post.objects.filter(id=post_id).exists()
        
    def test_delete_post_as_non_owner_fails(self, api_client, another_user, active_post):
        """Test that non-owners cannot delete posts."""
        api_client.force_authenticate(user=another_user)
        
        url = reverse('posts:post_delete', kwargs={'pk': active_post.pk})
        response = api_client.delete(url)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        
        # Verify post still exists
        assert Post.objects.filter(id=active_post.id).exists()
        
    def test_delete_post_unauthenticated_fails(self, api_client, active_post):
        """Test that unauthenticated users cannot delete posts."""
        url = reverse('posts:post_delete', kwargs={'pk': active_post.pk})
        response = api_client.delete(url)
        
        # DRF returns 403 for unauthenticated requests when IsAuthenticated permission is used
        assert response.status_code == status.HTTP_403_FORBIDDEN
        
        # Verify post still exists
        assert Post.objects.filter(id=active_post.id).exists()


@pytest.mark.django_db
class TestCommentCreateAPI:
    """Test cases for Comment Create API (requirement 3.3)."""
    
    def test_create_comment_as_authenticated_user(self, api_client, user, active_post):
        """
        REQUIREMENT 3.3: Test that you can create a Comment as a logged-in user on a Post
        
        Test that authenticated users can create comments.
        """
        api_client.force_authenticate(user=user)
        
        url = reverse('posts:comment_create')
        data = {
            'post': active_post.id,
            'content': 'This is a test comment from authenticated user.'
        }
        
        response = api_client.post(url, data)
        
        assert response.status_code == status.HTTP_201_CREATED
        
        # Verify comment was created - use content to find it since response might not have ID
        comment = Comment.objects.get(content=data['content'])
        assert comment.content == data['content']
        assert comment.user == user
        assert comment.post == active_post
        
    def test_create_comment_as_anonymous_user_succeeds(self, api_client, active_post):
        """
        REQUIREMENT 3.3: Test that you can create a Comment as non logged-in user on a Post
        
        Test that anonymous users can create comments with user=None.
        """
        url = reverse('posts:comment_create')
        data = {
            'post': active_post.id,
            'content': 'This is an anonymous comment.'
        }
        
        response = api_client.post(url, data)
        
        assert response.status_code == status.HTTP_201_CREATED
        
        # Verify comment was created with user=None for anonymous users
        comment = Comment.objects.get(content=data['content'])
        assert comment.content == data['content']
        assert comment.user is None  # Anonymous comment should have user=None
        assert comment.post == active_post
        
    def test_create_comment_on_inactive_post_fails(self, api_client, user, inactive_post):
        """Test that comments cannot be created on inactive posts."""
        api_client.force_authenticate(user=user)
        
        url = reverse('posts:comment_create')
        data = {
            'post': inactive_post.id,
            'content': 'This comment should fail.'
        }
        
        response = api_client.post(url, data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'post' in response.data
        assert 'Comments can only be created on active posts' in str(response.data['post'])
