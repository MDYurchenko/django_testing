from django.test import TestCase
from django.urls import reverse
from http import HTTPStatus
from ..models import Note
from django.contrib.auth import get_user_model

'''
+Главная страница доступна анонимному пользователю.
Аутентифицированному пользователю доступна
    страница со списком заметок notes/,
    страница успешного добавления заметки done/,
    страница добавления новой заметки add/.
Страницы
    отдельной заметки,
    удаления и
    редактирования заметки доступны 
    только автору заметки. 
    Если на эти страницы попытается зайти другой пользователь — вернётся ошибка 404.
При попытке перейти на страницу списка заметок,
    страницу успешного добавления записи,
    страницу добавления заметки,
    отдельной заметки,
    редактирования или удаления заметки
    анонимный пользователь перенаправляется на страницу логина.
Страницы
    регистрации пользователей,
    входа в учётную запись
    и выхода из неё доступны всем пользователям.
'''

User = get_user_model()


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Author')
        cls.reader = User.objects.create(username='Reader')

        cls.news = Note.objects.create(
            title='Заголовок',
            text='Текст',
            slug='some_slug',
            author=cls.author,
        )

    # def test_home_page(self):
    #   url = reverse('notes:home')
    #    response = self.client.get(url)
    #    self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_availability(self):
        urls = (
            ('notes:home', None),
            ('notes:detail', (self.note.id,)),
            ('users:login', None),
            ('users:logout', None),
            ('users:signup', None),
        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)
