import pytest
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import Author, Post, Comment


@pytest.mark.django_db
class TestAuthorModel:
    """Test cases for the Author model."""

    def test_author_creation_with_user(self):
        """Test creating an author linked to a user."""
        user = User.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='testpass123'
        )
        
        author = Author.objects.create(
            name='John Doe',
            email='john@example.com',
            user=user
        )
        
        assert author.name == 'John Doe'
        assert author.email == 'john@example.com'
        assert author.user == user
        assert author.created_at is not None
        assert author.updated_at is not None

    def test_author_creation_without_user(self):
        """Test creating an author without linking to a user."""
        author = Author.objects.create(
            name='Jane Smith',
            email='jane@example.com'
        )
        
        assert author.name == 'Jane Smith'
        assert author.email == 'jane@example.com'
        assert author.user is None

    def test_author_email_unique_constraint(self):
        """Test that author email must be unique."""
        Author.objects.create(
            name='John Doe',
            email='john@example.com'
        )
        
        with pytest.raises(IntegrityError):
            Author.objects.create(
                name='Jane Doe',
                email='john@example.com'
            )

    def test_author_str_method(self):
        """Test the string representation of Author."""
        author = Author.objects.create(
            name='John Doe',
            email='john@example.com'
        )
        
        assert str(author) == 'John Doe'

    def test_author_ordering(self):
        """Test that authors are ordered by name."""
        author_b = Author.objects.create(name='Bob', email='bob@example.com')
        author_a = Author.objects.create(name='Alice', email='alice@example.com')
        author_c = Author.objects.create(name='Charlie', email='charlie@example.com')
        
        authors = list(Author.objects.all())
        assert authors[0] == author_a
        assert authors[1] == author_b
        assert authors[2] == author_c


@pytest.mark.django_db
class TestPostModel:
    """Test cases for the Post model."""

    def test_post_creation_with_defaults(self):
        """Test creating a post with default values."""
        author = Author.objects.create(
            name='Test Author',
            email='author@example.com'
        )
        
        post = Post.objects.create(
            title='Test Post',
            content='This is test content.',
            author=author
        )
        
        assert post.title == 'Test Post'
        assert post.content == 'This is test content.'
        assert post.author == author
        assert post.status == Post.StatusChoices.DRAFT
        assert post.active is True
        assert post.published_date is not None
        assert post.created_at is not None
        assert post.updated_at is not None

    def test_post_creation_with_published_status(self):
        """Test creating a published post."""
        author = Author.objects.create(
            name='Test Author',
            email='author@example.com'
        )
        
        post = Post.objects.create(
            title='Published Post',
            content='This is published content.',
            author=author,
            status=Post.StatusChoices.PUBLISHED
        )
        
        assert post.status == Post.StatusChoices.PUBLISHED
        assert post.is_published is True

    def test_post_creation_with_inactive_status(self):
        """Test creating an inactive post."""
        author = Author.objects.create(
            name='Test Author',
            email='author@example.com'
        )
        
        post = Post.objects.create(
            title='Inactive Post',
            content='This is inactive content.',
            author=author,
            status=Post.StatusChoices.PUBLISHED,
            active=False
        )
        
        assert post.status == Post.StatusChoices.PUBLISHED
        assert post.active is False
        assert post.is_published is False

    def test_post_str_method(self):
        """Test the string representation of Post."""
        author = Author.objects.create(
            name='Test Author',
            email='author@example.com'
        )
        
        post = Post.objects.create(
            title='Test Post Title',
            content='Test content',
            author=author
        )
        
        assert str(post) == 'Test Post Title'

    def test_post_is_published_property(self):
        """Test the is_published property logic."""
        author = Author.objects.create(
            name='Test Author',
            email='author@example.com'
        )
        
        # Draft post should not be published
        draft_post = Post.objects.create(
            title='Draft Post',
            content='Draft content',
            author=author,
            status=Post.StatusChoices.DRAFT
        )
        assert draft_post.is_published is False
        
        # Published and active post should be published
        published_post = Post.objects.create(
            title='Published Post',
            content='Published content',
            author=author,
            status=Post.StatusChoices.PUBLISHED,
            active=True
        )
        assert published_post.is_published is True
        
        # Published but inactive post should not be published
        inactive_post = Post.objects.create(
            title='Inactive Post',
            content='Inactive content',
            author=author,
            status=Post.StatusChoices.PUBLISHED,
            active=False
        )
        assert inactive_post.is_published is False

    def test_post_ordering(self):
        """Test that posts are ordered by published_date descending."""
        author = Author.objects.create(
            name='Test Author',
            email='author@example.com'
        )
        
        post1 = Post.objects.create(
            title='First Post',
            content='First content',
            author=author
        )
        post2 = Post.objects.create(
            title='Second Post',
            content='Second content',
            author=author
        )
        
        posts = list(Post.objects.all())
        assert posts[0] == post2
        assert posts[1] == post1

    def test_post_cascade_delete_with_author(self):
        """Test that posts are deleted when author is deleted."""
        author = Author.objects.create(
            name='Test Author',
            email='author@example.com'
        )
        
        post = Post.objects.create(
            title='Test Post',
            content='Test content',
            author=author
        )
        
        post_id = post.id
        author.delete()
        
        with pytest.raises(Post.DoesNotExist):
            Post.objects.get(id=post_id)


