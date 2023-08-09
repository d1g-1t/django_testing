from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from http import HTTPStatus

from notes.models import Note

User = get_user_model()


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.reader = User.objects.create(username='Читатель')
        cls.note = Note.objects.create(
            author=cls.author,
            title='Заголовок',
            text='Текст заметки',
            slug='notes_slug',
        )

    def test_pages_availability_for_anonymous_user(self):
        """Проверяем доступность страниц сайта для"""
        """неавторизированного пользователя"""
        urls = (
            'notes:home',
            'users:signup',
            'users:login',
            'users:logout'
        )
        for page in urls:
            with self.subTest(page=page):
                url = reverse(page)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_availability_for_authorized_user(self):
        """Проверяем доступность страниц сайта"""
        """для авторизированного пользователя"""
        urls = (
            'notes:add',
            'notes:list',
            'notes:success',
            'users:signup',
            'users:login',
            'users:logout',
        )
        self.client.force_login(self.author)
        for page in urls:
            with self.subTest(page=page):
                url = reverse(page)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_author_can_edit_and_delete_his_notes(self):
        """Проверяем доступность редактирования и удаления заметок"""
        """авторизированным пользователем"""
        users_statuses = (
            (self.author, HTTPStatus.OK),
            (self.reader, HTTPStatus.NOT_FOUND),
        )
        for user, status in users_statuses:
            self.client.force_login(user)
            for page in (
                'notes:detail',
                'notes:edit',
                'notes:delete',
            ):
                with self.subTest(user=user.username, page=page):
                    url = reverse(page, args=[self.note.slug])
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status)

    def test_redirect_anonymous_user(self):
        """Проверяем редирект на страницу авторизации при посещении"""
        """страниц неавторизированным пользователем"""
        login_url = reverse('users:login')
        urls = (
            ('notes:list', None),
            ('notes:add', None),
            ('notes:edit', (self.note.slug,)),
            ('notes:detail', (self.note.slug,)),
            ('notes:delete', (self.note.slug,)),
            ('notes:success', None),
        )
        for page, args in urls:
            with self.subTest(page=page):
                url = reverse(page, args=args)
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)
