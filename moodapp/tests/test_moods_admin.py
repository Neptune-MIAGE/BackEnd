from django.test import TestCase
from django.contrib.admin.sites import site
from moods.models import CustomUser, Mood, UserMood, MoodGroup, GroupMembership

class AdminTests(TestCase):
    
    def test_register_models_in_admin(self):
        # Vérifier que les modèles sont bien enregistrés dans l'admin
        self.assertTrue(site.is_registered(CustomUser))
        self.assertTrue(site.is_registered(Mood))
        self.assertTrue(site.is_registered(UserMood))
        self.assertTrue(site.is_registered(MoodGroup))
        self.assertTrue(site.is_registered(GroupMembership))
