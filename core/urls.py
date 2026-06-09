from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # 1. AUTHENTIFICATION (Gestion de la sécurité)
    # Le personnel arrive d'abord ici pour se connecter
    path('', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    
    # UNE SEULE ROUTE LOGOUT : On utilise ta fonction sur mesure qui accepte le clic du Navbar
    path('logout/', views.deconnexion_utilisateur, name='logout'),
    
    # L'adresse d'aiguillage automatique configurée dans settings.py après un login réussi
    path('redirection/', views.page_connexion_reussie, name='page_connexion_reussie'),
    
    # 2. INTERFACE UNIQUE COLLABORATIVE (Le nouveau flux)
    # C'est ici que TOUT LE MONDE atterrit (Recherche, Admission, Registre) 
    # Dans urls.py
    path('dashboard/', views.tableau_de_bord, name='tableau_de_bord'),
    path('tableau-de-bord/', views.interface_principale_laboratoire, name='interface_principale_laboratoire'), 
    path('modifier-examen/<int:analyse_id>/', views.modifier_examen_catalogue, name='modifier_examen'),
    
    # Le cœur de métier : Gestion d'un dossier (Ajout examens via menu déroulant, Saisie des résultats)
    path('visite/<int:visite_id>/examens/', views.gestion_examens_visite, name='gestion_examens_visite'), 
    path('examens/', views.liste_examens, name='liste_examens'),
    path('fiches/', views.liste_fiches_techniques, name='liste_fiches_techniques'), 
    path('visite/<int:visite_id>/supprimer/', views.supprimer_visite, name='supprimer_visite'), 
    path('ajouter-examen/', views.ajouter_nouvel_examen, name='ajouter_nouvel_examen'),
    
    # 3. REGISTRE ET IMPRESSIONS OFFICIELLES
    path('visites/', views.liste_visites, name='liste_visites'),
    path('visite/<int:visite_id>/recu/', views.imprimer_recu_facture, name='imprimer_recu_facture'),
    path('visite/<int:visite_id>/bulletin/', views.imprimer_bulletin_resultats, name='imprimer_bulletin_resultats'), 
]