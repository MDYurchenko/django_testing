from django.test import TestCase
from django.urls import reverse
from pytest_django.asserts import assertRedirects, assertFormError

from ..models import Note
from django.contrib.auth import get_user_model
from ..forms import NoteForm, WARNING

'''
+Залогиненный пользователь может создать заметку, а анонимный — не может.

+Невозможно создать две заметки с одинаковым slug.

Если при создании заметки не заполнен slug, 
то он формируется автоматически, с помощью функции pytils.translit.slugify.

Пользователь может редактировать и удалять свои заметки,
 но не может редактировать или удалять чужие.
'''
User = get_user_model()


class TestContent(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author1 = User.objects.create(username='Author1')
        cls.author2 = User.objects.create(username='Author2')

        cls.note1 = Note.objects.create(
            title='Заголовок1',
            text='Текст1',
            slug='someslug1',
            author=cls.author1,
        )
        cls.note2 = Note.objects.create(
            title='Заголовок2',
            text='Текст2',
            slug='someslug2',
            author=cls.author2,
        )
        cls.form_note_data = {
            'title': 'Заголовок3',
            'text': 'Текст2',
            'slug': 'someslug3',
        }

    def test_add_notes(self):
        target_url = reverse('notes:add')
        login_url = reverse('users:login')
        unauthorized_user_redirect_url = f'{login_url}?next={target_url}'
        users = (
            (self.client, unauthorized_user_redirect_url),
            (self.author1, reverse('notes:success')),
        )
        for user, redirect_url in users:
            if user == self.author1:
                self.client.force_login(self.author1)
            response = self.client.post(target_url, data=self.form_note_data)
            assertRedirects(response, redirect_url)
            # !!! добавить проверку полей!!!

    def test_the_same_note(self):
        url = reverse('notes:add')
        self.form_note_data['slug'] = self.note1.slug
        self.client.force_login(self.author1)
        response = self.client.post(url, data=self.form_note_data)
        assertFormError(response, 'form',
                        'slug',
                        errors=(self.note1.slug + WARNING))
        self.assertEqual(Note.objects.count(), 2)
