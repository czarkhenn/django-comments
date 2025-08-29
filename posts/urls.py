from django.urls import path
from . import views

app_name = 'posts'

urlpatterns = [
    path('', views.PostListAPIView.as_view(), name='post_list'),
    path('<int:pk>/', views.PostDetailAPIView.as_view(), name='post_detail'),
    path('create/', views.PostCreateAPIView.as_view(), name='post_create'),
    path('<int:pk>/update/', views.PostUpdateAPIView.as_view(), name='post_update'),
    path('<int:pk>/delete/', views.PostDeleteAPIView.as_view(), name='post_delete'),
    path('comments/create/', views.CommentCreateAPIView.as_view(), name='comment_create'),
]
