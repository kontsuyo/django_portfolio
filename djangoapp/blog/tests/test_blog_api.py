from typing import cast

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.response import Response  # 型ヒント用
from rest_framework.test import APIClient


@pytest.mark.django_db
class TestPostList:
    def setup_method(self):
        self.client = APIClient()
        self.list_url = reverse("blogpost-list")

    def test_get_post_list(self):
        response = self.client.get(self.list_url)
        response = cast(Response, response)
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == []


@pytest.mark.django_db
class TestBlogPostDetail:
    def setup_method(self):
        self.client = APIClient()

    def get_detail_url(self, pk):
        return reverse("blogpost-detail", args=[pk])

    def test_get_post_detail(self):
        detail_url = self.get_detail_url(1)
        response = self.client.get(detail_url)
        response = cast(Response, response)
        assert response.status_code == status.HTTP_404_NOT_FOUND
