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

class LawyerProfile(models.Model):

    SPECIALIZATION_CHOICES = [
        ("Civil Law", "Civil Law"),
        ("Criminal Law", "Criminal Law"),
        ("Family Law", "Family Law"),
        ("Corporate Law", "Corporate Law"),
        ("Property Law", "Property Law"),
        ("Constitutional Law", "Constitutional Law"),
        ("Tax Law", "Tax Law"),
        ("Labor Law", "Labor Law"),
        ("Immigration Law", "Immigration Law"),
        ("Environmental Law", "Environmental Law"),
        ("Other", "Other"),
    ]

    full_name = models.CharField(max_length=150)

    profile_image = models.ImageField(
        upload_to="lawyers/profile_images/",
        blank=True,
        null=True,
    )

    specialization = models.CharField(
        max_length=100,
        choices=SPECIALIZATION_CHOICES,
    )

    years_of_experience = models.PositiveIntegerField()

    city = models.CharField(max_length=100)

    bio = models.TextField(blank=True)

    license_number = models.CharField(
        max_length=100,
        unique=True,
    )

    bar_association = models.CharField(
        max_length=150,
        blank=True,
    )

    education = models.TextField(blank=True)

    languages = models.CharField(
        max_length=255,
        blank=True,
        help_text="Example: English, Nepali, Hindi",
    )

    phone = models.CharField(
        max_length=20,
        blank=True,
    )

    email = models.EmailField(blank=True)

    office_address = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["full_name"]

    def __str__(self):
        return self.full_name