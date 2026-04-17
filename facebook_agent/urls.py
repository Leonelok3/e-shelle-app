from django.urls import path
from . import views

app_name = "facebook_agent"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("posts/publies/", views.published_posts, name="published_posts"),
    path("posts/planifies/", views.scheduled_posts, name="scheduled_posts"),
    path("posts/creer/", views.create_scheduled_post, name="create_scheduled_post"),
    path("logs/", views.agent_logs, name="logs"),

    # Actions
    path("publier/", views.publish_now, name="publish_now"),

    # API AJAX
    path("api/publier/", views.publish_now_ajax, name="api_publish_now"),
    path("api/apercu/", views.preview_ai_content, name="api_preview"),
    path("api/statut/", views.api_status, name="api_status"),
]
