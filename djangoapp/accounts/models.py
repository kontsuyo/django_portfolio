from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):

    class Meta:
        ordering = ["date_joined"]

    def __str__(self):
        return str(self.username)
