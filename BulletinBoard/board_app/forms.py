from django import forms
from django_ckeditor_5.widgets import CKEditor5Widget

from .models import Post, Response


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('category', 'title', 'text',)
        widgets = {'text': CKEditor5Widget(config_name='default')}

    def __init__(self, *args, **kwargs):
        super(PostForm, self).__init__(*args, **kwargs)
        self.fields['category'].label = "Категория:"
        self.fields['title'].label = "Заголовок"
        self.fields['text'].label = "Текст объявления:"


class PostCreateForm(forms.ModelForm):
    """
    Форма добавления статей на сайте
    """

    class Meta:
        model = Post
        fields = ('title', 'category', 'text',)
        widgets = {'text': CKEditor5Widget(config_name='default')}

    def __init__(self, *args, **kwargs):
        """
        Обновление стилей формы под Bootstrap
        """
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control', 'autocomplete': 'off'})

        self.fields['text'].widget.attrs.update({'class': 'form-control django_ckeditor_5'})
        self.fields['text'].required = False


class PostUpdateForm(PostCreateForm):
    """
    Форма обновления статьи на сайте
    """

    class Meta:
        model = Post
        fields = ('title', 'category', 'text',)

    def __init__(self, *args, **kwargs):
        """
        Обновление стилей формы под Bootstrap
        """
        super().__init__(*args, **kwargs)
        # Цикл обновления стилей формы под Bootstrap

        self.fields['text'].widget.attrs.update({'class': 'form-control django_ckeditor_5'})
        self.fields['text'].required = False


class RespondForm(forms.ModelForm):
    class Meta:
        model = Response
        fields = ('text',)

    def __init__(self, *args, **kwargs):
        super(RespondForm, self).__init__(*args, **kwargs)
        self.fields['text'].label = "Текст отклика:"


class ResponsesFilterForm(forms.Form):
    def __init__(self, user, *args, **kwargs):
        super(ResponsesFilterForm, self).__init__(*args, **kwargs)
        self.fields['title'] = forms.ModelChoiceField(
            label='Объявление',
            queryset=Post.objects.filter(author_id=user.id).order_by('-dateCreation').values_list('title', flat=True),
            empty_label="Все",
            required=False
        )
