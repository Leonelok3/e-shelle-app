"""
forms.py — auto_cameroun
"""
import re
from django import forms
from django.forms import inlineformset_factory

from .models import (
    Vehicule, PhotoVehicule, ProfilAuto,
    DemandeEssai, DemandeSoumissionVehicule, SignalementVehicule,
    TypeCarrosserie, TypeCarburant, TypeBoite, TypeTransaction, EtatVehicule,
)

VILLES_CM = [
    ("", "— Choisir une ville —"),
    ("Yaoundé", "Yaoundé"), ("Douala", "Douala"), ("Bafoussam", "Bafoussam"),
    ("Bamenda", "Bamenda"), ("Garoua", "Garoua"), ("Maroua", "Maroua"),
    ("Ngaoundéré", "Ngaoundéré"), ("Bertoua", "Bertoua"), ("Ebolowa", "Ebolowa"),
    ("Kribi", "Kribi"), ("Limbé", "Limbé"), ("Buea", "Buea"),
    ("Edéa", "Edéa"), ("Nkongsamba", "Nkongsamba"), ("Kumba", "Kumba"),
    ("Autre", "Autre"),
]

MARQUES_AUTO = [
    ("", "— Choisir une marque —"),
    ("Toyota", "Toyota"), ("Mercedes-Benz", "Mercedes-Benz"), ("BMW", "BMW"),
    ("Peugeot", "Peugeot"), ("Renault", "Renault"), ("Nissan", "Nissan"),
    ("Honda", "Honda"), ("Ford", "Ford"), ("Chevrolet", "Chevrolet"),
    ("Hyundai", "Hyundai"), ("Kia", "Kia"), ("Mitsubishi", "Mitsubishi"),
    ("Land Rover", "Land Rover"), ("Volkswagen", "Volkswagen"), ("Audi", "Audi"),
    ("Lexus", "Lexus"), ("Suzuki", "Suzuki"), ("Mazda", "Mazda"),
    ("Isuzu", "Isuzu"), ("Volvo", "Volvo"), ("Autre", "Autre"),
]


def valider_telephone(valeur):
    nettoye = re.sub(r"[\s\-\(\)]", "", valeur)
    if not re.match(r"^\+?[0-9]{8,15}$", nettoye):
        raise forms.ValidationError("Numéro de téléphone invalide.")
    return nettoye


