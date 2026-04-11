"""
Génération de PDF pour devis et factures avec ReportLab.
"""
from io import BytesIO
from django.utils import timezone

try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import cm
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
    )
    from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
    REPORTLAB_OK = True
except ImportError:
    REPORTLAB_OK = False


COULEUR_PRIMAIRE = (0.18, 0.42, 0.31)   # #2D6A4F
COULEUR_ACCENT   = (0.96, 0.64, 0.38)   # #F4A261


def _entete_pdf(elements, titre, reference, date_str):
    """Ajoute l'en-tête commun à tous les PDF."""
    styles = getSampleStyleSheet()

    style_titre = ParagraphStyle(
        'Titre', parent=styles['Title'],
        fontSize=18, textColor=colors.HexColor('#2D6A4F'),
        spaceAfter=4,
    )
    style_ref = ParagraphStyle(
        'Ref', parent=styles['Normal'],
        fontSize=10, textColor=colors.grey,
    )

    elements.append(Paragraph("🌿 E-SHELLE AGRO", style_titre))
    elements.append(Paragraph(f"{titre} — <b>{reference}</b>", style_ref))
    elements.append(Paragraph(f"Date : {date_str}", style_ref))
    elements.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#2D6A4F')))
    elements.append(Spacer(1, 0.4 * cm))


def generer_pdf_devis(devis):
    """Génère le PDF d'une demande de devis."""
    if not REPORTLAB_OK:
        return b"ReportLab non disponible"

    buffer = BytesIO()
    doc    = SimpleDocTemplate(buffer, pagesize=A4,
                rightMargin=2*cm, leftMargin=2*cm,
                topMargin=2*cm, bottomMargin=2*cm)
    elements = []
    styles   = getSampleStyleSheet()

    _entete_pdf(
        elements,
        "DEVIS / OFFRE DE PRIX",
        devis.reference,
        devis.date_creation.strftime('%d/%m/%Y')
    )

    # Parties impliquées
    style_section = ParagraphStyle(
        'Section', parent=styles['Heading2'],
        fontSize=11, textColor=colors.HexColor('#2D6A4F'),
        spaceBefore=12, spaceAfter=4,
    )
    elements.append(Paragraph("PARTIES IMPLIQUÉES", style_section))

    data_parties = [
        ['', 'ACHETEUR', 'VENDEUR'],
        ['Entreprise', devis.acheteur.nom_entreprise, devis.vendeur.nom_entreprise],
        ['Pays', devis.acheteur.pays, devis.vendeur.pays],
        ['Contact', devis.acheteur.telephone, devis.vendeur.telephone],
        ['Email', devis.acheteur.email_pro, devis.vendeur.email_pro],
    ]
    t = Table(data_parties, colWidths=[4*cm, 7*cm, 7*cm])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2D6A4F')),
        ('TEXTCOLOR',  (0, 0), (-1, 0), colors.white),
        ('FONTNAME',   (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('GRID',       (0, 0), (-1, -1), 0.5, colors.lightgrey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F8FAF5')]),
        ('FONTSIZE',   (0, 0), (-1, -1), 9),
        ('PADDING',    (0, 0), (-1, -1), 6),
    ]))
    elements.append(t)
    elements.append(Spacer(1, 0.5*cm))

    # Détail du devis
    elements.append(Paragraph("DÉTAIL DE LA DEMANDE", style_section))
    produit_nom = devis.produit.nom if devis.produit else 'Non spécifié'
    data_detail = [
        ['Produit',           produit_nom],
        ['Quantité demandée', f"{devis.quantite} {devis.unite_mesure}"],
        ['Destination',       devis.destination],
        ['Incoterm souhaité', devis.incoterm_souhaite or 'Non précisé'],
        ['Message',           devis.message[:200] + '...' if len(devis.message) > 200 else devis.message],
    ]
    if devis.prix_propose:
        data_detail.append(['Prix proposé', f"{devis.prix_propose} {devis.devise_propose}"])
    if devis.conditions_proposees:
        data_detail.append(['Conditions', devis.conditions_proposees[:200]])
    if devis.date_validite_devis:
        data_detail.append(['Validité devis', devis.date_validite_devis.strftime('%d/%m/%Y')])

    t2 = Table(data_detail, colWidths=[5*cm, 13*cm])
    t2.setStyle(TableStyle([
        ('GRID',     (0, 0), (-1, -1), 0.5, colors.lightgrey),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#F8FAF5')),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('PADDING',  (0, 0), (-1, -1), 6),
        ('VALIGN',   (0, 0), (-1, -1), 'TOP'),
    ]))
    elements.append(t2)
    elements.append(Spacer(1, 1*cm))

    # Pied de page
    style_footer = ParagraphStyle(
        'Footer', parent=styles['Normal'],
        fontSize=8, textColor=colors.grey, alignment=TA_CENTER
    )
    elements.append(HRFlowable(width="100%", thickness=1, color=colors.lightgrey))
    elements.append(Spacer(1, 0.2*cm))
    elements.append(Paragraph(
        "E-Shelle Agro — La plateforme agroalimentaire africaine | www.e-shelle.com/agro",
        style_footer
    ))

    doc.build(elements)
    return buffer.getvalue()


