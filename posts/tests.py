from django.test import TestCase
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import Author, Post, Comment


class AuthorModelTest(TestCase):
    """Test cases for the Author model."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='testpass123'
        )

    def test_author_creation_with_user(self):
        """Test creating an author linked to a user."""
        author = Author.objects.create(
            name='John Doe',
            email='john@example.com',
            user=self.user
        )
        
        self.assertEqual(author.name, 'John Doe')
        self.assertEqual(author.email, 'john@example.com')
        self.assertEqual(author.user, self.user)
        self.assertIsNotNone(author.created_at)
        self.assertIsNotNone(author.updated_at)

    def test_author_creation_without_user(self):
        """Test creating an author without linking to a user."""
        author = Author.objects.create(
            name='Jane Smith',
            email='jane@example.com'
        )
        
        self.assertEqual(author.name, 'Jane Smith')
        self.assertEqual(author.email, 'jane@example.com')
        self.assertIsNone(author.user)

    def test_author_email_unique_constraint(self):
        """Test that author email must be unique."""
        Author.objects.create(
            name='John Doe',
            email='john@example.com'
        )
        
        with self.assertRaises(IntegrityError):
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
        
        self.assertEqual(str(author), 'John Doe')

    def test_author_ordering(self):
        """Test that authors are ordered by name."""
        author_b = Author.objects.create(name='Bob', email='bob@example.com')
        author_a = Author.objects.create(name='Alice', email='alice@example.com')
        author_c = Author.objects.create(name='Charlie', email='charlie@example.com')
        
        authors = list(Author.objects.all())
        self.assertEqual(authors[0], author_a)
        self.assertEqual(authors[1], author_b)
        self.assertEqual(authors[2], author_c)


class PostModelTest(TestCase):
    """Test cases for the Post model."""

    def setUp(self):
        """Set up test data."""
        self.author = Author.objects.create(
            name='Test Author',
            email='author@example.com'
        )

    def test_post_creation_with_defaults(self):
        """Test creating a post with default values."""
        post = Post.objects.create(
            title='Test Post',
            content='This is test content.',
            author=self.author
        )
        
        self.assertEqual(post.title, 'Test Post')
        self.assertEqual(post.content, 'This is test content.')
        self.assertEqual(post.author, self.author)
        self.assertEqual(post.status, Post.StatusChoices.DRAFT)
        self.assertTrue(post.active)
        self.assertIsNotNone(post.published_date)
        self.assertIsNotNone(post.created_at)
        self.assertIsNotNone(post.updated_at)

    def test_post_creation_with_published_status(self):
        """Test creating a published post."""
        post = Post.objects.create(
            title='Published Post',
            content='This is published content.',
            author=self.author,
            status=Post.StatusChoices.PUBLISHED
        )
        
        self.assertEqual(post.status, Post.StatusChoices.PUBLISHED)
        self.assertTrue(post.is_published)

    def test_post_creation_with_inactive_status(self):
        """Test creating an inactive post."""
        post = Post.objects.create(
            title='Inactive Post',
            content='This is inactive content.',
            author=self.author,
            status=Post.StatusChoices.PUBLISHED,
            active=False
        )
        
        self.assertEqual(post.status, Post.StatusChoices.PUBLISHED)
        self.assertFalse(post.active)
        self.assertFalse(post.is_published)

    def test_post_str_method(self):
        """Test the string representation of Post."""
        post = Post.objects.create(
            title='Test Post Title',
            content='Test content',
            author=self.author
        )
        
        self.assertEqual(str(post), 'Test Post Title')

    def test_post_is_published_property(self):
        """Test the is_published property logic."""
        # Draft post should not be published
        draft_post = Post.objects.create(
            title='Draft Post',
            content='Draft content',
            author=self.author,
            status=Post.StatusChoices.DRAFT
        )
        self.assertFalse(draft_post.is_published)
        
        # Published and active post should be published
        published_post = Post.objects.create(
            title='Published Post',
            content='Published content',
            author=self.author,
            status=Post.StatusChoices.PUBLISHED,
            active=True
        )
        self.assertTrue(published_post.is_published)
        
        # Published but inactive post should not be published
        inactive_post = Post.objects.create(
            title='Inactive Post',
            content='Inactive content',
            author=self.author,
            status=Post.StatusChoices.PUBLISHED,
            active=False
        )
        self.assertFalse(inactive_post.is_published)

    def test_post_ordering(self):
        """Test that posts are ordered by published_date descending."""
        post1 = Post.objects.create(
            title='First Post',
            content='First content',
            author=self.author
        )
        post2 = Post.objects.create(
            title='Second Post',
            content='Second content',
            author=self.author
        )
        
        posts = list(Post.objects.all())
        self.assertEqual(posts[0], post2)
        self.assertEqual(posts[1], post1)

    def test_post_cascade_delete_with_author(self):
        """Test that posts are deleted when author is deleted."""
        post = Post.objects.create(
            title='Test Post',
            content='Test content',
            author=self.author
        )
        
        post_id = post.id
        self.author.delete()
        
        with self.assertRaises(Post.DoesNotExist):
            Post.objects.get(id=post_id)


class CommentModelTest(TestCase):
    """Test cases for the Comment model."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='commenter',
            email='commenter@example.com',
            password='testpass123'
        )
        self.author = Author.objects.create(
            name='Post Author',
            email='postauthor@example.com'
        )
        self.post = Post.objects.create(
            title='Test Post',
            content='Test post content',
            author=self.author
        )

    def test_comment_creation_with_user(self):
        """Test creating a comment with a user."""
        comment = Comment.objects.create(
            post=self.post,
            content='This is a test comment.',
            user=self.user
        )
        
        self.assertEqual(comment.post, self.post)
        self.assertEqual(comment.content, 'This is a test comment.')
        self.assertEqual(comment.user, self.user)
        self.assertIsNotNone(comment.created)
        self.assertIsNotNone(comment.updated_at)

    def test_comment_creation_without_user(self):
        """Test creating an anonymous comment."""
        comment = Comment.objects.create(
            post=self.post,
            content='This is an anonymous comment.'
        )
        
        self.assertEqual(comment.post, self.post)
        self.assertEqual(comment.content, 'This is an anonymous comment.')
        self.assertIsNone(comment.user)

    def test_comment_str_method_with_user(self):
        """Test the string representation of Comment with user."""
        comment = Comment.objects.create(
            post=self.post,
            content='Test comment',
            user=self.user
        )
        
        expected_str = f"Comment on '{self.post.title}' by {self.user.username}"
        self.assertEqual(str(comment), expected_str)

    def test_comment_str_method_without_user(self):
        """Test the string representation of Comment without user."""
        comment = Comment.objects.create(
            post=self.post,
            content='Anonymous comment'
        )
        
        expected_str = f"Comment on '{self.post.title}' by Anonymous"
        self.assertEqual(str(comment), expected_str)

    def test_comment_author_name_property_with_user(self):
        """Test the author_name property with user."""
        comment = Comment.objects.create(
            post=self.post,
            content='Test comment',
            user=self.user
        )
        
        self.assertEqual(comment.author_name, self.user.username)

    def test_comment_author_name_property_without_user(self):
        """Test the author_name property without user."""
        comment = Comment.objects.create(
            post=self.post,
            content='Anonymous comment'
        )
        
        self.assertEqual(comment.author_name, 'Anonymous')

    def test_comment_ordering(self):
        """Test that comments are ordered by created date descending."""
        comment1 = Comment.objects.create(
            post=self.post,
            content='First comment',
            user=self.user
        )
        comment2 = Comment.objects.create(
            post=self.post,
            content='Second comment',
            user=self.user
        )
        
        comments = list(Comment.objects.all())
        self.assertEqual(comments[0], comment2)
        self.assertEqual(comments[1], comment1)

    def test_comment_cascade_delete_with_post(self):
        """Test that comments are deleted when post is deleted."""
        comment = Comment.objects.create(
            post=self.post,
            content='Test comment',
            user=self.user
        )
        
        comment_id = comment.id
        self.post.delete()
        
        with self.assertRaises(Comment.DoesNotExist):
            Comment.objects.get(id=comment_id)

    def test_comment_user_set_null_on_delete(self):
        """Test that comment user is set to null when user is deleted."""
        comment = Comment.objects.create(
            post=self.post,
            content='Test comment',
            user=self.user
        )
        
        self.user.delete()
        comment.refresh_from_db()
        
        self.assertIsNone(comment.user)
        self.assertEqual(comment.author_name, 'Anonymous')


