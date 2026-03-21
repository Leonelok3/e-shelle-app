from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from .forms import LoginForm
from .models import Role


class AppLoginView(LoginView):
    template_name = "accounts/login.html"
    authentication_form = LoginForm


class AppLogoutView(LogoutView):
    pass


from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from .models import Role

@login_required
def role_redirect(request):
    user = request.user

    if user.role == Role.PARENT:
        return redirect("progress:parent_dashboard")
    if user.role == Role.TEACHER:
        return redirect("progress:teacher_dashboard")
    if user.role == Role.STUDENT:
        return redirect("progress:student_dashboard")

    return redirect("/admin/")
