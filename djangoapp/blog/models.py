from django.db import models

from accounts.models import CustomUser


class Post(models.Model):
    title = models.CharField(max_length=200)
    author = models.ForeignKey(
        CustomUser, related_name="blog_posts", on_delete=models.CASCADE
    )
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True)
    is_published = models.BooleanField(default=False)

    class Meta:
        ordering = ["published_at"]

    def __str__(self):
        return str(self.title)
