import pytest
from django.urls import reverse
from django.conf import settings
from ..forms import CommentForm


@pytest.mark.usefixtures("news_list")
@pytest.mark.django_db
def test_news_list(client):
    '''
    Тест проверяет, что
    Количество новостей на главной странице — не более 10.
    '''
    url = reverse('news:home')
    response = client.get(url)

    object_list = response.context['object_list']

    news_count = object_list.count()
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.usefixtures("news_list")
@pytest.mark.django_db
def test_news_order(client):
    '''
    Тест проверяет, что
    Новости отсортированы от самой свежей к самой старой.
    Свежие новости в начале списка.
    '''
    url = reverse('news:home')
    response = client.get(url)

    object_list = response.context['object_list']
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)

    assert sorted_dates == all_dates


@pytest.mark.usefixtures("news_object", "comment_list")
@pytest.mark.django_db
def test_comment_order(client, news_object, comment_list):
    '''
    Тест проверяет, что
    Комментарии на странице отдельной новости отсортированы
    хронологическом порядке: старые в начале списка, новые — в конце.
    '''
    url = reverse('news:detail', args=(news_object.pk,))
    response = client.get(url)

    news = response.context['news']
    all_comments = news.comment_set.all()

    all_timestamps = [comment.created for comment in all_comments]
    sorted_timestamps = sorted(all_timestamps)

    assert sorted_timestamps == all_timestamps


@pytest.mark.usefixtures("news_object")
@pytest.mark.django_db
def test_anonymous_client_has_no_form(client, news_object):
    '''
    Тест проверяет, что
    Анонимному пользователю недоступна форма для отправки комментария на странице отдельной новости.
    '''
    detail_url = reverse('news:detail', args=(news_object.pk,))
    response = client.get(detail_url)
    assert 'form' not in response.context


@pytest.mark.usefixtures("author_client")
@pytest.mark.django_db
def test_authorized_client_has_form(author_client, news_object):
    '''
    Анонимному пользователю доступна форма для отправки комментария на странице отдельной новости.
    '''
    detail_url = reverse('news:detail', args=(news_object.pk,))
    response = author_client.get(detail_url)
    assert 'form' in response.context
    assert isinstance(response.context['form'], CommentForm)
