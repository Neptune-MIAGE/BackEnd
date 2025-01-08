import os
import django

# Définir le fichier de configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'moodapp.settings')

# Initialiser Django
django.setup()

from moods.models import CustomUser, Mood, MoodGroup

####################################################################################################

# Crée un utilisateur admin 
if not CustomUser.objects.filter(username='admin').exists():
    CustomUser.objects.create_superuser(username='admin', password='admin', email='admin@example.com')
    print("Superuser 'admin' créé avec le mot de passe 'admin'.")

# Crée 3 utilisateurs standards
if not CustomUser.objects.filter(username='user').exists():
    CustomUser.objects.create_user(username='user', password='user', email='user@example.com')
    print("Utilisateur 'user' créé avec le mot de passe 'user'.")

if not CustomUser.objects.filter(username='user2').exists():
    CustomUser.objects.create_user(username='user2', password='user2', email='user2@example.com')
    print("Utilisateur 'user2' créé avec le mot de passe 'user2'.")
    
if not CustomUser.objects.filter(username='user3').exists():
    CustomUser.objects.create_user(username='user3', password='user3', email='user3@example.com')
    print("Utilisateur 'user3' créé avec le mot de passe 'user3'.")

####################################################################################################

# Crée les moods de base
if not Mood.objects.filter(name='Awesome').exists():
    Mood.objects.create(name='Awesome')
    print("Mood 'Awesome' créé.")

if not Mood.objects.filter(name='Happy').exists():
    Mood.objects.create(name='Happy')
    print("Mood 'Happy' créé.")
    
if not Mood.objects.filter(name='Neutral').exists():
    Mood.objects.create(name='Neutral')
    print("Mood 'Neutral' créé.") 
    
if not Mood.objects.filter(name='Sad').exists():
    Mood.objects.create(name='Sad')
    print("Mood 'Sad' créé.")
    
if not Mood.objects.filter(name='Awful').exists():
    Mood.objects.create(name='Awful')
    print("Mood 'Awful' créé.")
    
####################################################################################################

# Créer le groupe 'M1 MIAGE APP' et ajouter les utilisateurs
group_name = 'M1 MIAGE APP'
group_description = "Groupe de classe de la M1 MIAGE APP de l'Université Paris Nanterre"

# Vérifier si le groupe existe déjà
if not MoodGroup.objects.filter(name=group_name).exists():
    group = MoodGroup.objects.create(name=group_name, description=group_description)
    print(f"Groupe '{group_name}' créé.")

    # Ajouter les utilisateurs au groupe
    user = CustomUser.objects.get(username='user')
    user2 = CustomUser.objects.get(username='user2')
    user3 = CustomUser.objects.get(username='user3')

    # Ajouter les membres au groupe
    group.users.add(user, user2, user3)
    print("Utilisateurs ajoutés au groupe.")

    # Définir user2 comme leader du groupe
    group.leader = user2
    group.save()
    print("Leader du groupe défini comme 'user2'.")
else:
    print(f"Le groupe '{group_name}' existe déjà.")
    
####################################################################################################
