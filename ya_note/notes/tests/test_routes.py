from django.test import TestCase
from django.urls import reverse
from http import HTTPStatus
from ..models import Note
from django.contrib.auth import get_user_model
from .base import TestBase

User = get_user_model()


class TestRoutes(TestBase):

    def test_pages_availability(self):
        """
        Тест проверяет, что
        Главная страница доступна анонимному пользователю;
        страницы:
        регистрации пользователей,
        входа в учётную запись
        и выхода из неё
        доступны всем пользователям.
        """
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
        """
        Тест проверяет, что
        Аутентифицированному пользователю-автору доступна
        страница со списком заметок notes/,
        страница успешного добавления заметки done/,
        страница добавления новой заметки add/.
        Другой пользователь получит 404 ошибку.
        """
        urls = (
            ('notes:edit', (self.note1.slug,)),
            ('notes:detail', (self.note1.slug,)),
            ('notes:delete', (self.note1.slug,)),
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
        """
        Тест проверяет, что
        Страницы
        отдельной заметки,
        удаления и
        редактирования заметки доступны
        только автору заметки.
        """
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
        """
        Тест проверяет, что
        Если на эти страницы
        отдельной заметки,
        удаления и
        редактирования заметки
        попытается зайти не автор
         — вернётся ошибка 404.
        """
        urls = (
            ('notes:list', None),
            ('notes:success', None),
            ('notes:add', None),
            ('notes:edit', (self.note1.slug,)),
            ('notes:delete', (self.note1.slug,)),
            ('notes:detail', (self.note1.slug,)),
        )
        login_url = reverse('users:login')
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)
