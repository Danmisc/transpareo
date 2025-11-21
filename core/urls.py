from django.urls import path
from . import views

urlpatterns = [
    # ========== Page principale ==========
    path('', views.landing_page, name='landing-page'),
    path('map/', views.map_view, name='map'),
    path('liste/', views.liste_view, name='liste'),
    
    # ========== Authentification ==========
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # ========== Magic Link ==========
    path('auth/magic-link/<uuid:token>/', views.magic_link_login, name='magic-link-login'),
    path('auth/request-magic-link/', views.request_magic_link, name='request-magic-link'),
    
    # ========== 2FA ==========
    path('auth/verify-2fa/', views.verify_2fa_view, name='verify-2fa'),
    path('auth/setup-2fa/', views.setup_2fa_view, name='setup-2fa'),
    path('auth/disable-2fa/', views.disable_2fa_view, name='disable-2fa'),
    path('auth/2fa-backup-codes/', views.get_2fa_backup_codes, name='2fa-backup-codes'),
    
    # ========== Vérification email ==========
    path('verify-email/<uuid:token>/', views.verify_email, name='verify-email'),
    
    # ========== Réinitialisation mot de passe ==========
    path('password-reset/', views.password_reset_request, name='password-reset-request'),
    path('reset-password/<uuid:token>/', views.password_reset_confirm, name='password-reset-confirm'),
    
    # ========== Profil utilisateur ==========
    path('profile/', views.profile_view, name='profile'),
    path('profile/<int:user_id>/', views.profile_view, name='profile-user'),
    path('profile/edit/', views.profile_edit, name='profile-edit'),
    path('profile/check-badges/', views.check_badges, name='check-badges'),
    
    # ========== Sécurité ==========
    path('security/', views.security_settings, name='security-settings'),
    path('security/revoke-session/<int:session_id>/', views.revoke_session, name='revoke-session'),
    
    # ========== LOGEMENTS - DÉTAIL & ACTIONS ==========
    path('logement/<int:id>/', views.logement_detail, name='logement-detail'),
    path('logement/<int:id>/reclamer/', views.reclamer_bien, name='reclamer-bien'),
    path('logement/<int:id>/avis/ajouter/', views.ajouter_avis, name='ajouter-avis'),
    path('connect/profile/<int:user_id>/avis/ajouter/', views.ajouter_avis_profil, name='ajouter-avis-profil'),
    path('logement/<int:id>/candidater/', views.candidater_logement, name='candidater-logement'),
    
    # ========== PROPRIÉTAIRE - MES BIENS ==========
    path('mes-biens/', views.mes_biens, name='mes-biens'),
    
    # ========== LOCATAIRE - MES AVIS ==========
    path('mes-avis/', views.mes_avis, name='mes-avis'),
    
    # ========== API ==========
    path('api/get-user-favoris/', views.api_get_user_favoris, name='api-get-user-favoris'),
    path('api/toggle-favori/', views.api_toggle_favori, name='api-toggle-favori'),
    path('api/filter-by-radius/', views.api_filter_by_radius, name='api-filter-by-radius'),
    path('api/autocomplete-address/', views.api_autocomplete_address, name='api-autocomplete-address'),
    path('api/search-complete/', views.api_search_complete, name='api-search-complete'),
    path('api/logements/', views.api_get_logements, name='api-get-logements'),
# ============================================
# NOUVELLES URLS POUR LA MAP
# À ajouter dans core/urls.py
# ============================================

# Ajouter ces routes dans urlpatterns:

      # ========== MAP - PHASE 2 APIs ==========
    path('api/map/search-address-advanced/', views.api_search_address_advanced, name='api-search-address-advanced'),
    path('api/map/logements-by-radius/', views.api_logements_by_radius, name='api-logements-by-radius'),
    
    # ========== Autres APIs utiles (à garder si vous les utilisez) ==========
    path('api/map/logement/<int:id>/detail/', views.api_logement_detail, name='api-logement-detail'),
    path('api/map/logement/<int:id>/avis/', views.api_create_avis, name='api-create-avis'),
    path('api/map/logement/<int:id>/reclamer/', views.api_reclamer_bien, name='api-reclamer-bien'),
    path('api/map/logement/<int:id>/favori/', views.api_toggle_favori_map, name='api-toggle-favori-map'),

    # ========== LOGEMENT DÉTAIL PAGE ==========
    path('logement/<int:id>/', views.logement_detail_view, name='logement-detail-view'),
    
    # ========== API PHASE 3 ==========
    path('api/map/logement/<int:id>/detail-complet/', views.api_logement_detail_complet, name='api-logement-detail-complet'),
    path('api/map/logements-recommandes/<int:logement_id>/', views.api_logements_recommandes, name='api-logements-recommandes'),
    path('api/map/logements-triés/', views.api_logements_triés, name='api-logements-triés'),
    
    # ========== TRANSPAREO CONNECT ==========
    path('connect/', views.connect_home, name='connect-home'),
    path('connect/messages/', views.connect_messages, name='connect-messages'),
    path('connect/notifications/', views.connect_notifications, name='connect-notifications'),
    path('connect/lease/', views.connect_lease, name='connect-lease'),
    path('connect/users/search/', views.connect_user_search, name='connect-user-search'),
    path('api/connect/users/<int:user_id>/popup/', views.api_user_popup, name='api-user-popup'),
    path('api/connect/users/invite/', views.api_send_invitation, name='api-send-invitation'),
    path('api/connect/users/search/load-more/', views.api_load_more_users, name='api-load-more-users'),
    path('api/connect/users/suggestions/', views.api_get_suggestions, name='api-get-suggestions'),
    path('connect/properties/', views.connect_properties, name='connect-properties'),
    path('connect/groups/', views.connect_groups, name='connect-groups'),
    path('connect/search-users/', views.connect_search_users, name='connect-search-users'),
    path('connect/search/', views.connect_search_results, name='connect-search-results'),
    path('connect/settings/', views.connect_settings, name='connect-settings'),
    path('connect/help/', views.connect_help, name='connect-help'),
    
    # ========== CONNECT - ACTIONS POSTS ==========
    path('connect/posts/create/', views.create_post, name='create-post'),
    path('connect/posts/<int:post_id>/like/', views.toggle_post_like, name='toggle-post-like'),
    path('connect/posts/<int:post_id>/comment/', views.create_comment, name='create-comment'),
    path('connect/posts/<int:post_id>/share/', views.share_post, name='share-post'),
    path('connect/posts/<int:post_id>/delete/', views.delete_post, name='delete-post'),
    path('connect/comments/<int:comment_id>/like/', views.toggle_comment_like, name='toggle-comment-like'),
    path('connect/users/<int:user_id>/connect/', views.connect_user, name='connect-user'),
    path('connect/groups/<int:group_id>/join/', views.join_group, name='join-group'),
    
    # ========== CONNECT - NOUVELLES FONCTIONNALITÉS API ==========
    # API Feed & Posts
    path('api/feed/', views.api_feed, name='api-feed'),
    path('api/posts/', views.api_create_post, name='api-create-post'),
    path('api/posts/<int:post_id>/like/', views.api_toggle_like, name='api-toggle-like'),
    path('api/posts/<int:post_id>/comments/', views.api_create_comment, name='api-create-comment'),
    path('api/search/', views.api_search, name='api-search'),
    
    # API Connect existantes
    path('api/connect/posts/reaction/', views.api_add_reaction, name='api-add-reaction'),
    path('api/connect/posts/<int:post_id>/reactions/', views.api_get_reactions, name='api-get-reactions'),
    path('api/connect/posts/collaborative/join/', views.api_join_collaborative_post, name='api-join-collaborative-post'),
    path('api/connect/posts/load-more/', views.api_load_more_posts, name='api-load-more-posts'),
    path('api/connect/comments/<int:comment_id>/replies/', views.api_load_more_replies, name='api-load-more-replies'),
    
    # ========== CONNECT - API GROUPES AVANCÉS ==========
    path('api/connect/groups/sondage/<int:sondage_id>/vote/', views.api_vote_sondage, name='api-vote-sondage'),
    path('api/connect/groups/reponse/<int:reponse_id>/vote/', views.api_vote_reponse, name='api-vote-reponse'),
    path('api/connect/groups/question/<int:question_id>/repondre/', views.api_repondre_question, name='api-repondre-question'),
    path('api/connect/groups/question/<int:question_id>/reponses/', views.api_load_reponses, name='api-load-reponses'),
    path('api/connect/groups/question/<int:question_id>/mark-official/', views.api_mark_official_solution, name='api-mark-official-solution'),
    path('api/connect/groups/<int:group_id>/updates/', views.api_group_updates, name='api-group-updates'),
    
    # ========== CONNECT - ACTIONS PROFIL ==========
    path('connect/users/<int:user_id>/follow/', views.toggle_follow, name='toggle-follow'),
    path('connect/users/<int:user_id>/block/', views.block_user, name='block-user'),
    path('connect/users/<int:user_id>/unblock/', views.unblock_user, name='unblock-user'),
    path('connect/verification/request/', views.request_verification, name='request-verification'),
    
    # ========== CONNECT - ACTIONS MESSAGERIE ==========
    path('connect/conversations/<int:conversation_id>/send/', views.send_message, name='send-message'),
    path('connect/conversations/<int:conversation_id>/archive/', views.archive_conversation, name='archive-conversation'),
    path('connect/conversations/<int:conversation_id>/favorite/', views.favorite_conversation, name='favorite-conversation'),
    path('connect/conversations/<int:conversation_id>/unread/', views.mark_conversation_unread, name='mark-conversation-unread'),
    
    # ========== CONNECT - API MESSAGERIE AVANCÉE ==========
    path('api/connect/conversations/', views.api_get_conversations, name='api-get-conversations'),
    path('api/connect/conversations/create/', views.api_create_conversation, name='api-create-conversation'),
    path('api/connect/conversations/<int:conversation_id>/messages/', views.api_get_messages, name='api-get-messages'),
    path('api/connect/conversations/<int:conversation_id>/read/', views.api_mark_conversation_read, name='api-mark-conversation-read'),
    path('api/connect/conversations/<int:conversation_id>/archive/', views.api_archive_conversation, name='api-archive-conversation'),
    path('api/connect/conversations/mark-all-read/', views.api_mark_all_conversations_read, name='api-mark-all-conversations-read'),
    path('api/connect/conversations/archive-all/', views.api_archive_all_conversations, name='api-archive-all-conversations'),
    path('api/connect/conversations/<int:conversation_id>/important/', views.api_toggle_important, name='api-toggle-important'),
    path('api/connect/conversations/<int:conversation_id>/', views.api_delete_conversation, name='api-delete-conversation'),
    path('api/connect/messages/', views.api_send_message, name='api-send-message'),
    path('api/connect/messages/reaction/', views.api_add_message_reaction, name='api-add-message-reaction'),
    path('api/connect/messages/pin/', views.api_pin_message, name='api-pin-message'),
    path('api/connect/messages/unpin/', views.api_unpin_message, name='api-unpin-message'),
    path('api/connect/conversations/<int:conversation_id>/typing/', views.api_set_typing, name='api-set-typing'),
    path('api/connect/messages/share-logements/', views.api_get_user_logements, name='api-get-user-logements'),
    path('api/connect/messages/share-documents/', views.api_get_user_documents, name='api-get-user-documents'),
    path('api/connect/users/search/', views.api_search_users, name='api-search-users'),
    # ========== CONNECT - API APPELS ==========
    path('api/connect/calls/initiate/', views.api_initiate_call, name='api-initiate-call'),
    path('api/connect/calls/<int:call_id>/answer/', views.api_answer_call, name='api-answer-call'),
    path('api/connect/calls/<int:call_id>/end/', views.api_end_call, name='api-end-call'),
    path('api/connect/calls/<int:call_id>/reject/', views.api_reject_call, name='api-reject-call'),
    # ========== SIGNALEMENTS (PHASE 12.3) ==========
    path('connect/posts/<int:post_id>/report/', views.report_post, name='report-post'),
    path('connect/comments/<int:comment_id>/report/', views.report_comment, name='report-comment'),
    path('connect/messages/<int:message_id>/report/', views.report_message, name='report-message'),
    path('connect/users/<int:user_id>/report/', views.report_user, name='report-user'),
    path('connect/groups/<int:group_id>/report/', views.report_group, name='report-group'),
    
    # ========== CONNECT - GROUPES ==========
    path('connect/groups/<int:group_id>/', views.connect_group_detail, name='connect-group-detail'),
    path('connect/groups/<int:group_id>/leave/', views.leave_group, name='leave-group'),
    path('connect/groups/<int:group_id>/edit/', views.edit_group, name='edit-group'),
    path('connect/groups/<int:group_id>/delete/', views.delete_group, name='delete-group'),
    path('connect/groups/<int:group_id>/invite/', views.invite_to_group, name='invite-to-group'),
    path('connect/groups/<int:group_id>/requests/<int:membership_id>/approve/', views.approve_group_request, name='approve-group-request'),
    path('connect/groups/<int:group_id>/requests/<int:membership_id>/reject/', views.reject_group_request, name='reject-group-request'),
    path('connect/groups/<int:group_id>/members/<int:user_id>/ban/', views.ban_group_member, name='ban-group-member'),
    path('connect/groups/<int:group_id>/members/<int:user_id>/promote/', views.promote_group_member, name='promote-group-member'),
    path('connect/groups/create/', views.create_group, name='create-group'),
    
    # ========== CONNECT - ACTIONS NOTIFICATIONS ==========
    path('connect/notifications/<int:notification_id>/read/', views.mark_notification_read, name='mark-notification-read'),
    path('connect/notifications/mark-all-read/', views.mark_all_notifications_read, name='mark-all-notifications-read'),
    path('connect/notifications/<int:notification_id>/delete/', views.delete_notification, name='delete-notification'),
    path('connect/notifications/settings/', views.connect_notification_settings, name='connect-notification-settings'),
    
    # ========== CONNECT - API NOTIFICATIONS AVANCÉES ==========
    path('api/connect/notifications/<int:notification_id>/read/', views.mark_notification_read, name='api-mark-notification-read'),
    path('api/connect/notifications/<int:notification_id>/not-interested/', views.mark_notification_not_interested, name='api-mark-notification-not-interested'),
    path('api/connect/notifications/realtime/', views.api_get_notifications_realtime, name='api-get-notifications-realtime'),
    path('api/connect/notifications/email-summary/', views.api_get_email_summary, name='api-get-email-summary'),
    
    # ========== CONNECT - ACTIONS BAIL ==========
    path('connect/bail/<int:bail_id>/maintenance/', views.create_maintenance_request, name='create-maintenance-request'),
    path('connect/bail/<int:bail_id>/document/', views.upload_lease_document, name='upload-lease-document'),
    path('connect/bail/<int:bail_id>/termination/', views.create_termination_request, name='create-termination-request'),
    path('connect/bail/<int:bail_id>/documents/download/', views.download_lease_documents, name='download-lease-documents'),
    
    # ========== CONNECT - API GESTION BAIL AVANCÉE ==========
    path('api/connect/bail/<int:bail_id>/signature/', views.api_sign_document, name='api-sign-document'),
    path('api/connect/bail/<int:bail_id>/files/upload/', views.api_upload_shared_file, name='api-upload-shared-file'),
    path('api/connect/bail/<int:bail_id>/files/<int:file_id>/download/', views.api_download_shared_file, name='api-download-shared-file'),
    path('api/connect/bail/<int:bail_id>/files/<int:file_id>/logs/', views.api_get_file_logs, name='api-get-file-logs'),
    path('api/connect/bail/<int:bail_id>/checklist/create/', views.api_create_checklist, name='api-create-checklist'),
    path('api/connect/bail/<int:bail_id>/checklist/<int:checklist_id>/item/', views.api_add_checklist_item, name='api-add-checklist-item'),
    path('api/connect/bail/<int:bail_id>/checklist/<int:checklist_id>/validate/', views.api_validate_checklist, name='api-validate-checklist'),
    path('api/connect/bail/<int:bail_id>/tickets/create/', views.api_create_ticket, name='api-create-ticket'),
    path('api/connect/bail/tickets/<int:ticket_id>/comment/', views.api_add_ticket_comment, name='api-add-ticket-comment'),
    path('api/connect/bail/tickets/<int:ticket_id>/resolve/', views.api_resolve_ticket, name='api-resolve-ticket'),
    path('api/connect/bail/tickets/<int:ticket_id>/escalate/', views.api_escalate_ticket, name='api-escalate-ticket'),
    path('api/connect/bail/<int:bail_id>/history/export/', views.api_export_history, name='api-export-history'),
    path('api/connect/bail/<int:bail_id>/reminders/create/', views.api_create_reminder, name='api-create-reminder'),
    path('api/connect/bail/reminders/<int:reminder_id>/delete/', views.api_delete_reminder, name='api-delete-reminder'),
    path('connect/paiement/<int:paiement_id>/paid/', views.mark_payment_paid, name='mark-payment-paid'),
    
    # ========== CONNECT - ACTIONS PROPRIÉTAIRE ==========
    path('connect/properties/<int:bail_id>/', views.connect_property_detail, name='connect-property-detail'),
    path('connect/properties/<int:bail_id>/renew/', views.renew_lease, name='renew-lease'),
    path('connect/properties/<int:bail_id>/terminate/', views.terminate_lease_owner, name='terminate-lease-owner'),
    path('connect/properties/<int:bail_id>/republish/', views.republish_property, name='republish-property'),
    path('connect/paiement/<int:paiement_id>/quittance/', views.generate_quittance, name='generate-quittance'),
    path('connect/paiement/<int:paiement_id>/reminder/', views.send_payment_reminder, name='send-payment-reminder'),
    path('connect/demande/<int:demande_id>/respond/', views.respond_maintenance_request, name='respond-maintenance-request'),
    path('connect/demande/<int:demande_id>/resolve/', views.mark_maintenance_resolved, name='mark-maintenance-resolved'),
    path('connect/dashboard/', views.owner_dashboard, name='owner-dashboard'),
    path('connect/quittances/bulk/', views.generate_bulk_quittances, name='generate-bulk-quittances'),
    path('connect/fiscal/<int:annee>/', views.generate_fiscal_summary, name='generate-fiscal-summary'),
    
    # ========== CONNECT - RECHERCHE & CONNEXIONS ==========
    path('connect/search/autocomplete/', views.user_search_autocomplete, name='user-search-autocomplete'),
    path('connect/users/<int:user_id>/connect/', views.send_connection_request, name='send-connection-request'),
    path('connect/connections/<int:connection_id>/accept/', views.accept_connection_request, name='accept-connection-request'),
    path('connect/connections/<int:connection_id>/reject/', views.reject_connection_request, name='reject-connection-request'),
    path('connect/users/<int:user_id>/disconnect/', views.remove_connection, name='remove-connection'),
    path('connect/connections/', views.my_connections, name='my-connections'),
    
    # ========== CONNECT - PARAMÈTRES ==========
    path('connect/settings/profile/', views.update_profile_settings, name='update-profile-settings'),
    path('connect/settings/privacy/', views.update_privacy_settings, name='update-privacy-settings'),
    path('connect/settings/export-gdpr/', views.export_gdpr_data, name='export-gdpr-data'),
    path('connect/settings/export-activity/', views.export_activity_journal, name='export-activity-journal'),
    path('connect/settings/disable/', views.disable_connect_profile, name='disable-connect-profile'),
    path('connect/sessions/<int:session_id>/terminate/', views.terminate_session, name='terminate-session'),
    
    # ========== RGPD & CONFORMITÉ (PHASE 12.7) ==========
    path('rgpd/cgu/', views.cgu_connect, name='cgu-connect'),
    path('rgpd/politique-confidentialite/', views.politique_confidentialite, name='politique-confidentialite'),
    path('rgpd/transparence/algorithmes/', views.transparence_algorithmes, name='transparence-algorithmes'),
    path('rgpd/transparence/moderation/', views.transparence_moderation, name='transparence-moderation'),
    
    # ========== ADMIN - PANEL ADMIN (PHASE 11) ==========
    path('connect-admin/dashboard/', views.admin_dashboard, name='admin-dashboard'),
    path('connect-admin/users/', views.admin_users, name='admin-users'),
    path('connect-admin/users/<int:user_id>/', views.admin_user_detail, name='admin-user-detail'),
    path('connect-admin/users/<int:user_id>/suspend/', views.admin_suspend_user, name='admin-suspend-user'),
    path('connect-admin/users/<int:user_id>/ban/', views.admin_ban_user, name='admin-ban-user'),
    path('connect-admin/users/<int:user_id>/delete/', views.admin_delete_user, name='admin-delete-user'),
    path('connect-admin/users/<int:user_id>/revoke-badges/', views.admin_revoke_badges, name='admin-revoke-badges'),
    path('connect-admin/logements/', views.admin_logements, name='admin-logements'),
    path('connect-admin/logements/<int:logement_id>/detail/', views.admin_logement_detail_ajax, name='admin-logement-detail-ajax'),
    path('connect-admin/candidatures-locations/', views.admin_candidatures_locations, name='admin-candidatures-locations'),
    path('connect-admin/candidatures/<int:candidature_id>/detail/', views.admin_candidature_detail_ajax, name='admin-candidature-detail-ajax'),
    path('connect-admin/candidatures/<int:candidature_id>/refuse/', views.admin_candidature_refuse, name='admin-candidature-refuse'),
    path('connect-admin/avis/', views.admin_avis, name='admin-avis'),
    path('connect-admin/avis/<int:avis_id>/detail/', views.admin_avis_detail_ajax, name='admin-avis-detail-ajax'),
    path('connect-admin/posts/<int:post_id>/detail/', views.admin_post_detail_ajax, name='admin-post-detail-ajax'),
    path('connect-admin/groupes/<int:groupe_id>/detail/', views.admin_groupe_detail_ajax, name='admin-groupe-detail-ajax'),
    path('connect-admin/badges/', views.admin_badges, name='admin-badges'),
    
    path('connect-admin/moderation/posts/', views.admin_moderation_posts, name='admin-moderation-posts'),
    path('connect-admin/moderation/comments/', views.admin_moderation_comments, name='admin-moderation-comments'),
    path('connect-admin/moderation/messages/', views.admin_moderation_messages, name='admin-moderation-messages'),
    path('connect-admin/moderation/kanban/', views.admin_moderation_kanban, name='admin-moderation-kanban'),
    path('connect-admin/moderation/update-status/', views.admin_update_signalement_status, name='admin-update-signalement-status'),
    path('connect-admin/moderation/batch-action/', views.admin_batch_action, name='admin-batch-action'),
    path('connect-admin/moderation/post/<int:signalement_id>/', views.admin_moderate_post, name='admin-moderate-post'),
    path('connect-admin/moderation/comment/<int:signalement_id>/', views.admin_moderate_comment, name='admin-moderate-comment'),
    path('connect-admin/moderation/message/<int:signalement_id>/', views.admin_moderate_message, name='admin-moderate-message'),
    
    path('connect-admin/verifications/identity/', views.admin_verifications_identity, name='admin-verifications-identity'),
    path('connect-admin/verifications/owner/', views.admin_verifications_owner, name='admin-verifications-owner'),
    path('connect-admin/verifications/<int:request_id>/approve/', views.admin_approve_verification, name='admin-approve-verification'),
    path('connect-admin/verifications/<int:request_id>/reject/', views.admin_reject_verification, name='admin-reject-verification'),
    
    path('connect-admin/reclamations/', views.admin_reclamations, name='admin-reclamations'),
    path('connect-admin/reclamations/<int:reclamation_id>/', views.admin_reclamation_detail, name='admin-reclamation-detail'),
    path('connect-admin/reclamations/<int:reclamation_id>/approve/', views.admin_approve_reclamation, name='admin-approve-reclamation'),
    path('connect-admin/reclamations/<int:reclamation_id>/reject/', views.admin_reject_reclamation, name='admin-reject-reclamation'),
    
    path('connect-admin/connect/', views.admin_connect, name='admin-connect'),
    path('connect-admin/groups/', views.admin_groups, name='admin-groups'),
    path('connect-admin/groups/<int:group_id>/', views.admin_group_detail, name='admin-group-detail'),
    path('connect-admin/groups/signaled/', views.admin_groups_signaled, name='admin-groups-signaled'),
    
    path('connect-admin/tickets/', views.admin_tickets, name='admin-tickets'),
    path('connect-admin/tickets/<int:ticket_id>/', views.admin_ticket_detail, name='admin-ticket-detail'),
    path('connect-admin/tickets/<int:ticket_id>/reply/', views.admin_ticket_reply, name='admin-ticket-reply'),
    path('connect-admin/tickets/<int:ticket_id>/close/', views.admin_ticket_close, name='admin-ticket-close'),
    
    path('connect-admin/statistics/', views.admin_statistics, name='admin-statistics'),
    path('connect-admin/logs/', views.admin_logs, name='admin-logs'),
    path('connect-admin/export/csv/', views.admin_export_csv, name='admin-export-csv'),
    
    # ========== BUSINESS MODEL CANVAS - PHASE 4 ==========
    path('connect-admin/business-model-canvas/', views.admin_business_model_canvas, name='admin-business-model-canvas'),
    path('connect-admin/business-model-canvas/save/', views.admin_business_model_canvas_save, name='admin-business-model-canvas-save'),
    path('connect-admin/business-model-canvas/create-version/', views.admin_business_model_canvas_create_version, name='admin-business-model-canvas-create-version'),
    path('connect-admin/business-model-canvas/restore-version/<int:version_id>/', views.admin_business_model_canvas_restore_version, name='admin-business-model-canvas-restore-version'),
    path('connect-admin/business-model-canvas/reset/', views.admin_business_model_canvas_reset, name='admin-business-model-canvas-reset'),
    path('connect-admin/business-model-canvas/export-pdf/', views.admin_business_model_canvas_export_pdf, name='admin-business-model-canvas-export-pdf'),
    path('canvas/share/<uuid:token>/', views.admin_business_model_canvas_share, name='admin-business-model-canvas-share'),
    
    # ========== BUSINESS PLAN - PHASE 5 ==========
    path('connect-admin/business-plan/', views.admin_business_plan, name='admin-business-plan'),
    path('connect-admin/business-plan/<str:section>/', views.admin_business_plan, name='admin-business-plan-section'),
    path('connect-admin/business-plan/save/', views.admin_business_plan_save, name='admin-business-plan-save'),
    path('connect-admin/business-plan/create-version/', views.admin_business_plan_create_version, name='admin-business-plan-create-version'),
    path('connect-admin/business-plan/restore-version/<int:version_id>/', views.admin_business_plan_restore_version, name='admin-business-plan-restore-version'),
    path('connect-admin/business-plan/export-pdf/', views.admin_business_plan_export_pdf, name='admin-business-plan-export-pdf'),
    path('connect-admin/business-plan/upload-document/', views.admin_business_plan_upload_document, name='admin-business-plan-upload-document'),
    path('connect-admin/business-plan/add-comment/', views.admin_business_plan_add_comment, name='admin-business-plan-add-comment'),
    
    # ========== ÉTUDES DE MARCHÉ & FORMS - PHASE 6 ==========
    path('connect-admin/market-studies/', views.admin_market_studies, name='admin-market-studies'),
    path('connect-admin/market-studies/create/', views.admin_market_study_create, name='admin-market-study-create'),
    path('connect-admin/market-studies/<int:study_id>/builder/', views.admin_market_study_builder, name='admin-market-study-builder'),
    path('connect-admin/market-studies/<int:study_id>/save-question/', views.admin_market_study_save_question, name='admin-market-study-save-question'),
    path('connect-admin/market-studies/<int:study_id>/delete-question/<int:question_id>/', views.admin_market_study_delete_question, name='admin-market-study-delete-question'),
    path('connect-admin/market-studies/<int:study_id>/reorder-questions/', views.admin_market_study_reorder_questions, name='admin-market-study-reorder-questions'),
    path('connect-admin/market-studies/<int:study_id>/results/', views.admin_market_study_results, name='admin-market-study-results'),
    path('connect-admin/market-studies/<int:study_id>/export-excel/', views.admin_market_study_export_excel, name='admin-market-study-export-excel'),
    path('connect-admin/market-studies/<int:study_id>/export-csv/', views.admin_market_study_export_csv, name='admin-market-study-export-csv'),
    path('study/<uuid:token>/', views.market_study_form, name='market-study-form'),
    path('study/<uuid:token>/submit/', views.market_study_submit, name='market-study-submit'),
    
    # ========== ANALYSE CONCURRENTIELLE - PHASE 7 ==========
    path('connect-admin/competitive-analysis/', views.admin_competitive_analysis, name='admin-competitive-analysis'),
    path('connect-admin/competitive-analysis/add-competitor/', views.admin_competitive_analysis_add_competitor, name='admin-competitive-analysis-add-competitor'),
    path('connect-admin/competitive-analysis/<int:competitor_id>/edit/', views.admin_competitive_analysis_edit_competitor, name='admin-competitive-analysis-edit-competitor'),
    path('connect-admin/competitive-analysis/<int:competitor_id>/delete/', views.admin_competitive_analysis_delete_competitor, name='admin-competitive-analysis-delete-competitor'),
    path('connect-admin/competitive-analysis/<int:competitor_id>/data/', views.admin_competitive_analysis_get_competitor, name='admin-competitive-analysis-get-competitor'),
    path('connect-admin/competitive-analysis/save-swot/', views.admin_competitive_analysis_save_swot, name='admin-competitive-analysis-save-swot'),
    path('connect-admin/competitive-analysis/export/', views.admin_competitive_analysis_export, name='admin-competitive-analysis-export'),
    
    # ========== PROJECTIONS FINANCIÈRES AVANCÉES - PHASE 8 ==========
    path('connect-admin/financial-projections/', views.admin_financial_projections, name='admin-financial-projections'),
    path('connect-admin/financial-projections/save/', views.admin_financial_projection_save, name='admin-financial-projection-save'),
    path('connect-admin/financial-projections/cash-flow/save/', views.admin_cash_flow_save, name='admin-cash-flow-save'),
    path('connect-admin/financial-projections/balance-sheet/save/', views.admin_balance_sheet_save, name='admin-balance-sheet-save'),
    path('connect-admin/financial-projections/scenario/save/', views.admin_scenario_save, name='admin-scenario-save'),
    path('connect-admin/financial-projections/kpis/save/', views.admin_kpis_save, name='admin-kpis-save'),
    
    # ========== MODÉRATION & TICKETS SUPPORT - PHASE 9 ==========
    path('connect-admin/moderation/', views.admin_moderation, name='admin-moderation'),
    path('connect-admin/moderation/reported-content/<int:content_id>/action/', views.admin_reported_content_action, name='admin-reported-content-action'),
    path('connect-admin/moderation/user-moderation/<int:user_moderation_id>/action/', views.admin_user_moderation_action, name='admin-user-moderation-action'),
    path('connect-admin/moderation/verification/<int:verification_id>/action/', views.admin_verification_action, name='admin-verification-action'),
    path('connect-admin/moderation/property-claim/<int:claim_id>/action/', views.admin_property_claim_action, name='admin-property-claim-action'),
    path('connect-admin/support-tickets/', views.admin_support_tickets, name='admin-support-tickets'),
    path('connect-admin/support-tickets/<str:ticket_id>/', views.admin_support_ticket_detail, name='admin-support-ticket-detail'),
    path('connect-admin/support-tickets/<str:ticket_id>/update-status/', views.admin_support_ticket_update_status, name='admin-support-ticket-update-status'),
    path('connect-admin/support-tickets/<str:ticket_id>/reply/', views.admin_support_ticket_reply, name='admin-support-ticket-reply'),
    path('connect-admin/support-tickets/<str:ticket_id>/assign/', views.admin_support_ticket_assign, name='admin-support-ticket-assign'),
    
    # ========== PARAMÈTRES & CONFIGURATION - PHASE 10 ==========
    path('connect-admin/settings/', views.admin_settings, name='admin-settings'),
    path('connect-admin/settings/save/', views.admin_settings_save, name='admin-settings-save'),
    path('connect-admin/settings/role/create/', views.admin_role_create, name='admin-role-create'),
    path('connect-admin/settings/role/<int:role_id>/update/', views.admin_role_update, name='admin-role-update'),
    path('connect-admin/settings/role/<int:role_id>/delete/', views.admin_role_delete, name='admin-role-delete'),
    path('connect-admin/settings/invitation/send/', views.admin_invitation_send, name='admin-invitation-send'),
    path('connect-admin/settings/payment-config/save/', views.admin_payment_config_save, name='admin-payment-config-save'),
    path('connect-admin/settings/notification-config/save/', views.admin_notification_config_save, name='admin-notification-config-save'),
    path('connect-admin/settings/notification-template/save/', views.admin_notification_template_save, name='admin-notification-template-save'),
    path('connect-admin/settings/security-config/save/', views.admin_security_config_save, name='admin-security-config-save'),
    path('connect-admin/settings/integration-config/save/', views.admin_integration_config_save, name='admin-integration-config-save'),
    path('connect-admin/settings/activity-logs/export/', views.admin_activity_logs_export, name='admin-activity-logs-export'),
    
    # ========== TRANSPARENCE & CONFIANCE ==========
    path('transparency/algorithms/', views.algorithms_transparency, name='algorithms-transparency'),
    path('rgpd/center/', views.rgpd_center, name='rgpd-center'),
    path('rgpd/export-data/', views.export_user_data, name='export-user-data'),
    path('rgpd/delete-account/', views.delete_user_account, name='delete-user-account'),
    
    # ========== DESIGN SYSTEM DEMO ==========
    path('design-system/demo/', views.design_system_demo, name='design-system-demo'),
]