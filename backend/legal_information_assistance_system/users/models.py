from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse


class User(AbstractUser):
    email = models.EmailField(unique=True)
    is_verified = models.BooleanField(default=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def __str__(self):
        return self.email

    @property
    def name(self) -> str:
        full_name = f"{self.first_name} {self.last_name}".strip()
        return full_name or self.username

    def get_absolute_url(self) -> str:
        return reverse("users:detail", kwargs={"username": self.username})
