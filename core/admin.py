from django.contrib import admin
from django.utils.html import format_html
from .models import (
    CustomUser, Logement, Favori, ReclamationProprietaire, 
    AvisLogement, LoginHistory, UserSession, Profil,
    EmailVerificationToken, PasswordResetToken,
    BusinessModelCanvas, BusinessModelCanvasVersion,
    BusinessPlan, BusinessPlanVersion, BusinessPlanDocument, BusinessPlanComment,
    MarketStudy, MarketStudyQuestion, MarketStudyResponse, MarketStudyAnswer,
    Competitor, CompetitiveAnalysis,
    FinancialProjection, CashFlow, BalanceSheet, FinancialScenario, FinancialKPI,
    ReportedContent, UserModeration, VerificationRequest, PropertyClaimModeration,
    SupportTicket, TicketReply, ReplyTemplate,
    Settings, Role, AdminInvitation, PaymentConfig, NotificationConfig, NotificationTemplate,
    SecurityConfig, IntegrationConfig, ActivityLog
)

# ============================================
# ADMIN CUSTOMUSER
# ============================================

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('email', 'username', 'email_verified', 'account_locked', 'date_joined')
    list_filter = ('email_verified', 'account_locked', 'newsletter_subscribed')
    search_fields = ('email', 'username', 'phone_number')
    readonly_fields = ('date_joined', 'last_login', 'last_ip')
    
    fieldsets = (
        ('Identifiants', {
            'fields': ('email', 'username', 'phone_number')
        }),
        ('Vérifications', {
            'fields': ('email_verified', 'phone_verified')
        }),
        ('Profil', {
            'fields': ('avatar', 'bio', 'date_of_birth', 'first_name', 'last_name')
        }),
        ('2FA', {
            'fields': ('two_factor_enabled', 'two_factor_secret'),
            'classes': ('collapse',)
        }),
        ('Préférences', {
            'fields': ('newsletter_subscribed', 'notifications_enabled')
        }),
        ('Sécurité', {
            'fields': ('account_locked', 'failed_login_attempts', 'last_failed_login', 'last_ip', 'last_login_location')
        }),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
            'classes': ('collapse',)
        }),
        ('Dates', {
            'fields': ('date_joined', 'last_login'),
            'classes': ('collapse',)
        })
    )


# ============================================
# ADMIN LOGEMENT
# ============================================

@admin.register(Logement)
class LogementAdmin(admin.ModelAdmin):
    list_display = ('titre', 'adresse', 'prix', 'surface', 'type_logement', 'statut_badge', 'note_moyenne', 'date_creation')
    list_filter = ('statut', 'type_logement', 'code_postal', 'date_creation')
    search_fields = ('titre', 'adresse', 'id_parcelle')
    readonly_fields = ('date_creation', 'date_modification', 'note_moyenne', 'nombre_avis')
    
    fieldsets = (
        ('Informations de base', {
            'fields': ('titre', 'adresse', 'code_postal', 'type_logement', 'description')
        }),
        ('Localisation', {
            'fields': ('latitude', 'longitude')
        }),
        ('Caractéristiques', {
            'fields': ('surface', 'chambres', 'etage', 'prix')
        }),
        ('DVF (Données Valeurs Foncières)', {
            'fields': ('date_mutation', 'valeur_fonciere'),
            'classes': ('collapse',)
        }),
        ('Cadastre', {
            'fields': ('id_parcelle',),
            'classes': ('collapse',)
        }),
        ('Propriété', {
            'fields': ('proprietaire', 'statut')
        }),
        ('Évaluation', {
            'fields': ('note_moyenne', 'nombre_avis'),
            'classes': ('collapse',)
        }),
        ('Dates', {
            'fields': ('date_creation', 'date_modification'),
            'classes': ('collapse',)
        })
    )
    
    def statut_badge(self, obj):
        colors = {
            'disponible': '#FFC107',
            'reclame': '#FF9800',
            'verifie': '#4CAF50',
        }
        color = colors.get(obj.statut, '#9E9E9E')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            color,
            obj.get_statut_display()
        )
    statut_badge.short_description = 'Statut'


