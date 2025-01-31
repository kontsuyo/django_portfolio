import pytest
from django.db.utils import IntegrityError

from accounts.models import CustomUser


@pytest.mark.django_db
class TestCustomUserModel:
    def test_create_user(self):
        """ユーザーを正しく作成できるか確認"""
        user = CustomUser.objects.create_user(username="testuser", password="password")

        assert user.check_password("password")
        assert user.is_active is True
        assert user.is_staff is False
        assert user.is_superuser is False

    def test_create_superuser(self):
        """スーパーユーザーを正しく作成できるか確認"""
        user = CustomUser.objects.create_superuser(
            username="admin",
            password="admin-password",
            email="",
        )

        assert user.is_superuser is True
        assert user.is_staff is True
        assert user.is_active is True

    def test_create_user_without_username(self):
        """ユーザー作成時のバリデーション"""
        with pytest.raises(ValueError):
            CustomUser.objects.create_user(username="", password="password")

    def test_duplicate_username(self):
        """usernameに一意性が必要なことを確認"""
        CustomUser.objects.create_user(username="testuser", password="password")
        with pytest.raises(IntegrityError):
            CustomUser.objects.create_user(username="testuser", password="password2")

    def test_deactivate_user(self):
        """ユーザーを無効化できることを確認"""
        user = CustomUser.objects.create_user(username="testuser", password="password")
        user.is_active = False
        user.save()

        assert user.is_active is False

    def test_user_str_representation(self):
        """__str__メソッドの動作を確認"""
        user = CustomUser.objects.create_user(username="testuser", password="password")
        assert str(user) == "testuser"
