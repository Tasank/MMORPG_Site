from django.db import models
from django.contrib.auth.models import User
# Поле необходимое для форматирования текста, возможность добавления изображения и видео
from django_ckeditor_5.fields import CKEditor5Field

# Категории как выбор из фиксированного набора
CAT = (
    ('tanks', 'Танки'),
    ('healers', 'Хилы'),
    ('damage_dealers', 'ДД'),
    ('dealers', 'Торговцы'),
    ('gildmasters', 'Гилдмастеры'),
    ('quest_givers', 'Квестгиверы'),
    ('blacksmiths', 'Кузнецы'),
    ('tanners', 'Кожевники'),
    ('potion_makers', 'Зельевары'),
    ('spell_masters', 'Мастера заклинаний'),
)


# Класс объявления
class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.CharField(max_length=15, choices=CAT, verbose_name='Категория')
    title = models.CharField(max_length=20)
    text = CKEditor5Field(config_name='default')
    status = models.BooleanField(default=True)
    created_ad = models.DateTimeField(auto_now_add=True)
    updated_ad = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


# Класс отклика
class Response(models.Model):
    STATUS_PENDING = 'pending'
    STATUS_ACCEPTED = 'accepted'
    STATUS_REJECTED = 'rejected'

    STATUS_CHOICES = (
        (STATUS_PENDING, 'Ожидание'),
        (STATUS_ACCEPTED, 'Принят'),
        (STATUS_REJECTED, 'Отклонен'),
    )

    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_ad = models.DateTimeField(auto_now_add=True)
    updated_ad = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Отклик на объявление "{self.post.title}" от {self.user.username}'

