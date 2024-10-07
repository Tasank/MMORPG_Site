from django.urls import path
from .views import PostList, CreatePost, PostDetail, EditPost, DeletePost

urlpatterns = [
    path('', PostList.as_view(), name='home'),
    path('post/<int:post_id>/', PostDetail.as_view(), name='detail_post'),
    path('created_post/', CreatePost.as_view(), name='created_post'),
    path('post/edit/<int:pk>/', EditPost.as_view(), name='edit_post'),
    path('post/delete/<int:pk>/', DeletePost.as_view(), name='delete_post'),
]
