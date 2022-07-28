import shutil
import tempfile

from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from posts.forms import PostForm
from posts.models import Comment, Follow, Group, Post

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
User = get_user_model()


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostsPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Author')
        cls.subscriber = User.objects.create_user(username='Subscriber')
        cls.group = Group.objects.create(
            title='title_value',
            slug='1',
        )
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый текст',
            group=cls.group,
            image=uploaded,
            id=0,
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        cache.clear()
        self.guest_client = Client()
        self.subscriber_client = Client()
        self.subscriber_client.force_login(self.subscriber)
        self.author_client = Client()
        self.author_client.force_login(self.user)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            'posts/index.html': reverse('posts:index'),
            'posts/create_post.html': reverse('posts:post_create'),
            'posts/group_list.html': (
                reverse('posts:group_list', kwargs={'slug': '1'})
            ),
            'posts/profile.html': (
                reverse('posts:profile', kwargs={'username': 'Author'})
            ),
            'posts/post_detail.html': (
                reverse('posts:post_detail', kwargs={'post_id': self.post.id})
            ),
        }
        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.author_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        first_object = (
            self.author_client.get(reverse('posts:index')).
            context['page_obj'][0]
        )
        obj_fields = {
            first_object.author: self.post.author,
            first_object.text: self.post.text,
            first_object.group: self.post.group,
            first_object.image: self.post.image,
        }
        for field, expected in obj_fields.items():
            with self.subTest(field=field):
                self.assertEqual(field, expected)

    def test_index_page_is_cashed(self):
        """Шаблон index кэшируется корректно."""
        posts_text = 'Для кэширования'
        post_cashed = Post.objects.create(
            author=self.user,
            text=posts_text,
        )
        response = self.author_client.get(reverse('posts:index'))
        first_object = (response.context['page_obj'][0])
        self.assertEqual(first_object.text, posts_text)
        post_cashed.delete()
        response_two = self.author_client.get(reverse('posts:index'))
        self.assertContains(response_two, posts_text)
        cache.clear()
        response_three = self.author_client.get(reverse('posts:index'))
        object_after_clear_cash = (response_three.context['page_obj'][0]
                                   )
        self.assertEqual(object_after_clear_cash, self.post)

    def test_group_posts_page_show_correct_context(self):
        """Шаблон group_posts сформирован с правильным контекстом."""
        response = self.author_client.get(reverse('posts:group_list',
                                          kwargs={'slug': '1'})
                                          )
        first_object = response.context['page_obj'][0]
        obj_fields = {
            first_object.author: self.post.author,
            first_object.text: self.post.text,
            first_object.group: self.post.group,
            first_object.image: self.post.image,
        }
        for field, expected in obj_fields.items():
            with self.subTest(field=field):
                self.assertEqual(field, expected)

    def test_group_list_not_show_post_from_another_group(self):
        """Шаблон group_posts не показывает пост другой группы."""
        group_1 = Group.objects.create(
            title='title_value',
            slug=2,
        )
        Post.objects.create(
            author=self.user,
            text='Тестовый текст',
            group=group_1,
            id=1,
        )
        response = self.author_client.get(reverse('posts:group_list',
                                          kwargs={'slug': group_1.slug})
                                          )
        first_object = response.context['page_obj'][0]
        self.assertTrue(first_object != self.post)

    def test_profile_page_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = (self.author_client.get
                    (reverse('posts:profile',
                     kwargs={'username': self.user.username}))
                    )
        first_object = response.context['page_obj'][0]
        obj_fields = {
            first_object.author: self.post.author,
            first_object.text: self.post.text,
            first_object.group: self.post.group,
            first_object.image: self.post.image,
        }
        for field, expected in obj_fields.items():
            with self.subTest(field=field):
                self.assertEqual(field, expected)

    def test_post_detail_page_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.author_client.get(reverse('posts:post_detail',
                                          kwargs={'post_id': self.post.id})
                                          )
        post = response.context.get('post')
        post_fields = {
            post.author: self.post.author,
            post.text: self.post.text,
            post.group: self.post.group,
            post.image: self.post.image,
        }
        for field, expected in post_fields.items():
            with self.subTest(field=field):
                self.assertEqual(field, expected)

    def test_nonauthorized_user_can_not_make_comments(self):
        """
        Неавторизованный пользователь не может оставлять комментарии к посту.
        """
        comment_count = Comment.objects.count()
        form_data = {
            'text': 'Тестовый комментарий',
        }
        self.guest_client.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True
        )
        self.assertEqual(Comment.objects.count(), comment_count)

    def test_post_detail_show_new_comment(self):
        """
        Шаблон post_detail показывает новый комментарий.
        """
        form_data = {
            'text': 'Тестовый комментарий',
        }
        self.author_client.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True
        )
        response = self.author_client.get(reverse('posts:post_detail',
                                          kwargs={'post_id': self.post.id})
                                          )
        self.assertTrue(response.context.get('comments'))

    def test_post_create_page_show_correct_context(self):
        """Шаблон post_create сформирован с правильным контекстом."""
        response = self.author_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
            'image': forms.fields.ImageField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)
        self.assertIsInstance(response.context.get('form'), PostForm)

    def test_post_edit_page_show_correct_context(self):
        """Шаблон post_edit сформирован с правильным контекстом."""
        response = self.author_client.get(reverse('posts:post_edit',
                                          kwargs={'post_id': self.post.id})
                                          )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
            'image': forms.fields.ImageField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)
        is_edit = response.context.get('is_edit')
        self.assertEqual(len(response.context['form'].fields), 3)
        self.assertIsInstance(is_edit, bool)
        self.assertTrue(is_edit)
        self.assertIsInstance(response.context.get('form'), PostForm)

    def test_authorized_user_can_subscribe(self):
        """
        Авторизованный пользователь может подписаться на автора.
        """
        subscribe_count = Follow.objects.count()

        self.subscriber_client.get(reverse('posts:profile_follow',
                                   kwargs={'username': self.user.username})
                                   )
        self.assertEqual(Follow.objects.count(), subscribe_count + 1)

    def test_authorized_user_can_unsubscribe(self):
        """
        Подписчик может отписаться от автора.
        """
        self.subscriber_client.get(reverse('posts:profile_follow',
                                   kwargs={'username': self.user.username})
                                   )
        subscribe_count = Follow.objects.count()
        self.subscriber_client.get(reverse('posts:profile_unfollow',
                                   kwargs={'username': self.user.username})
                                   )
        self.assertEqual(Follow.objects.count(), subscribe_count - 1)

    def test_new_post_show_on_subscriber_page(self):
        """
        Новая запись пользователя появляется в ленте тех, кто на него подписан.
        """
        self.subscriber_client.get(reverse('posts:profile_follow',
                                   kwargs={'username': self.user.username})
                                   )
        response = self.subscriber_client.get(reverse('posts:follow_index'))
        first_object = (response.context['page_obj'][0])
        self.assertEqual(first_object, self.post)

    def test_new_post_not_show_on_unsubscriber_page(self):
        """
        Новая запись пользователя не появляется в ленте тех, кто не подписан.
        """
        reader = User.objects.create_user(username='Reader')
        reader_client = Client()
        reader_client.force_login(reader)
        response = reader_client.get(reverse('posts:follow_index'))
        self.assertEqual(len(response.context['page_obj']), 0)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Author')
        cls.group = Group.objects.create(
            title='title_value',
            slug='1',
        )
        for i in range(13):
            Post.objects.create(
                author=cls.user,
                text='Тестовый текст',
                group=cls.group,
            )

    def setUp(self):
        self.author_client = Client()
        self.author_client.force_login(PaginatorViewsTest.user)
        cache.clear()

    def test_pages_contains_only_ten_records(self):
        """Паджинатор на страницах index показывает по 10 постов."""
        url_choices = {
            'posts:index': None,
            'posts:group_list': {'slug': self.group.slug},
            'posts:profile': {'username': self.user.username}
        }
        for url, choice in url_choices.items():
            with self.subTest(url=url):
                response = self.author_client.get(reverse(url, kwargs=choice))
                self.assertEqual(len(response.context['page_obj']), 10)

    def test_second_page_contains_only_three_records(self):
        """Паджинатор показывает нужное количество постов на 2 странице."""
        url_choices = {
            'posts:index': None,
            'posts:group_list': {'slug': self.group.slug},
            'posts:profile': {'username': self.user.username}
        }
        for url, choice in url_choices.items():
            with self.subTest(url=url):
                response = self.author_client.get(
                    reverse(url, kwargs=choice),
                    {'page': 2}
                )
                self.assertEqual(len(response.context['page_obj']), 3)
