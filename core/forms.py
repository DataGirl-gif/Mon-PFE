from django import forms
from .models import Patient, Visite

class PatientForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = ['prenom', 'nom', 'date_naissance', 'sexe', 'telephone']
        widgets = {
            'prenom': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Prénom du patient'}),
            'nom': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom du patient'}),
            'date_naissance': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'sexe': forms.Select(attrs={'class': 'form-select'}),
            'telephone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: 44332211'}),
        }

class VisiteForm(forms.ModelForm):
    class Meta:
        model = Visite
        fields = ['docteur_prescripteur', 'majoration', 'deplacement', 'taux_reduction']
        widgets = {
            'docteur_prescripteur': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom du médecin (Optionnel)'}),
            'majoration': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'deplacement': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'taux_reduction': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'max': '100', 'placeholder': 'Ex: 10 pour 10%'}),
        }