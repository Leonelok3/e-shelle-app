"""
Administration Django pour edu_platform.
Upload direct de PDF / Vidéo / Audio depuis l'admin.
"""
from django.contrib import admin
from django.utils.html import format_html
from edu_platform.models import (
    EduProfile, SubscriptionPlan, AccessCode,
    DeviceBinding, Subject, ExamDocument, VideoLesson,
    AudioResource, PaymentTransaction,
)


# ──────────────────────────────────────────────────────────────────────────────
# Inlines pour Subject (upload direct depuis la fiche matière)
# ──────────────────────────────────────────────────────────────────────────────

class ExamDocumentInline(admin.TabularInline):
    model = ExamDocument
    extra = 1
    fields = ['doc_type', 'title', 'file', 'is_downloadable', 'preview_pages']
    show_change_link = True


class VideoLessonInline(admin.TabularInline):
    model = VideoLesson
    extra = 1
    fields = ['title', 'video_url', 'video_file', 'duration_minutes', 'is_preview', 'order']
    show_change_link = True


class AudioResourceInline(admin.TabularInline):
    model = AudioResource
    extra = 1
    fields = ['audio_type', 'title', 'audio_file', 'duration_minutes', 'is_preview', 'order']
    show_change_link = True


# ──────────────────────────────────────────────────────────────────────────────
# Subject — page centrale pour tout le contenu
# ──────────────────────────────────────────────────────────────────────────────

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'section_badge', 'level', 'subject_type',
        'year', 'doc_count', 'video_count', 'audio_count_display',
        'is_premium', 'is_published', 'order',
    ]
    list_filter = ['section', 'level', 'subject_type', 'is_premium', 'is_published']
    list_editable = ['is_published', 'order']
    prepopulated_fields = {'slug': ('title',)}
    search_fields = ['title', 'description']
    filter_horizontal = ['allowed_plans']
    inlines = [ExamDocumentInline, VideoLessonInline, AudioResourceInline]

    fieldsets = (
        ('Identification', {
            'fields': ('title', 'slug', 'section', 'level', 'subject_type', 'year'),
        }),
        ('Contenu', {
            'fields': ('description', 'thumbnail'),
        }),
        ('Accès', {
            'fields': ('is_premium', 'is_published', 'order', 'allowed_plans'),
        }),
    )

    def section_badge(self, obj):
        colors = {
            'francophone': '#27ae60',
            'technique':   '#e67e22',
            'anglophone':  '#2980b9',
        }
        color = colors.get(obj.section, '#888')
        return format_html(
            '<span style="background:{};color:#fff;padding:2px 8px;border-radius:4px;font-size:11px">{}</span>',
            color, obj.get_section_display()
        )
    section_badge.short_description = 'Section'

    def doc_count(self, obj):
        n = obj.document_count
        return format_html('<b>{}</b> PDF', n) if n else '—'
    doc_count.short_description = 'Docs'

    def video_count(self, obj):
        n = obj.video_count
        return format_html('<b>{}</b> vidéo(s)', n) if n else '—'
    video_count.short_description = 'Vidéos'

    def audio_count_display(self, obj):
        n = obj.audio_count
        return format_html('<b>{}</b> audio(s)', n) if n else '—'
    audio_count_display.short_description = 'Audios'


# ──────────────────────────────────────────────────────────────────────────────
# Documents, Vidéos, Audios — pages dédiées avec filtres par section/niveau
# ──────────────────────────────────────────────────────────────────────────────

@admin.register(ExamDocument)
class ExamDocumentAdmin(admin.ModelAdmin):
    list_display = ['title', 'subject', 'section_display', 'level_display', 'doc_type', 'file_size_kb', 'is_downloadable', 'uploaded_at']
    list_filter = ['doc_type', 'is_downloadable', 'subject__section', 'subject__level', 'subject__subject_type']
    search_fields = ['title', 'subject__title']
    readonly_fields = ['file_size_kb', 'uploaded_at']
    raw_id_fields = ['subject']

    def section_display(self, obj):
        return obj.subject.get_section_display()
    section_display.short_description = 'Section'

    def level_display(self, obj):
        return obj.subject.get_level_display()
    level_display.short_description = 'Niveau'


@admin.register(VideoLesson)
class VideoLessonAdmin(admin.ModelAdmin):
    list_display = ['title', 'subject', 'section_display', 'level_display', 'duration_minutes', 'is_preview', 'view_count', 'order']
    list_filter = ['is_preview', 'subject__section', 'subject__level']
    list_editable = ['order']
    search_fields = ['title', 'subject__title']
    raw_id_fields = ['subject']

    def section_display(self, obj):
        return obj.subject.get_section_display()
    section_display.short_description = 'Section'

    def level_display(self, obj):
        return obj.subject.get_level_display()
    level_display.short_description = 'Niveau'


@admin.register(AudioResource)
class AudioResourceAdmin(admin.ModelAdmin):
    list_display = ['title', 'subject', 'section_display', 'level_display', 'audio_type', 'duration_minutes', 'is_preview', 'play_count', 'order']
    list_filter = ['audio_type', 'is_preview', 'subject__section', 'subject__level']
    list_editable = ['order']
    search_fields = ['title', 'subject__title']
    raw_id_fields = ['subject']

    def section_display(self, obj):
        return obj.subject.get_section_display()
    section_display.short_description = 'Section'

    def level_display(self, obj):
        return obj.subject.get_level_display()
    level_display.short_description = 'Niveau'


# ──────────────────────────────────────────────────────────────────────────────
# Abonnements & Paiements
# ──────────────────────────────────────────────────────────────────────────────

@admin.register(EduProfile)
class EduProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone_number', 'country', 'created_at']
    search_fields = ['user__email', 'user__first_name', 'phone_number']
    list_filter = ['country']


@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = ['name', 'plan_type', 'price_xaf', 'duration_days', 'is_active']
    list_filter = ['plan_type', 'is_active']
    list_editable = ['is_active']


@admin.register(AccessCode)
class AccessCodeAdmin(admin.ModelAdmin):
    list_display = ['code', 'plan', 'status', 'activated_by', 'generated_at', 'expires_at']
    list_filter = ['status', 'plan']
    search_fields = ['code', 'activated_by__email']
    readonly_fields = ['code', 'generated_at', 'activation_count']
    raw_id_fields = ['activated_by', 'transaction']


@admin.register(DeviceBinding)
class DeviceBindingAdmin(admin.ModelAdmin):
    list_display = ['user', 'device_label', 'first_seen', 'last_seen', 'connection_count']
    search_fields = ['user__email', 'device_label']
    readonly_fields = ['device_fingerprint', 'first_seen']


@admin.register(PaymentTransaction)
class PaymentTransactionAdmin(admin.ModelAdmin):
    list_display = ['transaction_id', 'user', 'provider', 'amount_xaf', 'status', 'created_at']
    list_filter = ['provider', 'status']
    search_fields = ['user__email', 'phone_number', 'external_reference']
    readonly_fields = ['transaction_id', 'created_at', 'webhook_data']
