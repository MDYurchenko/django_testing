from django.test import TestCase
from ..models import Note
from django.contrib.auth import get_user_model
from django.test import Client

User = get_user_model()


class TestBase(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Author1')
        cls.reader = User.objects.create(username='Author2')

        cls.note1 = Note.objects.create(
            title='Заголовок1',
            text='Текст1',
            slug='someslug1',
            author=cls.author,
        )

        cls.author_logged = Client()
        cls.reader_logged = Client()
        cls.anonymous = Client()

        cls.author_logged.force_login(user=cls.author)
        cls.reader_logged.force_login(user=cls.reader)
