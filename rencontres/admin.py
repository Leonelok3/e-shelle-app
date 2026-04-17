from django.contrib import admin
from django.utils.html import mark_safe
from django.utils import timezone

from rencontres.models import (
    ProfilRencontre, PhotoProfil, Like, Match, Blocage,
    Conversation, Message, PlanPremiumRencontre, AbonnementRencontre,
    Signalement
)


@admin.register(ProfilRencontre)
class ProfilRencontreAdmin(admin.ModelAdmin):
    list_display = [
        'prenom_affiche', 'user', 'genre', 'age_display', 'ville',
        'pays', 'est_verifie', 'est_premium', 'est_actif',
        'profil_complet', 'derniere_connexion'
    ]
    list_filter = ['genre', 'est_verifie', 'est_premium', 'est_actif', 'pays', 'religion', 'est_diaspora']
    search_fields = ['prenom_affiche', 'user__email', 'user__username', 'ville']
    readonly_fields = ['derniere_connexion', 'vues_profil', 'profil_complet', 'date_creation']
    actions = ['verifier_profils', 'suspendre_profils', 'reactiver_profils', 'activer_premium_test']

    fieldsets = (
        ('Identité', {
            'fields': ('user', 'prenom_affiche', 'date_naissance', 'genre', 'orientation')
        }),
        ('Localisation', {
            'fields': ('pays', 'ville', 'latitude', 'longitude', 'nationalite', 'est_diaspora', 'pays_residence')
        }),
        ('Origine', {
            'fields': ('origine_ethnique',)
        }),
        ('Apparence', {
            'fields': ('taille_cm', 'morphologie', 'teint', 'photo_principale')
        }),
        ('Situation personnelle', {
            'fields': ('situation_matrimoniale', 'a_des_enfants', 'nb_enfants', 'veut_des_enfants')
        }),
        ('Formation & travail', {
            'fields': ('niveau_etude', 'profession', 'revenus')
        }),
        ('Religion', {
            'fields': ('religion', 'pratique_religieuse')
        }),
        ('À propos', {
            'fields': ('biographie', 'ce_que_je_cherche', 'interets', 'langues')
        }),
        ('Recherche partenaire', {
            'fields': ('recherche_age_min', 'recherche_age_max', 'recherche_genre',
                       'recherche_pays', 'recherche_religion', 'recherche_distance_km')
        }),
        ('Statut', {
            'fields': ('est_verifie', 'badge_verifie', 'est_actif', 'est_premium',
                       'profil_complet', 'vues_profil', 'derniere_connexion', 'date_creation')
        }),
        ('Confidentialité', {
            'fields': ('afficher_en_ligne', 'afficher_distance', 'qui_peut_ecrire')
        }),
    )

    def age_display(self, obj):
        try:
            return f"{obj.age()} ans"
        except Exception:
            return "—"
    age_display.short_description = "Âge"

    @admin.action(description="Vérifier les profils sélectionnés")
    def verifier_profils(self, request, queryset):
        queryset.update(est_verifie=True, badge_verifie=True)
        self.message_user(request, f"{queryset.count()} profil(s) vérifiés.")

    @admin.action(description="Suspendre les profils sélectionnés")
    def suspendre_profils(self, request, queryset):
        queryset.update(est_actif=False)
        self.message_user(request, f"{queryset.count()} profil(s) suspendus.")

    @admin.action(description="Réactiver les profils sélectionnés")
    def reactiver_profils(self, request, queryset):
        queryset.update(est_actif=True)
        self.message_user(request, f"{queryset.count()} profil(s) réactivés.")

    @admin.action(description="Activer le premium (test 30j)")
    def activer_premium_test(self, request, queryset):
        from rencontres.models import PlanPremiumRencontre, AbonnementRencontre
        plan = PlanPremiumRencontre.objects.filter(nom='gold').first()
        if not plan:
            self.message_user(request, "Plan Gold introuvable.", level='error')
            return
        for profil in queryset:
            AbonnementRencontre.objects.create(
                profil=profil,
                plan=plan,
                date_fin=timezone.now() + timezone.timedelta(days=30)
            )
        self.message_user(request, f"{queryset.count()} profil(s) passés en premium (30j).")


@admin.register(PhotoProfil)
class PhotoProfilAdmin(admin.ModelAdmin):
    list_display = ['profil', 'est_approuvee', 'est_principale', 'ordre', 'date_ajout', 'image_preview']
    list_filter = ['est_approuvee', 'est_principale']
    actions = ['approuver_photos', 'rejeter_photos']

    def image_preview(self, obj):
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}" height="60" style="border-radius:4px;"/>')
        return "—"
    image_preview.short_description = "Aperçu"

    @admin.action(description="Approuver les photos sélectionnées")
    def approuver_photos(self, request, queryset):
        queryset.update(est_approuvee=True)
        self.message_user(request, f"{queryset.count()} photo(s) approuvée(s).")

    @admin.action(description="Rejeter (supprimer) les photos sélectionnées")
    def rejeter_photos(self, request, queryset):
        count = queryset.count()
        queryset.delete()
        self.message_user(request, f"{count} photo(s) supprimée(s).")


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ['envoyeur', 'recepteur', 'type_like', 'date_like', 'est_lu']
    list_filter = ['type_like', 'est_lu']
    search_fields = ['envoyeur__prenom_affiche', 'recepteur__prenom_affiche']


