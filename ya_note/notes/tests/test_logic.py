from django.test import TestCase
from django.urls import reverse
from pytest_django.asserts import assertRedirects, assertFormError
from http import HTTPStatus
from ..models import Note
from django.contrib.auth import get_user_model
from ..forms import WARNING
from pytils.translit import slugify

User = get_user_model()


class TestLogic(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author1 = User.objects.create(username='Author1')
        cls.author2 = User.objects.create(username='Author2')

        cls.note1 = Note.objects.create(
            title='head1',
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

    def test_the_same_note(self):
        '''
        Тест проверяет, что
        невозможно создать две заметки с одинаковым slug.
        '''
        url = reverse('notes:add')
        self.form_note_data['slug'] = self.note1.slug
        self.client.force_login(self.author1)
        response = self.client.post(url, data=self.form_note_data)
        assertFormError(response, 'form',
                        'slug',
                        errors=(self.note1.slug + WARNING))
        self.assertEqual(Note.objects.count(), 2)

    def test_edit_foreign_note(self):
        '''
        Тест проверяет, что
        пользователь не может редактировать чужие заметки
        '''
        self.client.force_login(self.author1)
        response = self.client.post(reverse('notes:edit',
                                            args=(self.note2.slug,)))
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

        note_from_db = Note.objects.get(id=self.note2.id)

        self.assertEqual(self.note2.title, note_from_db.title)
        self.assertEqual(self.note2.text, note_from_db.text)
        self.assertEqual(self.note2.slug, note_from_db.slug)

    def test_delete_foreign_note(self):
        '''
        Тест проверяет, что
        пользователь не может удалять чужие заметки
        '''
        self.client.force_login(self.author1)
        response = self.client.post(reverse('notes:delete',
                                            args=(self.note2.slug,)))
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(Note.objects.count(), 2)

    def test_edit_your_note(self):
        '''
        Тест проверяет, что
        пользователь может редактировать свои заметки
        '''
        self.client.force_login(self.author1)
        response = self.client.post(reverse('notes:edit',
                                            args=(self.note1.slug,)
                                            ),
                                    self.form_note_data)
        self.assertRedirects(response, reverse('notes:success'))

        self.note1.refresh_from_db()

        self.assertEqual(self.note1.title, self.form_note_data['title'])
        self.assertEqual(self.note1.text, self.form_note_data['text'])
        self.assertEqual(self.note1.slug, self.form_note_data['slug'])

    def test_delete_your_note(self):
        '''
        Тест проверяет, что
        пользователь может удалять свои заметки
        '''
        self.client.force_login(self.author1)
        response = self.client.post(reverse('notes:delete',
                                            args=(self.note1.slug,)))
        self.assertRedirects(response, reverse('notes:success'))
        self.assertEqual(Note.objects.count(), 1)


class TestLogicFrom(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author1 = User.objects.create(username='Author1')
        cls.form_note_data = {
            'title': 'Заголовок3',
            'text': 'Текст2',
            'slug': 'someslug3',
        }

    def test_add_notes(self):
        '''
        Тест проверяет, что
        залогиненный пользователь может создать заметку, а анонимный — не может.
        '''
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

        note = Note.objects.get()

        self.assertEqual(note.title, self.form_note_data['title'])
        self.assertEqual(note.text, self.form_note_data['text'])
        self.assertEqual(note.slug, self.form_note_data['slug'])

    def test_empty_slug(self):
        '''
        Тест проверяет, что
        если при создании заметки не заполнен slug,
        то он формируется автоматически, с помощью функции pytils.translit.slugify.
        '''
        url = reverse('notes:add')
        self.form_note_data.pop('slug')
        self.client.force_login(self.author1)
        response = self.client.post(url, data=self.form_note_data)
        self.assertRedirects(response, reverse('notes:success'))
        self.assertEqual(Note.objects.count(), 1)
        new_note = Note.objects.get()
        expected_slug = slugify(self.form_note_data['title'])
        self.assertEqual(new_note.slug, expected_slug)
