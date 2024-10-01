from pytest_django.asserts import assertRedirects
from http import HTTPStatus
from django.urls import reverse
import pytest
from django.test import TestCase
from news.models import News

'''
В файле test_routes.py:
+Главная страница доступна анонимному пользователю.
+Страница отдельной новости доступна анонимному пользователю.
Страницы удаления и редактирования комментария доступны автору
 комментария.
При попытке перейти на страницу редактирования или удаления комментария
 анонимный пользователь перенаправляется на страницу авторизации.
Авторизованный пользователь не может зайти на страницы редактирования 
или удаления чужих комментариев (возвращается ошибка 404).
+Страницы регистрации пользователей, входа в учётную запись и выхода из
 неё доступны анонимным пользователям.
'''


@pytest.mark.parametrize(
    'url_name',
    ('news:home', 'users:login', 'users:logout', 'users:signup')  # маршруты
)
@pytest.mark.django_db
def test_home_availability_for_anonymous_user(client, url_name):
    '''
    Тестирует возможность не авторизированного пользователя получить
    доступ к страницам: домашней, логина, логаута, регистарции.
    '''
    url = reverse(url_name)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK, f'Проверьте доступность' \
                                                  'странице {url_name} анонимному пользователю.'


@pytest.mark.django_db
def test_news_page_for_anonymous_user(client, news_object):
    url = reverse('news:detail', kwargs={'pk': news_object.id})
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'name', 'comment',
    (
            ('news:edit', pytest.lazy_fixture('comment')),
            ('news:delete', pytest.lazy_fixture('comment')),
    ),
)
def test_pages_availability_for_author(author_client, name, comment_object):
    url = reverse(name, args=(comment_object.pk,))
    response = author_client.get(url)
    assert response.status_code == HTTPStatus.OK
