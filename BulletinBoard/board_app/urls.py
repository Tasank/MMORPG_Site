from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('site1/', views.site1, name='site1'),
    path('post/<int:post_id>/', views.detail_post, name='detail_post'),
]