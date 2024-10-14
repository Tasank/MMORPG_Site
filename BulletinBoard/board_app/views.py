from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseForbidden
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views.generic import ListView, UpdateView, CreateView, DetailView, DeleteView

from .forms import PostForm, PostCreateForm, RespondForm, ResponsesFilterForm, PostUpdateForm
from .models import Post, Response
from .task import respond_send_email, respond_accept_send_email


class PostList(ListView):
    model = Post
    ordering = ['-created_ad']
    template_name = 'home.html'
    context_object_name = 'posts'


class PostDetail(DetailView):
    model = Post
    template_name = 'detail_post.html'
    context_object_name = 'post'

    # Извлечение объекта Post по идентификатору
    def get_object(self, queryset=None):
        return get_object_or_404(Post, id=self.kwargs.get('post_id'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = self.get_object()
        user = self.request.user

        # Получаем последний отклик и общее количество откликов
        latest_response = post.response_set.order_by('-created_ad').first()
        total_responses = post.response_set.count()

        # Добавляем данные в контекст
        context['latest_response'] = latest_response
        context['total_responses'] = total_responses

        # Проверка, откликнулся ли пользователь
        if Response.objects.filter(user=user, post=post).exists():
            context['respond'] = "Откликнулся"
        elif user == post.author:
            context['respond'] = "Мое_объявление"

        # Возможность отклика, если пользователь не является автором и ещё не откликнулся
        context['can_respond'] = not (user == post.author or Response.objects.filter(user=user, post=post).exists())

        return context


class CreatePost(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Post
    template_name = 'created_post.html'
    form_class = PostCreateForm
    permission_required = 'board.add_post'


    # Сохранение поста с указанием текущего пользователя как автора
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

    # Проверка разрешений для редактирования поста
    def has_permission(self):
        obj = self.get_object()
        return super().has_permission() and (self.request.user.username == 'admin' or self.request.user == obj.author)

    def get_object(self, **kwargs):
        return get_object_or_404(Post, id=self.kwargs.get('id'))

    def get_success_url(self):
        return reverse_lazy('detail_post', kwargs={'post_id': self.object.pk})

    def handle_no_permission(self):
        return HttpResponseForbidden("Редактировать объявление может только его автор")


class DeletePost(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Post
    template_name = 'delete_post.html'
    permission_required = 'board.delete_post'
    success_url = reverse_lazy('home')

    # Проверка прав на удаление поста
    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if self.request.user.username != 'admin' and self.request.user != obj.author:
            raise PermissionDenied("Нет прав для удаления объявления")
        return obj


class ResponsesView(LoginRequiredMixin, ListView):
    model = Response
    template_name = 'responses.html'
    context_object_name = 'responses'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = ResponsesFilterForm(self.request.user)
        # Фильтрация откликов по названию объявления
        title = self.request.GET.get('title')
        filter_params = {'post__author': self.request.user}
        if title:
            filter_params['posttitleicontains'] = title

        context['filter_responses'] = Response.objects.filter(**filter_params).order_by('-created_ad')

        # Отклики текущего пользователя
        context['myresponses'] = Response.objects.filter(user=self.request.user).order_by('-created_ad')
        return context

    def post(self, request, *args, **kwargs):
        title = request.POST.get('title')
        if title:
            post = Post.objects.filter(title=title).first()
            if post:
                return redirect(reverse('responses') + f'?title={title}')
        return self.get(request, *args, **kwargs)


@login_required
def accept_response(request, pk):
    response = get_object_or_404(Response, id=pk)
    response.status = Response.STATUS_ACCEPTED
    response.save()
    # Отправка уведомления отклика
    respond_accept_send_email.delay(response_id=response.id)
    return redirect(reverse_lazy('detail_post', kwargs={'post_id': response.post.id}))


@login_required
def delete_response(request, pk):
    response = get_object_or_404(Response, id=pk)
    response.delete()
    return redirect(reverse_lazy('detail_post', kwargs={'post_id': response.post.id}))


class RespondCreateView(LoginRequiredMixin, CreateView):
    model = Response
    template_name = 'respond.html'
    form_class = RespondForm

    # Создание нового отклика и отправка уведомления
    def form_valid(self, form):
        respond = form.save(commit=False)
        respond.user = self.request.user
        respond.post = get_object_or_404(Post, id=self.kwargs.get('pk'))
        respond.save()
        respond_send_email.delay(respond_id=respond.id)
        return redirect('detail_post', pk=self.kwargs.get('pk'))