class ModelRelationshipTest(TestCase):
    """Test cases for model relationships and related managers."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='testpass123'
        )
        self.author = Author.objects.create(
            name='Test Author',
            email='author@example.com',
            user=self.user
        )

    def test_author_posts_relationship(self):
        """Test the reverse relationship from author to posts."""
        post1 = Post.objects.create(
            title='Post 1',
            content='Content 1',
            author=self.author
        )
        post2 = Post.objects.create(
            title='Post 2',
            content='Content 2',
            author=self.author
        )
        
        author_posts = self.author.posts.all()
        self.assertEqual(author_posts.count(), 2)
        self.assertIn(post1, author_posts)
        self.assertIn(post2, author_posts)

    def test_post_comments_relationship(self):
        """Test the reverse relationship from post to comments."""
        post = Post.objects.create(
            title='Test Post',
            content='Test content',
            author=self.author
        )
        
        comment1 = Comment.objects.create(
            post=post,
            content='Comment 1',
            user=self.user
        )
        comment2 = Comment.objects.create(
            post=post,
            content='Comment 2'
        )
        
        post_comments = post.comments.all()
        self.assertEqual(post_comments.count(), 2)
        self.assertIn(comment1, post_comments)
        self.assertIn(comment2, post_comments)

    def test_user_author_profile_relationship(self):
        """Test the reverse relationship from user to author profile."""
        self.assertEqual(self.user.author_profile.first(), self.author)
        self.assertIn(self.author, self.user.author_profile.all())

    def test_user_comments_relationship(self):
        """Test the reverse relationship from user to comments."""
        post = Post.objects.create(
            title='Test Post',
            content='Test content',
            author=self.author
        )
        
        comment1 = Comment.objects.create(
            post=post,
            content='Comment 1',
            user=self.user
        )
        comment2 = Comment.objects.create(
            post=post,
            content='Comment 2',
            user=self.user
        )
        
        user_comments = self.user.comments.all()
        self.assertEqual(user_comments.count(), 2)
        self.assertIn(comment1, user_comments)
        self.assertIn(comment2, user_comments)
