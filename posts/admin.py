from django.contrib import admin
from .models import Author, Post, Comment


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    
    list_display = ['name', 'email', 'user', 'created_at']
    list_filter = ['created_at', 'updated_at']
    search_fields = ['name', 'email']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['name']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'email', 'user')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    
    list_display = ['title', 'author', 'status', 'active', 'published_date']
    list_filter = ['status', 'active', 'published_date', 'created_at', 'author']
    search_fields = ['title', 'content', 'author__name']
    readonly_fields = ['published_date', 'created_at', 'updated_at']
    ordering = ['-published_date']
    list_per_page = 20
    
    fieldsets = (
        ('Content', {
            'fields': ('title', 'content', 'author')
        }),
        ('Publication', {
            'fields': ('status', 'active')
        }),
        ('Timestamps', {
            'fields': ('published_date', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        """Optimize queryset with select_related."""
        return super().get_queryset(request).select_related('author')


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    
    list_display = ['get_post_title', 'user', 'created', 'content_preview']
    list_filter = ['created', 'updated_at', 'post__status']
    search_fields = ['content', 'post__title', 'user__username']
    readonly_fields = ['created', 'updated_at']
    ordering = ['-created']
    list_per_page = 30
    
    fieldsets = (
        ('Comment Details', {
            'fields': ('post', 'content', 'user')
        }),
        ('Timestamps', {
            'fields': ('created', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        """Optimize queryset with select_related."""
        return super().get_queryset(request).select_related('post', 'user', 'post__author')
    
    def get_post_title(self, obj):
        """Display post title in list view."""
        return obj.post.title
    get_post_title.short_description = 'Post'
    get_post_title.admin_order_field = 'post__title'
    

    
    def content_preview(self, obj):
        """Display content preview in list view."""
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Content Preview'


admin.site.site_header = "Django Comments Admin"
admin.site.site_title = "Django Comments"
admin.site.index_title = "Welcome to Django Comments Administration"
