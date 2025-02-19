from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from datetime import datetime, timezone
from moods.models import Mood, UserMood, MoodGroup, GroupMembership, CustomUser
from json import loads


class MoodAppTests(TestCase):
    
    def setUp(self):
        # Création d'un utilisateur fictif pour les tests
        self.user = get_user_model().objects.create_user(
            username="testuser", password="testpassword"
        )
        self.mood = Mood.objects.create(name="Happy")
        self.group = MoodGroup.objects.create(name="Test Group", description="Test Group Description", leader=self.user)
        GroupMembership.objects.create(user=self.user, group=self.group)
    
    def test_list_moods(self):
        # Test que la vue de la liste des humeurs fonctionne
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(reverse('list_moods'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.mood.name)

    def test_add_user_mood(self):
        # Test l'ajout d'une humeur pour un utilisateur
        self.client.login(username='testuser', password='testpassword')
        response = self.client.post(reverse('add_user_mood'), {'mood_id': self.mood.id})
        self.assertEqual(response.status_code, 302)  # Redirection vers la page des humeurs
        self.assertEqual(UserMood.objects.count(), 1)

    def test_user_moods(self):
        self.client.login(username='testuser', password='testpassword')
        
        # Crée un enregistrement avec une date précise
        user_mood = UserMood.objects.create(user=self.user, mood=self.mood)
        creation_time = user_mood.date.replace(microsecond=0, tzinfo=timezone.utc)  # Assurez-vous que le champ `created_at` est utilisé.

        response = self.client.get(reverse('user_moods'))
        self.assertEqual(response.status_code, 200)
        
        # Analyse la réponse JSON
        response_data = loads(response.content)
        self.assertEqual(len(response_data), 1)  # Assurez-vous qu'il y a un seul élément.

        # Extrait la date et l'heure renvoyées
        returned_datetime = datetime.fromisoformat(response_data[0]['date'].replace('Z', '+00:00'))  # Parse ISO 8601.

        # Validez que la date et l'heure correspondent (avec une tolérance de ±1 seconde pour éviter des problèmes de précision)
        time_difference = abs((creation_time - returned_datetime).total_seconds())
        self.assertLessEqual(time_difference, 1, "La date et l'heure ne correspondent pas exactement.")

        # Validez les autres champs
        self.assertEqual(response_data[0]['mood__name'], "Happy")

    def test_create_group(self):
        # Test la création d'un groupe
        self.client.login(username='testuser', password='testpassword')
        response = self.client.post(reverse('create_group'), {'group_name': 'New Group', 'description': 'New Group Description'})
        self.assertEqual(response.status_code, 302)
        self.assertTrue(MoodGroup.objects.filter(name='New Group').exists())

    def test_create_group_duplicate_name(self):
        # Test la gestion d'un groupe avec un nom déjà existant
        self.client.login(username='testuser', password='testpassword')
        response = self.client.post(reverse('create_group'), {'group_name': 'Test Group', 'description': 'Duplicate Name Test'})
        self.assertEqual(response.status_code, 302)
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(str(messages[0]), "Un groupe avec ce nom existe déjà.")

    def test_delete_group(self):
        # Test la suppression d'un groupe
        self.client.login(username='testuser', password='testpassword')
        group_id = self.group.id
        response = self.client.post(reverse('delete_group', args=[group_id]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(MoodGroup.objects.filter(id=group_id).exists())



    def test_remove_user_from_group(self):
        # Test qu'un utilisateur peut être retiré d'un groupe
        other_user = get_user_model().objects.create_user(username='otheruser', password='otherpassword')
        self.group.users.add(other_user)
        self.client.login(username='testuser', password='testpassword')
        response = self.client.post(reverse('remove_user_from_group', args=[self.group.id, other_user.id]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(self.group.users.filter(id=other_user.id).exists())

    def test_group_stats(self):
        # Test que les statistiques du groupe sont calculées correctement
        self.client.login(username='testuser', password='testpassword')
        UserMood.objects.create(user=self.user, mood=self.mood)
        response = self.client.get(reverse('group_stats', args=[self.group.id]))
        
        self.assertEqual(response.status_code, 200)
        # Vérifiez les libellés réels dans le HTML
        self.assertContains(response, "Moyenne d'Humeur")
        self.assertContains(response, "Médiane d'Humeur")


    def test_transfer_leadership(self):
        # Test que le leadership peut être transféré
        new_leader = get_user_model().objects.create_user(username='newleader', password='newpassword')
        self.group.users.add(new_leader)
        self.client.login(username='testuser', password='testpassword')
        response = self.client.post(reverse('transfer_leadership', args=[self.group.id, new_leader.id]))
        self.assertEqual(response.status_code, 302)
        self.group.refresh_from_db()
        self.assertEqual(self.group.leader, new_leader)

    def test_rankings_list(self):
        # Test la vue des classements
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(reverse('rankings'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Groupe")
        self.assertContains(response, "Moyenne")

    def test_user_details(self):
        # Test les détails d'un utilisateur
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(reverse('user_details', args=[self.user.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.user.username)

    def test_manage_groups(self):
        # Test que l'utilisateur voit les groupes qu'il gère
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(reverse('manage_groups'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.group.name)