# ============================================
# ADMIN RÉCLAMATION PROPRIÉTAIRE
# ============================================

@admin.register(ReclamationProprietaire)
class ReclamationProprietaireAdmin(admin.ModelAdmin):
    list_display = ('logement', 'utilisateur', 'statut_badge', 'date_reclamation', 'actions_admin')
    list_filter = ('statut', 'date_reclamation')
    search_fields = ('logement__titre', 'utilisateur__email')
    readonly_fields = ('date_reclamation', 'date_traitement', 'traite_par')
    
    fieldsets = (
        ('Réclamation', {
            'fields': ('logement', 'utilisateur', 'message', 'justificatif')
        }),
        ('Traitement', {
            'fields': ('statut', 'commentaire_admin', 'traite_par', 'date_traitement')
        }),
        ('Dates', {
            'fields': ('date_reclamation',)
        })
    )
    
    actions = ['accepter_reclamation', 'refuser_reclamation']
    
    def statut_badge(self, obj):
        colors = {
            'en_attente': '#FFC107',
            'accepte': '#4CAF50',
            'refuse': '#F44336',
        }
        color = colors.get(obj.statut, '#9E9E9E')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            color,
            obj.get_statut_display()
        )
    statut_badge.short_description = 'Statut'
    
    def actions_admin(self, obj):
        if obj.statut == 'en_attente':
            return '⚠️ À traiter'
        elif obj.statut == 'accepte':
            return '✅ Acceptée'
        else:
            return '❌ Refusée'
    actions_admin.short_description = 'Actions'
    
    def accepter_reclamation(self, request, queryset):
        for reclamation in queryset.filter(statut='en_attente'):
            reclamation.accepter(request.user)
        self.message_user(request, f"{queryset.count()} réclamation(s) acceptée(s)")
    accepter_reclamation.short_description = "✅ Accepter les réclamations sélectionnées"
    
    def refuser_reclamation(self, request, queryset):
        for reclamation in queryset.filter(statut='en_attente'):
            reclamation.refuser(request.user, "Refusée par administrateur")
        self.message_user(request, f"{queryset.count()} réclamation(s) refusée(s)")
    refuser_reclamation.short_description = "❌ Refuser les réclamations sélectionnées"


# ============================================
# ADMIN AVIS LOGEMENT
# ============================================

@admin.register(AvisLogement)
class AvisLogementAdmin(admin.ModelAdmin):
    list_display = ('logement', 'locataire', 'note', 'verifie_badge', 'date_avis')
    list_filter = ('note', 'verifie', 'date_avis')
    search_fields = ('logement__titre', 'locataire__email', 'titre')
    readonly_fields = ('date_avis', 'date_verification', 'verifie_par')
    
    fieldsets = (
        ('Avis', {
            'fields': ('logement', 'locataire', 'titre', 'commentaire', 'note')
        }),
        ('Critères détaillés', {
            'fields': ('note_proprete', 'note_equipements', 'note_localisation', 'note_bailleur'),
            'classes': ('collapse',)
        }),
        ('Vérification', {
            'fields': ('verifie', 'justificatif', 'verifie_par', 'date_verification')
        }),
        ('Dates', {
            'fields': ('date_avis',)
        })
    )
    
    actions = ['verifier_avis', 'rejeter_avis']
    
    def verifie_badge(self, obj):
        if obj.verifie:
            return format_html('<span style="color: green;">✅ Vérifié</span>')
        else:
            return format_html('<span style="color: orange;">⚠️ En attente</span>')
    verifie_badge.short_description = 'Vérification'
    
    def verifier_avis(self, request, queryset):
        count = queryset.filter(verifie=False).update(
            verifie=True,
            date_verification=timezone.now(),
            verifie_par=request.user
        )
        self.message_user(request, f"{count} avis vérifiés")
    verifier_avis.short_description = "✅ Vérifier les avis sélectionnés"
    
    def rejeter_avis(self, request, queryset):
        count = queryset.filter(verifie=False).delete()[0]
        self.message_user(request, f"{count} avis rejetés")
    rejeter_avis.short_description = "❌ Rejeter les avis sélectionnés"


