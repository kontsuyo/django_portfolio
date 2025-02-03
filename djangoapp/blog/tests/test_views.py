from datetime import datetime

import pytest
from django.urls import reverse
from django.utils import timezone
from django.utils.timezone import is_aware
from rest_framework import status
from rest_framework.test import APIClient

from accounts.models import CustomUser
from blog.models import Post


@pytest.mark.django_db
class TestPostListView:
    def setup_method(self):
        self.client = APIClient()
        self.url = reverse("post-list")
        self.user = CustomUser.objects.create_user(
            username="testuser", password="password"
        )

    def test_unauthenticated_user_can_read_posts(self):
        """未認証ユーザーが投稿を読み取れるか確認"""
        response = self.client.get(self.url)
        assert response.status_code == status.HTTP_200_OK  # type: ignore

    def test_unauthenticated_user_can_not_create_post(self):
        """
        未認証ユーザーが投稿を作成できないことを確認
        """
        post_data = {"title": "Test Post", "content": "This is a test post."}
        response = self.client.post(self.url, post_data)
        assert response.status_code == status.HTTP_403_FORBIDDEN  # type: ignore

    def test_authenticated_user_can_create_post(self):
        """
        認証済みのユーザーが投稿を作成できることを確認
        """
        self.client.force_authenticate(user=self.user)
        post_data = {"title": "Test Post", "content": "This is a test post."}
        response = self.client.post(self.url, post_data)
        assert response.status_code == status.HTTP_201_CREATED  # type: ignore
        assert Post.objects.get(title="Test Post", author=self.user)

    def test_authenticated_user_has_correct_author(self):
        """
        作成された投稿のauthorが認証ユーザーになっているか確認
        """
        self.client.force_authenticate(user=self.user)
        post_data = {"title": "Test Post", "content": "This is a test post."}
        response = self.client.post(self.url, post_data)
        assert response.status_code == status.HTTP_201_CREATED  # type: ignore

        post = Post.objects.get(title="Test Post", author=self.user)
        assert post is not None
        assert post.author == self.user  # type: ignore

    def test_authenticated_user_can_not_create_post_with_long_title(self):
        self.client.force_authenticate(user=self.user)
        long_title = "X" * 201
        post_data = {"title": long_title, "content": "This is a test post."}
        response = self.client.post(self.url, post_data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST  # type: ignore

    def test_created_at_is_set_on_post_creation(self):
        self.client.force_authenticate(user=self.user)
        post_data = {"title": "Test Post", "content": "This is a test post."}

        before_creation = timezone.now()

        response = self.client.post(self.url, post_data)
        assert response.status_code == status.HTTP_201_CREATED  # type: ignore

        after_creation = timezone.now()

        post = Post.objects.get(title="Test Post", author=self.user)
        assert post.created_at is not None
        assert isinstance(post.created_at, datetime)
        assert is_aware(post.created_at)
        assert before_creation <= post.created_at <= after_creation

    def test_posts_are_ordered_by_published_at(self):
        """`published_at` の昇順で並んでいるか確認"""
        self.client.force_authenticate()

        # 古い順に3つの投稿を作成
        Post.objects.create(
            title="Old Post",
            content="Content",
            author=self.user,
            published_at="2024-01-01T00:00:00Z",
        )
        Post.objects.create(
            title="Middle Post",
            content="Content",
            author=self.user,
            published_at="2024-06-01T00:00:00Z",
        )
        Post.objects.create(
            title="New Post",
            content="Content",
            author=self.user,
            published_at="2024-12-01T00:00:00Z",
        )

        response = self.client.get(self.url)
        assert response.status_code == status.HTTP_200_OK  # type: ignore

        results = response.json()  # type: ignore
        post_titles = [post["title"] for post in results]

        # `published_at` が古い順に並んでいるか
        assert post_titles == ["Old Post", "Middle Post", "New Post"]


@pytest.mark.django_db
class TestPostDetailView:
    def setup_method(self):
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

    def test_unauthenticated_user_can_read_post_detail(self):
        """
        未認証ユーザーが投稿の詳細を読み取れるか確認
        """
        response = self.client.get(self.detail_url)
        assert response.status_code == status.HTTP_200_OK  # type: ignore

    def test_unauthenticated_user_can_not_update_post(self):
        """未認証ユーザーが投稿を更新できないことを確認"""
        response = self.client.put(self.detail_url, self.update_data)
        assert response.status_code == status.HTTP_403_FORBIDDEN  # type: ignore

    def test_authenticated_user_can_update_post(self):
        """
        認証済みユーザーが投稿を更新できることを確認
        """
        self.client.force_authenticate(user=self.user)
        response = self.client.put(self.detail_url, self.update_data)
        assert response.status_code == status.HTTP_200_OK  # type: ignore

        post = Post.objects.first()
        assert post.title == self.update_data["title"]  # type: ignore
        assert post.content == self.update_data["content"]  # type: ignore
        assert post.author == self.user  # type: ignore
