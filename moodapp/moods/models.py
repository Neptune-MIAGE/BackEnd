from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.db.models import Avg

# Modèle utilisateur personnalisé
class CustomUser(AbstractUser):
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    location = models.CharField(max_length=100, null=True, blank=True)  # Facultatif pour conserver la ville
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

# Modèle UserMood
class UserMood(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="user_moods")
    mood = models.ForeignKey(Mood, on_delete=models.CASCADE)
    date = models.DateTimeField(default=timezone.now)  # Définit une date par défaut
    note = models.TextField(null=True, blank=True)  # Note optionnelle
    weather_condition = models.CharField(max_length=100, null=True, blank=True)  # Nouveau champ pour la météo

    def __str__(self):
        return f"{self.user.username} - {self.mood.name} on {self.date}"

# Modèle MoodGroup : les groupes créés
class MoodGroup(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    users = models.ManyToManyField(CustomUser, through="GroupMembership")
    leader = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="led_groups", null=True, blank=True)

    def __str__(self):
        return self.name
    
    def average_mood(self):
        return UserMood.objects.filter(user__in=self.users.all()).aggregate(Avg("mood__id"))["mood__id__avg"]

    def median_mood(self):
        # Récupère les IDs des humeurs des utilisateurs du groupe
        moods = UserMood.objects.filter(user__in=self.users.all()).values_list('mood__id', flat=True).order_by('mood__id')
        
        # Si le nombre de valeurs est impair, la médiane est l'élément du milieu
        num_moods = len(moods)
        if num_moods == 0:
            return None  # Aucun mood dans le groupe

        midpoint = num_moods // 2
        if num_moods % 2 == 1:
            return moods[midpoint]  # Médiane si impair
        else:
            # Si pair, prendre la moyenne des deux éléments du milieu
            return (moods[midpoint - 1] + moods[midpoint]) / 2
    
# Modèle GroupMembership : relation utilisateur-groupe
class GroupMembership(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    group = models.ForeignKey(MoodGroup, on_delete=models.CASCADE)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "group")