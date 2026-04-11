from django import forms
from ..models import ActeurAgro, TypeActeur


class InscriptionActeurForm(forms.ModelForm):
    """Formulaire d'inscription acteur (onboarding simplifié)."""

    class Meta:
        model  = ActeurAgro
        fields = [
            'type_acteur', 'nom_entreprise', 'nom_contact', 'poste_contact',
            'pays', 'region', 'ville',
            'telephone', 'whatsapp', 'email_pro',
            'description',
        ]
        widgets = {
            'type_acteur':    forms.Select(attrs={'class': 'form-select form-select-lg'}),
            'nom_entreprise': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'Nom de votre entreprise / exploitation'
            }),
            'nom_contact':    forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'Votre nom complet'
            }),
            'poste_contact':  forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'Directeur, Gérant, Président GIC...'
            }),
            'pays':           forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'Cameroun, Côte d\'Ivoire...'
            }),
            'region':         forms.TextInput(attrs={'class': 'form-control'}),
            'ville':          forms.TextInput(attrs={'class': 'form-control'}),
            'telephone':      forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': '+237 6XX XXX XXX'
            }),
            'whatsapp':       forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': '+237 6XX XXX XXX (si différent)'
            }),
            'email_pro':      forms.EmailInput(attrs={
                'class': 'form-control', 'placeholder': 'contact@monentreprise.com'
            }),
            'description':    forms.Textarea(attrs={
                'class': 'form-control', 'rows': 4,
                'placeholder': 'Décrivez votre activité, vos produits principaux...'
            }),
        }

    def clean_nom_entreprise(self):
        nom = self.cleaned_data.get('nom_entreprise', '').strip()
        if len(nom) < 3:
            raise forms.ValidationError("Le nom doit comporter au moins 3 caractères.")
        return nom


class ActeurAgroForm(forms.ModelForm):
    """Formulaire complet de modification du profil acteur."""

    class Meta:
        model  = ActeurAgro
        fields = [
            'type_acteur', 'nom_entreprise', 'nom_contact', 'poste_contact',
            'logo', 'photo_couverture', 'description', 'annee_creation', 'nb_employes',
            'pays', 'region', 'ville', 'adresse', 'latitude', 'longitude', 'code_postal',
            'telephone', 'telephone2', 'whatsapp', 'email_pro', 'site_web',
            'superficie_ha', 'capacite_stockage_tonnes', 'volume_annuel_tonnes',
            'vend_localement', 'vend_nationalement', 'vend_internationalement',
        ]
        widgets = {
            'type_acteur':     forms.Select(attrs={'class': 'form-select'}),
            'nom_entreprise':  forms.TextInput(attrs={'class': 'form-control'}),
            'nom_contact':     forms.TextInput(attrs={'class': 'form-control'}),
            'poste_contact':   forms.TextInput(attrs={'class': 'form-control'}),
            'description':     forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'annee_creation':  forms.NumberInput(attrs={'class': 'form-control', 'min': 1900, 'max': 2026}),
            'nb_employes':     forms.Select(attrs={'class': 'form-select'}),
            'pays':            forms.TextInput(attrs={'class': 'form-control'}),
            'region':          forms.TextInput(attrs={'class': 'form-control'}),
            'ville':           forms.TextInput(attrs={'class': 'form-control'}),
            'adresse':         forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'latitude':        forms.NumberInput(attrs={'class': 'form-control', 'step': 'any'}),
            'longitude':       forms.NumberInput(attrs={'class': 'form-control', 'step': 'any'}),
            'code_postal':     forms.TextInput(attrs={'class': 'form-control'}),
            'telephone':       forms.TextInput(attrs={'class': 'form-control'}),
            'telephone2':      forms.TextInput(attrs={'class': 'form-control'}),
            'whatsapp':        forms.TextInput(attrs={'class': 'form-control'}),
            'email_pro':       forms.EmailInput(attrs={'class': 'form-control'}),
            'site_web':        forms.URLInput(attrs={'class': 'form-control'}),
            'superficie_ha':   forms.NumberInput(attrs={'class': 'form-control', 'step': 'any'}),
            'capacite_stockage_tonnes': forms.NumberInput(attrs={'class': 'form-control', 'step': 'any'}),
            'volume_annuel_tonnes':     forms.NumberInput(attrs={'class': 'form-control', 'step': 'any'}),
        }

    def clean_logo(self):
        logo = self.cleaned_data.get('logo')
        if logo and hasattr(logo, 'size'):
            if logo.size > 5 * 1024 * 1024:
                raise forms.ValidationError("Le logo ne doit pas dépasser 5 Mo.")
        return logo
