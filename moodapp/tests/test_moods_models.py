from django.test import TestCase
from moods.models import CustomUser, Mood, UserMood, MoodGroup, GroupMembership, MoodRanking

class CustomUserTests(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create(username="testuser")
        self.mood1 = Mood.objects.create(name="Happy")
        self.mood2 = Mood.objects.create(name="Sad")
        
        UserMood.objects.create(user=self.user, mood=self.mood1)
        UserMood.objects.create(user=self.user, mood=self.mood2)
    
    def test_average_mood(self):
        avg_mood = self.user.average_mood()
        self.assertIsNotNone(avg_mood)

class MoodGroupTests(TestCase):
    def setUp(self):
        self.user1 = CustomUser.objects.create(username="user1")
        self.user2 = CustomUser.objects.create(username="user2")
        self.mood = Mood.objects.create(name="Excited")
        
        self.group = MoodGroup.objects.create(name="Group A")
        GroupMembership.objects.create(user=self.user1, group=self.group)
        GroupMembership.objects.create(user=self.user2, group=self.group)
        
        UserMood.objects.create(user=self.user1, mood=self.mood)
        UserMood.objects.create(user=self.user2, mood=self.mood)
    
    def test_average_mood(self):
        avg_mood = self.group.average_mood()
        self.assertIsNotNone(avg_mood)
        
class MoodRankingTests(TestCase):
    def setUp(self):
        self.user1 = CustomUser.objects.create(username="user1")
        self.user2 = CustomUser.objects.create(username="user2")
        self.mood = Mood.objects.create(name="Joyful")
        
        UserMood.objects.create(user=self.user1, mood=self.mood, note="Great")
        UserMood.objects.create(user=self.user2, mood=self.mood, note="Good")
    
    def test_rank_users(self):
        rankings = MoodRanking.rank_users()
        self.assertEqual(len(rankings), 2)
    
    def test_get_best_user(self):
        best_user = MoodRanking.get_best_user()
        self.assertEqual(best_user.username, "user1")

class ModelTests(TestCase):
    def test_mood_str(self):
        mood = Mood.objects.create(name="Calm")
        self.assertEqual(str(mood), "Calm")
    
    def test_user_mood_str(self):
        user = CustomUser.objects.create(username="testuser")
        mood = Mood.objects.create(name="Energetic")
        user_mood = UserMood.objects.create(user=user, mood=mood)
        self.assertEqual(str(user_mood), f"{user.username} - {mood.name} on {user_mood.date}")
    