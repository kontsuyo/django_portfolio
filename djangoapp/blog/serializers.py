from rest_framework import serializers

from blog.models import Post


class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = (
            "id",
            "title",
            "author",
            "content",
            "created_at",
            "updated_at",
            "published_at",
            "is_published",
        )
