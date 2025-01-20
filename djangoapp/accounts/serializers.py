from rest_framework import serializers

from blog.models import Post

from .models import CustomUser


class CustomUserSerializer(serializers.ModelSerializer):
    blog_posts = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Post.objects.all()
    )

    class Meta:
        model = CustomUser
        fields = ["id", "username", "blog_posts"]
        # fields = "__all__"
