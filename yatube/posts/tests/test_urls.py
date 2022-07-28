from http import HTTPStatus

from django.core.cache import cache
from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from posts.models import Group, Post

User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Author')
        cls.group = Group.objects.create(
            title='title_value',
            slug='1',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый текст',
        )

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='HasNoName')
        self.user_client = Client()
        self.user_client.force_login(self.user)
        self.author_client = Client()
        self.author_client.force_login(PostURLTests.user)
        cache.clear()

    def test_url_exists_for_all(self):
        """Проверка доступности адресов для неавторизованных посетителей."""
        url_names = {
            '/': HTTPStatus.OK,
            '/create/': HTTPStatus.FOUND,
            '/follow/': HTTPStatus.FOUND,
            '/group/1/': HTTPStatus.OK,
            '/profile/Author/': HTTPStatus.OK,
            '/profile/Author/follow/': HTTPStatus.FOUND,
            '/profile/Author/unfollow/': HTTPStatus.FOUND,
            '/posts/1/': HTTPStatus.OK,
            '/posts/1/comment/': HTTPStatus.FOUND,
            '/posts/1/edit/': HTTPStatus.FOUND,
            '/unexisting_page/': HTTPStatus.NOT_FOUND,
        }
        for url, code in url_names.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, code)

    def test_url_exists_for_user(self):
        """ Проверка доступности адресов для пользователя."""
        url_names = {
            '/create/': HTTPStatus.OK,
            '/follow/': HTTPStatus.OK,
            '/posts/1/edit/': HTTPStatus.FOUND,
            '/profile/Author/follow/': HTTPStatus.FOUND,
            '/profile/Author/unfollow/': HTTPStatus.FOUND,
        }
        for url, code in url_names.items():
            with self.subTest(url=url):
                response = self.user_client.get(url)
                self.assertEqual(response.status_code, code)

    def test_url_exists_for_author(self):
        """ Проверка доступности адресов для автора."""
        url_names = {
            '/posts/1/edit/': HTTPStatus.OK,
            '/follow/': HTTPStatus.OK,
            '/profile/Author/follow/': HTTPStatus.FOUND,
            '/profile/Author/unfollow/': HTTPStatus.FOUND,
        }
        for url, code in url_names.items():
            with self.subTest(url=url):
                response = self.author_client.get(url)
                self.assertEqual(response.status_code, code)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            '/': 'posts/index.html',
            '/create/': 'posts/create_post.html',
            '/group/1/': 'posts/group_list.html',
            '/profile/Author/': 'posts/profile.html',
            '/posts/1/': 'posts/post_detail.html',
            '/posts/1/edit/': 'posts/create_post.html',
            '/unexisting_page/': 'core/404.html',
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.author_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_create_url_redirect_anonymous_on_admin_login(self):
        """
        Страница по адресу /create/ перенаправит анонимного пользователя на
        страницу логина.
        """
        response = self.guest_client.get('/create/', follow=True)
        self.assertRedirects(
            response, '/auth/login/?next=/create/'
        )

    def test_edit_post_url_redirect_not_author_on_post_list(self):
        """
        Страница по адресу /posts/1/edit/ перенаправит не автора на
        страницу логина.
        """
        response = self.user_client.get('/posts/1/edit/', follow=True)
        self.assertRedirects(
            response, '/posts/1/'
        )

    def test_edit_url_redirect_anonymous_on_admin_login(self):
        """
        Страница по адресу post/edit/ перенаправит анонимного пользователя на
        страницу логина.
        """
        response = self.guest_client.get('/posts/1/edit/', follow=True)
        self.assertRedirects(
            response, '/auth/login/?next=/posts/1/edit/'
        )
