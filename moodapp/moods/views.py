import random
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import render
from .models import CustomUser, MapEmoji, Mood, UserMood, MoodGroup, GroupMembership, MoodRanking
from django.shortcuts import redirect, get_object_or_404
from django.utils import timezone  # Utilisez timezone pour garantir la bonne heure
from django.http import JsonResponse
from .models import UserMood
from django.db.models import Avg
from statistics import median
from django.http import HttpResponse
from datetime import datetime, timedelta
from django.db.models import Count
from django.utils.timezone import now



# Vue pour afficher la liste des humeurs disponibles
@login_required
def list_moods(request):
    moods = Mood.objects.all()  # Récupère tous les moods
    return render(request, 'moods/choose_mood.html', {'moods': moods})

def mood_trends(request):
    today = now().date()
    start_date = today - timedelta(days=30)  # Analyse sur les 30 derniers jours

    trends = UserMood.objects.filter(date__gte=start_date).values("date", "mood__name") \
        .annotate(count=Count("mood")).order_by("date")

    trend_data = {}
    for entry in trends:
        date_str = entry["date"].strftime("%Y-%m-%d")
        if date_str not in trend_data:
            trend_data[date_str] = {}
        trend_data[date_str][entry["mood__name"]] = entry["count"]

    return JsonResponse(trend_data)
@login_required
def mood_streak(request):
    moods = UserMood.objects.filter(user=request.user).order_by('-date')

    streak = 0
    previous_date = None

    for mood in moods:
        mood_date = mood.date.date()
        
        # Premier jour du streak
        if previous_date is None:
            streak = 1
        elif previous_date - mood_date == timedelta(days=1):  # Jour précédent
            streak += 1
        else:
            break  # Fin du streak

        previous_date = mood_date

    return JsonResponse({"streak": streak})
# Vue pour ajouter une humeur pour l'utilisateur connecté
@login_required
def add_user_mood(request):
    if request.method == "POST":
        mood_id = request.POST.get("mood_id")
        note = request.POST.get("note", "").strip()  # Récupère la note et supprime les espaces
        weather_condition = request.POST.get("weather_condition", "")

        if mood_id:
            # Récupère l'humeur associée à l'ID
            mood = get_object_or_404(Mood, id=mood_id)

            # Si la note est vide, on peut la remplacer par une valeur par défaut
            if not note:
                note = "Aucune note"

            # Crée un enregistrement dans UserMood avec l'humeur, la note et la condition météo
            UserMood.objects.create(user=request.user, mood=mood, note=note, weather_condition=weather_condition)


            # Position de référence : Université Paris Nanterre
            base_lat = 48.90310022158126
            base_lng = 2.2157004596174414
            # Variation aléatoire jusqu'à ±0.0003 ~ 30 mètres environ
            delta_lat = random.uniform(-0.0003, 0.0003)
            delta_lng = random.uniform(-0.0003, 0.0003)
             # Utilise le nom du mood comme emoji (ex: Happy pour "😊")
            MapEmoji.objects.create(user=request.user,emoji=mood.emoji,  latitude=base_lat + delta_lat,  longitude=base_lng + delta_lng)

        return redirect('user_moods_page')  # Redirige vers la page des humeurs de l'utilisateur après l'enregistrement

    if request.method == "GET":
        moods = Mood.objects.all()
        return render(request, 'moods/choose_mood.html', {'moods': moods})

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
def mood_trends(request):
    # Filtrer les humeurs des 30 derniers jours
    thirty_days_ago = timezone.now() - timezone.timedelta(days=30)
    moods = (
        UserMood.objects.filter(user=request.user, date__gte=thirty_days_ago)
        .values("date__date", "mood__name")
        .annotate(count=Count("mood"))
        .order_by("date__date")
    )

    # Structurer les données
    trends = {}
    for entry in moods:
        date = entry["date__date"].strftime("%Y-%m-%d")
        if date not in trends:
            trends[date] = {}
        trends[date][entry["mood__name"]] = entry["count"]

    return JsonResponse(trends)


@login_required
def user_moods_page(request):
    return render(request, 'moods/user_moods.html')


def user_moods_json(request):
    moods = UserMood.objects.filter(user=request.user).values('date', 'mood__name')
    return JsonResponse(list(moods), safe=False)


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
        return redirect('manage_groups', group_id=group.id)

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


from django.http import HttpResponse
from .models import MapEmoji

from django.http import HttpResponse
from .models import MapEmoji

def map_script(request):
    emojis = MapEmoji.objects.filter(user=request.user).values("latitude", "longitude", "emoji")

    emoji_js_array = ",\n".join([
        f"{{ lat: {e['latitude']}, lng: {e['longitude']}, emoji: '{e['emoji']}' }}"
        for e in emojis
    ])

    script_content = f"""
    document.addEventListener("DOMContentLoaded", function () {{
        var latitude = 48.90310022158126;
        var longitude = 2.2157004596174414;
        var map = L.map('map').setView([latitude, longitude], 15);

        L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
            attribution: '&copy; OpenStreetMap contributors'
        }}).addTo(map);

        const markers = [
            {emoji_js_array}
        ];

        markers.forEach(marker => {{
            var emojiIcon = L.divIcon({{
                className: 'emoji-marker',
                html: `<div style="font-size: 24px;">${{marker.emoji}}</div>`,
                iconSize: [30, 30],
                iconAnchor: [15, 15],
                popupAnchor: [0, -10]
            }});

            L.marker([marker.lat, marker.lng], {{ icon: emojiIcon }})
                .bindPopup(marker.emoji)
                .addTo(map);
        }});
    }});
    """

    return HttpResponse(script_content, content_type="application/javascript")





#Pour afficher les emojis ajoutés sur la carte 
@login_required
def get_map_emojis(request):
    emojis = MapEmoji.objects.all().values("latitude", "longitude", "emoji")
    return JsonResponse(list(emojis), safe=False)
