
import os
import django

# Configuration avec le VRAI nom de ton projet trouvé dans manage.py
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'saas_laboratoire.settings')
django.setup()

from core.models import Utilisateur

def generer_utilisateurs_terrain():
    print("Injection des profils du Laboratoire Ibn Heitham (Sécurité ajoutée)...")

    # 1. Le Réceptionniste (Fait tout le processus par défaut)
    user1, created1 = Utilisateur.objects.get_or_create(
        username="reception_ibn",
        defaults={
            "email": "reception@ibnheitham.com",
            "first_name": "Sidi",
            "last_name": "Mohamed",
            "role": "PERSONNEL",
            "is_staff": False
        }
    )
    if created1:
        user1.set_password("IbnHeitham2026")
        user1.save()
        print("✅ Compte [Réceptionniste] créé : 'reception_ibn' | MDP: 'IbnHeitham2026'")

    # 2. Le Technicien (Peut remplacer le réceptionniste si absent)
    user2, created2 = Utilisateur.objects.get_or_create(
        username="tech_ibn",
        defaults={
            "email": "technicien@ibnheitham.com",
            "first_name": "Fatimetou",
            "last_name": "Aly",
            "role": "PERSONNEL",
            "is_staff": False
        }
    )
    if created2:
        user2.set_password("TechIbn2026")
        user2.save()
        print("✅ Compte [Technicien] créé : 'tech_ibn' | MDP: 'TechIbn2026'")

    # 3. Le Biologiste (Superviseur qui valide les résultats)
    user3, created3 = Utilisateur.objects.get_or_create(
        username="biologiste_ibn",
        defaults={
            "email": "biologiste@ibnheitham.com",
            "first_name": "Dr. Ahmed",
            "last_name": "Sall",
            "role": "ADMIN",
            "is_staff": True,
            "is_superuser": True
        }
    )
    if created3:
        user3.set_password("BioIbn2026")
        user3.save()
        print("✅ Compte [Biologiste/Admin] créé : 'biologiste_ibn' | MDP: 'BioIbn2026'")

if __name__ == "__main__":
    generer_utilisateurs_terrain()