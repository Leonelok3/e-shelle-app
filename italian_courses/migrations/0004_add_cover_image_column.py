from django.db import migrations

class Migration(migrations.Migration):
    dependencies = [
        ("italian_courses", "0003_alter_lesson_cover_image"),
    ]

    # Colonne déjà créée par la migration 0003 via Django.
    # RunSQL PostgreSQL-only retiré pour compatibilité SQLite en dev.
    operations = []
