import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from accounts.models import CustomUser
from blog.models import Post


@pytest.mark.django_db
class TestPostListView:
    @pytest.fixture
    def setup(self):
        self.client = APIClient()
        self.url = reverse("post-list")
        self.user = CustomUser.objects.create_user(
            username="testuser", password="password"
        )

    def test_unauthenticated_user_can_read_posts(self, setup):
        """未認証ユーザーが投稿を読み取れるか確認"""
        response = self.client.get(self.url)
        assert response.status_code == status.HTTP_200_OK  # type: ignore

    def test_unauthenticated_user_can_not_create_post(self, setup):
        """
        未認証ユーザーが投稿を作成できないことを確認
        """
        post_data = {"title": "Test Post", "content": "This is a test post."}
        response = self.client.post(self.url, post_data)
        assert response.status_code == status.HTTP_403_FORBIDDEN  # type: ignore

    def test_authenticated_user_can_create_post(self, setup):
        """
        認証済みのユーザーが投稿を作成できることを確認
        """
        self.client.login(username="testuser", password="password")
        post_data = {"title": "Test Post", "content": "This is a test post."}
        response = self.client.post(self.url, post_data)
        assert response.status_code == status.HTTP_201_CREATED  # type: ignore
        assert Post.objects.count() == 1

    def test_authenticated_user_has_correct_author(self, setup):
        """
        作成された投稿のauthorが認証ユーザーになっているか確認
        """
        self.client.login(username="testuser", password="password")
        post_data = {"title": "Test Post", "content": "This is a test post."}
        response = self.client.post(self.url, post_data)
        assert response.status_code == status.HTTP_201_CREATED  # type: ignore

        post = Post.objects.first()
        assert post.author == self.user  # type: ignore


@pytest.mark.django_db
class TestPostDetailView:
    @pytest.fixture
    def setup(self):
        self.client = APIClient()
        self.user = CustomUser.objects.create_user(
            username="testuser", password="password"
        )
        self.post = Post.objects.create(
            title="Test Post", content="This is a test content.", author=self.user
        )
        self.detail_url = reverse("post-detail", kwargs={"pk": self.post.pk})
        self.update_data = {
            "title": "Update Post",
            "content": "I want to update post.",
        }

    def test_unauthenticated_user_can_read_post_detail(self, setup):
        """
        未認証ユーザーが投稿の詳細を読み取れるか確認
        """
        response = self.client.get(self.detail_url)
        assert response.status_code == status.HTTP_200_OK  # type: ignore

    def test_unauthenticated_user_can_not_update_post(self, setup):
        """未認証ユーザーが投稿を更新できないことを確認"""
        response = self.client.put(self.detail_url, self.update_data)
        assert response.status_code == status.HTTP_403_FORBIDDEN  # type: ignore

    def test_authenticated_user_can_update_post(self, setup):
        """
        認証済みユーザーが投稿を更新できることを確認
        """
        self.client.login(username="testuser", password="password")
        response = self.client.put(self.detail_url, self.update_data)
        assert response.status_code == status.HTTP_200_OK  # type: ignore

        post = Post.objects.first()
        assert post.title == self.update_data["title"]  # type: ignore
        assert post.content == self.update_data["content"]  # type: ignore
        assert post.author == self.user  # type: ignore
