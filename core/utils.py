# core/utils.py — Utilitaires partagés

from .constants import LEVEL_ORDER

_LEVELS = sorted(LEVEL_ORDER.keys(), key=lambda l: LEVEL_ORDER[l])


def get_next_level(current_level: str) -> str | None:
    """Retourne le niveau CECR suivant, ou None si déjà au maximum."""
    try:
        idx = _LEVELS.index(current_level)
        return _LEVELS[idx + 1] if idx + 1 < len(_LEVELS) else None
    except ValueError:
        return None


def get_prev_level(current_level: str) -> str | None:
    """Retourne le niveau CECR précédent, ou None si déjà au minimum."""
    try:
        idx = _LEVELS.index(current_level)
        return _LEVELS[idx - 1] if idx > 0 else None
    except ValueError:
        return None
