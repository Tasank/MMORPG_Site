from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import Post
from django.views.generic import ListView
from .forms import PostForm, PostCreateForm

# Create your views here.
class PostList(ListView):
    model = Post
    ordering = ['-created_ad']
    template_name = 'home.html'
    context_object_name = 'posts'

# def home(request):
#     posts = Post.objects.all()
#     return render(request, 'home.html', {'posts': posts})
#

def detail_post(request, post_id):
    post = Post.objects.get(id=post_id)
    return render(request, 'detail_post.html', {'post': post})
@login_required
def created_post(request):
    if request.method == 'POST':
        form = PostCreateForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
    else:
        form = PostForm()
    return render(request, 'created_post.html', {'form': form})
