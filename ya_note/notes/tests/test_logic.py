from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse
from django.db.utils import IntegrityError

from notes.models import Note

from http import HTTPStatus

from pytils.translit import slugify

User = get_user_model()


class TestLogic(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.client_author = Client()
        cls.client_author.force_login(cls.author)
        cls.reader = User.objects.create(username='Читатель')
        cls.client_reader = Client()
        cls.client_reader.force_login(cls.reader)
        cls.ADD_PAGE = reverse('notes:add')
        cls.SUCCESS_PAGE = reverse('notes:success')
        cls.note = Note.objects.create(
            author=cls.author,
            title='Заметка',
            text='Текст',
            slug='note_slug'
        )
        cls.note_no_slug = Note.objects.create(
            author=cls.author,
            title='Заметка',
            text='Текст'
        )
        cls.form_data = {
            'title': 'Заметка',
            'text': 'Текст',
            'slug': 'form_slug'
        }
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))
        cls.delete_url = reverse('notes:delete', args=(cls.note.slug,))

    def test_authorized_user_can_create_notes(self):
        """Проверяем, что авторизированный пользователь"""
        """может создать заметку"""
        count_before_create = Note.objects.count()
        response = self.client_author.post(
            self.ADD_PAGE, data=self.form_data
        )
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        count_after_create = Note.objects.count() - 1
        self.assertEqual(count_before_create, count_after_create)

    def test_unauthorized_user_cant_create_notes(self):
        """Проверяем, что неавторизированный пользователь"""
        """не может создать заметку"""
        count_before_create = Note.objects.count()
        response = self.client.post(
            self.ADD_PAGE,
            data=self.form_data
        )
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        count_after_create = Note.objects.count()
        self.assertEqual(count_before_create, count_after_create)

    def test_users_cant_create_same_note_slug(self):
        """Проверяем, что нельзя создать заметки с одинаковым slug"""
        with self.assertRaises(IntegrityError):
            self.note_with_same_slug = Note.objects.create(
                author=self.author,
                title='Заметка',
                text='Текст',
                slug='note_slug'
            )

    def test_auto_generated_slug(self):
        """Проверяем, что при пустом slug в заметке он автоматически"""
        """генерируется с помощью функции pyutls.translit.slugify"""
        new_note = Note.objects.create(
            author=self.author,
            title='Новая Заметка',
            text='Текст'
        )
        expected_slug = slugify(new_note.title)
        self.assertEqual(new_note.slug, expected_slug)

    def test_author_can_edit_his_notes(self):
        """Проверяем, что пользователь может редактировать свои заметки"""
        response = self.client_author.post(self.edit_url, data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(response, self.SUCCESS_PAGE)

    def test_author_can_delete_his_notes(self):
        """Проверяем, что пользователь может удалять свои заметки"""
        response = self.client_author.delete(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(response, self.SUCCESS_PAGE)

    def test_author_cant_edit_others_notes(self):
        """Проверяем, что пользователь не может редактировать чужие заметки"""
        another_author = User.objects.create(username='Другой_автор')
        another_note = Note.objects.create(
            author=another_author,
            title='Чужая заметка',
            text='Текст чужой заметки'
        )
        response = self.client_author.post(reverse(
            'notes:edit',
            args=(another_note.slug,)),
            data=self.form_data
        )
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_author_cant_delete_others_notes(self):
        """Проверяем, что пользователь не может удалять чужие заметки"""
        another_author = User.objects.create(username='Другой_автор')
        another_note = Note.objects.create(
            author=another_author,
            title='Чужая заметка',
            text='Текст чужой заметки'
        )
        response = self.client_author.delete(reverse(
            'notes:delete',
            args=(another_note.slug,)
        ))
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
