from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib import messages
from .forms import LoginForm
from .models import Role, CustomUser, UserProfile


class AppLoginView(LoginView):
    template_name = "accounts/login.html"
    authentication_form = LoginForm


class AppLogoutView(LogoutView):
    pass


@login_required
def role_redirect(request):
    """Redirige l'utilisateur vers son dashboard selon son rôle."""
    return redirect("dashboard:index")


def register(request):
    """Inscription d'un nouvel utilisateur."""
    if request.user.is_authenticated:
        return redirect("dashboard:index")

    if request.method == "POST":
        username   = request.POST.get("username", "").strip()
        email      = request.POST.get("email", "").strip()
        password1  = request.POST.get("password1", "")
        password2  = request.POST.get("password2", "")
        first_name = request.POST.get("first_name", "").strip()
        last_name  = request.POST.get("last_name", "").strip()
        role       = request.POST.get("role", Role.STUDENT)

        # Validations basiques
        if not username or not email or not password1:
            messages.error(request, "Tous les champs obligatoires doivent être remplis.")
        elif password1 != password2:
            messages.error(request, "Les mots de passe ne correspondent pas.")
        elif CustomUser.objects.filter(username=username).exists():
            messages.error(request, "Ce nom d'utilisateur est déjà pris.")
        elif CustomUser.objects.filter(email=email).exists():
            messages.error(request, "Cet email est déjà utilisé.")
        else:
            user = CustomUser.objects.create_user(
                username=username,
                email=email,
                password=password1,
                first_name=first_name,
                last_name=last_name,
                role=role if role in dict(Role.choices) else Role.STUDENT,
            )
            # Créer le profil étendu
            UserProfile.objects.get_or_create(user=user)
            login(request, user)
            messages.success(request, f"Bienvenue {user.first_name or user.username} ! 🎉")
            return redirect("dashboard:index")

    plan = request.GET.get("plan", "free")
    return render(request, "accounts/register.html", {"plan": plan, "roles": Role.choices})


@login_required
def profil(request):
    """Page de profil utilisateur."""
    profile, _ = UserProfile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        user = request.user
        user.first_name = request.POST.get("first_name", user.first_name)
        user.last_name  = request.POST.get("last_name",  user.last_name)
        user.email      = request.POST.get("email",      user.email)
        user.save(update_fields=["first_name", "last_name", "email"])

        profile.bio      = request.POST.get("bio",      profile.bio)
        profile.telephone = request.POST.get("telephone", profile.telephone)
        profile.ville    = request.POST.get("ville",    profile.ville)
        profile.pays     = request.POST.get("pays",     profile.pays)
        profile.site_web = request.POST.get("site_web", profile.site_web)
        if "avatar" in request.FILES:
            profile.avatar = request.FILES["avatar"]
        profile.save()

        messages.success(request, "Profil mis à jour avec succès.")
        return redirect("accounts:profil")

    return render(request, "accounts/profil.html", {"profile": profile})
