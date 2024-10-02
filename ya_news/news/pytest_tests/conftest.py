import time

import pytest
from django.test.client import Client
from news.models import News, Comment
from django.conf import settings
from datetime import timedelta
from django.utils import timezone


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


@pytest.fixture
def news_list():
    all_news = []
    today = timezone.now()
    for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1):
        news = News(title=f'Новость {index}',
                    text=f'Текст нововсти {index}',
                    date=today - timedelta(days=index)
                    )
        all_news.append(news)
    News.objects.bulk_create(all_news)


@pytest.fixture
@pytest.mark.usefixtures("author", "news_object")
def comment_list(author, news_object):
    now = timezone.now()
    for index in range(2):
        comment = Comment.objects.create(
            news=news_object,
            author=author,
            text=f'Текст комментария {index}'
        )
        comment.created = now + timedelta(hours=index)
        comment.save()


@pytest.fixture
def form_comment():
    return {
        'news': news_object,
        'author': author,
        'text': 'Текст комментария Х'
    }
