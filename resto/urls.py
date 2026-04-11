"""
E-Shelle Resto — URL Configuration
Namespace: resto
"""
from django.urls import path
from . import views

app_name = "resto"

urlpatterns = [
    # ── Public ────────────────────────────────────────────────────────────────
    path("", views.HomeView.as_view(), name="home"),
    path("restaurants/", views.RestaurantListView.as_view(), name="restaurant_list"),
    path("r/<slug:slug>/", views.RestaurantDetailView.as_view(), name="restaurant_detail"),
    path("recherche/", views.SearchView.as_view(), name="search"),
    path("inscription/", views.RestaurantRegisterView.as_view(), name="register"),

    # ── HTMX actions ──────────────────────────────────────────────────────────
    path("track/", views.TrackContactView.as_view(), name="track_contact"),
    path("favoris/<slug:slug>/toggle/", views.ToggleFavoriteView.as_view(), name="toggle_favorite"),
    path("r/<slug:slug>/avis/", views.SubmitReviewView.as_view(), name="submit_review"),

    # ── Dashboard ─────────────────────────────────────────────────────────────
    path("dashboard/", views.DashboardHomeView.as_view(), name="dashboard_home"),
    path("dashboard/profil/", views.DashboardProfileView.as_view(), name="dashboard_profile"),
    path("dashboard/menu/", views.DashboardMenuView.as_view(), name="dashboard_menu"),
    path("dashboard/analytics/", views.DashboardAnalyticsView.as_view(), name="dashboard_analytics"),
    path("dashboard/notifications/", views.DashboardNotificationsView.as_view(), name="dashboard_notifications"),
    path(
        "dashboard/plat/<int:pk>/disponibilite/",
        views.DishAvailabilityToggleView.as_view(),
        name="dish_availability_toggle",
    ),

    # ── Admin panel ───────────────────────────────────────────────────────────
    path("admin-panel/", views.admin_dashboard, name="admin_dashboard"),
]
