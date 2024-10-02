from django.test import TestCase
from django.urls import reverse
from ..models import Note
from django.contrib.auth import get_user_model
from ..forms import NoteForm

'''
+отдельная заметка передаётся на страницу со списком заметок в
 списке object_list в словаре context;
+в список заметок одного пользователя не попадают заметки
 другого пользователя;
+на страницы создания и редактирования заметки передаются формы.
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

    def test_note_in_object_list(self):
        self.client.force_login(self.author1)
        url = reverse('notes:list')
        response = self.client.get(url)
        object_list = response.context['object_list']
        self.assertIn(self.note1, object_list)

    def test_note_not_in_object_list(self):
        self.client.force_login(self.author1)
        url = reverse('notes:list')
        response = self.client.get(url)
        object_list = response.context['object_list']
        self.assertNotIn(self.note2, object_list)

    def test_form_at_pages(self):
        urls = (
            ('notes:add', None),
            ('notes:edit', (self.note1.slug,))
        )
        self.client.force_login(self.author1)
        for url, args in urls:
            response = self.client.get(reverse(url, args=args))
            self.assertIn('form', response.context)
            self.assertIsInstance(response.context['form'], NoteForm)
