from django import forms

from .models import DemandeSante, ProduitSante, ProfessionnelSante, RendezVousSante


class ProduitSanteForm(forms.ModelForm):
    class Meta:
        model = ProduitSante
        fields = [
            "titre", "type_produit", "categorie", "description", "image", "ville",
            "vendeur_nom", "telephone", "whatsapp", "prix", "prix_barre",
            "stock_disponible", "livraison", "ordonnance_requise",
        ]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
        }


class ProfessionnelSanteForm(forms.ModelForm):
    class Meta:
        model = ProfessionnelSante
        fields = [
            "nom", "type_pro", "specialites", "ville", "quartier", "adresse",
            "description", "telephone", "whatsapp", "horaires",
            "consultation_domicile", "urgence", "teleconsultation",
        ]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
            "specialites": forms.CheckboxSelectMultiple(),
        }


class DemandeSanteForm(forms.ModelForm):
    class Meta:
        model = DemandeSante
        fields = ["nom", "telephone", "ville", "besoin", "message"]
        widgets = {
            "message": forms.Textarea(attrs={"rows": 3, "placeholder": "Décrivez votre besoin, quartier, urgence, produit recherché..."}),
        }


class RendezVousSanteForm(forms.ModelForm):
    class Meta:
        model = RendezVousSante
        fields = ["nom", "telephone", "motif", "date_souhaitee", "heure_souhaitee", "message"]
        widgets = {
            "date_souhaitee": forms.DateInput(attrs={"type": "date"}),
            "heure_souhaitee": forms.TimeInput(attrs={"type": "time"}),
            "message": forms.Textarea(attrs={"rows": 3, "placeholder": "Symptômes, disponibilité, préférence téléconsultation ou présentiel..."}),
        }
