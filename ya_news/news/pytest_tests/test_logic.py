from http import HTTPStatus

import pytest

from django.urls import reverse

from news.models import Comment
from news.forms import WARNING, BAD_WORDS


@pytest.mark.django_db
class TestCommentsCreate:
    NEWS_PAGE_DETAIL = 'news:detail'

    """Проверяем, что только авторизированные пользователи"""
    """могут создавать комментарии"""

    @pytest.mark.parametrize(
        'parametrized_client, expected_status',
        (
            (pytest.lazy_fixture('client'), False),
            (pytest.lazy_fixture('author_client'), True)
        ),
    )
    def test_creating_comments(
        self, parametrized_client, expected_status, form_data, news_pk
    ):
        url = reverse(self.NEWS_PAGE_DETAIL, args=news_pk)
        count_before_comment = Comment.objects.count()
        response = parametrized_client.post(url, data=form_data)
        assert response.status_code == HTTPStatus.FOUND
        count_after_comment = Comment.objects.count()
        assert (count_before_comment != count_after_comment) == expected_status

    def test_bad_words_not_allowed_in_comments(self, author_client, news_pk):
        """Проверяем, что в комментариях нельзя использовать "плохие" слова"""
        url = reverse(self.NEWS_PAGE_DETAIL, args=news_pk)
        bad_words_data = {'text': BAD_WORDS[0]}
        response = author_client.post(url, data=bad_words_data)
        assert response.status_code == HTTPStatus.OK
        assert Comment.objects.count() == 0
        assert 'form' in response.context
        form = response.context['form']
        assert 'text' in form.errors
        assert WARNING in form.errors['text']


@pytest.mark.django_db
@pytest.mark.usefixtures('comment')
class TestCommentsDelete:
    PAGE_COMMENT_DELETE = 'news:delete'

    def test_author_can_delete_his_comments(self, author_client, comment_pk):
        """Проверяем, что автор комментариев может их удалять"""
        url = reverse(self.PAGE_COMMENT_DELETE, args=comment_pk)
        response = author_client.post(url)
        assert response.status_code == HTTPStatus.FOUND
        assert Comment.objects.count() == 0

    def test_user_cannot_delete_others_comments(
            self, admin_client, comment_pk
    ):
        """Проверяем, что авторизированный пользователь"""
        """не может удалять чужие комментарии"""
        url = reverse(self.PAGE_COMMENT_DELETE, args=comment_pk)
        response = admin_client.post(url)
        assert response.status_code == HTTPStatus.NOT_FOUND
        assert Comment.objects.count() == 1


class TestCommentsEdit:
    PAGE_COMMENT_EDIT = 'news:edit'

    def test_author_can_edit_his_comments(
            self, author_client, form_data, comment, comment_pk
    ):
        """Проверяем, что автор комментариев может их редактировать"""
        url = reverse(self.PAGE_COMMENT_EDIT, args=comment_pk)
        response = author_client.post(url, data=form_data)
        assert response.status_code == HTTPStatus.FOUND
        comment.refresh_from_db()
        assert comment.text == form_data['text']

    def test_another_user_cant_edit_comments(
            self, admin_client, form_data, comment, comment_pk
    ):
        """Проверяем, что пользователь не может"""
        """редактировать чужие комментарии"""
        url = reverse(self.PAGE_COMMENT_EDIT, args=comment_pk)
        response = admin_client.post(url, data=form_data)
        assert response.status_code == HTTPStatus.NOT_FOUND
        comments_from_database = Comment.objects.get(id=comment.id)
        assert comment.text == comments_from_database.text
