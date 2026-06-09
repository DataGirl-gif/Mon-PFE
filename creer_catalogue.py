import os
import django

# Configuration avec le nom de ton projet
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'saas_laboratoire.settings')
django.setup()

from core.models import Analyse

def generer_catalogue_terrain():
    print("Mise à jour du catalogue avec les PRIX FINAUX du Laboratoire Ibn Heitham...")

    # Ta liste mise à jour avec les prix exacts fournis par le terrain
    catalogue = [
        {"nom": "Glycémie à jeun", "prix": 100.0, "unite": "g/L", "valeurs_normales": "0.70 - 1.10"},
        {"nom": "Urée Sérique", "prix": 150.0, "unite": "g/L", "valeurs_normales": "0.15 - 0.45"},
        {"nom": "Créatinine Sérique (Create)", "prix": 150.0, "unite": "mg/L", "valeurs_normales": "7.0 - 14.0"},
        {"nom": "Hémoglobine Glyquée (Hb Glyquée)", "prix": 600.0, "unite": "%", "valeurs_normales": "4.0 - 6.0"},
        {"nom": "TSH (Thyroid Stimulating Hormone)", "prix": 650.0, "unite": "µUI/mL", "valeurs_normales": "0.27 - 4.20"},
        {"nom": "FT4 (Thyroxine Libre)", "prix": 600.0, "unite": "ng/dL", "valeurs_normales": "0.93 - 1.70"},
        {"nom": "NFS (Numération Formule Sanguine)", "prix": 300.0, "unite": "—", "valeurs_normales": "Voir détails"},
        {"nom": "Vitamine D (VIT D)", "prix": 1800.0, "unite": "ng/mL", "valeurs_normales": "30.0 - 100.0"}
    ]

    for item in catalogue:
        analyse, created = Analyse.objects.get_or_create(
            nom=item["nom"],
            defaults={
                "prix": item["prix"],
                "unite": item["unite"],
                "valeurs_normales": item["valeurs_normales"]
            }
        )
        # Si l'analyse existait déjà, on force la mise à jour du prix réel
        analyse.prix = item["prix"]
        analyse.unite = item["unite"]
        analyse.valeurs_normales = item["valeurs_normales"]
        analyse.save()
        print(f"✅ Synchronisé : {item['nom']} -> {item['prix']} MRU")

    print("🚀 Base de données synchronisée à 100% avec les prix réels !")

if __name__ == "__main__":
    generer_catalogue_terrain()