# ============================================
# ADMIN FAVORI
# ============================================

@admin.register(Favori)
class FavoriAdmin(admin.ModelAdmin):
    list_display = ('utilisateur', 'logement', 'date_ajout')
    list_filter = ('date_ajout',)
    search_fields = ('utilisateur__email', 'logement__titre')
    readonly_fields = ('date_ajout',)


# ============================================
# ADMIN LOGIN HISTORY
# ============================================

@admin.register(LoginHistory)
class LoginHistoryAdmin(admin.ModelAdmin):
    list_display = ('user', 'success_badge', 'device_type', 'timestamp')
    list_filter = ('success', 'suspicious', 'timestamp')
    search_fields = ('user__email', 'ip_address', 'device_type')
    readonly_fields = ('timestamp',)
    
    def success_badge(self, obj):
        if obj.success:
            color, text = 'green', '✅ Réussi'
        elif obj.suspicious:
            color, text = 'orange', '⚠️ Suspect'
        else:
            color, text = 'red', '❌ Échoué'
        return format_html('<span style="color: {};">{}</span>', color, text)
    success_badge.short_description = 'Statut'


# ============================================
# ADMIN USER SESSION
# ============================================

@admin.register(UserSession)
class UserSessionAdmin(admin.ModelAdmin):
    list_display = ('user', 'device_name', 'browser', 'created_at', 'last_activity')
    list_filter = ('created_at', 'last_activity')
    search_fields = ('user__email', 'device_name', 'ip_address')
    readonly_fields = ('session_key', 'created_at', 'last_activity')


# ============================================
# ADMIN PROFIL
# ============================================

@admin.register(Profil)
class ProfilAdmin(admin.ModelAdmin):
    list_display = ('utilisateur', 'date_creation')
    list_filter = ('date_creation',)
    search_fields = ('utilisateur__email',)
    readonly_fields = ('date_creation',)


# ============================================
# TOKENS (Lecture seule)
# ============================================

@admin.register(EmailVerificationToken)
class EmailVerificationTokenAdmin(admin.ModelAdmin):
    list_display = ('user', 'used', 'created_at', 'expires_at')
    list_filter = ('used', 'created_at')
    search_fields = ('user__email',)
    readonly_fields = ('token', 'created_at')


@admin.register(PasswordResetToken)
class PasswordResetTokenAdmin(admin.ModelAdmin):
    list_display = ('user', 'used', 'created_at', 'expires_at')
    list_filter = ('used', 'created_at')
    search_fields = ('user__email',)
    readonly_fields = ('token', 'created_at', 'ip_address')


# ============================================
# ADMIN MARKET STUDIES - PHASE 6
# ============================================

@admin.register(MarketStudy)
class MarketStudyAdmin(admin.ModelAdmin):
    list_display = ('title', 'status', 'target_type', 'created_by', 'created_at', 'responses_count_display')
    list_filter = ('status', 'target_type', 'created_at')
    search_fields = ('title', 'description')
    readonly_fields = ('created_at', 'updated_at', 'share_token', 'responses_count_display', 'completion_rate_display', 'average_duration_display')
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('title', 'description', 'created_by')
        }),
        ('Dates et statut', {
            'fields': ('status', 'date_start', 'date_end', 'created_at', 'updated_at')
        }),
        ('Cible', {
            'fields': ('target_type', 'share_token')
        }),
        ('Design', {
            'fields': ('theme_color', 'logo', 'completion_message')
        }),
        ('Statistiques', {
            'fields': ('responses_count_display', 'completion_rate_display', 'average_duration_display'),
            'classes': ('collapse',)
        })
    )
    
    def responses_count_display(self, obj):
        return obj.get_responses_count()
    responses_count_display.short_description = 'Nombre de réponses'
    
    def completion_rate_display(self, obj):
        return f"{obj.get_completion_rate()}%"
    completion_rate_display.short_description = 'Taux de complétion'
    
    def average_duration_display(self, obj):
        return f"{obj.get_average_duration()} min"
    average_duration_display.short_description = 'Durée moyenne'


