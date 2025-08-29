from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Post, Comment, Author


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for User model to return user details.
    """
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'date_joined']
        read_only_fields = ['id', 'username', 'email', 'first_name', 'last_name', 'date_joined']


class AuthorSerializer(serializers.ModelSerializer):
    """
    Serializer for Author model.
    """
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Author
        fields = ['id', 'name', 'email', 'user', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class CommentSerializer(serializers.ModelSerializer):
    """
    Serializer for Comment model.
    """
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Comment
        fields = ['id', 'content', 'user', 'created', 'updated_at']
        read_only_fields = ['id', 'user', 'created', 'updated_at']


class CommentCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating comments.
    """
    
    class Meta:
        model = Comment
        fields = ['post', 'content']
        
    def validate_post(self, value):
        """
        Validate that comments can only be created on active posts.
        """
        if not value.active:
            raise serializers.ValidationError("Comments can only be created on active posts.")
        return value


class PostListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing posts with basic information.
    """
    author_name = serializers.CharField(source='author.name', read_only=True)
    
    class Meta:
        model = Post
        fields = ['id', 'title', 'content', 'published_date', 'author_name', 'active']
        read_only_fields = ['id', 'published_date', 'author_name']


class PostDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for post detail view with nested comments.
    """
    comments = CommentSerializer(many=True, read_only=True)
    author = AuthorSerializer(read_only=True)
    
    class Meta:
        model = Post
        fields = [
            'id', 'title', 'content', 'published_date', 
            'status', 'active', 'created_at', 'updated_at', 'comments', 'author'
        ]
        read_only_fields = [
            'id', 'published_date', 'created_at', 
            'updated_at', 'comments', 'author'
        ]


class PostCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating posts.
    """
    author_name = serializers.CharField(source='author.name', read_only=True)
    
    class Meta:
        model = Post
        fields = ['id', 'title', 'content', 'published_date', 'author_name', 'status']
        read_only_fields = ['id', 'published_date', 'author_name']
        
    def create(self, validated_data):
        """
        Create a post and associate it with the current user's author profile.
        """
        user = self.context['request'].user
        
        author, created = Author.objects.get_or_create(
            user=user,
            defaults={
                'name': user.get_full_name() or user.username,
                'email': user.email
            }
        )
        
        validated_data['author'] = author
        return super().create(validated_data)


class PostUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating posts (title, content, active field only).
    """
    
    class Meta:
        model = Post
        fields = ['id', 'title', 'content', 'active', 'updated_at']
        read_only_fields = ['id', 'updated_at']
