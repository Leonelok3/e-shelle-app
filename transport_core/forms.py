from django import forms
from .models import DemandeTrajet, Trajet


class TrajetForm(forms.ModelForm):
    class Meta:
        model = Trajet
        fields = [
            "type_trajet", "depart", "arrivee", "lieu_depart", "lieu_arrivee",
            "date_depart", "heure_depart", "places_disponibles", "prix_place",
            "conducteur_nom", "telephone", "whatsapp", "vehicule",
            "bagages_acceptes", "colis_acceptes", "description", "conditions",
        ]
        widgets = {
            "date_depart": forms.DateInput(attrs={"type": "date"}),
            "heure_depart": forms.TimeInput(attrs={"type": "time"}),
            "description": forms.Textarea(attrs={"rows": 4}),
            "conditions": forms.Textarea(attrs={"rows": 3}),
        }


class DemandeTrajetForm(forms.ModelForm):
    class Meta:
        model = DemandeTrajet
        fields = ["depart", "arrivee", "date_souhaitee", "nom", "telephone", "places", "budget_max", "message"]
        widgets = {
            "date_souhaitee": forms.DateInput(attrs={"type": "date"}),
            "message": forms.Textarea(attrs={"rows": 3, "placeholder": "Heure souhaitée, bagages, point de départ..."}),
        }