class VehiculeForm(forms.ModelForm):
    marque = forms.ChoiceField(
        choices=MARQUES_AUTO,
        widget=forms.Select(attrs={"class": "auto-input"}),
        label="Marque",
    )
    marque_autre = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"class": "auto-input", "placeholder": "Préciser la marque"}),
        label="Autre marque",
    )
    ville = forms.ChoiceField(
        choices=VILLES_CM,
        widget=forms.Select(attrs={"class": "auto-input"}),
        label="Ville",
    )

    class Meta:
        model  = Vehicule
        fields = [
            "marque", "modele", "annee", "version", "couleur",
            "type_transaction", "type_carrosserie", "etat",
            "carburant", "boite", "puissance_cv", "cylindree", "conduite",
            "kilometrage", "nombre_places", "nombre_portes",
            "ville", "quartier", "adresse_complete",
            "prix", "devise", "periode_prix", "prix_negociable",
            "description", "options_equipements",
            "est_dedouane", "garantie", "premiere_main",
            "date_disponibilite",
        ]
        widgets = {
            "modele":           forms.TextInput(attrs={"class": "auto-input", "placeholder": "Ex : Corolla, C-Class, 208…"}),
            "annee":            forms.NumberInput(attrs={"class": "auto-input", "min": 1960, "max": 2026}),
            "version":          forms.TextInput(attrs={"class": "auto-input", "placeholder": "Ex : 1.6 HDi Confort"}),
            "couleur":          forms.TextInput(attrs={"class": "auto-input", "placeholder": "Ex : Gris métallisé"}),
            "type_transaction": forms.Select(attrs={"class": "auto-input"}),
            "type_carrosserie": forms.Select(attrs={"class": "auto-input"}),
            "etat":             forms.Select(attrs={"class": "auto-input"}),
            "carburant":        forms.Select(attrs={"class": "auto-input"}),
            "boite":            forms.Select(attrs={"class": "auto-input"}),
            "conduite":         forms.Select(attrs={"class": "auto-input"}),
            "puissance_cv":     forms.NumberInput(attrs={"class": "auto-input", "placeholder": "Ex : 90"}),
            "cylindree":        forms.TextInput(attrs={"class": "auto-input", "placeholder": "Ex : 1.6L"}),
            "kilometrage":      forms.NumberInput(attrs={"class": "auto-input", "placeholder": "Ex : 85000"}),
            "nombre_places":    forms.NumberInput(attrs={"class": "auto-input", "min": 1, "max": 60}),
            "nombre_portes":    forms.NumberInput(attrs={"class": "auto-input", "min": 1, "max": 6}),
            "quartier":         forms.TextInput(attrs={"class": "auto-input", "placeholder": "Ex : Bastos, Bonamoussadi…"}),
            "adresse_complete": forms.TextInput(attrs={"class": "auto-input"}),
            "prix":             forms.NumberInput(attrs={"class": "auto-input", "placeholder": "Ex : 4500000"}),
            "devise":           forms.Select(attrs={"class": "auto-input"}),
            "periode_prix":     forms.Select(attrs={"class": "auto-input"}),
            "prix_negociable":  forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "est_dedouane":     forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "premiere_main":    forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "garantie":         forms.TextInput(attrs={"class": "auto-input", "placeholder": "Ex : 6 mois"}),
            "description":      forms.Textarea(attrs={"class": "auto-input", "rows": 5, "placeholder": "Décrivez le véhicule…"}),
            "options_equipements": forms.Textarea(attrs={"class": "auto-input", "rows": 3, "placeholder": "Climatisation, GPS, Caméra de recul…"}),
            "date_disponibilite": forms.DateInput(attrs={"class": "auto-input", "type": "date"}),
        }

    def clean(self):
        cleaned = super().clean()
        if cleaned.get("marque") == "Autre":
            autre = cleaned.get("marque_autre", "").strip()
            if not autre:
                self.add_error("marque_autre", "Précisez la marque.")
            else:
                cleaned["marque"] = autre
        return cleaned


PhotoVehiculeFormSet = inlineformset_factory(
    Vehicule, PhotoVehicule,
    fields=["image", "legende", "est_photo_principale", "ordre"],
    extra=4, can_delete=True, max_num=10,
    widgets={
        "image":   forms.ClearableFileInput(attrs={"class": "auto-input", "accept": "image/*"}),
        "legende": forms.TextInput(attrs={"class": "auto-input", "placeholder": "Légende (optionnel)"}),
        "ordre":   forms.NumberInput(attrs={"class": "auto-input", "min": 0}),
    }
)


class ProfilAutoForm(forms.ModelForm):
    class Meta:
        model  = ProfilAuto
        fields = ["role", "telephone", "ville", "photo_profil", "description"]
        widgets = {
            "role":        forms.Select(attrs={"class": "auto-input"}),
            "telephone":   forms.TextInput(attrs={"class": "auto-input", "placeholder": "+237 6XX XX XX XX"}),
            "ville":       forms.TextInput(attrs={"class": "auto-input"}),
            "description": forms.Textarea(attrs={"class": "auto-input", "rows": 3}),
            "photo_profil": forms.ClearableFileInput(attrs={"class": "auto-input", "accept": "image/*"}),
        }

    def clean_telephone(self):
        return valider_telephone(self.cleaned_data.get("telephone", ""))


class DemandeEssaiForm(forms.ModelForm):
    class Meta:
        model  = DemandeEssai
        fields = ["nom_complet", "telephone", "email", "date_souhaitee", "message"]
        widgets = {
            "nom_complet":   forms.TextInput(attrs={"class": "auto-input", "placeholder": "Votre nom complet"}),
            "telephone":     forms.TextInput(attrs={"class": "auto-input", "placeholder": "+237 6XX XX XX XX"}),
            "email":         forms.EmailInput(attrs={"class": "auto-input", "placeholder": "email@exemple.com"}),
            "date_souhaitee": forms.DateInput(attrs={"class": "auto-input", "type": "date"}),
            "message":       forms.Textarea(attrs={"class": "auto-input", "rows": 3, "placeholder": "Message optionnel…"}),
        }

    def clean_telephone(self):
        return valider_telephone(self.cleaned_data.get("telephone", ""))


