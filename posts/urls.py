from django.urls import path
from .views import (
    PostListView, PostDetailView, PostCreateView, PostUpdateView,
    PostDeleteView, add_comment_view, chat_room, like_post, dislike_post
)

app_name = 'posts'

urlpatterns = [
    path('', PostListView.as_view(), name='post_list'),
    path('post/<int:pk>/', PostDetailView.as_view(), name='post_detail'),
    path('post/new/', PostCreateView.as_view(), name='post_create'),
    path(
        'post/<int:pk>/update/',
        PostUpdateView.as_view(),
        name='post_update'
    ),
    path(
        'post/<int:pk>/delete/',
        PostDeleteView.as_view(),
        name='post_delete'
    ),
    path(
        'post/<int:pk>/comment/',
        add_comment_view,
        name='add_comment'
    ),
    path('chat/<str:room_name>/', chat_room, name='chat_room'),
    path(
        'post/<int:pk>/like/',
        like_post,
        name='like_post'
    ),
    path(
        'post/<int:pk>/dislike/',
        dislike_post,
        name='dislike_post'
    ),
]
