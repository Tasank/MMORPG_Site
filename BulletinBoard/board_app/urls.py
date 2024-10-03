from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),

    path('post/<int:post_id>/', views.detail_post, name='detail_post'),
]