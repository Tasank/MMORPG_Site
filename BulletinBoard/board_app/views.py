from django.shortcuts import render
from .models import Post
# Create your views here.
def home(request):
    posts = Post.objects.all()
    return render(request, 'home.html', {'posts': posts})
def detail_post(request, post_id):
    post = Post.objects.get(id=post_id)
    return render(request, 'detail_post.html', {'post': post})