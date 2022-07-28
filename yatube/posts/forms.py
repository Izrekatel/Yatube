from django import forms
from django.utils.text import slugify

from .models import Comment, Group, Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('text', 'group', 'image')
        labels = {
            'text': ('Текст поста'),
            'group': ('Группа поста'),
            'image': ('Картинка поста'),
        }
        help_texts = {
            'text': ('Введите текст поста'),
            'group': ('Группа, к которой будет относиться пост'),
            'image': ('Картинка для поста'),
        }


class GroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = '__all__'

    def clean_slug(self):
        """Обрабатывает случай, если slug не уникален."""
        cleaned_data = super().clean()
        slug = cleaned_data.get('slug')
        title = cleaned_data.get('title')
        slug = slugify(title)[:100]
        return slug


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
        labels = {
            'text': ('Текст комментария'),
        }
        help_texts = {
            'text': ('Текст комментария к посту'),
        }
