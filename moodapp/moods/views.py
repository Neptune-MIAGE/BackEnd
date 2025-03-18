from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import render
from .models import CustomUser, Mood, UserMood, MoodGroup, GroupMembership, MoodRanking
from django.shortcuts import redirect, get_object_or_404
from django.utils import timezone  # Utilisez timezone pour garantir la bonne heure
from django.http import JsonResponse
from .models import UserMood
from django.db.models import Avg
from statistics import median
from django.http import HttpResponse



# Vue pour afficher la liste des humeurs disponibles
@login_required
def list_moods(request):
    moods = Mood.objects.all()  # Récupère tous les moods
    return render(request, 'moods/choose_mood.html', {'moods': moods})

# Vue pour ajouter une humeur pour l'utilisateur connecté
@login_required
def add_user_mood(request):
    if request.method == "POST":
        # Récupère l'utilisateur connecté et le mood choisi
        mood_id = request.POST.get("mood_id")
        if mood_id:
            mood = get_object_or_404(Mood, id=mood_id)
            UserMood.objects.create(user=request.user, mood=mood)

        # Redirige directement vers la page du graphique des humeurs après enregistrement
        return redirect('user_moods_page')  
    if request.method == "GET":
        moods = Mood.objects.all()  # Récupère tous les moods
        return render(request, 'moods/choose_mood.html', {'moods': moods})
    # Si la méthode n'est pas POST, retourne une erreur
    return JsonResponse({"error": "Méthode non autorisée."}, status=405)

# Vue pour récupérer les humeurs d’un utilisateur

@login_required
def user_moods(request):
    # Récupérer les 10 derniers humeurs triées par date (ordre croissant)
    user_moods = (
        UserMood.objects.filter(user=request.user)  # Filtrer par utilisateur
        .order_by('date')[:12]  # Tri par date croissante et limiter aux 10 derniers
        .values("mood__name", "date")  # Sélectionner les champs d'intérêt
    )
    
    # Convertir le QuerySet en une liste pour le renvoyer en JSON
    user_moods_list = list(user_moods)
    
    # Retourner les données JSON
    return JsonResponse(user_moods_list, safe=False)


@login_required
def user_moods_page(request):
    return render(request, 'moods/user_moods.html')


def user_moods_json(request):
    user_moods = UserMood.objects.filter(user=request.user).values('date', 'mood__name', 'note')
    return JsonResponse(list(user_moods), safe=False)


# Vue pour créer un groupe d'humeurs
@login_required
def create_group(request):
    if request.method == 'POST':
        group_name = request.POST.get('group_name')
        description = request.POST.get('description')
        
        # Vérifier si le groupe existe déjà
        if MoodGroup.objects.filter(name=group_name).exists():
            # Ajouter un message d'erreur si le nom existe déjà
            messages.error(request, "Un groupe avec ce nom existe déjà.")
            return redirect('create_group')  # Redirige vers la page de création du groupe
        
        # Si pas d'erreur, créer le groupe
        new_group = MoodGroup.objects.create(name=group_name, description=description, leader=request.user)
        GroupMembership.objects.create(user=request.user, group=new_group)
        messages.success(request, "Groupe créé avec succès !")
        return redirect('group_stats', group_id=new_group.id)  # Rediriger vers la page du groupe

    return render(request, 'moods/create_group.html')  # Pour les requêtes GET

# Vue pour supprimer un groupe
@login_required
def delete_group(request, group_id):
    group = get_object_or_404(MoodGroup, id=group_id)
    
    # Vérifier si l'utilisateur est le chef du groupe
    if group.leader != request.user:
        return JsonResponse({"error": "Vous devez être le chef du groupe pour le supprimer."}, status=403)
    
    # Supprimer le groupe
    group.delete()
    messages.success(request, "Vous avez supprimé le groupe avec succès.")
    return redirect('manage_groups')


# Vue pour rejoindre un groupe
@login_required
def join_group(request, group_id):
    group = get_object_or_404(MoodGroup, id=group_id)
    if not GroupMembership.objects.filter(user=request.user, group=group).exists():
        GroupMembership.objects.create(user=request.user, group=group)
    return redirect('group_stats', group_id=group_id)

# Vue pour quitter un groupe
@login_required
def leave_group(request, group_id):
    group = get_object_or_404(MoodGroup, id=group_id)

    # Vérification si l'utilisateur est le leader
    if group.leader == request.user:
        messages.error(request, "Impossible de quitter le groupe en tant que leader. Transférez le rôle ou supprimez le groupe.")
        return redirect('group_stats', group_id=group.id)

    membership = GroupMembership.objects.filter(user=request.user, group=group).first()

    if membership:
        membership.delete()

    messages.success(request, "Vous avez quitté le groupe avec succès.")
    return redirect('manage_groups')


