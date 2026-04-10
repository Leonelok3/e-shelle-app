"""
Migration 0002 :
- Ajout du champ `section` sur Subject (francophone/technique/anglophone)
- Mise à jour des choix du champ `level` (niveaux du programme camerounais)
- Ajout du type de document 'exercise' sur ExamDocument
- Création du modèle AudioResource
- Ajout du champ `save()` auto file_size_kb sur ExamDocument
"""
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('edu_platform', '0001_initial'),
    ]

    operations = [
        # 1. Ajouter le champ section sur Subject
        migrations.AddField(
            model_name='subject',
            name='section',
            field=models.CharField(
                choices=[
                    ('francophone', 'Section Francophone'),
                    ('technique',   'Section Technique'),
                    ('anglophone',  'Section Anglophone'),
                ],
                default='francophone',
                max_length=20,
                verbose_name='Section',
                db_index=True,
            ),
        ),

        # 2. Mettre à jour les choix du champ level
        migrations.AlterField(
            model_name='subject',
            name='level',
            field=models.CharField(
                choices=[
                    ('3eme',        '3ème'),
                    ('2nde',        '2nde'),
                    ('1ere',        '1ère'),
                    ('tle',         'Terminale'),
                    ('4eme_tech',   '4ème (Technique)'),
                    ('3eme_tech',   '3ème (Technique)'),
                    ('2nde_tech',   '2nde (Technique)'),
                    ('1ere_tech',   '1ère (Technique)'),
                    ('tle_tech',    'Terminale (Technique)'),
                    ('form5',       'Form 5'),
                    ('lower_sixth', 'Lower Sixth'),
                    ('upper_sixth', 'Upper Sixth'),
                ],
                max_length=20,
                verbose_name='Niveau',
                db_index=True,
            ),
        ),

        # 3. Mettre à jour les choix du champ subject_type
        migrations.AlterField(
            model_name='subject',
            name='subject_type',
            field=models.CharField(
                choices=[
                    ('math',       'Mathématiques'),
                    ('french',     'Français / Literature'),
                    ('physics',    'Physique-Chimie'),
                    ('biology',    'SVT / Biology'),
                    ('history',    'Histoire-Géo'),
                    ('english',    'Anglais / English'),
                    ('philosophy', 'Philosophie'),
                    ('economics',  'Économie / Commerce'),
                    ('computer',   'Informatique / ICT'),
                    ('technical',  'Sciences Techniques'),
                    ('arts',       'Arts'),
                    ('sport',      'EPS / Sport'),
                    ('other',      'Autre'),
                ],
                max_length=30,
                verbose_name='Matière',
            ),
        ),

        # 4. Ajouter le type 'exercise' sur ExamDocument (choix uniquement, pas de champ DB)
        migrations.AlterField(
            model_name='examdocument',
            name='doc_type',
            field=models.CharField(
                choices=[
                    ('subject',             "Sujet d'examen"),
                    ('correction',          'Correction officielle'),
                    ('correction_proposed', 'Correction proposée'),
                    ('course_notes',        'Cours / Résumé'),
                    ('exercise',            'Exercices types'),
                ],
                max_length=30,
                verbose_name='Type de document',
            ),
        ),

        # 5. Créer le modèle AudioResource
        migrations.CreateModel(
            name='AudioResource',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('audio_type', models.CharField(
                    choices=[
                        ('course',     'Cours oral'),
                        ('correction', 'Correction audio'),
                        ('exercise',   'Exercice corrigé'),
                        ('interview',  'Interview / Témoignage'),
                        ('other',      'Autre'),
                    ],
                    default='course',
                    max_length=20,
                    verbose_name='Type',
                )),
                ('title',            models.CharField(max_length=200, verbose_name='Titre')),
                ('description',      models.TextField(blank=True, verbose_name='Description')),
                ('audio_file',       models.FileField(upload_to='edu_platform/audio/', verbose_name='Fichier audio (MP3/M4A/OGG)')),
                ('duration_minutes', models.IntegerField(default=0, verbose_name='Durée (minutes)')),
                ('is_preview',       models.BooleanField(default=False, verbose_name='Extrait gratuit')),
                ('order',            models.IntegerField(default=0, verbose_name='Ordre')),
                ('created_at',       models.DateTimeField(auto_now_add=True)),
                ('play_count',       models.IntegerField(default=0, verbose_name="Nombre d'écoutes")),
                ('subject', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='audios',
                    to='edu_platform.subject',
                    verbose_name='Matière',
                )),
            ],
            options={
                'verbose_name': 'Ressource audio',
                'verbose_name_plural': 'Ressources audio',
                'ordering': ['subject', 'order'],
            },
        ),
    ]
