from django import forms
from .models import CandidatureJob, OffreJob


class CandidatureJobForm(forms.ModelForm):
    class Meta:
        model = CandidatureJob
        fields = ["nom", "telephone", "email", "ville", "message", "cv"]
        widgets = {
            "nom": forms.TextInput(attrs={"placeholder": "Votre nom complet"}),
            "telephone": forms.TextInput(attrs={"placeholder": "+237 6xx xxx xxx"}),
            "email": forms.EmailInput(attrs={"placeholder": "email@exemple.com"}),
            "ville": forms.TextInput(attrs={"placeholder": "Votre ville"}),
            "message": forms.Textarea(attrs={"rows": 4, "placeholder": "Courte presentation, experience, disponibilite..."}),
        }


class OffreJobForm(forms.ModelForm):
    class Meta:
        model = OffreJob
        fields = [
            "titre", "entreprise", "secteur", "ville", "quartier", "type_contrat", "mode_travail",
            "salaire_min", "salaire_max", "description", "missions", "profil_recherche",
            "telephone", "whatsapp", "email", "lien_externe", "date_limite",
        ]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 5}),
            "missions": forms.Textarea(attrs={"rows": 4}),
            "profil_recherche": forms.Textarea(attrs={"rows": 4}),
            "date_limite": forms.DateInput(attrs={"type": "date"}),
        }
