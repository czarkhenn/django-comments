from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Author(models.Model):
    """
    Author model for storing blog post authors.
    """
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True, db_index=True)
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='author_profile'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return self.name


class Post(models.Model):
    """
    Blog post model with status management and author relationship.
    """
    
    class StatusChoices(models.TextChoices):
        DRAFT = 'draft', 'Draft'
        PUBLISHED = 'published', 'Published'

    title = models.CharField(max_length=200)
    content = models.TextField()
    published_date = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(
        Author,
        on_delete=models.CASCADE,
        related_name='posts'
    )
    status = models.CharField(
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.DRAFT,
        db_index=True
    )
    active = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-published_date']
        indexes = [
            models.Index(fields=['status', 'active']),
            models.Index(fields=['published_date']),
            models.Index(fields=['author', 'status']),
            models.Index(fields=['active', 'published_date']),
        ]

    def __str__(self):
        return self.title

    @property
    def is_published(self):
        return self.status == self.StatusChoices.PUBLISHED and self.active


class Comment(models.Model):
    """
    Comment model for blog posts.
    """
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    content = models.TextField()
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='comments'
    )
    created = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created']
        indexes = [
            models.Index(fields=['post', 'created']),
            models.Index(fields=['created']),
            models.Index(fields=['user']),
        ]

    def __str__(self):
        user_info = f"by {self.user.username}" if self.user else "by Anonymous"
        return f"Comment on '{self.post.title}' {user_info}"

    @property
    def author_name(self):
        return self.user.username if self.user else 'Anonymous'
