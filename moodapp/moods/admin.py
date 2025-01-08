from django.contrib import admin
from .models import CustomUser, Mood, UserMood, MoodGroup, GroupMembership

admin.site.register(CustomUser)
admin.site.register(Mood)
admin.site.register(UserMood)
admin.site.register(MoodGroup)
admin.site.register(GroupMembership)