def generer_pdf_facture(commande):
    """Génère le PDF d'une facture de commande."""
    if not REPORTLAB_OK:
        return b"ReportLab non disponible"

    buffer = BytesIO()
    doc    = SimpleDocTemplate(buffer, pagesize=A4,
                rightMargin=2*cm, leftMargin=2*cm,
                topMargin=2*cm, bottomMargin=2*cm)
    elements = []
    styles   = getSampleStyleSheet()

    _entete_pdf(
        elements,
        "FACTURE COMMERCIALE",
        commande.numero_commande,
        commande.date_creation.strftime('%d/%m/%Y')
    )

    style_section = ParagraphStyle(
        'Section', parent=styles['Heading2'],
        fontSize=11, textColor=colors.HexColor('#2D6A4F'),
        spaceBefore=12, spaceAfter=4,
    )

    elements.append(Paragraph("PARTIES", style_section))
    data_parties = [
        ['', 'ACHETEUR', 'VENDEUR'],
        ['Entreprise', commande.acheteur.nom_entreprise, commande.vendeur.nom_entreprise],
        ['Pays', commande.acheteur.pays, commande.vendeur.pays],
        ['Contact', commande.acheteur.telephone, commande.vendeur.telephone],
    ]
    t = Table(data_parties, colWidths=[4*cm, 7*cm, 7*cm])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2D6A4F')),
        ('TEXTCOLOR',  (0, 0), (-1, 0), colors.white),
        ('FONTNAME',   (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('GRID',       (0, 0), (-1, -1), 0.5, colors.lightgrey),
        ('FONTSIZE',   (0, 0), (-1, -1), 9),
        ('PADDING',    (0, 0), (-1, -1), 6),
    ]))
    elements.append(t)
    elements.append(Spacer(1, 0.5*cm))

    elements.append(Paragraph("DÉTAIL COMMANDE", style_section))
    produit_nom = commande.devis.produit.nom if commande.devis and commande.devis.produit else 'Produit'
    data_cmd = [
        ['N° Commande',   commande.numero_commande],
        ['Produit',       produit_nom],
        ['Incoterm',      commande.incoterm],
        ['Port départ',   commande.port_depart or '—'],
        ['Port arrivée',  commande.port_arrivee or '—'],
        ['Transporteur',  commande.transporteur or '—'],
        ['Statut',        commande.get_statut_display()],
        ['Paiement',      commande.get_paiement_statut_display()],
    ]

    t2 = Table(data_cmd, colWidths=[5*cm, 13*cm])
    t2.setStyle(TableStyle([
        ('GRID',     (0, 0), (-1, -1), 0.5, colors.lightgrey),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#F8FAF5')),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('PADDING',  (0, 0), (-1, -1), 6),
    ]))
    elements.append(t2)
    elements.append(Spacer(1, 0.5*cm))

    # Total
    style_total = ParagraphStyle(
        'Total', parent=styles['Normal'],
        fontSize=14, fontName='Helvetica-Bold',
        textColor=colors.HexColor('#2D6A4F'),
        alignment=TA_RIGHT,
    )
    elements.append(Paragraph(
        f"MONTANT TOTAL : {commande.montant_total:,.2f} {commande.devise}",
        style_total
    ))
    elements.append(Spacer(1, 1*cm))

    style_footer = ParagraphStyle(
        'Footer', parent=styles['Normal'],
        fontSize=8, textColor=colors.grey, alignment=TA_CENTER
    )
    elements.append(HRFlowable(width="100%", thickness=1, color=colors.lightgrey))
    elements.append(Spacer(1, 0.2*cm))
    elements.append(Paragraph(
        "E-Shelle Agro — La plateforme agroalimentaire africaine | www.e-shelle.com/agro",
        style_footer
    ))

    doc.build(elements)
    return buffer.getvalue()