class MarketStudyQuestionInline(admin.TabularInline):
    model = MarketStudyQuestion
    extra = 0
    fields = ('order', 'question_type', 'label', 'required')
    ordering = ('order',)


@admin.register(MarketStudyQuestion)
class MarketStudyQuestionAdmin(admin.ModelAdmin):
    list_display = ('label', 'study', 'question_type', 'order', 'required', 'created_at')
    list_filter = ('question_type', 'required', 'study')
    search_fields = ('label', 'description')
    ordering = ('study', 'order', 'created_at')


@admin.register(MarketStudyResponse)
class MarketStudyResponseAdmin(admin.ModelAdmin):
    list_display = ('study', 'user', 'completed', 'created_at', 'completed_at', 'duration_display')
    list_filter = ('completed', 'study', 'created_at')
    search_fields = ('study__title', 'user__email', 'ip_address')
    readonly_fields = ('created_at', 'duration_display')
    
    def duration_display(self, obj):
        duration = obj.get_duration_minutes()
        return f"{duration} min" if duration else "N/A"
    duration_display.short_description = 'Durée'


@admin.register(MarketStudyAnswer)
class MarketStudyAnswerAdmin(admin.ModelAdmin):
    list_display = ('question', 'response', 'answer_display', 'created_at')
    list_filter = ('question__question_type', 'question__study', 'created_at')
    search_fields = ('question__label', 'response__study__title')
    readonly_fields = ('created_at', 'answer_display')
    
    def answer_display(self, obj):
        return obj.get_answer_display()
    answer_display.short_description = 'Réponse'


# ============================================
# ADMIN BUSINESS MODEL CANVAS - PHASE 4
# ============================================

@admin.register(BusinessModelCanvas)
class BusinessModelCanvasAdmin(admin.ModelAdmin):
    list_display = ('id', 'version', 'created_by', 'created_at', 'updated_at', 'share_enabled')
    list_filter = ('share_enabled', 'created_at')
    readonly_fields = ('created_at', 'updated_at', 'share_token')


@admin.register(BusinessModelCanvasVersion)
class BusinessModelCanvasVersionAdmin(admin.ModelAdmin):
    list_display = ('canvas', 'version', 'created_by', 'created_at')
    list_filter = ('canvas', 'created_at')
    readonly_fields = ('created_at',)


# ============================================
# ADMIN BUSINESS PLAN - PHASE 5
# ============================================

@admin.register(BusinessPlan)
class BusinessPlanAdmin(admin.ModelAdmin):
    list_display = ('id', 'nom_entreprise', 'version', 'created_by', 'created_at', 'updated_at')
    list_filter = ('created_at',)
    readonly_fields = ('created_at', 'updated_at')


@admin.register(BusinessPlanVersion)
class BusinessPlanVersionAdmin(admin.ModelAdmin):
    list_display = ('plan', 'version', 'created_by', 'created_at')
    list_filter = ('plan', 'created_at')
    readonly_fields = ('created_at',)


@admin.register(BusinessPlanDocument)
class BusinessPlanDocumentAdmin(admin.ModelAdmin):
    list_display = ('plan', 'title', 'document_type', 'uploaded_by', 'uploaded_at')
    list_filter = ('document_type', 'uploaded_at')
    search_fields = ('title', 'description')


@admin.register(BusinessPlanComment)
class BusinessPlanCommentAdmin(admin.ModelAdmin):
    list_display = ('plan', 'section', 'created_by', 'created_at')
    list_filter = ('section', 'created_at')
    search_fields = ('comment', 'section')
    readonly_fields = ('created_at',)


# ============================================
# ADMIN COMPETITIVE ANALYSIS - PHASE 7
# ============================================