@pytest.mark.django_db
class TestCommentModel:
    """Test cases for the Comment model."""

    def test_comment_creation_with_user(self):
        """Test creating a comment with a user."""
        user = User.objects.create_user(
            username='commenter',
            email='commenter@example.com',
            password='testpass123'
        )
        author = Author.objects.create(
            name='Post Author',
            email='postauthor@example.com'
        )
        post = Post.objects.create(
            title='Test Post',
            content='Test post content',
            author=author
        )
        
        comment = Comment.objects.create(
            post=post,
            content='This is a test comment.',
            user=user
        )
        
        assert comment.post == post
        assert comment.content == 'This is a test comment.'
        assert comment.user == user
        assert comment.created is not None
        assert comment.updated_at is not None

    def test_comment_creation_without_user(self):
        """Test creating an anonymous comment."""
        author = Author.objects.create(
            name='Post Author',
            email='postauthor@example.com'
        )
        post = Post.objects.create(
            title='Test Post',
            content='Test post content',
            author=author
        )
        
        comment = Comment.objects.create(
            post=post,
            content='This is an anonymous comment.'
        )
        
        assert comment.post == post
        assert comment.content == 'This is an anonymous comment.'
        assert comment.user is None

    def test_comment_str_method_with_user(self):
        """Test the string representation of Comment with user."""
        user = User.objects.create_user(
            username='commenter',
            email='commenter@example.com',
            password='testpass123'
        )
        author = Author.objects.create(
            name='Post Author',
            email='postauthor@example.com'
        )
        post = Post.objects.create(
            title='Test Post',
            content='Test post content',
            author=author
        )
        
        comment = Comment.objects.create(
            post=post,
            content='Test comment',
            user=user
        )
        
        expected_str = f"Comment on '{post.title}' by {user.username}"
        assert str(comment) == expected_str

    def test_comment_str_method_without_user(self):
        """Test the string representation of Comment without user."""
        author = Author.objects.create(
            name='Post Author',
            email='postauthor@example.com'
        )
        post = Post.objects.create(
            title='Test Post',
            content='Test post content',
            author=author
        )
        
        comment = Comment.objects.create(
            post=post,
            content='Anonymous comment'
        )
        
        expected_str = f"Comment on '{post.title}' by Anonymous"
        assert str(comment) == expected_str

    def test_comment_author_name_property_with_user(self):
        """Test the author_name property with user."""
        user = User.objects.create_user(
            username='commenter',
            email='commenter@example.com',
            password='testpass123'
        )
        author = Author.objects.create(
            name='Post Author',
            email='postauthor@example.com'
        )
        post = Post.objects.create(
            title='Test Post',
            content='Test post content',
            author=author
        )
        
        comment = Comment.objects.create(
            post=post,
            content='Test comment',
            user=user
        )
        
        assert comment.author_name == user.username

    def test_comment_author_name_property_without_user(self):
        """Test the author_name property without user."""
        author = Author.objects.create(
            name='Post Author',
            email='postauthor@example.com'
        )
        post = Post.objects.create(
            title='Test Post',
            content='Test post content',
            author=author
        )
        
        comment = Comment.objects.create(
            post=post,
            content='Anonymous comment'
        )
        
        assert comment.author_name == 'Anonymous'

    def test_comment_ordering(self):
        """Test that comments are ordered by created date descending."""
        user = User.objects.create_user(
            username='commenter',
            email='commenter@example.com',
            password='testpass123'
        )
        author = Author.objects.create(
            name='Post Author',
            email='postauthor@example.com'
        )
        post = Post.objects.create(
            title='Test Post',
            content='Test post content',
            author=author
        )
        
        comment1 = Comment.objects.create(
            post=post,
            content='First comment',
            user=user
        )
        comment2 = Comment.objects.create(
            post=post,
            content='Second comment',
            user=user
        )
        
        comments = list(Comment.objects.all())
        assert comments[0] == comment2
        assert comments[1] == comment1

    def test_comment_cascade_delete_with_post(self):
        """Test that comments are deleted when post is deleted."""
        user = User.objects.create_user(
            username='commenter',
            email='commenter@example.com',
            password='testpass123'
        )
        author = Author.objects.create(
            name='Post Author',
            email='postauthor@example.com'
        )
        post = Post.objects.create(
            title='Test Post',
            content='Test post content',
            author=author
        )
        
        comment = Comment.objects.create(
            post=post,
            content='Test comment',
            user=user
        )
        
        comment_id = comment.id
        post.delete()
        
        with pytest.raises(Comment.DoesNotExist):
            Comment.objects.get(id=comment_id)

    def test_comment_user_set_null_on_delete(self):
        """Test that comment user is set to null when user is deleted."""
        user = User.objects.create_user(
            username='commenter',
            email='commenter@example.com',
            password='testpass123'
        )
        author = Author.objects.create(
            name='Post Author',
            email='postauthor@example.com'
        )
        post = Post.objects.create(
            title='Test Post',
            content='Test post content',
            author=author
        )
        
        comment = Comment.objects.create(
            post=post,
            content='Test comment',
            user=user
        )
        
        user.delete()
        comment.refresh_from_db()
        
        assert comment.user is None
        assert comment.author_name == 'Anonymous'


