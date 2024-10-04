import pytest
from django.shortcuts import reverse
from ..models import Comment
from pytest_django.asserts import assertRedirects, assertFormError
from http import HTTPStatus
from ..forms import BAD_WORDS, WARNING


@pytest.mark.django_db
@pytest.mark.parametrize(
    'user, expected_result',
    ((pytest.lazy_fixture('client'), 0),
     (pytest.lazy_fixture('not_author_client'), 1),
     )
)
def test_user_create_comment(user, expected_result, form_comment, news_object):
    """
    Анонимный пользователь не может отправить комментарий.
    Авторизованный пользователь может отправить комментарий.
    """
    url = reverse('news:detail', args=(news_object.id,))
    user.post(url, data=form_comment)

    assert Comment.objects.count() == expected_result


@pytest.mark.django_db
def test_author_can_edit_comment(author_client, form_comment,
                                 comment_object, news_object):
    """Авторизованный пользователь может редактировать свои комментарии."""
    url = reverse('news:edit', args=(comment_object.id,))
    response = author_client.post(url, data=form_comment)

    assertRedirects(response, reverse('news:detail',
                                      args=(news_object.id,)) + '#comments')

    comment_object.refresh_from_db()

    assert comment_object.text == form_comment['text']
    assert comment_object.news == form_comment['news']
    assert comment_object.author == form_comment['author']


@pytest.mark.django_db
def test_not_author_can_edit_comment(not_author_client, form_comment,
                                     comment_object, news_object):
    """Авторизованный пользователь не может редактировать чужие комментарии."""
    url = reverse('news:edit', args=(comment_object.id,))
    response = not_author_client.post(url, data=form_comment)

    assert response.status_code == HTTPStatus.NOT_FOUND

    comment_object.refresh_from_db()

    assert comment_object.text != form_comment['text']


@pytest.mark.django_db
def test_author_can_delete_comment(author_client, form_comment,
                                   comment_object, news_object):
    """Авторизованный пользователь может удалять свои комментарии."""
    comment_count_before = Comment.objects.count()
    url = reverse('news:delete', args=(comment_object.id,))
    response = author_client.post(url, data=form_comment)

    assertRedirects(response, reverse('news:detail',
                                      args=(news_object.id,)) + '#comments')

    comment_number_after = Comment.objects.count()

    assert comment_count_before - comment_number_after == 1


@pytest.mark.django_db
def test_not_author_can_delete_comment(not_author_client, form_comment,
                                       comment_object, news_object):
    """Авторизованный пользователь не может удалять чужие комментарии."""
    comment_count_before = Comment.objects.count()

    url = reverse('news:delete', args=(comment_object.id,))
    response = not_author_client.post(url, data=form_comment)

    assert response.status_code == HTTPStatus.NOT_FOUND

    comment_number_after = Comment.objects.count()

    assert comment_count_before - comment_number_after == 0


@pytest.mark.django_db
def test_comment_wrong_words(not_author_client, form_comment, news_object):
    """
    Если комментарий содержит запрещённые слова,
    он не будет опубликован, а форма вернёт ошибку.
    """
    url = reverse('news:detail', args=(news_object.id,))

    form_comment.pop('text')
    form_comment['text'] = f'текст, а тут вдруг {BAD_WORDS[0]}, ужасно'

    response = not_author_client.post(url, data=form_comment)

    assertFormError(
        response,
        form='form',
        field='text',
        errors=WARNING
    )

    comments_count = Comment.objects.count()
    assert comments_count == 0