@admin.register(Competitor)
class CompetitorAdmin(admin.ModelAdmin):
    list_display = ('name', 'website', 'year_founded', 'pricing_model', 'estimated_users', 'created_at')
    list_filter = ('pricing_model', 'year_founded', 'created_at')
    search_fields = ('name', 'website')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Général', {
            'fields': ('logo', 'name', 'website', 'year_founded', 'funding_raised', 'estimated_users', 'order')
        }),
        ('Fonctionnalités', {
            'fields': ('feature_search', 'feature_verified_reviews', 'feature_social_network', 
                      'feature_lease_management', 'feature_interactive_map', 'feature_mobile_app', 'custom_features')
        }),
        ('Tarification', {
            'fields': ('pricing_model', 'average_price', 'commission_rate')
        }),
        ('UX/UI', {
            'fields': ('design_score', 'mobile_friendly', 'speed_score')
        }),
        ('Marketing', {
            'fields': ('social_media_score', 'seo_score', 'advertising_type')
        }),
        ('Analyse', {
            'fields': ('strengths', 'weaknesses', 'notes')
        }),
        ('Métadonnées', {
            'fields': ('created_at', 'updated_at', 'created_by'),
            'classes': ('collapse',)
        })
    )


@admin.register(CompetitiveAnalysis)
class CompetitiveAnalysisAdmin(admin.ModelAdmin):
    list_display = ('updated_at', 'updated_by')
    readonly_fields = ('created_at', 'updated_at', 'updated_by')
    
    fieldsets = (
        ('Analyse SWOT Comparée', {
            'fields': ('our_strengths_vs_competitors', 'their_strengths_to_adopt', 
                      'market_opportunities', 'competitive_threats')
        }),
        ('Métadonnées', {
            'fields': ('created_at', 'updated_at', 'updated_by'),
            'classes': ('collapse',)
        })
    )
    
    def save_model(self, request, obj, form, change):
        if not change:  # Création
            obj.updated_by = request.user
        super().save_model(request, obj, form, change)


# ============================================
# ADMIN FINANCIAL PROJECTIONS - PHASE 8
# ============================================

@admin.register(FinancialProjection)
class FinancialProjectionAdmin(admin.ModelAdmin):
    list_display = ('updated_at', 'updated_by')
    readonly_fields = ('created_at', 'updated_at', 'updated_by')
    
    fieldsets = (
        ('Revenus', {
            'fields': ('revenue_subscriptions_tenants', 'revenue_subscriptions_owners', 
                      'revenue_subscriptions_companies', 'revenue_commissions_leases', 
                      'revenue_additional_services', 'total_revenue')
        }),
        ('Charges Variables', {
            'fields': ('variable_cost_payment_commissions', 'variable_cost_support', 
                      'variable_cost_marketing', 'total_variable_costs')
        }),
        ('Charges Fixes', {
            'fields': ('fixed_cost_salaries', 'fixed_cost_rent', 'fixed_cost_infrastructure',
                      'fixed_cost_marketing', 'fixed_cost_insurance_legal', 'fixed_cost_other',
                      'total_fixed_costs')
        }),
        ('Résultats', {
            'fields': ('gross_margin', 'ebitda', 'net_result')
        }),
        ('Métadonnées', {
            'fields': ('created_at', 'updated_at', 'updated_by'),
            'classes': ('collapse',)
        })
    )


@admin.register(CashFlow)
class CashFlowAdmin(admin.ModelAdmin):
    list_display = ('month', 'year', 'total_inflows', 'total_outflows', 'variation', 'closing_balance')
    list_filter = ('year', 'month')
    readonly_fields = ('total_inflows', 'total_outflows', 'variation', 'closing_balance')


@admin.register(BalanceSheet)
class BalanceSheetAdmin(admin.ModelAdmin):
    list_display = ('year', 'total_assets', 'total_liabilities', 'balance_check')
    list_filter = ('year', 'balance_check')
    readonly_fields = ('total_assets', 'total_liabilities', 'balance_check')


@admin.register(FinancialScenario)
class FinancialScenarioAdmin(admin.ModelAdmin):
    list_display = ('name', 'revenue_growth_rate', 'conversion_rate_tenants', 'users_month_12', 'updated_at')
    list_filter = ('name',)
    readonly_fields = ('created_at', 'updated_at')


@admin.register(FinancialKPI)
class FinancialKPIAdmin(admin.ModelAdmin):
    list_display = ('cac_current', 'ltv_current', 'ltv_cac_ratio', 'churn_rate_monthly', 'mrr_current', 'updated_at')
    readonly_fields = ('updated_at',)


