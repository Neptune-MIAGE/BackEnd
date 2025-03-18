from django.urls import path
from . import views

urlpatterns = [
    path('', views.list_moods, name='list_moods'),  # Liste des humeurs disponibles
    path('add/', views.add_user_mood, name='add_user_mood'),  # Ajouter une humeur
    path('user/', views.user_moods, name='user_moods'),  # API pour le JSON
    path('user/page/', views.user_moods_page, name='user_moods_page'),  # Page HTML
    path('user_moods_json/', views.user_moods_json, name='user_moods_json'),  # API pour le JSON
    path('user_moods_page/', views.user_moods_page, name='user_moods_page'),  # Page HTML
    path('mood_streak/', views.mood_streak, name='mood_streak'),
    path("moods/trends/", views.mood_trends, name="mood_trends"),

    
    # Routes liées aux groupes
    path('groups/', views.manage_groups, name='manage_groups'),
    path('groups/create/', views.create_group, name='create_group'),
    path('groups/delete/<int:group_id>/', views.delete_group, name='delete_group'),
    path('groups/join/<int:group_id>/', views.join_group, name='join_group'),
    path('groups/leave/<int:group_id>/', views.leave_group, name='leave_group'),
    path('group/<int:group_id>/remove_user/<int:member_id>/', views.remove_user_from_group, name='remove_user_from_group'),
    path('group/<int:group_id>/transfer_leadership/<int:member_id>/', views.transfer_leadership, name='transfer_leadership'),
    path('groups/stats/<int:group_id>/', views.group_stats, name='group_stats'),

    #routes liées au ranking
    path('rankings/', views.rankings_list, name='rankings'),
    path('rankings/users',views.rankings_users, name = 'rankings_users'),
    path('rankings/groups/',views.rankings_groups, name = 'rankings_groups'),
    path('user/details/<int:user_id>/', views.user_details, name='user_details'),

    #routes pour la map
    path('map/', views.map_view, name='map'),
    path('moods/map/script.js', views.map_script, name='map_script'),  # Script Leaflet
   


]
