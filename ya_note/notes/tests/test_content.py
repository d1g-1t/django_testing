from django import forms
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestContent(TestCase):

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
        cls.list_url = reverse('notes:list')

    def test_author_notes_are_placed_in_their_own_notes_list(self):
        """Проверяем, что после создания заметки"""
        """пользователем она попадает именно в его список заметок"""
        self.client.force_login(self.author)
        response = self.client.get(self.list_url)
        self.assertIn(self.note, response.context['object_list'])

    def test_author_notes_do_not_appear_in_other_notes_list(self):
        """Проверяем, что заметка одного пользователя"""
        """не попадает в список другого пользователя"""
        user_notes = [
            (self.author, True),
            (self.reader, False),
        ]
        url = reverse('notes:list')
        for user, note_in_list in user_notes:
            self.client.force_login(user)
            with self.subTest(user=user.username, note_in_list=note_in_list):
                response = self.client.get(url)
                note_in_object_list = self.note in response.context[
                    'object_list'
                ]
                self.assertEqual(note_in_object_list, note_in_list)

    def test_pages_contain_form(self):
        """Проверка того, что на страницы создания и редактирования"""
        """заметок передаются формы"""
        urls = (
            ('notes:add', None),
            ('notes:edit', (self.note.slug,)),
        )
        for page, args in urls:
            with self.subTest(page=page):
                url = reverse(page, args=args)
                self.client.force_login(self.author)
                response = self.client.get(url)
                self.assertIn('form', response.context)
                form = response.context['form']
                self.assertIsInstance(form, forms.ModelForm)
