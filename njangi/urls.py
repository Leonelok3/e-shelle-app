"""
Njangi+ — URLs
"""
from django.urls import path
from . import views

app_name = "njangi"

urlpatterns = [
    # ── Pages publiques ───────────────────────────────────────────────────────
    path("",                        views.LandingView.as_view(),         name="landing"),
    path("rejoindre/",              views.JoinGroupView.as_view(),        name="join"),
    path("groupe/creer/",           views.CreateGroupView.as_view(),      name="create_group"),
    path("groupe/<slug:slug>/",     views.GroupDetailView.as_view(),      name="group_detail"),

    # ── Dashboard membre ──────────────────────────────────────────────────────
    path("mon-espace/",                     views.MemberDashboardView.as_view(),      name="member_dashboard"),
    path("mon-espace/cotisations/",         views.MemberContributionsView.as_view(),  name="member_contributions"),
    path("mon-espace/prets/",               views.MemberLoansView.as_view(),          name="member_loans"),
    path("mon-espace/prets/demande/",       views.LoanRequestView.as_view(),          name="loan_request"),
    path("mon-espace/depots/",              views.MemberDepositsView.as_view(),       name="member_deposits"),
    path("mon-espace/depots/nouveau/",      views.DepositCreateView.as_view(),        name="deposit_create"),
    path("mon-espace/depots/<int:pk>/retirer/", views.DepositWithdrawView.as_view(), name="deposit_withdraw"),
    path("mon-espace/notifications/",       views.MemberNotificationsView.as_view(),  name="member_notifications"),

    # ── Bureau (président / trésorier / secrétaire) ───────────────────────────
    path("bureau/<slug:slug>/",                         views.BureauDashboardView.as_view(),    name="bureau_dashboard"),
    path("bureau/<slug:slug>/membres/",                 views.BureauMembersView.as_view(),      name="bureau_members"),
    path("bureau/<slug:slug>/seances/",                 views.BureauSessionsView.as_view(),     name="bureau_sessions"),
    path("bureau/<slug:slug>/seances/creer/",           views.SessionCreateView.as_view(),      name="session_create"),
    path("bureau/<slug:slug>/seances/<int:pk>/",        views.SessionDetailView.as_view(),      name="session_detail"),
    path("bureau/<slug:slug>/seances/<int:pk>/ouvrir/", views.SessionOpenView.as_view(),        name="session_open"),
    path("bureau/<slug:slug>/seances/<int:pk>/cloturer/", views.SessionCloseView.as_view(),    name="session_close"),
    path("bureau/<slug:slug>/prets/",                   views.BureauLoansView.as_view(),        name="bureau_loans"),
    path("bureau/<slug:slug>/prets/<int:pk>/approuver/", views.LoanApproveView.as_view(),      name="loan_approve"),
    path("bureau/<slug:slug>/prets/<int:pk>/refuser/",  views.LoanRejectView.as_view(),         name="loan_reject"),
    path("bureau/<slug:slug>/prets/<int:pk>/decaisser/", views.LoanDisburseView.as_view(),     name="loan_disburse"),
    path("bureau/<slug:slug>/fond/",                    views.FundView.as_view(),               name="fund"),

    # ── Premium ───────────────────────────────────────────────────────────────
    path("premium/", views.PremiumView.as_view(), name="premium"),

    # ── HTMX partials ─────────────────────────────────────────────────────────
    path("htmx/cotisation/<int:pk>/payer/",   views.HtmxContributionPayView.as_view(),  name="htmx_contribution_pay"),
    path("htmx/remboursement/<int:pk>/",      views.HtmxRepaymentView.as_view(),        name="htmx_repayment"),
    path("htmx/notifications/marquer-lues/",  views.HtmxMarkNotificationsRead.as_view(), name="htmx_mark_read"),
]
