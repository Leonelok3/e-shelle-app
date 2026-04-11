# profiles/models.py — Alias de compatibilité vers accounts.UserProfile
# Les apps importées de immigration97 utilisent `from profiles.models import Profile`
from accounts.models import UserProfile as Profile

__all__ = ["Profile"]
