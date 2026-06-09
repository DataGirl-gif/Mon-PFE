from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Utilisateur, Patient, Analyse, Visite, VisiteAnalyse

# 1. Personnalisation de l'affichage de l'Utilisateur (Polyvalent)
class UtilisateurAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'is_staff')
    fieldsets = UserAdmin.fieldsets + (
        ('Informations de Rôle - Laboratoire Ibn Heitham', {'fields': ('role',)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Informations de Rôle - Laboratoire Ibn Heitham', {'fields': ('role',)}),
    )

# 2. Personnalisation de l'affichage des Patients
class PatientAdmin(admin.ModelAdmin):
    list_display = ('id', 'nom_majuscule', 'prenom', 'sexe', 'telephone', 'date_naissance')
    list_filter = ('sexe',)
    search_fields = ('nom', 'prenom', 'telephone')

    def nom_majuscule(self, obj):
        return obj.nom.upper()
    nom_majuscule.short_description = 'Nom'

# 3. Personnalisation de l'affichage du Catalogue des Analyses
class AnalyseAdmin(admin.ModelAdmin):
    list_display = ('id', 'nom', 'prix', 'unite', 'valeurs_normales')
    search_fields = ('nom',)
    list_editable = ('prix', 'unite', 'valeurs_normales') # Permet de modifier les tarifs et normes directement dans le tableau

# 4. Personnalisation de l'affichage des Visites (Le Registre)
class VisiteAdmin(admin.ModelAdmin):
    list_display = ('id', 'patient', 'date_visite', 'statut', 'net_a_payer_estime', 'valide_par')
    list_filter = ('statut', 'date_visite')
    search_fields = ('patient__nom', 'patient__prenom', 'id')
    date_hierarchy = 'date_visite'

    def net_a_payer_estime(self, obj):
        examens = obj.examens.all()
        frais_brut = sum(float(item.analyse.prix or 0) for item in examens)
        reduction = frais_brut * (obj.taux_reduction / 100)
        return f"{frais_brut - reduction + float(obj.majoration) + float(obj.deplacement):.2f} MRU"
    net_a_payer_estime.short_description = 'Total Facturé'

# 5. Affichage des lignes d'analyses associées aux visites (Saisie directe sur le terrain)
class VisiteAnalyseAdmin(admin.ModelAdmin):
    list_display = ('id', 'visite', 'analyse', 'valeur_resultat', 'saisi_par')
    list_filter = ('analyse',)
    search_fields = ('visite__id', 'visite__patient__nom', 'analyse__nom')


# Enregistrement final de tous les modèles dans l'administration Django
admin.site.register(Utilisateur, UtilisateurAdmin)
admin.site.register(Patient, PatientAdmin)
admin.site.register(Analyse, AnalyseAdmin)
admin.site.register(Visite, VisiteAdmin)
admin.site.register(VisiteAnalyse, VisiteAnalyseAdmin)