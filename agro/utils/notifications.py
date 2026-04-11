"""
Notifications email automatiques pour E-Shelle Agro.
Utilise le système email Django (settings.EMAIL_BACKEND).
"""
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings

EXPEDITEUR = getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@e-shelle.com')
NOM_PLATEFORME = 'E-Shelle Agro'


def _envoyer(sujet, destinataire, template, contexte):
    """Helper interne d'envoi d'email HTML."""
    try:
        corps_html  = render_to_string(f'agro/emails/{template}.html', contexte)
        corps_texte = render_to_string(f'agro/emails/{template}.txt', contexte)
        send_mail(
            subject=sujet,
            message=corps_texte,
            from_email=f"{NOM_PLATEFORME} <{EXPEDITEUR}>",
            recipient_list=[destinataire],
            html_message=corps_html,
            fail_silently=True,
        )
    except Exception as e:
        import logging
        logging.getLogger('agro').warning(f"Erreur envoi email {template}: {e}")


def notifier_bienvenue_producteur(acteur):
    _envoyer(
        f"Bienvenue sur E-Shelle Agro — Complétez votre profil",
        acteur.email_pro,
        'bienvenue_producteur',
        {'acteur': acteur}
    )


def notifier_produit_valide(produit):
    _envoyer(
        f"✅ Votre produit « {produit.nom} » est maintenant en ligne",
        produit.acteur.email_pro,
        'produit_valide',
        {'produit': produit}
    )


def notifier_produit_rejete(produit, motif):
    _envoyer(
        f"⚠️ Votre produit « {produit.nom} » nécessite des corrections",
        produit.acteur.email_pro,
        'produit_rejete',
        {'produit': produit, 'motif': motif}
    )


def notifier_nouvelle_demande_devis(devis):
    _envoyer(
        f"📩 Nouvelle demande de devis de {devis.acheteur.nom_entreprise}",
        devis.vendeur.email_pro,
        'nouvelle_demande_devis',
        {'devis': devis}
    )


def notifier_devis_recu(devis):
    _envoyer(
        f"✉️ {devis.vendeur.nom_entreprise} a répondu à votre demande de devis",
        devis.acheteur.email_pro,
        'devis_recu',
        {'devis': devis}
    )


def notifier_commande_confirmee(commande):
    for acteur in [commande.acheteur, commande.vendeur]:
        _envoyer(
            f"✅ Commande #{commande.numero_commande} confirmée",
            acteur.email_pro,
            'commande_confirmee',
            {'commande': commande, 'acteur': acteur}
        )


def notifier_commande_expediee(commande):
    _envoyer(
        f"🚢 Votre commande #{commande.numero_commande} a été expédiée",
        commande.acheteur.email_pro,
        'commande_expediee',
        {'commande': commande}
    )


def notifier_nouvel_avis(avis):
    _envoyer(
        f"⭐ {avis.evaluateur.nom_entreprise} a laissé un avis sur votre profil",
        avis.evalue.email_pro,
        'nouvel_avis',
        {'avis': avis}
    )
