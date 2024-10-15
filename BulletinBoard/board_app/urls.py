from django.shortcuts import redirect
from django.urls import path
from .views import PostList, CreatePost, PostDetail, EditPost, DeletePost, ResponsesView, RespondCreateView, \
    accept_response, delete_response

urlpatterns = [
    path('', PostList.as_view(), name='home'),
    path('post/<int:post_id>/', PostDetail.as_view(), name='detail_post'),
    path('created_post/', CreatePost.as_view(), name='created_post'),
    path('post/edit/<int:id>/', EditPost.as_view(), name='edit_post'),
    path('post/delete/<int:pk>/', DeletePost.as_view(), name='delete_post'),
    path('responses/', ResponsesView.as_view(), name='responses'),
    path('responses/<int:pk>', ResponsesView.as_view(), name='responses'),
    path('respond/<int:pk>/', RespondCreateView.as_view(), name='respond'),
    path('response/accept/<int:pk>/', accept_response, name='accept_response'),
    path('response/delete/<int:pk>/', delete_response, name='delete_response'),
]
