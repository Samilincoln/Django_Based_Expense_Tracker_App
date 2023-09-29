from django.contrib import admin
from .models import Addbook_info

class Addbook_infoAdmin(admin.ModelAdmin):
    list_display = ("user", 'book_id', 'title', 'subtitle', 'authors', 'publisher', 'Date', 'category', 'distribution_expense')

admin.site.register(Addbook_info,Addbook_infoAdmin)

from django.contrib.sessions.models import Session
admin.site.register(Session)

from .models import UserProfile
admin.site.register(UserProfile)
