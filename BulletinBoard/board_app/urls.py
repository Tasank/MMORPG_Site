from django.urls import path
from . import views
from .views import PostList

urlpatterns = [
    path('', PostList.as_view(), name='home'),
    path('post/<int:post_id>/', views.detail_post, name='detail_post'),
    path('created_post/', views.created_post, name='created_post'),
]