@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = ['profil_1', 'profil_2', 'date_match', 'est_actif', 'score_compatibilite']
    list_filter = ['est_actif']
    search_fields = ['profil_1__prenom_affiche', 'profil_2__prenom_affiche']


@admin.register(PlanPremiumRencontre)
class PlanPremiumRencontreAdmin(admin.ModelAdmin):
    list_display = [
        'plan_badge', 'prix_xaf_display', 'prix_annuel_display',
        'likes_par_jour', 'messages_par_jour', 'photos_max',
        'filtre_avance', 'mode_incognito',
    ]
    ordering = ['prix_xaf_mensuel']

    fieldsets = (
        ('🏷️ Identité du plan', {
            'fields': ('nom', 'description'),
            'description': 'Silver = entrée de gamme · Gold = populaire · Platinum = tout illimité'
        }),
        ('💰 Tarification FCFA (Mobile Money)', {
            'fields': ('prix_xaf_mensuel', 'prix_xaf_annuel'),
            'description': 'Saisir les prix en FCFA. Le prix annuel doit offrir ~2 mois gratuits.'
        }),
        ('📊 Limites d\'utilisation', {
            'fields': ('likes_par_jour', 'super_likes_par_jour', 'messages_par_jour', 'photos_max', 'boost_profil_par_semaine'),
            'description': 'Mettre -1 pour illimité.'
        }),
        ('✨ Fonctionnalités incluses', {
            'fields': ('peut_voir_qui_a_like', 'peut_rembobiner', 'badge_premium',
                       'filtre_avance', 'sans_publicite', 'mode_incognito', 'stats_profil'),
        }),
    )

    def plan_badge(self, obj):
        colors = {'silver': '#9CA3AF', 'gold': '#F59E0B', 'platinum': '#8B5CF6'}
        icons  = {'silver': '🥈', 'gold': '🥇', 'platinum': '💎'}
        color  = colors.get(obj.nom, '#666')
        icon   = icons.get(obj.nom, '⭐')
        return format_html(
            '<span style="color:{};font-weight:800;font-size:1rem">{} {}</span>',
            color, icon, obj.get_nom_display()
        )
    plan_badge.short_description = 'Plan'
    plan_badge.admin_order_field = 'nom'

    def prix_xaf_display(self, obj):
        return format_html('<strong>{:,} FCFA</strong>/mois', int(obj.prix_xaf_mensuel)).replace(',', ' ')
    prix_xaf_display.short_description = 'Prix mensuel'
    prix_xaf_display.admin_order_field = 'prix_xaf_mensuel'

    def prix_annuel_display(self, obj):
        return format_html('{:,} FCFA/an', int(obj.prix_xaf_annuel)).replace(',', ' ')
    prix_annuel_display.short_description = 'Prix annuel'


@admin.register(AbonnementRencontre)
class AbonnementRencontreAdmin(admin.ModelAdmin):
    list_display = ['profil', 'plan', 'date_debut', 'date_fin', 'est_actif', 'jours_restants_display']
    list_filter = ['est_actif', 'plan']
    search_fields = ['profil__prenom_affiche']

    def jours_restants_display(self, obj):
        return f"{obj.jours_restants()} jours"
    jours_restants_display.short_description = "Jours restants"


@admin.register(Signalement)
class SignalementAdmin(admin.ModelAdmin):
    list_display = ['signaleur', 'signale', 'raison', 'date_signalement', 'est_traite', 'action_prise']
    list_filter = ['raison', 'est_traite']
    search_fields = ['signaleur__prenom_affiche', 'signale__prenom_affiche']
    actions = ['marquer_traites', 'suspendre_signales']

    @admin.action(description="Marquer comme traités")
    def marquer_traites(self, request, queryset):
        queryset.update(
            est_traite=True, action_prise='ignore',
            traite_par=request.user, date_traitement=timezone.now()
        )
        self.message_user(request, f"{queryset.count()} signalement(s) traités.")

    @admin.action(description="Suspendre les profils signalés")
    def suspendre_signales(self, request, queryset):
        profils = set(s.signale for s in queryset)
        for p in profils:
            p.est_actif = False
            p.save(update_fields=['est_actif'])
        queryset.update(
            est_traite=True, action_prise='suspension_temp',
            traite_par=request.user, date_traitement=timezone.now()
        )
        self.message_user(request, f"{len(profils)} profil(s) suspendu(s).")
