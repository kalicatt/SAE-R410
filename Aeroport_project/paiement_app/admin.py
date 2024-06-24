from django.contrib import admin
from .models import Paiement

@admin.register(Paiement)
class PaiementAdmin(admin.ModelAdmin):
    list_display = ('id', 'client', 'reservation', 'montant', 'paiement_date', 'paiement_methode', 'status')
    search_fields = ('client__nom', 'client__email', 'reservation__id')
    list_filter = ('paiement_date', 'status', 'paiement_methode')
    ordering = ('-paiement_date',)

