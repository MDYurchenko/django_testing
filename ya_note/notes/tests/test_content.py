from django.urls import reverse
from ..models import Note
from django.contrib.auth import get_user_model
from ..forms import NoteForm
from .base import TestBase

User = get_user_model()


class TestContent(TestBase):

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.note2 = Note.objects.create(
            title='Заголовок2',
            text='Текст2',
            slug='someslug2',
            author=cls.reader,
        )

    def test_note_in_object_list(self):
        """
        Тест проверяет, что
        отдельная заметка передаётся на страницу со списком заметок в
        списке object_list в словаре context
        """

        url = reverse('notes:list')
        response = self.author_logged.get(url)
        object_list = response.context['object_list']
        self.assertIn(self.note1, object_list)

    def test_note_not_in_object_list(self):
        """
        Тест проверяет, что
        в список заметок одного пользователя не попадают заметки
        другого пользователя;
        """
        # Не понял, как вынести пути в setupdata:
        # у меня же каждый раз разные пути, например,
        # в следующей функции test_form_at_pages уже другой набор
        url = reverse('notes:list')
        response = self.author_logged.get(url)
        object_list = response.context['object_list']
        self.assertNotIn(self.note2, object_list)

    def test_form_at_pages(self):
        """
        Тест проверяет, что
        на страницы создания и редактирования заметки передаются формы.
        """
        urls = (
            ('notes:add', None),
            ('notes:edit', (self.note1.slug,))
        )
        for url, args in urls:
            with self.subTest(name=url):
                response = self.author_logged.get(reverse(url, args=args))
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context['form'], NoteForm)
