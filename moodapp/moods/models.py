from django.db import models
from django.contrib.auth.models import AbstractUser

# Modèle utilisateur personnalisé
class CustomUser(AbstractUser):
    birth_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.username

# Modèle Mood
class Mood(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

# Modèle UserMood (Association entre Utilisateur et Mood)
class UserMood(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="user_moods")
    mood = models.ForeignKey(Mood, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.mood.name} on {self.date}"
