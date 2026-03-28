from django import forms
from ..models import DemandeDevis, CommandeAgro, UniteMesure


class DemandeDevisForm(forms.ModelForm):
    """Formulaire de demande de devis."""

    class Meta:
        model  = DemandeDevis
        fields = [
            'quantite', 'unite_mesure', 'destination',
            'incoterm_souhaite', 'message',
        ]
        widgets = {
            'quantite':    forms.NumberInput(attrs={
                'class': 'form-control', 'step': 'any', 'min': 0
            }),
            'unite_mesure': forms.Select(attrs={'class': 'form-select'}),
            'destination': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Paris, France / Rotterdam, Pays-Bas'
            }),
            'incoterm_souhaite': forms.Select(attrs={'class': 'form-select'}),
            'message':     forms.Textarea(attrs={
                'class': 'form-control', 'rows': 4,
                'placeholder': (
                    'Précisez vos besoins : qualité souhaitée, certifications requises, '
                    'délais, conditions de paiement préférées...'
                )
            }),
        }

    def clean_quantite(self):
        qte = self.cleaned_data.get('quantite')
        if qte and qte <= 0:
            raise forms.ValidationError("La quantité doit être positive.")
        return qte

    def clean_message(self):
        msg = self.cleaned_data.get('message', '').strip()
        if len(msg) < 20:
            raise forms.ValidationError("Votre message doit comporter au moins 20 caractères.")
        return msg


class ReponseDevisForm(forms.ModelForm):
    """Formulaire de réponse du vendeur à une demande de devis."""

    class Meta:
        model  = DemandeDevis
        fields = [
            'prix_propose', 'devise_propose',
            'conditions_proposees', 'date_validite_devis',
        ]
        widgets = {
            'prix_propose':   forms.NumberInput(attrs={
                'class': 'form-control', 'step': '0.01'
            }),
            'devise_propose': forms.Select(
                choices=[
                    ('XAF', 'FCFA CFA'), ('XOF', 'FCFA Ouest'),
                    ('EUR', 'Euro'), ('USD', 'Dollar USD'),
                    ('GBP', 'Livre Sterling'),
                ],
                attrs={'class': 'form-select'}
            ),
            'conditions_proposees': forms.Textarea(attrs={
                'class': 'form-control', 'rows': 4,
                'placeholder': (
                    'Incoterm, délai de livraison, conditions de paiement '
                    '(acompte, virement, LC...), certificats disponibles...'
                )
            }),
            'date_validite_devis': forms.DateInput(
                attrs={'class': 'form-control', 'type': 'date'}
            ),
        }

    def clean_prix_propose(self):
        prix = self.cleaned_data.get('prix_propose')
        if prix and prix <= 0:
            raise forms.ValidationError("Le prix doit être positif.")
        return prix


class CommandeAgroForm(forms.ModelForm):
    """Formulaire de mise à jour statut commande (vendeur)."""

    class Meta:
        model  = CommandeAgro
        fields = [
            'statut', 'incoterm', 'port_depart', 'port_arrivee',
            'numero_connaissement', 'transporteur',
            'date_expedition', 'date_livraison_prevue',
            'paiement_statut', 'notes_vendeur',
        ]
        widgets = {
            'statut':             forms.Select(attrs={'class': 'form-select'}),
            'incoterm':           forms.Select(
                choices=[
                    ('EXW', 'EXW'), ('FOB', 'FOB'), ('CIF', 'CIF'),
                    ('DAP', 'DAP'), ('DDP', 'DDP'), ('CFR', 'CFR'),
                ],
                attrs={'class': 'form-select'}
            ),
            'port_depart':        forms.TextInput(attrs={'class': 'form-control'}),
            'port_arrivee':       forms.TextInput(attrs={'class': 'form-control'}),
            'numero_connaissement': forms.TextInput(attrs={'class': 'form-control'}),
            'transporteur':       forms.TextInput(attrs={'class': 'form-control'}),
            'date_expedition':    forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'date_livraison_prevue': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'paiement_statut':    forms.Select(attrs={'class': 'form-select'}),
            'notes_vendeur':      forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
