"""
Conversion de devises pour E-Shelle Agro.
Taux fixes pour XAF/EUR (parité BCEAO), taux variables via API pour le reste.
"""

# Taux de change en XAF (1 unité de devise = X XAF)
TAUX_FIXES = {
    'XAF': 1.0,
    'XOF': 1.0,           # parité avec XAF
    'EUR': 655.957,        # taux fixe BCEAO/BEAC
}

# Cache simple des taux variables (réinitialisé au restart)
_taux_cache = {}
_taux_cache_ts = {}


def _get_taux_variable(devise):
    """Récupère le taux de change via API avec cache 1h."""
    import time
    now = time.time()
    if devise in _taux_cache and (now - _taux_cache_ts.get(devise, 0)) < 3600:
        return _taux_cache[devise]

    try:
        import urllib.request, json
        url = f"https://api.exchangerate-api.com/v4/latest/XAF"
        with urllib.request.urlopen(url, timeout=5) as resp:
            data = json.loads(resp.read())
            rates = data.get('rates', {})
            if devise in rates and rates[devise] != 0:
                taux = 1.0 / rates[devise]
                _taux_cache[devise] = taux
                _taux_cache_ts[devise] = now
                return taux
    except Exception:
        pass

    # Taux de secours si l'API est indisponible
    FALLBACK = {
        'USD': 610.0,
        'GBP': 780.0,
        'NGN': 0.40,
        'GHS': 45.0,
        'MAD': 60.0,
    }
    return FALLBACK.get(devise, 1.0)


def get_taux_en_xaf(devise):
    """Retourne le taux de 1 unité de devise exprimé en XAF."""
    if devise in TAUX_FIXES:
        return TAUX_FIXES[devise]
    return _get_taux_variable(devise)


def convertir_prix(montant, devise_source, devise_cible):
    """Convertit un montant d'une devise vers une autre, via XAF comme pivot."""
    if devise_source == devise_cible:
        return round(float(montant), 2)

    taux_source = get_taux_en_xaf(devise_source)
    taux_cible  = get_taux_en_xaf(devise_cible)

    montant_xaf = float(montant) * taux_source
    montant_cible = montant_xaf / taux_cible

    return round(montant_cible, 2)


def formater_prix_local(montant, devise, locale_code='fr'):
    """Formate un prix avec le séparateur local."""
    try:
        montant = float(montant)
        if devise in ('XAF', 'XOF', 'NGN', 'GHS'):
            return f"{montant:,.0f} {devise}".replace(',', ' ')
        else:
            return f"{montant:,.2f} {devise}".replace(',', ' ')
    except (ValueError, TypeError):
        return f"{montant} {devise}"