# Vue pour supprimer un utilisateur d'un groupe
@login_required
def remove_user_from_group(request, group_id, member_id):
    group = get_object_or_404(MoodGroup, id=group_id)
    
    # Vérifier si l'utilisateur est le chef du groupe
    if group.leader != request.user:
        return JsonResponse({"error": "Vous devez être le chef du groupe pour retirer un membre."}, status=403)

    # Vérifier si l'utilisateur est dans le groupe
    member = get_object_or_404(CustomUser, id=member_id)
    if member not in group.users.all():
        return JsonResponse({"error": "L'utilisateur n'est pas membre du groupe."}, status=400)

    # Retirer le membre du groupe
    group.users.remove(member)
    messages.success(request, "Membre supprimé avec succès.")
    return redirect('group_stats', group_id=group.id)


# Vue pour afficher les statistiques d'un groupe
@login_required
def group_stats(request, group_id):
    group = get_object_or_404(MoodGroup, id=group_id)
    user_moods = UserMood.objects.filter(user__in=group.users.all())
    
    # Récupérer les membres du groupe
    group_members = group.users.all()
    
    # Vérifie si l'utilisateur est membre du groupe
    is_member = GroupMembership.objects.filter(user=request.user, group=group).exists()

    
    if user_moods.exists():
        average_mood = user_moods.aggregate(Avg("mood__id"))["mood__id__avg"]
        median_mood = median([mood.mood.id for mood in user_moods])
    else:
        average_mood = None
        median_mood = None
    
    context = {
        "group": group,
        "average_mood": average_mood,
        "median_mood": median_mood,
        "group_members": group_members,
        "is_member": is_member,
    }
    return render(request, "moods/group_stats.html", context)

# Vue pour transferer la gestion du groupe
@login_required
def transfer_leadership(request, group_id, member_id):
    group = get_object_or_404(MoodGroup, id=group_id)
    
    # Vérifier si l'utilisateur est le chef du groupe
    if group.leader != request.user:
        return JsonResponse({"error": "Vous devez être le chef du groupe pour transférer le rôle."}, status=403)

    # Vérifier si le membre est dans le groupe
    new_leader = get_object_or_404(CustomUser, id=member_id)
    if new_leader not in group.users.all():
        return JsonResponse({"error": "Le nouveau chef doit être membre du groupe."}, status=400)

    # Passer le flambeau
    group.leader = new_leader
    group.save()
    messages.success(request, "Flambeau transféré avec succès.")
    return redirect('group_stats', group_id=group.id)

# Vue pour gérer les groupes de l'utilisateur
@login_required
def manage_groups(request):
    user_groups = MoodGroup.objects.filter(users=request.user)  # Récupère les groupes de l'utilisateur
    all_groups = MoodGroup.objects.all()  # Récupère tous les groupes
    context = {
        'user_groups': user_groups,
        'all_groups': all_groups,
    }

    # Pour chaque groupe, vérifier si l'utilisateur en fait partie
    for group in all_groups:
        group.is_member = GroupMembership.objects.filter(user=request.user, group=group).exists()

    return render(request, 'moods/manage_groups.html', context)


#vues liées au ranking
@login_required
def rankings_list(request):
    user_ranks = MoodRanking.rank_users #recupere tous les users
    groups_ranks = MoodRanking.rank_groups # Récupère tous les groupes
    best_user = MoodRanking.get_best_user()
    best_group = MoodRanking.get_best_group()

    context = {
        'user_ranks': user_ranks,
        'group_ranks': groups_ranks,
        'best_user': best_user,
        'best_group': best_group,
    }
    return render(request, 'moods/rankings.html', context )

@login_required
def rankings_users(request):
    user_ranks = MoodRanking.rank_users #recupere tous les users
    best_user = MoodRanking.get_best_user()
    context = {
        'user_ranks': user_ranks,
        'best_user': best_user,
    }
    return render(request, 'moods/rankings_users.html', context )

@login_required
def rankings_groups(request):
    groups_ranks = MoodRanking.rank_groups # Récupère tous les groupes
    best_group = MoodRanking.get_best_group()    
    context = {
        'group_ranks': groups_ranks,
        'best_group': best_group,
    }
    return render(request, 'moods/rankings_groups.html', context )


@login_required
def user_details(request, user_id):
    # Récupère l'utilisateur correspondant à l'id
    user = get_object_or_404(CustomUser, id=user_id)
    
    # Crée le contexte avec les informations de l'utilisateur
    context = {
        'user': user,
    }
    return render(request, 'moods/user_details.html', context)


@login_required
def map_view(request):
    context = {}
    return render(request, 'moods/map.html',context)


def map_script(request):
    """Génère dynamiquement le script JavaScript avec les coordonnées"""
    script_content = f"""
    document.addEventListener("DOMContentLoaded", function () {{
        var latitude = {48.8566};  
        var longitude = {2.3522};  
        var zoom = {13};  

        var map = L.map('map').setView([latitude, longitude], zoom);

        L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
            attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        }}).addTo(map);
    }});
    """
    return HttpResponse(script_content, content_type="application/javascript")