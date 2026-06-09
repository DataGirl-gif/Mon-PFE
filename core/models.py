from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractUser

class Utilisateur(AbstractUser):
    ROLE_CHOICES = [
        ('ADMIN', 'Administrateur / Superviseur'),
        ('PERSONNEL', 'Personnel du Laboratoire (Polyvalent)'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='PERSONNEL')

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

class Patient(models.Model):
    SEXE_CHOICES = [
        ('M', 'Masculin'),
        ('F', 'Féminin'),
    ]
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    # Date de naissance optionnelle (marquée nulle sur le terrain)
    date_naissance = models.DateField(blank=True, null=True) 
    sexe = models.CharField(max_length=1, choices=SEXE_CHOICES)
    telephone = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.nom.upper()} {self.prenom}"

class Analyse(models.Model):
    nom = models.CharField(max_length=150)  # Ex: Ac-Anti Phospholipides Total, 25-OH VITD TOTAL
    prix = models.DecimalField(max_length=10, max_digits=10, decimal_places=2, default=0.00)
    unite = models.CharField(max_length=50, blank=True, null=True)
    valeurs_normales = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nom

class Visite(models.Model):
    STATUT_CHOICES = [
        ('EN_COURS', 'En cours de traitement'),
        ('VALIDE', 'Visite validée médicalement'),
    ]
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='visites')
    date_visite = models.DateTimeField(default=timezone.now)
    
    # Paramètres financiers observés sur le terrain (0 par défaut)
    deplacement = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    majoration = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    taux_reduction = models.IntegerField(default=0) # Pourcentage de réduction
    
    # Docteur optionnel (vu sur le terrain)
    docteur_prescripteur = models.CharField(max_length=150, blank=True, null=True)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='EN_COURS')
    
    # Traçabilité de la validation
    valide_par = models.ForeignKey(Utilisateur, on_delete=models.SET_NULL, null=True, blank=True, related_name='visites_validees')

    def __str__(self):
        return f"Visite N°{self.id} - Patient: {self.patient.nom}"

class VisiteAnalyse(models.Model):
    """Table centrale contenant la désignation, le résultat saisie, l'unité et la description"""
    visite = models.ForeignKey(Visite, on_delete=models.CASCADE, related_name='examens')
    analyse = models.ForeignKey(Analyse, on_delete=models.CASCADE)
    valeur_resultat = models.CharField(max_length=100, blank=True, null=True) # Résultat saisi au clavier
    saisi_par = models.ForeignKey(Utilisateur, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.analyse.nom} pour Visite #{self.visite.id}"