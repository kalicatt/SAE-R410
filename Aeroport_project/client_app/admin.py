
from django.contrib import admin
from .models import Clients

class ClientsAdmin(admin.ModelAdmin):
    list_display = ('nom', 'prenom', 'email', 'argent', 'is_staff', 'is_superuser')
    search_fields = ('nom', 'prenom', 'email')

admin.site.register(Clients, ClientsAdmin)
