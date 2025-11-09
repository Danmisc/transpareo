from django.urls import path
from . import views

urlpatterns = [
    # ========== Page principale ==========
    path('', views.landing_page, name='landing-page'),
    path('map/', views.map_view, name='map'),
    
    # ========== Authentification ==========
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # ========== Vérification email ==========
    path('verify-email/<uuid:token>/', views.verify_email, name='verify-email'),
    
    # ========== Réinitialisation mot de passe ==========
    path('password-reset/', views.password_reset_request, name='password-reset-request'),
    path('reset-password/<uuid:token>/', views.password_reset_confirm, name='password-reset-confirm'),
    
    # ========== Profil utilisateur ==========
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.profile_edit, name='profile-edit'),
    
    # ========== Sécurité ==========
    path('security/', views.security_settings, name='security-settings'),
    path('security/revoke-session/<int:session_id>/', views.revoke_session, name='revoke-session'),
    
    # ========== LOGEMENTS - DÉTAIL & ACTIONS ==========
    path('logement/<int:id>/', views.logement_detail, name='logement-detail'),
    path('logement/<int:id>/reclamer/', views.reclamer_bien, name='reclamer-bien'),
    path('logement/<int:id>/avis/ajouter/', views.ajouter_avis, name='ajouter-avis'),
    
    # ========== PROPRIÉTAIRE - MES BIENS ==========
    path('mes-biens/', views.mes_biens, name='mes-biens'),
    
    # ========== LOCATAIRE - MES AVIS ==========
    path('mes-avis/', views.mes_avis, name='mes-avis'),
    
    # ========== API ==========
    path('api/get-user-favoris/', views.api_get_user_favoris, name='api-get-user-favoris'),
    path('api/toggle-favori/', views.api_toggle_favori, name='api-toggle-favori'),
    path('api/filter-by-radius/', views.api_filter_by_radius, name='api-filter-by-radius'),

    path('api/logements/', views.api_get_logements, name='api-get-logements'),

]
