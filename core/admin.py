from django.contrib import admin
from django.utils.html import format_html
from .models import (
    CustomUser, Logement, Favori, ReclamationProprietaire, 
    AvisLogement, LoginHistory, UserSession, Profil,
    EmailVerificationToken, PasswordResetToken
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
# CUSTOMISATION GLOBALE ADMIN
# ============================================

from django.utils import timezone
admin.site.site_header = "🏠 Transpareo Administration"
admin.site.site_title = "Admin Transpareo"
admin.site.index_title = "Bienvenue sur le panel d'administration"
