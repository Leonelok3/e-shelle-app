"""
Migration de données : création des plans premium initiaux.
"""
from django.db import migrations


def creer_plans_initiaux(apps, schema_editor):
    PlanPremiumRencontre = apps.get_model('rencontres', 'PlanPremiumRencontre')

    plans = [
        {
            'nom': 'silver',
            'prix_mensuel': 9.00,
            'prix_annuel': 75.00,
            'prix_xaf_mensuel': 5500,
            'prix_xaf_annuel': 45000,
            'likes_par_jour': -1,
            'super_likes_par_jour': 5,
            'messages_par_jour': -1,
            'peut_voir_qui_a_like': True,
            'peut_rembobiner': False,
            'boost_profil_par_semaine': 0,
            'photos_max': 12,
            'badge_premium': True,
            'filtre_avance': False,
            'sans_publicite': True,
            'mode_incognito': False,
            'stats_profil': False,
            'description': 'Likes illimités, voir qui vous a liké, 12 photos.',
        },
        {
            'nom': 'gold',
            'prix_mensuel': 19.00,
            'prix_annuel': 159.00,
            'prix_xaf_mensuel': 11500,
            'prix_xaf_annuel': 95000,
            'likes_par_jour': -1,
            'super_likes_par_jour': 10,
            'messages_par_jour': -1,
            'peut_voir_qui_a_like': True,
            'peut_rembobiner': True,
            'boost_profil_par_semaine': 1,
            'photos_max': 12,
            'badge_premium': True,
            'filtre_avance': True,
            'sans_publicite': True,
            'mode_incognito': True,
            'stats_profil': False,
            'description': 'Tout Silver + rembobinage, boost hebdo, filtres avancés, incognito.',
        },
        {
            'nom': 'platinum',
            'prix_mensuel': 35.00,
            'prix_annuel': 289.00,
            'prix_xaf_mensuel': 21000,
            'prix_xaf_annuel': 170000,
            'likes_par_jour': -1,
            'super_likes_par_jour': -1,
            'messages_par_jour': -1,
            'peut_voir_qui_a_like': True,
            'peut_rembobiner': True,
            'boost_profil_par_semaine': 3,
            'photos_max': 12,
            'badge_premium': True,
            'filtre_avance': True,
            'sans_publicite': True,
            'mode_incognito': True,
            'stats_profil': True,
            'description': 'TOUT débridé. Super likes illimités, 3 boosts/semaine, stats profil.',
        },
    ]

    for plan_data in plans:
        PlanPremiumRencontre.objects.get_or_create(
            nom=plan_data['nom'],
            defaults=plan_data
        )


def supprimer_plans(apps, schema_editor):
    PlanPremiumRencontre = apps.get_model('rencontres', 'PlanPremiumRencontre')
    PlanPremiumRencontre.objects.filter(nom__in=['silver', 'gold', 'platinum']).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('rencontres', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(creer_plans_initiaux, supprimer_plans),
    ]
