from django.urls import path
from . import views

urlpatterns = [
    # ... другие URL-адреса ...
    path('site1/', views.site1, name='site1'),
]