from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0002_alter_transaction_type_tx'),
    ]

    operations = [
        migrations.CreateModel(
            name='PlanPremiumApp',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('module', models.CharField(
                    choices=[
                        ('annonces',   '📋 Annonces Cam'),
                        ('immo',       '🏠 Immobilier'),
                        ('auto',       '🚗 Auto Cameroun'),
                        ('agro',       '🌿 E-Shelle Agro'),
                        ('gaz',        '🔥 E-Shelle Gaz'),
                        ('pharma',     '💊 E-Shelle Pharma'),
                        ('pressing',   '👔 E-Shelle Pressing'),
                        ('formations', '📚 Formations'),
                        ('boutique',   '🛒 Boutique'),
                        ('rencontres', '❤️ E-Shelle Love'),
                        ('njangi',     '💰 Njangi'),
                        ('general',    '🌐 Général (toutes apps)'),
                    ],
                    max_length=30,
                    verbose_name='Application',
                )),
                ('slug', models.SlugField(
                    help_text='ex: starter, pro, expert — sans espaces',
                    verbose_name='Identifiant',
                )),
                ('nom', models.CharField(max_length=50, verbose_name='Nom du plan')),
                ('emoji', models.CharField(default='⭐', max_length=10, verbose_name='Emoji')),
                ('prix', models.PositiveIntegerField(verbose_name='Prix (FCFA)')),
                ('duree_jours', models.PositiveIntegerField(default=30, verbose_name='Durée (jours)')),
                ('description', models.TextField(
                    blank=True,
                    help_text="Phrase d'accroche affichée sous le nom du plan",
                    verbose_name='Description courte',
                )),
                ('benefices', models.JSONField(
                    default=list,
                    help_text='Liste JSON des avantages. Ex: ["30 jours Premium","Annonces illimitées"]',
                    verbose_name='Bénéfices',
                )),
                ('populaire', models.BooleanField(default=False, verbose_name='Plan populaire ⭐')),
                ('couleur', models.CharField(
                    default='#4CAF50',
                    help_text='Ex: #8B5CF6 pour violet',
                    max_length=20,
                    verbose_name='Couleur hex',
                )),
                ('actif', models.BooleanField(default=True, verbose_name='Actif')),
                ('ordre', models.PositiveSmallIntegerField(default=0, verbose_name="Ordre d'affichage")),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Plan Premium (par app)',
                'verbose_name_plural': 'Plans Premium (par app)',
                'ordering': ['module', 'ordre', 'prix'],
            },
        ),
        migrations.AlterUniqueTogether(
            name='planpremiumapp',
            unique_together={('module', 'slug')},
        ),
    ]
