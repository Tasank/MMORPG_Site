from django.urls import path
from .views import PostList, CreatePost, PostDetail

urlpatterns = [
    path('', PostList.as_view(), name='home'),
    path('post/<int:post_id>/', PostDetail.as_view(), name='detail_post'),
    path('created_post/', CreatePost.as_view(), name='created_post'),
]
