import pytest
from django.db.utils import DataError
from django.utils import timezone

from accounts.models import CustomUser
from blog.models import Post


@pytest.mark.django_db
class TestPostModel:
    def setup_method(self):
        """各テストの前にデータをセットアップ"""
        self.user = CustomUser.objects.create_user(
            username="testuser", password="password"
        )

    def test_create_post(self):
        """投稿が正しく作成されるか確認"""
        post = Post.objects.create(
            title="Test Post",
            content="This is a test content.",
            author=self.user,
        )
        assert post.title == "Test Post"
        assert post.content == "This is a test content."
        assert post.author == self.user

    def test_update_post(self):
        """投稿が正しく更新されるか確認"""
        post = Post.objects.create(
            title="Test Post",
            content="This is a test content.",
            author=self.user,
        )
        post.title = "Update"
        post.content = "Update content."
        post.save()

        updated_post = Post.objects.get(id=post.id)  # type: ignore
        assert updated_post.title == "Update"
        assert updated_post.content == "Update content."

    def test_delete_post(self):
        """投稿が正しく削除されるか確認"""
        post = Post.objects.create(
            title="Test Post",
            content="This is a test content.",
            author=self.user,
        )
        Post.objects.filter(id=post.id).delete()  # type: ignore
        assert not Post.objects.filter(id=post.id).exists()  # type: ignore

    def test_title_max_length(self):
        """タイトルが２００文字超えたときにエラーが発生することを確認"""
        long_title = "A" * 201
        with pytest.raises(DataError):
            Post.objects.create(
                title=long_title,
                content="Test content.",
                author=self.user,
            )

    def test_content_is_empty(self):
        """コンテントが空でも投稿できることを確認"""
        post = Post.objects.create(
            title="Test Post",
            content="",
            author=self.user,
        )
        assert post.content == ""

    def test_delete_related_author_deletes_posts(self):
        """authorが削除されたときに、投稿も削除されるか確認"""
        Post.objects.create(
            title="Test Post",
            content="Test content.",
            author=self.user,
        )
        user_id = self.user.id  # type: ignore
        self.user.delete()
        assert not Post.objects.filter(author_id=user_id).exists()

    def test_default_is_published(self):
        """is_publishedフィールドのデフォルト値がFalseであることを確認"""
        post = Post.objects.create(
            title="Test Post",
            content="Test content.",
            author=self.user,
        )
        assert post.is_published is False

    def test_published_at_is_default(self):
        post = Post.objects.create(
            title="Test Post",
            content="Test content.",
            author=self.user,
        )
        assert post.published_at is None

    def test_is_published_and_published_at(self):
        post = Post.objects.create(
            title="Test Post",
            content="Test content.",
            author=self.user,
            is_published=True,
            published_at=timezone.now(),
        )
        assert post.is_published is True
        assert post.published_at is not None

    def test_ordering_by_published_at(self):
        post1 = Post.objects.create(
            title="Test Post 1",
            content="Content 1",
            author=self.user,
            published_at=timezone.now(),
        )
        post2 = Post.objects.create(
            title="Test Post 2",
            content="Content 2",
            author=self.user,
            published_at=timezone.now(),
        )
        posts = Post.objects.all()
        assert posts[0] == post1
        assert posts[1] == post2

    def test_title_str_representation(self):
        """__str__メソッドの動作を確認"""
        post = Post.objects.create(
            title="Test Post",
            content="Test content.",
            author=self.user,
        )
        assert str(post) == "Test Post"

    def test_published_at_updated_on_publish(self):
        post = Post.objects.create(
            title="Test Post",
            content="Test content.",
            author=self.user,
            is_published=False,
        )

        assert post.published_at is None

        post.is_published = True
        post.save()

        post.refresh_from_db()
        assert post.published_at is not None
        assert isinstance(post.published_at, timezone.datetime)
