from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import TestCase

from posts.models import Comment, Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост из теста по моделям',
        )
        cls.comment = Comment.objects.create(
            post=cls.post,
            author=cls.user,
            text='Тестовый комментарий'
        )

    def setUp(self):
        cache.clear()

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        group = self.group
        post = self.post
        comment = self.comment
        field_expect = {
            group: self.group.title,
            post: self.post.text[:15],
            comment: self.comment.text[:15],
        }
        for unit, expected_value in field_expect.items():
            with self.subTest(unit=unit):
                self.assertEqual(str(unit), expected_value)
