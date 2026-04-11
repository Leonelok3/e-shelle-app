from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from .forms import LoginForm
from .models import Role, CustomUser, UserProfile, EmailVerification


class AppLoginView(LoginView):
    template_name = "accounts/login.html"
    authentication_form = LoginForm


class AppLogoutView(LogoutView):
    pass


@login_required
def role_redirect(request):
    """Redirige l'utilisateur vers son dashboard selon son rôle."""
    return redirect("dashboard:index")


def _envoyer_code_verification(user, code):
    """Envoie l'email de vérification avec le code à 6 chiffres."""
    sujet = f"[E-Shelle] Votre code de vérification : {code}"
    corps_txt = (
        f"Bonjour {user.first_name or user.username},\n\n"
        f"Votre code de vérification E-Shelle est :\n\n"
        f"  {code}\n\n"
        f"Ce code est valable 15 minutes.\n"
        f"Si vous n'avez pas créé de compte, ignorez cet email.\n\n"
        f"— L'équipe E-Shelle"
    )
    corps_html = f"""
    <div style="font-family:Arial,sans-serif;max-width:480px;margin:0 auto;padding:2rem;
                background:#0d0d0d;color:#fff;border-radius:12px;">
      <div style="text-align:center;margin-bottom:2rem;">
        <span style="font-size:2rem;font-weight:900;letter-spacing:-1px;">
          <span style="color:#4CAF50">E</span>
          <span style="color:#F5C518">-Shelle</span>
        </span>
      </div>
      <h2 style="text-align:center;font-size:1.2rem;margin-bottom:.5rem;">
        Vérifiez votre adresse email
      </h2>
      <p style="color:#aaa;text-align:center;font-size:.9rem;margin-bottom:2rem;">
        Bonjour <strong style="color:#fff">{user.first_name or user.username}</strong>,<br>
        entrez ce code dans l'application pour activer votre compte :
      </p>
      <div style="background:#1a1a1a;border:2px solid #4CAF50;border-radius:12px;
                  padding:2rem;text-align:center;margin-bottom:2rem;">
        <span style="font-size:2.5rem;font-weight:900;letter-spacing:.5rem;
                     font-family:monospace;color:#4CAF50">{code}</span>
        <p style="color:#888;font-size:.8rem;margin:.75rem 0 0;">Valable 15 minutes</p>
      </div>
      <p style="color:#666;font-size:.78rem;text-align:center;">
        Si vous n'avez pas créé de compte sur E-Shelle, ignorez cet email.
      </p>
    </div>
    """
    import traceback
    try:
        send_mail(
            subject=sujet,
            message=corps_txt,
            html_message=corps_html,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )
        with open('/var/www/eshelle/email_debug.log', 'a') as f:
            f.write(f"OK: {user.email} | BACKEND={settings.EMAIL_BACKEND} | USER={settings.EMAIL_HOST_USER}\n")
    except Exception as e:
        with open('/var/www/eshelle/email_debug.log', 'a') as f:
            f.write(f"ERROR: {user.email} | {e}\n{traceback.format_exc()}\n")


def register(request):
    """Inscription — crée le compte inactif et envoie un code de vérification."""
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

        # Validations
        if not username or not email or not password1:
            messages.error(request, "Tous les champs obligatoires doivent être remplis.")
        elif password1 != password2:
            messages.error(request, "Les mots de passe ne correspondent pas.")
        elif len(password1) < 8:
            messages.error(request, "Le mot de passe doit contenir au moins 8 caractères.")
        elif CustomUser.objects.filter(username=username).exists():
            messages.error(request, "Ce nom d'utilisateur est déjà pris.")
        elif CustomUser.objects.filter(email=email).exists():
            messages.error(request, "Cet email est déjà utilisé.")
        else:
            # Créer le compte ACTIF directement
            user = CustomUser.objects.create_user(
                username=username,
                email=email,
                password=password1,
                first_name=first_name,
                last_name=last_name,
                role=role if role in dict(Role.choices) else Role.STUDENT,
                is_active=True,
            )
            UserProfile.objects.get_or_create(user=user)
            login(request, user)
            messages.success(request, f"Bienvenue {user.first_name or user.username} ! Votre compte a été créé.")
            return redirect("dashboard:index")

    plan = request.GET.get("plan", "free")
    return render(request, "accounts/register.html", {"plan": plan, "roles": Role.choices})


def verify_email(request):
    """Page de saisie du code de vérification."""
    user_id = request.session.get("verif_user_id")
    if not user_id:
        return redirect("accounts:register")

    user = get_object_or_404(CustomUser, pk=user_id, is_active=False)

    if request.method == "POST":
        code_saisi = "".join([
            request.POST.get(f"d{i}", "") for i in range(1, 7)
        ]).strip()

        try:
            verif = EmailVerification.objects.get(user=user)
        except EmailVerification.DoesNotExist:
            messages.error(request, "Aucun code trouvé. Veuillez vous réinscrire.")
            return redirect("accounts:register")

        if verif.is_verified:
            messages.info(request, "Compte déjà vérifié. Connectez-vous.")
            return redirect("accounts:login")

        if verif.est_expire:
            messages.error(request, "⏰ Code expiré. Cliquez sur « Renvoyer le code ».")
        elif verif.tentatives >= 5:
            messages.error(request, "Trop de tentatives. Cliquez sur « Renvoyer le code ».")
        elif code_saisi != verif.code:
            verif.tentatives += 1
            verif.save(update_fields=["tentatives"])
            restantes = 5 - verif.tentatives
            messages.error(request, f"❌ Code incorrect. {restantes} tentative(s) restante(s).")
        else:
            # ✅ Code correct — activer le compte
            verif.is_verified = True
            verif.save(update_fields=["is_verified"])
            user.is_active = True
            user.save(update_fields=["is_active"])

            del request.session["verif_user_id"]
            login(request, user, backend="django.contrib.auth.backends.ModelBackend")
            messages.success(request, f"🎉 Bienvenue {user.first_name or user.username} ! Votre compte est activé.")
            return redirect("dashboard:index")

    # Masquer une partie de l'email pour affichage
    em = user.email
    parts = em.split("@")
    email_masque = parts[0][:2] + "***@" + parts[1] if len(parts) == 2 else em

    return render(request, "accounts/verify_email.html", {
        "user": user,
        "email_masque": email_masque,
    })


def resend_code(request):
    """Renvoyer un nouveau code de vérification."""
    user_id = request.session.get("verif_user_id")
    if not user_id:
        return redirect("accounts:register")

    user = get_object_or_404(CustomUser, pk=user_id, is_active=False)
    verif = EmailVerification.generer(user)
    _envoyer_code_verification(user, verif.code)
    messages.success(request, f"✅ Nouveau code envoyé à {user.email}. Vérifiez votre boîte mail.")
    return redirect("accounts:verify_email")


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

        profile.bio       = request.POST.get("bio",       profile.bio)
        profile.telephone = request.POST.get("telephone", profile.telephone)
        profile.ville     = request.POST.get("ville",     profile.ville)
        profile.pays      = request.POST.get("pays",      profile.pays)
        profile.site_web  = request.POST.get("site_web",  profile.site_web)
        if "avatar" in request.FILES:
            profile.avatar = request.FILES["avatar"]
        profile.save()

        messages.success(request, "Profil mis à jour avec succès.")
        return redirect("accounts:profil")

    return render(request, "accounts/profil.html", {"profile": profile})
