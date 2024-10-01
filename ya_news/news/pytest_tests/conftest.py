import pytest
from django.test.client import Client
from news.models import News, Comment


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def not_author(django_user_model):
    return django_user_model.objects.create(username='Не автор')


@pytest.fixture
def author_client(author):
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def not_author_client(not_author):
    client = Client()
    client.force_login(not_author)
    return client


@pytest.fixture
def news_object():
    news_object = News.objects.create(
        title='Заголовок новости',
        text='Текст новости',
    )
    return news_object


@pytest.mark.usefixtures("news_object")
@pytest.fixture
def comment_object(author, news_object):
    comment_obj = Comment.objects.create(
        news=news_object,
        author=author,
        text='Текст комментария 1'
    )
    return comment_obj
