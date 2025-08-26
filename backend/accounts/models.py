from django.db import models
from django.utils import timezone
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.models import AbstractBaseUser

ROLE_CHOICES = [
    ("ADMIN", "Admin"),
    ("USER", "User"),
    ("VIEWER", "Viewer"),
]


class User(AbstractBaseUser):
    user_id = models.AutoField(primary_key=True)
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150, unique=True)  # ✅ unique username
    name = models.CharField(max_length=100)
    password = models.CharField(max_length=255)  # Storing hashed password
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default="VIEWER")
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = "email"   # login with email
    REQUIRED_FIELDS = ["username", "name"]  # ✅ username required during createsuperuser

    def set_password(self, raw_password):
        """Hashes and sets the password."""
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        """Validates the password."""
        return check_password(raw_password, self.password)

    def __str__(self):
        return f"{self.username} | {self.email} ({self.role})"