# ============================================
# ADMIN MODÉRATION & TICKETS SUPPORT - PHASE 9
# ============================================

@admin.register(ReportedContent)
class ReportedContentAdmin(admin.ModelAdmin):
    list_display = ('content_type', 'content_id', 'author', 'reports_count', 'severity', 'status', 'created_at')
    list_filter = ('content_type', 'status', 'severity', 'created_at')
    search_fields = ('author__username', 'author__email', 'content_preview')
    readonly_fields = ('reports_count', 'created_at', 'updated_at', 'treated_at')
    
    fieldsets = (
        ('Contenu', {
            'fields': ('content_type', 'content_id', 'content_preview', 'content_full', 'author')
        }),
        ('Signalements', {
            'fields': ('reported_by', 'reports_count', 'reason', 'reason_detail', 'severity')
        }),
        ('Traitement', {
            'fields': ('status', 'treated_by', 'treated_at', 'treatment_notes')
        }),
        ('Métadonnées', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )


@admin.register(UserModeration)
class UserModerationAdmin(admin.ModelAdmin):
    list_display = ('user', 'alert_type', 'reports_count', 'status', 'created_at')
    list_filter = ('alert_type', 'status', 'created_at')
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('created_at', 'updated_at', 'moderated_at')
    
    fieldsets = (
        ('Utilisateur', {
            'fields': ('user', 'alert_type', 'reports_count', 'suspicious_patterns')
        }),
        ('Modération', {
            'fields': ('status', 'suspension_end', 'ban_reason', 'moderated_by', 'moderated_at')
        }),
        ('Métadonnées', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )


@admin.register(PropertyClaimModeration)
class PropertyClaimModerationAdmin(admin.ModelAdmin):
    list_display = ('user', 'property_address', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('user__username', 'property_address')
    readonly_fields = ('created_at', 'updated_at', 'reviewed_at')


@admin.register(SupportTicket)
class SupportTicketAdmin(admin.ModelAdmin):
    list_display = ('ticket_id', 'title', 'user', 'category', 'priority', 'status', 'assigned_to', 'created_at')
    list_filter = ('category', 'priority', 'status', 'created_at')
    search_fields = ('ticket_id', 'title', 'description', 'user__username')
    readonly_fields = ('ticket_id', 'created_at', 'updated_at', 'last_reply_at')
    
    fieldsets = (
        ('Ticket', {
            'fields': ('ticket_id', 'title', 'description', 'user', 'category', 'priority', 'status')
        }),
        ('Assignation', {
            'fields': ('assigned_to',)
        }),
        ('Métadonnées', {
            'fields': ('created_at', 'updated_at', 'last_reply_at'),
            'classes': ('collapse',)
        })
    )


@admin.register(TicketReply)
class TicketReplyAdmin(admin.ModelAdmin):
    list_display = ('ticket', 'author', 'is_admin_reply', 'created_at')
    list_filter = ('is_admin_reply', 'created_at')
    search_fields = ('ticket__ticket_id', 'author__username', 'content')
    readonly_fields = ('created_at',)


@admin.register(ReplyTemplate)
class ReplyTemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'updated_at')
    list_filter = ('category',)
    search_fields = ('name', 'content')
    readonly_fields = ('created_at', 'updated_at')


# ============================================
# ADMIN PARAMÈTRES & CONFIGURATION - PHASE 10
# ============================================

@admin.register(Settings)
class SettingsAdmin(admin.ModelAdmin):
    list_display = ('site_name', 'contact_email', 'maintenance_mode', 'updated_at', 'updated_by')
    readonly_fields = ('updated_at', 'updated_by')
    
    fieldsets = (
        ('Informations Entreprise', {
            'fields': ('site_name', 'site_logo', 'site_favicon', 'site_description', 'contact_email', 'contact_phone')
        }),
        ('Paramètres Régionaux', {
            'fields': ('default_language', 'default_currency', 'timezone', 'date_format')
        }),
        ('Maintenance', {
            'fields': ('maintenance_mode', 'maintenance_message', 'maintenance_allowed_ips')
        }),
        ('Personnalisation', {
            'fields': ('primary_color', 'secondary_color', 'font_family', 'header_logo')
        }),
        ('Pages Légales', {
            'fields': ('cgu_content', 'privacy_policy_content', 'legal_notices_content', 'faq_data')
        }),
        ('SEO', {
            'fields': ('meta_title', 'meta_description', 'meta_keywords', 'sitemap_auto_generate')
        }),
        ('Métadonnées', {
            'fields': ('updated_at', 'updated_by'),
            'classes': ('collapse',)
        })
    )


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_system', 'created_at')
    list_filter = ('is_system', 'created_at')
    search_fields = ('name', 'description')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Rôle', {
            'fields': ('name', 'description', 'is_system')
        }),
        ('Permissions Utilisateurs', {
            'fields': ('can_view_users', 'can_edit_users', 'can_delete_users')
        }),
        ('Permissions Logements', {
            'fields': ('can_view_properties', 'can_edit_properties', 'can_delete_properties')
        }),
        ('Permissions Modération', {
            'fields': ('can_view_moderation', 'can_treat_moderation')
        }),
        ('Permissions Business', {
            'fields': ('can_view_business', 'can_edit_business')
        }),
        ('Permissions Finance', {
            'fields': ('can_view_finance', 'can_edit_finance')
        }),
        ('Permissions Paramètres', {
            'fields': ('can_view_settings', 'can_edit_settings')
        }),
        ('Permissions Analytics', {
            'fields': ('can_view_analytics', 'can_export_analytics')
        }),
        ('Métadonnées', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )


