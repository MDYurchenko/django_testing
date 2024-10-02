from django.test import TestCase
from django.urls import reverse
from http import HTTPStatus
from ..models import Note
from django.contrib.auth import get_user_model

'''
+Главная страница доступна анонимному пользователю.
+Аутентифицированному пользователю доступна
    страница со списком заметок notes/,
    страница успешного добавления заметки done/,
    страница добавления новой заметки add/.
+Страницы
    отдельной заметки,
    удаления и
    редактирования заметки доступны 
    только автору заметки. 
    Если на эти страницы попытается зайти другой пользователь — вернётся ошибка 404.
+При попытке перейти на страницу списка заметок,
    страницу успешного добавления записи,
    страницу добавления заметки,
    отдельной заметки,
    редактирования или удаления заметки
    анонимный пользователь перенаправляется на страницу логина.
+Страницы
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

        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            slug='someslug',
            author=cls.author,
        )

    def test_pages_availability(self):
        urls = (
            ('notes:home', None),
            ('users:login', None),
            ('users:logout', None),
            ('users:signup', None),
        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_authentificated_user_pages_availability(self):
        urls = (
            ('notes:edit', (self.note.slug,)),
            ('notes:detail', (self.note.slug,)),
            ('notes:delete', (self.note.slug,)),
        )
        users = (
            (self.author, HTTPStatus.OK),
            (self.reader, HTTPStatus.NOT_FOUND)

        )
        for user, status in users:
            self.client.force_login(user)
            for name, args in urls:
                with self.subTest(name=name):
                    url = reverse(name, args=args)
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status)

    def test_auth_user_pages(self):
        urls = (
            'notes:list',
            'notes:success',
            'notes:add'
        )
        self.client.force_login(self.reader)
        for name in urls:
            with self.subTest(name=name):
                url = reverse(name)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_anon_user_pages(self):
        urls = (
            ('notes:list', None),
            ('notes:success', None),
            ('notes:add', None),
            ('notes:edit', (self.note.slug,)),
            ('notes:delete', (self.note.slug,)),
            ('notes:detail', (self.note.slug,)),
        )
        login_url = reverse('users:login')
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)
