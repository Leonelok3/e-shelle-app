from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.db.models import Avg, Max, Count
from django.utils import timezone

from accounts.models import Role, ParentStudentLink
from .models import Attempt


def _role_guard(request, role):
    if not request.user.is_authenticated:
        return redirect("accounts:login")
    if request.user.role != role:
        return redirect("home")
    return None


def _stats_for_user(u):
    qs = Attempt.objects.filter(user=u).order_by("-created_at")
    total = qs.count()
    avg_score = qs.aggregate(a=Avg("score"))["a"] or 0
    best = qs.aggregate(m=Max("score"))["m"] or 0

    chart_qs = list(qs[:20])[::-1]  # ordre chronologique
    labels = [timezone.localtime(a.created_at).strftime("%d/%m") for a in chart_qs]
    data = [float(a.score) for a in chart_qs]

    recent = qs.select_related("exercise", "exam")[:10]

    return {
        "total": total,
        "avg_score": round(float(avg_score), 2),
        "best": float(best),
        "labels": labels,
        "data": data,
        "recent": recent,
    }


@login_required
def student_dashboard(request):
    deny = _role_guard(request, Role.STUDENT)
    if deny:
        return deny

    stats = _stats_for_user(request.user)
    return render(request, "student/dashboard.html", {"stats": stats})


@login_required
def parent_dashboard(request):
    deny = _role_guard(request, Role.PARENT)
    if deny:
        return deny

    links = ParentStudentLink.objects.filter(parent=request.user).select_related("student")
    children = [l.student for l in links]

    children_cards = []
    for child in children:
        card = _stats_for_user(child)
        card["child"] = child
        card["class_level"] = getattr(getattr(child, "student_profile", None), "class_level", None)
        children_cards.append(card)

    return render(request, "parent/dashboard.html", {"children_cards": children_cards})


@login_required
def teacher_dashboard(request):
    deny = _role_guard(request, Role.TEACHER)
    if deny:
        return deny

    attempts = Attempt.objects.select_related("user", "exercise", "exam").order_by("-created_at")

    recent_attempts = attempts[:15]
    leaderboard = (
        attempts.values("user__id", "user__username")
        .annotate(avg=Avg("score"), total=Count("id"))
        .order_by("-avg")[:10]
    )

    return render(request, "teacher/dashboard.html", {
        "recent_attempts": recent_attempts,
        "leaderboard": leaderboard
    })
