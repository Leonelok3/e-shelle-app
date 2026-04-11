from django.db.models import Q


def filtrer_produits(queryset, params):
    """
    Filtre avancé du catalogue produits.

    Paramètres GET supportés :
    - q           : recherche textuelle (nom, description, tags)
    - categorie   : slug catégorie
    - pays        : pays du producteur
    - devise      : devise du prix
    - prix_min    : prix minimum
    - prix_max    : prix maximum
    - unite       : unité de mesure
    - qte_min     : quantité minimale disponible en stock
    - disponibilite : en_stock | sur_commande | saisonnier | pre_commande
    - peut_exporter : true/false
    - incoterms   : FOB | CIF | EXW | DAP | DDP
    - est_bio     : true/false
    - est_equitable : true/false
    - note_min    : note minimale (1-5)
    - est_verifie : vendeur vérifié uniquement (true/false)
    - tri         : recent | prix_asc | prix_desc | populaire | note
    """

    # Recherche textuelle
    q = params.get('q', '').strip()
    if q:
        queryset = queryset.filter(
            Q(nom__icontains=q) |
            Q(nom_local__icontains=q) |
            Q(description__icontains=q) |
            Q(origine_geographique__icontains=q) |
            Q(acteur__nom_entreprise__icontains=q)
        )

    # Catégorie
    categorie_slug = params.get('categorie')
    if categorie_slug:
        queryset = queryset.filter(
            Q(categorie__slug=categorie_slug) |
            Q(categorie__parent__slug=categorie_slug)
        )

    # Pays du producteur
    pays = params.get('pays')
    if pays:
        queryset = queryset.filter(acteur__pays__icontains=pays)

    # Devise
    devise = params.get('devise')
    if devise:
        queryset = queryset.filter(devise=devise)

    # Fourchette de prix
    prix_min = params.get('prix_min')
    if prix_min:
        try:
            queryset = queryset.filter(prix_unitaire__gte=float(prix_min))
        except ValueError:
            pass

    prix_max = params.get('prix_max')
    if prix_max:
        try:
            queryset = queryset.filter(prix_unitaire__lte=float(prix_max))
        except ValueError:
            pass

    # Unité de mesure
    unite = params.get('unite')
    if unite:
        queryset = queryset.filter(unite_mesure=unite)

    # Quantité min disponible
    qte_min = params.get('qte_min')
    if qte_min:
        try:
            queryset = queryset.filter(quantite_stock__gte=float(qte_min))
        except ValueError:
            pass

    # Disponibilité
    disponibilite = params.get('disponibilite')
    if disponibilite:
        queryset = queryset.filter(disponibilite=disponibilite)

    # Export
    peut_exporter = params.get('peut_exporter')
    if peut_exporter == 'true':
        queryset = queryset.filter(peut_exporter=True)

    # Incoterms (contenu dans le JSONField)
    incoterm = params.get('incoterms')
    if incoterm:
        queryset = queryset.filter(incoterms_disponibles__contains=incoterm)

    # Bio
    est_bio = params.get('est_bio')
    if est_bio == 'true':
        queryset = queryset.filter(est_bio=True)

    # Équitable
    est_equitable = params.get('est_equitable')
    if est_equitable == 'true':
        queryset = queryset.filter(est_equitable=True)

    # Note minimale
    note_min = params.get('note_min')
    if note_min:
        try:
            queryset = queryset.filter(note_moyenne__gte=float(note_min))
        except ValueError:
            pass

    # Vendeur vérifié
    est_verifie = params.get('est_verifie')
    if est_verifie == 'true':
        queryset = queryset.filter(acteur__est_verifie=True)

    # Tri
    tri = params.get('tri', 'populaire')
    tri_map = {
        'recent':    '-date_creation',
        'prix_asc':  'prix_unitaire',
        'prix_desc': '-prix_unitaire',
        'populaire': '-nb_vues',
        'note':      '-note_moyenne',
    }
    queryset = queryset.order_by(
        '-est_mis_en_avant',
        tri_map.get(tri, '-nb_vues')
    )

    return queryset
