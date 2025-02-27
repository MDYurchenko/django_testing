from http import HTTPStatus

import pytest
from django.urls import reverse
from pytest_django.asserts import assertRedirects


@pytest.mark.parametrize(
    'url_name',
    ('news:home', 'users:login', 'users:logout', 'users:signup')  # маршруты
)
@pytest.mark.django_db
def test_home_availability_for_anonymous_user(client, url_name):
    """
    Тестирует возможность не авторизированного пользователя получить
    доступ к страницам: домашней, логина, логаута, регистарции.
    """
    url = reverse(url_name)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK, \
        f'Проверьте доступность странице {url} анонимному пользователю.'


@pytest.mark.django_db
def test_news_page_for_anonymous_user(client, news_object):
    """
    Тестируует, что страница отдельной новости доступна
    анонимному пользователю.
    """
    url = reverse('news:detail', kwargs={'pk': news_object.id})
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'user, name, comment, status_code',
    ((pytest.lazy_fixture('author_client'),
      'news:edit',
      pytest.lazy_fixture('comment_object'),
      HTTPStatus.OK,
      ),

     (pytest.lazy_fixture('author_client'),
      'news:delete',
      pytest.lazy_fixture('comment_object'),
      HTTPStatus.OK,
      ),

     (pytest.lazy_fixture('not_author_client'),
      'news:edit',
      pytest.lazy_fixture('comment_object'),
      HTTPStatus.NOT_FOUND,
      ),

     (pytest.lazy_fixture('not_author_client'),
      'news:edit',
      pytest.lazy_fixture('comment_object'),
      HTTPStatus.NOT_FOUND,
      ),
     ),
)
@pytest.mark.django_db
def test_pages_availability_for_author(user, name, comment, status_code):
    """
    Тестирует, что:
    Страницы удаления и редактирования комментария доступны автору
    комментария;
    Авторизованный пользователь не может зайти на страницы редактирования
    или удаления чужих комментариев (возвращается ошибка 404).
    """
    url = reverse(name, args=(comment.pk,))
    response = user.get(url)
    assert response.status_code == status_code


@pytest.mark.parametrize(
    'name, comment',
    (('news:delete', pytest.lazy_fixture('comment_object')),
     ('news:edit', pytest.lazy_fixture('comment_object')),
     ),
)
@pytest.mark.django_db
def test_redirects(client, name, comment):
    """
    Тестирует, что
    При попытке перейти на страницу редактирования или удаления комментария
    анонимный пользователь перенаправляется на страницу авторизации.
    """
    login_url = reverse('users:login')
    url = reverse(name, args=(comment.pk,))
    expected_url = f'{login_url}?next={url}'
    response = client.get(url)

    assertRedirects(response, expected_url)
