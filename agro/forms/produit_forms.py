from django import forms
from django.forms import inlineformset_factory
from ..models import ProduitAgro, PhotoProduit, UniteMesure, CategorieAgro


class ProduitAgroForm(forms.ModelForm):
    """Formulaire d'ajout/modification d'un produit agroalimentaire."""

    class Meta:
        model  = ProduitAgro
        fields = [
            'categorie', 'nom', 'nom_local', 'code_hs',
            'description', 'caracteristiques', 'origine_geographique',
            'prix_unitaire', 'devise', 'prix_negociable',
            'unite_mesure', 'quantite_stock', 'quantite_min_commande',
            'quantite_max_commande', 'conditionnement',
            'disponibilite', 'delai_livraison_jours',
            'saison_disponible', 'production_annuelle_tonnes',
            'normes_qualite', 'est_bio', 'est_equitable',
            'taux_humidite', 'granulometrie',
            'peut_exporter', 'incoterms_disponibles', 'port_embarquement',
            'image_principale', 'video_url', 'tags',
        ]
        widgets = {
            'categorie':     forms.Select(attrs={'class': 'form-select'}),
            'nom':           forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'Ex: Cacao Brut Grade 1'
            }),
            'nom_local':     forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'Nom local ou variété'
            }),
            'code_hs':       forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'Ex: 1801.00.00'
            }),
            'description':   forms.Textarea(attrs={
                'class': 'form-control', 'rows': 5,
                'placeholder': 'Décrivez votre produit en détail...'
            }),
            'origine_geographique': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Région du Centre, Cameroun'
            }),
            'prix_unitaire': forms.NumberInput(attrs={
                'class': 'form-control', 'step': '0.01'
            }),
            'devise':        forms.Select(attrs={'class': 'form-select'}),
            'unite_mesure':  forms.Select(attrs={'class': 'form-select'}),
            'quantite_stock': forms.NumberInput(attrs={
                'class': 'form-control', 'step': 'any'
            }),
            'quantite_min_commande': forms.NumberInput(attrs={
                'class': 'form-control', 'step': 'any'
            }),
            'quantite_max_commande': forms.NumberInput(attrs={
                'class': 'form-control', 'step': 'any'
            }),
            'conditionnement': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'Ex: Sacs de 50 kg'
            }),
            'disponibilite': forms.Select(attrs={'class': 'form-select'}),
            'delai_livraison_jours': forms.NumberInput(attrs={
                'class': 'form-control', 'min': 1
            }),
            'saison_disponible': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'Ex: Octobre à Février'
            }),
            'production_annuelle_tonnes': forms.NumberInput(attrs={
                'class': 'form-control', 'step': 'any'
            }),
            'taux_humidite': forms.NumberInput(attrs={
                'class': 'form-control', 'step': '0.1', 'min': 0, 'max': 100
            }),
            'granulometrie': forms.TextInput(attrs={'class': 'form-control'}),
            'port_embarquement': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'Ex: Port de Douala'
            }),
            'video_url':     forms.URLInput(attrs={
                'class': 'form-control', 'placeholder': 'https://youtube.com/...'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Uniquement les catégories actives
        self.fields['categorie'].queryset = CategorieAgro.objects.filter(
            est_active=True
        ).order_by('parent__nom', 'nom')

    def clean_image_principale(self):
        image = self.cleaned_data.get('image_principale')
        if image and hasattr(image, 'size'):
            if image.size > 5 * 1024 * 1024:
                raise forms.ValidationError("L'image ne doit pas dépasser 5 Mo.")
            # Vérifier le type MIME
            import imghdr, io
            image.seek(0)
            img_type = imghdr.what(None, image.read(512))
            image.seek(0)
            if img_type not in ['jpeg', 'png', 'webp']:
                raise forms.ValidationError("Format accepté : JPG, PNG ou WebP.")
        return image

    def clean_prix_unitaire(self):
        prix = self.cleaned_data.get('prix_unitaire')
        if prix and prix <= 0:
            raise forms.ValidationError("Le prix doit être positif.")
        return prix


PhotoProduitFormSet = inlineformset_factory(
    ProduitAgro, PhotoProduit,
    fields=['image', 'legende', 'est_principale', 'ordre'],
    extra=3, max_num=8, can_delete=True,
)
