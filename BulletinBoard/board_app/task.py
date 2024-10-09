from datetime import timedelta

from celery import shared_task
from django.conf import settings
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.utils import timezone

from .models import Post, Response


@shared_task
def respond_send_email(respond_id):
    respond = Response.objects.get(id=respond_id)
    subject = f"Новый отклик на ваше объявление: {respond.post.title}"
    message = f"Пользователь {respond.user.username} оставил отклик: {respond.text}"
    recipient_list = [respond.post.author.email]  # Email автора объявления
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, recipient_list)


@shared_task
def respond_accept_send_email(response_id):
    response = Response.objects.get(id=response_id)
    subject = "Ваш отклик принят"
    message = f"Ваш отклик на объявление '{response.post.title}' принят!"
    recipient_list = [response.user.email]  # Email пользователя, оставившего отклик
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, recipient_list)

@shared_task
def send_mail_monday_8am():
    # Создаем список всех объявлений, созданных за последние 7 дней (list_week_posts)
    now = timezone.now()
    list_week_posts = list(Post.objects.filter(dateCreation__gte=now - timedelta(days=7)))
    if list_week_posts:
        for user in User.objects.filter():
            print(user)
            list_posts = ''
            for post in list_week_posts:
                list_posts += f'\n{post.title}\nhttp://127.0.0.1:8000/post/{post.id}'
            send_mail(
                subject=f'ММОРПГ: посты за прошедшую неделю.',
                message=f'Доброго дня, {user.username}!\nПредлагаем Вам ознакомиться с новыми объявлениями, '
                        f'появившимися за последние 7 дней:\n{list_posts}',
                from_email='testmail272@gmail.com',
                recipient_list=[user.email, ],
            )