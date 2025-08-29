from rest_framework import generics, filters, permissions, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from django_filters import rest_framework as django_filters
from django.db.models import Q
from datetime import datetime

from .models import Post, Comment, Author
from .serializers import (
    PostListSerializer, PostDetailSerializer, PostCreateSerializer, 
    PostUpdateSerializer, CommentCreateSerializer
)


class PostFilter(django_filters.FilterSet):
    """
    Custom filter set for Post model with advanced filtering options.
    """
    title = django_filters.CharFilter(lookup_expr='icontains', help_text='Filter by title (case-insensitive partial match)')
    author_name = django_filters.CharFilter(field_name='author__name', lookup_expr='icontains', help_text='Filter by author name (case-insensitive partial match)')
    published_date = django_filters.DateFilter(field_name='published_date__date', help_text='Filter by exact published date (YYYY-MM-DD)')
    published_date_from = django_filters.DateFilter(field_name='published_date__date', lookup_expr='gte', help_text='Filter posts published from this date onwards (YYYY-MM-DD)')
    published_date_to = django_filters.DateFilter(field_name='published_date__date', lookup_expr='lte', help_text='Filter posts published up to this date (YYYY-MM-DD)')
    
    class Meta:
        model = Post
        fields = ['title', 'author_name', 'published_date', 'published_date_from', 'published_date_to']



class PostListAPIView(generics.ListAPIView):
    """
    List all active posts with comprehensive filtering capabilities.
    
    Available filters:
    - title: Filter by title (case-insensitive partial match)
    - author_name: Filter by author name (case-insensitive partial match)
    - published_date: Filter by exact published date (YYYY-MM-DD)
    - published_date_from: Filter posts published from this date onwards (YYYY-MM-DD)
    - published_date_to: Filter posts published up to this date (YYYY-MM-DD)
    - search: Search in title and author name (partial match)
    """
    serializer_class = PostListSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = PostFilter
    search_fields = ['title', 'author__name']
    ordering_fields = ['published_date', 'title']
    ordering = ['-published_date']
    
    def get_queryset(self):
        """Return only active posts with optimized queries."""
        return Post.objects.filter(active=True).select_related('author')


class PostDetailAPIView(generics.RetrieveAPIView):
    """
    Retrieve a specific post with its comments.
    """
    serializer_class = PostDetailSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Return only active posts."""
        return Post.objects.filter(active=True).select_related('author').prefetch_related('comments__user')


class PostCreateAPIView(generics.CreateAPIView):
    """
    Create a new post. Only authenticated users with author profiles can create posts.
    """
    serializer_class = PostCreateSerializer
    permission_classes = [IsAuthenticated]
    
    def perform_create(self, serializer):
        """Ensure the post is created with the current user as author."""
        serializer.save()


class PostUpdateAPIView(generics.UpdateAPIView):
    """
    Update a post (title, content, active field). Only the post owner can update.
    """
    serializer_class = PostUpdateSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Return posts that belong to the current user."""
        return Post.objects.filter(author__user=self.request.user)


class PostDeleteAPIView(generics.DestroyAPIView):
    """
    Delete a post. Only the post owner can delete.
    """
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Return posts that belong to the current user."""
        return Post.objects.filter(author__user=self.request.user)


class CommentCreateAPIView(generics.CreateAPIView):
    """
    Create a comment on a post. Both authenticated and anonymous users can comment.
    """
    serializer_class = CommentCreateSerializer
    permission_classes = [AllowAny]
    
    def perform_create(self, serializer):
        """Create comment with authenticated user or None for anonymous users."""
        user = self.request.user if self.request.user.is_authenticated else None
        serializer.save(user=user)
