# core/constants.py — Constantes partagées CECR / CEFR

LEVEL_CHOICES = [
    ("A1", "A1 — Débutant"),
    ("A2", "A2 — Élémentaire"),
    ("B1", "B1 — Intermédiaire"),
    ("B2", "B2 — Intermédiaire supérieur"),
    ("C1", "C1 — Avancé"),
    ("C2", "C2 — Maîtrise"),
]

LEVEL_ORDER = {
    "A1": 1,
    "A2": 2,
    "B1": 3,
    "B2": 4,
    "C1": 5,
    "C2": 6,
}

# Seuil de réussite par défaut (score en %)
LEVEL_PASS_THRESHOLD = 60

# Badges CECR attribués à chaque niveau
CEFR_BADGES = {
    "A1": {
        "label": "Débutant",
        "icon": "🌱",
        "color": "#9E9E9E",
        "description": "Premiers pas en langue",
    },
    "A2": {
        "label": "Élémentaire",
        "icon": "⭐",
        "color": "#4CAF50",
        "description": "Communication de base",
    },
    "B1": {
        "label": "Intermédiaire",
        "icon": "🎯",
        "color": "#2196F3",
        "description": "Autonomie conversationnelle",
    },
    "B2": {
        "label": "Intermédiaire supérieur",
        "icon": "🏆",
        "color": "#FF9800",
        "description": "Aisance dans des contextes variés",
    },
    "C1": {
        "label": "Avancé",
        "icon": "💎",
        "color": "#9C27B0",
        "description": "Expression fluide et précise",
    },
    "C2": {
        "label": "Maîtrise",
        "icon": "👑",
        "color": "#FFD700",
        "description": "Niveau bilingue",
    },
}
