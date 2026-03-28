from django import forms
from django.core.validators import FileExtensionValidator
from rencontres.models import ProfilRencontre, PhotoProfil

INTERETS_CHOICES = [
    ('Voyage', 'Voyage'), ('Cuisine', 'Cuisine'), ('Sport', 'Sport'),
    ('Musique', 'Musique'), ('Lecture', 'Lecture'), ('Cinéma', 'Cinéma'),
    ('Danse', 'Danse'), ('Art', 'Art'), ('Technologie', 'Technologie'),
    ('Nature', 'Nature'), ('Fitness', 'Fitness'), ('Mode', 'Mode'),
    ('Photographie', 'Photographie'), ('Gaming', 'Gaming'), ('Yoga', 'Yoga'),
    ('Entrepreneuriat', 'Entrepreneuriat'), ('Spiritualité', 'Spiritualité'),
    ('Famille', 'Famille'), ('Bénévolat', 'Bénévolat'), ('Agriculture', 'Agriculture'),
]

LANGUES_CHOICES = [
    ('Français', 'Français'), ('Anglais', 'Anglais'), ('Espagnol', 'Espagnol'),
    ('Portugais', 'Portugais'), ('Arabe', 'Arabe'), ('Wolof', 'Wolof'),
    ('Dioula', 'Dioula'), ('Ewondo', 'Ewondo'), ('Bamiléké', 'Bamiléké'),
    ('Lingala', 'Lingala'), ('Swahili', 'Swahili'), ('Haoussa', 'Haoussa'),
    ('Yoruba', 'Yoruba'), ('Igbo', 'Igbo'), ('Twi', 'Twi'),
    ('Allemand', 'Allemand'), ('Italien', 'Italien'), ('Fulfulde', 'Fulfulde'),
]


class ProfilRencontreForm(forms.ModelForm):
    interets = forms.MultipleChoiceField(
        choices=INTERETS_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Centres d'intérêt"
    )
    langues = forms.MultipleChoiceField(
        choices=LANGUES_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Langues parlées"
    )

    class Meta:
        model = ProfilRencontre
        fields = [
            'prenom_affiche', 'date_naissance', 'genre', 'orientation',
            'pays', 'ville', 'nationalite', 'est_diaspora', 'pays_residence',
            'origine_ethnique', 'taille_cm', 'morphologie', 'teint',
            'situation_matrimoniale', 'a_des_enfants', 'nb_enfants', 'veut_des_enfants',
            'niveau_etude', 'profession', 'revenus',
            'religion', 'pratique_religieuse',
            'langues', 'biographie', 'ce_que_je_cherche', 'interets',
            'recherche_age_min', 'recherche_age_max', 'recherche_genre',
            'recherche_distance_km',
            'afficher_en_ligne', 'afficher_distance', 'qui_peut_ecrire',
        ]
        widgets = {
            'date_naissance': forms.DateInput(
                attrs={'type': 'date', 'class': 'form-control'},
                format='%Y-%m-%d'
            ),
            'biographie': forms.Textarea(attrs={'rows': 4, 'maxlength': 1000}),
            'ce_que_je_cherche': forms.Textarea(attrs={'rows': 3, 'maxlength': 500}),
            'taille_cm': forms.NumberInput(attrs={'min': 100, 'max': 250}),
            'recherche_age_min': forms.NumberInput(attrs={'min': 18, 'max': 99}),
            'recherche_age_max': forms.NumberInput(attrs={'min': 18, 'max': 99}),
            'recherche_distance_km': forms.NumberInput(attrs={'min': 10, 'max': 20000}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Ajouter la classe Bootstrap à tous les champs
        for field_name, field in self.fields.items():
            if isinstance(field.widget, (forms.TextInput, forms.Select,
                                         forms.NumberInput, forms.EmailInput,
                                         forms.URLInput, forms.PasswordInput)):
                field.widget.attrs.setdefault('class', 'form-control')
            elif isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.setdefault('class', 'form-check-input')
            elif isinstance(field.widget, forms.Textarea):
                field.widget.attrs.setdefault('class', 'form-control')

        # Initialiser les champs JSON
        if self.instance and self.instance.pk:
            if self.instance.interets:
                self.initial['interets'] = self.instance.interets
            if self.instance.langues:
                self.initial['langues'] = self.instance.langues

    def clean_interets(self):
        return list(self.cleaned_data.get('interets', []))

    def clean_langues(self):
        return list(self.cleaned_data.get('langues', []))

    def clean(self):
        cleaned = super().clean()
        age_min = cleaned.get('recherche_age_min', 18)
        age_max = cleaned.get('recherche_age_max', 60)
        if age_min and age_max and age_min > age_max:
            raise forms.ValidationError(
                "L'âge minimum doit être inférieur à l'âge maximum."
            )
        return cleaned


class PhotoProfilForm(forms.ModelForm):
    class Meta:
        model = PhotoProfil
        fields = ['image', 'est_principale']

    def clean_image(self):
        image = self.cleaned_data.get('image')
        if image:
            # Vérifier la taille (max 5 Mo)
            if image.size > 5 * 1024 * 1024:
                raise forms.ValidationError("L'image ne doit pas dépasser 5 Mo.")
            # Vérifier le type MIME
            allowed_types = ['image/jpeg', 'image/png', 'image/webp']
            if hasattr(image, 'content_type') and image.content_type not in allowed_types:
                raise forms.ValidationError("Format accepté : JPEG, PNG, WebP.")
        return image