@pytest.mark.django_db
class TestModelRelationships:
    """Test cases for model relationships and related managers."""

    def test_author_posts_relationship(self):
        """Test the reverse relationship from author to posts."""
        user = User.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='testpass123'
        )
        author = Author.objects.create(
            name='Test Author',
            email='author@example.com',
            user=user
        )
        
        post1 = Post.objects.create(
            title='Post 1',
            content='Content 1',
            author=author
        )
        post2 = Post.objects.create(
            title='Post 2',
            content='Content 2',
            author=author
        )
        
        author_posts = author.posts.all()
        assert author_posts.count() == 2
        assert post1 in author_posts
        assert post2 in author_posts

    def test_post_comments_relationship(self):
        """Test the reverse relationship from post to comments."""
        user = User.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='testpass123'
        )
        author = Author.objects.create(
            name='Test Author',
            email='author@example.com',
            user=user
        )
        
        post = Post.objects.create(
            title='Test Post',
            content='Test content',
            author=author
        )
        
        comment1 = Comment.objects.create(
            post=post,
            content='Comment 1',
            user=user
        )
        comment2 = Comment.objects.create(
            post=post,
            content='Comment 2'
        )
        
        post_comments = post.comments.all()
        assert post_comments.count() == 2
        assert comment1 in post_comments
        assert comment2 in post_comments

    def test_user_author_profile_relationship(self):
        """Test the reverse relationship from user to author profile."""
        user = User.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='testpass123'
        )
        author = Author.objects.create(
            name='Test Author',
            email='author@example.com',
            user=user
        )
        
        assert user.author_profile.first() == author
        assert author in user.author_profile.all()

    def test_user_comments_relationship(self):
        """Test the reverse relationship from user to comments."""
        user = User.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='testpass123'
        )
        author = Author.objects.create(
            name='Test Author',
            email='author@example.com',
            user=user
        )
        
        post = Post.objects.create(
            title='Test Post',
            content='Test content',
            author=author
        )
        
        comment1 = Comment.objects.create(
            post=post,
            content='Comment 1',
            user=user
        )
        comment2 = Comment.objects.create(
            post=post,
            content='Comment 2',
            user=user
        )
        
        user_comments = user.comments.all()
        assert user_comments.count() == 2
        assert comment1 in user_comments
        assert comment2 in user_comments
