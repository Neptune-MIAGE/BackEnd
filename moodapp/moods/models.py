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
    
    def average_mood(user):
        """
        Calcule le mood moyen d'un utilisateur.
        """
        return UserMood.objects.filter(user=user).aggregate(Avg("mood__id"))["mood__id__avg"]

    

# Modèle Mood
class Mood(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    emoji = models.CharField(max_length=50)

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


#Modèle MoodRanking pour classer les users et groupes selon leur mood
class MoodRanking(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Mood Ranking"
        verbose_name_plural = "Mood Rankings"

   

    def rank_users():
        """
        Classe les utilisateurs par leur moyenne de mood.
        Retourne une liste triée de tuples : (utilisateur, moyenne).
        """
        users_with_avg = CustomUser.objects.annotate(avg_mood=Avg("user_moods__note")).order_by("-avg_mood")
        return [(user, user.average_mood or 0, user.id) for user in users_with_avg]

    def rank_groups():
        """
        Classe les groupes par leur moyenne de mood.
        Retourne une liste triée de tuples : (groupe, moyenne).
        """
        groups_with_avg = MoodGroup.objects.annotate(avg_mood=Avg("users__user_moods__note")).order_by("-avg_mood")
        return [(group, group.average_mood or 0,group.id) for group in groups_with_avg]

    @staticmethod
    def get_best_user():
        """
        Retourne l'utilisateur avec le meilleur mood (moyenne la plus haute).
        """
        best_user = CustomUser.objects.annotate(avg_mood=Avg("user_moods__note")).order_by("-avg_mood").first()
        return best_user

    @staticmethod
    def get_best_group():
        """
        Retourne le groupe avec le meilleur mood (moyenne la plus haute).
        """
        best_group = MoodGroup.objects.annotate(avg_mood=Avg("users__user_moods__note")).order_by("-avg_mood").first()
        return best_group
    

class MapEmoji(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    latitude = models.FloatField()
    longitude = models.FloatField()
    emoji = models.CharField(max_length=10)  # <-- correction ici
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.emoji:
            from moods.models import Mood
            mood = Mood.objects.first()
            self.emoji = mood.emoji if mood else "🙂"
        super().save(*args, **kwargs)