class DemandeSoumissionForm(forms.ModelForm):
    class Meta:
        model  = DemandeSoumissionVehicule
        fields = ["nom_complet", "telephone", "email", "marque", "modele", "annee", "type_transaction", "ville", "prix", "description"]
        widgets = {
            "nom_complet":      forms.TextInput(attrs={"class": "auto-input"}),
            "telephone":        forms.TextInput(attrs={"class": "auto-input", "placeholder": "+237 6XX XX XX XX"}),
            "email":            forms.EmailInput(attrs={"class": "auto-input"}),
            "marque":           forms.TextInput(attrs={"class": "auto-input"}),
            "modele":           forms.TextInput(attrs={"class": "auto-input"}),
            "annee":            forms.NumberInput(attrs={"class": "auto-input", "min": 1960, "max": 2026}),
            "type_transaction": forms.Select(attrs={"class": "auto-input"}),
            "ville":            forms.Select(attrs={"class": "auto-input"}, choices=VILLES_CM),
            "prix":             forms.NumberInput(attrs={"class": "auto-input"}),
            "description":      forms.Textarea(attrs={"class": "auto-input", "rows": 4}),
        }

    def clean_telephone(self):
        return valider_telephone(self.cleaned_data.get("telephone", ""))


class SignalementAutoForm(forms.ModelForm):
    class Meta:
        model  = SignalementVehicule
        fields = ["motif", "description"]
        widgets = {
            "motif":       forms.Select(attrs={"class": "auto-input"}),
            "description": forms.Textarea(attrs={"class": "auto-input", "rows": 4, "placeholder": "Détaillez le problème…"}),
        }


class RechercheAutoForm(forms.Form):
    q            = forms.CharField(required=False, widget=forms.TextInput(attrs={"class": "auto-input", "placeholder": "Marque, modèle…"}))
    type_transaction = forms.ChoiceField(required=False, choices=[("", "Vente & Location")] + list(TypeTransaction.choices), widget=forms.Select(attrs={"class": "auto-input"}))
    type_carrosserie = forms.ChoiceField(required=False, choices=[("", "Toutes")] + list(TypeCarrosserie.choices), widget=forms.Select(attrs={"class": "auto-input"}))
    carburant    = forms.ChoiceField(required=False, choices=[("", "Tous")] + list(TypeCarburant.choices), widget=forms.Select(attrs={"class": "auto-input"}))
    boite        = forms.ChoiceField(required=False, choices=[("", "Toutes")] + list(TypeBoite.choices), widget=forms.Select(attrs={"class": "auto-input"}))
    etat         = forms.ChoiceField(required=False, choices=[("", "Tous")] + list(EtatVehicule.choices), widget=forms.Select(attrs={"class": "auto-input"}))
    ville        = forms.ChoiceField(required=False, choices=VILLES_CM, widget=forms.Select(attrs={"class": "auto-input"}))
    annee_min    = forms.IntegerField(required=False, min_value=1960, widget=forms.NumberInput(attrs={"class": "auto-input", "placeholder": "Année min"}))
    annee_max    = forms.IntegerField(required=False, max_value=2030, widget=forms.NumberInput(attrs={"class": "auto-input", "placeholder": "Année max"}))
    prix_min     = forms.IntegerField(required=False, widget=forms.NumberInput(attrs={"class": "auto-input", "placeholder": "Prix min"}))
    prix_max     = forms.IntegerField(required=False, widget=forms.NumberInput(attrs={"class": "auto-input", "placeholder": "Prix max"}))
    km_max       = forms.IntegerField(required=False, widget=forms.NumberInput(attrs={"class": "auto-input", "placeholder": "Km max"}))
