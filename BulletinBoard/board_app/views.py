from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, UpdateView, CreateView, DetailView, DeleteView, FormView
from django.shortcuts import redirect, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseForbidden
from django.urls import reverse, reverse_lazy

from .models import Post, Response
from .forms import PostForm, PostCreateForm, RespondForm, ResponsesFilterForm, PostUpdateForm


# from .tasks import respond_send_email, respond_accept_send_email

class PostList(ListView):
    model = Post
    ordering = ['-created_ad']
    template_name = 'home.html'
    context_object_name = 'posts'


class PostDetail(DetailView):
    model = Post
    template_name = 'detail_post.html'
    context_object_name = 'post'
    def get_object(self, queryset=None):
        return get_object_or_404(Post, id=self.kwargs.get('post_id'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Используем правильное поле из модели Response
        if Response.objects.filter(user_id=self.request.user.id).filter(post_id=self.kwargs.get('post_id')):
            context['respond'] = "Откликнулся"
        elif self.request.user == Post.objects.get(id=self.kwargs.get('post_id')).author:
            context['respond'] = "Мое_объявление"
        # Проверка, откликнулся ли пользователь
        context['can_respond'] = not Response.objects.filter(user=self.request.user,
                                                             post=self.get_object()).exists() and self.request.user != self.get_object().author
        return context


class CreatePost(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Post
    template_name = 'created_post.html'
    form_class = PostCreateForm
    permission_required = 'board.add_post'

    # Метод, который будет вызван, если форма валидна
    # Он будет сохранять созданный пост, и автором поста будет текущий пользователь
    # После создания поста, будет происходить редирект на страницу созданного поста
    def form_valid(self, form):
        post = form.save(commit=False)
        post.author = self.request.user
        post.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('detail_post', kwargs={'post_id': self.object.pk})


class EditPost(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Post
    template_name = 'edit_post.html'
    form_class = PostUpdateForm
    permission_required = 'board.change_post'

    # Проверяет разрешение и является ли пользователь автором или администратором.
    def has_permission(self):
        obj = self.get_object()
        return super().has_permission() and (self.request.user.username == 'admin' or self.request.user == obj.author)

    # Использует get_object_or_404 для извлечения объекта по его идентификатору.
    def get_object(self, **kwargs):
        return get_object_or_404(Post, id=self.kwargs.get('id'))

    # Используется для определения URL-адреса перенаправления после успешного обновления.
    def get_success_url(self):
        return reverse('detail', kwargs={'id': self.object.id})

    # Если пользователь не является автором или администратором, то будет возвращено сообщение об ошибке.
    def handle_no_permission(self):
        return HttpResponseForbidden("Редактировать объявление может только его автор")


class DeletePost(PermissionRequiredMixin, DeleteView):
    permission_required = 'board.delete_post'
    template_name = 'delete_post.html'
    queryset = Post.objects.all()
    success_url = '/home/'

    def dispatch(self, request, *args, **kwargs):
        author = Post.objects.get(pk=self.kwargs.get('pk')).author.username
        if self.request.user.username == 'admin' or self.request.user.username == author:
            return super().dispatch(request, *args, **kwargs)
        else:
            return HttpResponse("Нет прав для удаления объявления")


# Это переменная, в которой будет храниться название объявления, нужно для вывода в шаблон
title = str("")


class Responses(LoginRequiredMixin, ListView):
    model = Response
    template_name = 'responses.html'
    context_object_name = 'responses'

    def get_context_data(self, **kwargs):
        context = super(Responses, self).get_context_data(**kwargs)
        global title
        """
        Далее в условии - если пользователь попал на страницу через ссылку из письма, в которой содержится
        ID поста для фильтра - фильтр работает по этому ID
        """
        if self.kwargs.get('pk') and Post.objects.filter(id=self.kwargs.get('pk')).exists():
            title = str(Post.objects.get(id=self.kwargs.get('pk')).title)
            print(title)
        context['form'] = ResponsesFilterForm(self.request.user, initial={'title': title})
        context['title'] = title
        if title:
            post_id = Post.objects.get(title=title)
            context['filter_responses'] = list(Response.objects.filter(post_id=post_id).order_by('-dateCreation'))
            context['response_post_id'] = post_id.id
        else:
            context['filter_responses'] = list(
                Response.objects.filter(post_id__author_id=self.request.user).order_by('-dateCreation'))
        context['myresponses'] = list(Response.objects.filter(author_id=self.request.user).order_by('-dateCreation'))
        return context

    def post(self, request, *args, **kwargs):
        global title
        title = self.request.POST.get('title')
        """
        Далее в условии - При событии POST (если в пути открытой страницы есть ID) - нужно перезайти уже без этого ID
        чтобы фильтр отрабатывал запрос уже из формы, так как ID, если он есть - приоритетный 
        """
        if self.kwargs.get('pk'):
            return HttpResponseRedirect('/responses')
        return self.get(request, *args, **kwargs)


@login_required
def response_accept(request, **kwargs):
    if request.user.is_authenticated:
        response = Response.objects.get(id=kwargs.get('pk'))
        response.status = True
        response.save()
        respond_accept_send_email.delay(response_id=response.id)
        return HttpResponseRedirect('/responses')
    else:
        return HttpResponseRedirect('/accounts/login')


@login_required
def response_delete(request, **kwargs):
    if request.user.is_authenticated:
        response = Response.objects.get(id=kwargs.get('pk'))
        response.delete()
        return HttpResponseRedirect('/responses')
    else:
        return HttpResponseRedirect('/accounts/login')


class Respond(LoginRequiredMixin, CreateView):
    model = Response
    template_name = 'respond.html'
    form_class = RespondForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def form_valid(self, form):
        respond = form.save(commit=False)
        respond.author = User.objects.get(id=self.request.user.id)
        respond.post = Post.objects.get(id=self.kwargs.get('pk'))
        respond.save()
        respond_send_email.delay(respond_id=respond.id)
        return redirect(f'/post/{self.kwargs.get("pk")}')