@admin.register(AdminInvitation)
class AdminInvitationAdmin(admin.ModelAdmin):
    list_display = ('email', 'role', 'status', 'invited_by', 'created_at', 'expires_at')
    list_filter = ('status', 'created_at')
    search_fields = ('email',)
    readonly_fields = ('token', 'created_at', 'accepted_at')


@admin.register(PaymentConfig)
class PaymentConfigAdmin(admin.ModelAdmin):
    list_display = ('stripe_enabled', 'paypal_enabled', 'bank_transfer_enabled', 'updated_at')
    readonly_fields = ('updated_at',)


@admin.register(NotificationConfig)
class NotificationConfigAdmin(admin.ModelAdmin):
    list_display = ('email_enabled_default', 'push_enabled_default', 'sms_enabled_default', 'updated_at')
    readonly_fields = ('updated_at',)


@admin.register(NotificationTemplate)
class NotificationTemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'template_type', 'subject', 'updated_at')
    list_filter = ('template_type',)
    search_fields = ('name', 'subject', 'body')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(SecurityConfig)
class SecurityConfigAdmin(admin.ModelAdmin):
    list_display = ('two_factor_required_admins', 'session_duration_minutes', 'password_min_length', 'updated_at')
    readonly_fields = ('updated_at',)


@admin.register(IntegrationConfig)
class IntegrationConfigAdmin(admin.ModelAdmin):
    list_display = ('google_maps_enabled', 'google_analytics_enabled', 'email_service', 'updated_at')
    readonly_fields = ('updated_at',)


@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ('admin', 'action', 'resource_type', 'resource_name', 'ip_address', 'created_at')
    list_filter = ('action', 'resource_type', 'created_at')
    search_fields = ('admin__username', 'resource_name', 'ip_address')
    readonly_fields = ('created_at',)
    
    fieldsets = (
        ('Log', {
            'fields': ('admin', 'action', 'resource_type', 'resource_id', 'resource_name', 'details')
        }),
        ('Métadonnées', {
            'fields': ('ip_address', 'user_agent', 'created_at'),
            'classes': ('collapse',)
        })
    )


# ============================================
# CUSTOMISATION GLOBALE ADMIN
# ============================================

from django.utils import timezone
admin.site.site_header = "🏠 Transpareo Administration"
admin.site.site_title = "Admin Transpareo"
admin.site.index_title = "Bienvenue sur le panel d'administration"


