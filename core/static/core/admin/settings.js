/**
 * SETTINGS - JavaScript pour gestion paramètres
 */

// ============================================
// INITIALISATION
// ============================================

function initSettings() {
    // Initialiser les sections
    initSections();
    
    // Initialiser les formulaires
    initForms();
    
    // Initialiser les données dynamiques
    initPricingTable();
    initEventNotifications();
    initCustomWebhooks();
    initWebhookEvents();
    initFAQ();
    initMetaKeywords();
}

// ============================================
// SECTIONS NAVIGATION
// ============================================

function switchSettingsSection(sectionName) {
    // Masquer toutes les sections
    document.querySelectorAll('.settings-section').forEach(section => {
        section.classList.remove('active');
    });
    
    // Retirer active de tous les boutons
    document.querySelectorAll('.settings-nav-item').forEach(btn => {
        btn.classList.remove('active');
    });
    
    // Afficher la section sélectionnée
    const section = document.getElementById(`section-${sectionName}`);
    if (section) {
        section.classList.add('active');
    }
    
    // Activer le bouton
    const btn = document.querySelector(`[data-section="${sectionName}"]`);
    if (btn) {
        btn.classList.add('active');
    }
    
    // Sauvegarder la section active dans localStorage
    localStorage.setItem('settings-active-section', sectionName);
}

function initSections() {
    // Restaurer la section active depuis localStorage
    const activeSection = localStorage.getItem('settings-active-section') || 'general';
    switchSettingsSection(activeSection);
}

// ============================================
// FORMS
// ============================================

function initForms() {
    // Formulaire général
    const generalForm = document.getElementById('settings-general-form');
    if (generalForm) {
        generalForm.addEventListener('submit', handleGeneralFormSubmit);
    }
    
    // Formulaire personnalisation
    const personalizationForm = document.getElementById('settings-personalization-form');
    if (personalizationForm) {
        personalizationForm.addEventListener('submit', handlePersonalizationFormSubmit);
    }
    
    // Formulaire paiements
    const paymentForm = document.getElementById('payment-config-form');
    if (paymentForm) {
        paymentForm.addEventListener('submit', handlePaymentFormSubmit);
    }
    
    // Formulaire notifications
    const notificationForm = document.getElementById('notification-config-form');
    if (notificationForm) {
        notificationForm.addEventListener('submit', handleNotificationFormSubmit);
    }
    
    // Formulaire sécurité
    const securityForm = document.getElementById('security-config-form');
    if (securityForm) {
        securityForm.addEventListener('submit', handleSecurityFormSubmit);
    }
    
    // Formulaire intégrations
    const integrationForm = document.getElementById('integration-config-form');
    if (integrationForm) {
        integrationForm.addEventListener('submit', handleIntegrationFormSubmit);
    }
    
    // Formulaire invitation
    const invitationForm = document.getElementById('invitation-form');
    if (invitationForm) {
        invitationForm.addEventListener('submit', handleInvitationFormSubmit);
    }
    
    // Formulaire rôle
    const roleForm = document.getElementById('role-form');
    if (roleForm) {
        roleForm.addEventListener('submit', handleRoleFormSubmit);
    }
    
    // Formulaire template
    const templateForm = document.getElementById('template-form');
    if (templateForm) {
        templateForm.addEventListener('submit', handleTemplateFormSubmit);
    }
}

function handleGeneralFormSubmit(e) {
    e.preventDefault();
    const formData = new FormData(this);
    saveSettings('general', formData);
}

function handlePersonalizationFormSubmit(e) {
    e.preventDefault();
    const formData = new FormData(this);
    
    // Ajouter les données JSON
    const faqData = JSON.stringify(getFAQData());
    formData.append('faq_data', faqData);
    
    const metaKeywordsData = JSON.stringify(getMetaKeywordsData());
    formData.append('meta_keywords', metaKeywordsData);
    
    saveSettings('personalization', formData);
}

function handlePaymentFormSubmit(e) {
    e.preventDefault();
    const formData = new FormData(this);
    
    // Ajouter la grille tarifaire
    const pricingData = JSON.stringify(getPricingData());
    formData.append('pricing_table', pricingData);
    
    saveConfig('payment', paymentConfigSaveUrl, formData);
}

function handleNotificationFormSubmit(e) {
    e.preventDefault();
    const formData = new FormData(this);
    
    // Ajouter les notifications par événement
    const eventNotificationsData = JSON.stringify(getEventNotificationsData());
    formData.append('event_notifications', eventNotificationsData);
    
    saveConfig('notification', notificationConfigSaveUrl, formData);
}

function handleSecurityFormSubmit(e) {
    e.preventDefault();
    const formData = new FormData(this);
    saveConfig('security', securityConfigSaveUrl, formData);
}

function handleIntegrationFormSubmit(e) {
    e.preventDefault();
    const formData = new FormData(this);
    
    // Ajouter les webhooks
    const webhookEvents = JSON.stringify(getWebhookEvents());
    formData.append('webhook_events', webhookEvents);
    
    const customWebhooks = JSON.stringify(getCustomWebhooks());
    formData.append('custom_webhooks', customWebhooks);
    
    saveConfig('integration', integrationConfigSaveUrl, formData);
}

function handleInvitationFormSubmit(e) {
    e.preventDefault();
    const formData = new FormData(this);
    
    fetch(invitationSendUrl, {
        method: 'POST',
        body: formData,
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showSuccessMessage(data.message || 'Invitation envoyée avec succès');
            this.reset();
            setTimeout(() => {
                window.location.reload();
            }, 1000);
        } else {
            alert('Erreur: ' + (data.error || 'Impossible d\'envoyer l\'invitation'));
        }
    })
    .catch(error => {
        console.error('Erreur:', error);
        alert('Erreur lors de l\'envoi de l\'invitation');
    });
}

function handleRoleFormSubmit(e) {
    e.preventDefault();
    const formData = new FormData(this);
    const roleId = formData.get('role_id');
    
    // Convertir les checkboxes en boolean
    const checkboxes = ['can_view_users', 'can_edit_users', 'can_delete_users',
                       'can_view_properties', 'can_edit_properties', 'can_delete_properties',
                       'can_view_moderation', 'can_treat_moderation',
                       'can_view_business', 'can_edit_business',
                       'can_view_finance', 'can_edit_finance',
                       'can_view_settings', 'can_edit_settings',
                       'can_view_analytics', 'can_export_analytics'];
    
    checkboxes.forEach(key => {
        formData.set(key, formData.get(key) ? 'true' : 'false');
    });
    
    const url = roleId ? `${roleUpdateUrl}${roleId}/update/` : roleCreateUrl;
    
    fetch(url, {
        method: 'POST',
        body: formData,
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showSuccessMessage(data.message || 'Rôle sauvegardé avec succès');
            closeRoleModal();
            setTimeout(() => {
                window.location.reload();
            }, 1000);
        } else {
            alert('Erreur: ' + (data.error || 'Impossible de sauvegarder le rôle'));
        }
    })
    .catch(error => {
        console.error('Erreur:', error);
        alert('Erreur lors de la sauvegarde du rôle');
    });
}

function handleTemplateFormSubmit(e) {
    e.preventDefault();
    const formData = new FormData(this);
    
    fetch(notificationTemplateSaveUrl, {
        method: 'POST',
        body: formData,
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showSuccessMessage(data.message || 'Template sauvegardé avec succès');
            closeTemplateModal();
            setTimeout(() => {
                window.location.reload();
            }, 1000);
        } else {
            alert('Erreur: ' + (data.error || 'Impossible de sauvegarder le template'));
        }
    })
    .catch(error => {
        console.error('Erreur:', error);
        alert('Erreur lors de la sauvegarde du template');
    });
}

// ============================================
// SAVE FUNCTIONS
// ============================================

function saveSettings(section, formData) {
    formData.append('section', section);
    formData.append('csrfmiddlewaretoken', csrfToken);
    
    fetch(settingsSaveUrl, {
        method: 'POST',
        body: formData,
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showSuccessMessage(data.message || 'Paramètres sauvegardés avec succès');
        } else {
            alert('Erreur: ' + (data.error || 'Impossible de sauvegarder les paramètres'));
        }
    })
    .catch(error => {
        console.error('Erreur:', error);
        alert('Erreur lors de la sauvegarde');
    });
}

function saveConfig(configType, url, formData) {
    formData.append('csrfmiddlewaretoken', csrfToken);
    
    fetch(url, {
        method: 'POST',
        body: formData,
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showSuccessMessage(data.message || 'Configuration sauvegardée avec succès');
        } else {
            alert('Erreur: ' + (data.error || 'Impossible de sauvegarder la configuration'));
        }
    })
    .catch(error => {
        console.error('Erreur:', error);
        alert('Erreur lors de la sauvegarde');
    });
}

// ============================================
// PRICING TABLE
// ============================================

function initPricingTable() {
    const tbody = document.getElementById('pricing-table-body');
    if (!tbody) return;
    
    const defaultPricing = [
        { plan: 'Gratuit', monthly: 0, annual: 0, features: 'Recherche basique' },
        { plan: 'Basique', monthly: 9.99, annual: 99.99, features: 'Recherche avancée, notifications' },
        { plan: 'Premium', monthly: 19.99, annual: 199.99, features: 'Toutes fonctionnalités, support prioritaire' },
        { plan: 'Entreprise', monthly: 49.99, annual: 499.99, features: 'Personnalisation, API dédiée' },
    ];
    
    const data = pricingData && pricingData.length > 0 ? pricingData : defaultPricing;
    
    data.forEach((row, index) => {
        addPricingRow(row, index);
    });
}

function addPricingRow(data = {}, index = null) {
    const tbody = document.getElementById('pricing-table-body');
    if (!tbody) return;
    
    const row = document.createElement('tr');
    row.innerHTML = `
        <td>
            <input type="text" class="pricing-plan" value="${data.plan || ''}" placeholder="Nom du plan">
        </td>
        <td>
            <input type="number" class="pricing-monthly" value="${data.monthly || 0}" step="0.01" min="0" placeholder="0.00">
        </td>
        <td>
            <input type="number" class="pricing-annual" value="${data.annual || 0}" step="0.01" min="0" placeholder="0.00">
        </td>
        <td>
            <textarea class="pricing-features" rows="2" placeholder="Fonctionnalités...">${data.features || ''}</textarea>
        </td>
        <td>
            <button type="button" class="btn-icon btn-danger" onclick="removePricingRow(this)" title="Supprimer">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <polyline points="3 6 5 6 21 6"></polyline>
                    <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
                </svg>
            </button>
        </td>
    `;
    
    if (index !== null) {
        tbody.insertBefore(row, tbody.children[index]);
    } else {
        tbody.appendChild(row);
    }
}

function removePricingRow(button) {
    if (confirm('Êtes-vous sûr de vouloir supprimer cette ligne ?')) {
        button.closest('tr').remove();
    }
}

function getPricingData() {
    const rows = document.querySelectorAll('#pricing-table-body tr');
    const data = [];
    
    rows.forEach(row => {
        const plan = row.querySelector('.pricing-plan')?.value || '';
        const monthly = parseFloat(row.querySelector('.pricing-monthly')?.value || 0);
        const annual = parseFloat(row.querySelector('.pricing-annual')?.value || 0);
        const features = row.querySelector('.pricing-features')?.value || '';
        
        if (plan || monthly || annual || features) {
            data.push({ plan, monthly, annual, features });
        }
    });
    
    return data;
}

// ============================================
// EVENT NOTIFICATIONS
// ============================================

function initEventNotifications() {
    const tbody = document.querySelector('#event-notifications-table tbody');
    if (!tbody) return;
    
    const defaultEvents = [
        { event: 'Nouvelle candidature', email: true, push: true, sms: false },
        { event: 'Message reçu', email: true, push: true, sms: false },
        { event: 'Paiement reçu', email: true, push: false, sms: false },
        { event: 'Avis reçu', email: true, push: true, sms: false },
        { event: 'Demande vérification', email: true, push: false, sms: false },
    ];
    
    const data = eventNotificationsData && Object.keys(eventNotificationsData).length > 0 
        ? Object.entries(eventNotificationsData).map(([event, config]) => ({
            event,
            email: config.email || false,
            push: config.push || false,
            sms: config.sms || false,
        }))
        : defaultEvents;
    
    data.forEach(row => {
        addEventNotificationRow(row);
    });
}

function addEventNotificationRow(data = {}) {
    const tbody = document.querySelector('#event-notifications-table tbody');
    if (!tbody) return;
    
    const row = document.createElement('tr');
    row.innerHTML = `
        <td>
            <input type="text" class="event-name" value="${data.event || ''}" placeholder="Nom de l'événement">
        </td>
        <td>
            <input type="checkbox" class="event-email" ${data.email ? 'checked' : ''}>
        </td>
        <td>
            <input type="checkbox" class="event-push" ${data.push ? 'checked' : ''}>
        </td>
        <td>
            <input type="checkbox" class="event-sms" ${data.sms ? 'checked' : ''}>
        </td>
    `;
    
    tbody.appendChild(row);
}

function getEventNotificationsData() {
    const rows = document.querySelectorAll('#event-notifications-table tbody tr');
    const data = {};
    
    rows.forEach(row => {
        const event = row.querySelector('.event-name')?.value || '';
        if (event) {
            data[event] = {
                email: row.querySelector('.event-email')?.checked || false,
                push: row.querySelector('.event-push')?.checked || false,
                sms: row.querySelector('.event-sms')?.checked || false,
            };
        }
    });
    
    return data;
}

// ============================================
// CUSTOM WEBHOOKS
// ============================================

function initCustomWebhooks() {
    const container = document.getElementById('custom-webhooks-container');
    if (!container) return;
    
    const data = customWebhooksData && customWebhooksData.length > 0 ? customWebhooksData : [];
    
    data.forEach(webhook => {
        addCustomWebhook(webhook);
    });
}

function addCustomWebhook(data = {}) {
    const container = document.getElementById('custom-webhooks-container');
    if (!container) return;
    
    const item = document.createElement('div');
    item.className = 'custom-webhook-item';
    item.innerHTML = `
        <div class="custom-webhook-header">
            <input type="text" class="webhook-url" value="${data.url || ''}" placeholder="https://example.com/webhook">
            <input type="text" class="webhook-secret" value="${data.secret || ''}" placeholder="Secret">
            <button type="button" class="btn-icon btn-danger" onclick="removeCustomWebhook(this)" title="Supprimer">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <polyline points="3 6 5 6 21 6"></polyline>
                    <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
                </svg>
            </button>
        </div>
        <div class="webhook-events-list">
            <label><input type="checkbox" class="webhook-event" value="user.created" ${(data.events || []).includes('user.created') ? 'checked' : ''}> Création utilisateur</label>
            <label><input type="checkbox" class="webhook-event" value="property.created" ${(data.events || []).includes('property.created') ? 'checked' : ''}> Création logement</label>
            <label><input type="checkbox" class="webhook-event" value="payment.completed" ${(data.events || []).includes('payment.completed') ? 'checked' : ''}> Paiement complété</label>
        </div>
        <button type="button" class="btn-secondary" onclick="testWebhook(this)">Tester webhook</button>
    `;
    
    container.appendChild(item);
}

function removeCustomWebhook(button) {
    if (confirm('Êtes-vous sûr de vouloir supprimer ce webhook ?')) {
        button.closest('.custom-webhook-item').remove();
    }
}

function getCustomWebhooks() {
    const items = document.querySelectorAll('.custom-webhook-item');
    const data = [];
    
    items.forEach(item => {
        const url = item.querySelector('.webhook-url')?.value || '';
        const secret = item.querySelector('.webhook-secret')?.value || '';
        const events = Array.from(item.querySelectorAll('.webhook-event:checked')).map(cb => cb.value);
        
        if (url) {
            data.push({ url, secret, events });
        }
    });
    
    return data;
}

function testWebhook(button) {
    const item = button.closest('.custom-webhook-item');
    const url = item.querySelector('.webhook-url')?.value;
    
    if (!url) {
        alert('Veuillez renseigner l\'URL du webhook');
        return;
    }
    
    // TODO: Envoyer une requête de test
    alert('Test webhook non implémenté');
}

// ============================================
// WEBHOOK EVENTS
// ============================================

function initWebhookEvents() {
    const container = document.getElementById('webhook-events-list');
    if (!container) return;
    
    const defaultEvents = [
        { value: 'user.created', label: 'Création utilisateur' },
        { value: 'user.updated', label: 'Modification utilisateur' },
        { value: 'property.created', label: 'Création logement' },
        { value: 'property.updated', label: 'Modification logement' },
        { value: 'payment.completed', label: 'Paiement complété' },
        { value: 'application.created', label: 'Nouvelle candidature' },
    ];
    
    const selectedEvents = Array.isArray(webhookEventsData) ? webhookEventsData : [];
    
    defaultEvents.forEach(event => {
        const label = document.createElement('label');
        label.className = 'checkbox-label';
        label.innerHTML = `
            <input type="checkbox" class="webhook-event-checkbox" value="${event.value}" ${selectedEvents.includes(event.value) ? 'checked' : ''}>
            <span>${event.label}</span>
        `;
        container.appendChild(label);
    });
}

function initWebhookEvents() {
    const container = document.getElementById('webhook-events-list');
    if (!container) return;
    
    const defaultEvents = [
        { value: 'user.created', label: 'Création utilisateur' },
        { value: 'user.updated', label: 'Modification utilisateur' },
        { value: 'property.created', label: 'Création logement' },
        { value: 'property.updated', label: 'Modification logement' },
        { value: 'payment.completed', label: 'Paiement complété' },
        { value: 'application.created', label: 'Nouvelle candidature' },
    ];
    
    // Récupérer les événements sélectionnés depuis le serveur si disponible
    const selectedEvents = typeof webhookEventsData !== 'undefined' ? webhookEventsData : [];
    
    defaultEvents.forEach(event => {
        const label = document.createElement('label');
        label.className = 'checkbox-label';
        label.innerHTML = `
            <input type="checkbox" class="webhook-event-checkbox" value="${event.value}" ${selectedEvents.includes(event.value) ? 'checked' : ''}>
            <span>${event.label}</span>
        `;
        container.appendChild(label);
    });
}

function getWebhookEvents() {
    const checkboxes = document.querySelectorAll('.webhook-event-checkbox:checked');
    return Array.from(checkboxes).map(cb => cb.value);
}

// ============================================
// FAQ
// ============================================

function initFAQ() {
    const container = document.getElementById('faq-container');
    if (!container) return;
    
    const data = faqData && faqData.length > 0 ? faqData : [];
    
    data.forEach(item => {
        addFAQItem(item);
    });
}

function addFAQItem(data = {}) {
    const container = document.getElementById('faq-container');
    if (!container) return;
    
    const item = document.createElement('div');
    item.className = 'faq-item';
    item.innerHTML = `
        <div class="faq-header">
            <input type="text" class="faq-question" value="${data.question || ''}" placeholder="Question">
            <button type="button" class="btn-icon btn-danger" onclick="removeFAQItem(this)" title="Supprimer">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <polyline points="3 6 5 6 21 6"></polyline>
                    <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
                </svg>
            </button>
        </div>
        <div class="faq-answer">
            <textarea class="faq-answer-text" rows="3" placeholder="Réponse...">${data.answer || ''}</textarea>
        </div>
    `;
    
    container.appendChild(item);
}

function removeFAQItem(button) {
    if (confirm('Êtes-vous sûr de vouloir supprimer cette question ?')) {
        button.closest('.faq-item').remove();
    }
}

function getFAQData() {
    const items = document.querySelectorAll('.faq-item');
    const data = [];
    
    items.forEach(item => {
        const question = item.querySelector('.faq-question')?.value || '';
        const answer = item.querySelector('.faq-answer-text')?.value || '';
        
        if (question || answer) {
            data.push({ question, answer });
        }
    });
    
    return data;
}

// ============================================
// META KEYWORDS
// ============================================

function initMetaKeywords() {
    const input = document.getElementById('meta_keywords');
    const container = document.getElementById('meta-keywords-tags');
    
    if (!input || !container) return;
    
    const keywords = metaKeywordsData && metaKeywordsData.length > 0 ? metaKeywordsData : [];
    
    keywords.forEach(keyword => {
        addMetaKeywordTag(keyword);
    });
    
    // Ajouter un tag quand on appuie sur Enter ou virgule
    input.addEventListener('keydown', function(e) {
        if (e.key === 'Enter' || e.key === ',') {
            e.preventDefault();
            const value = this.value.trim();
            if (value) {
                addMetaKeywordTag(value);
                this.value = '';
            }
        }
    });
}

function addMetaKeywordTag(keyword) {
    const container = document.getElementById('meta-keywords-tags');
    if (!container) return;
    
    // Vérifier si le tag existe déjà
    const existingTags = Array.from(container.querySelectorAll('.tag-item span')).map(span => span.textContent);
    if (existingTags.includes(keyword)) return;
    
    const tag = document.createElement('div');
    tag.className = 'tag-item';
    tag.innerHTML = `
        <span>${keyword}</span>
        <button type="button" onclick="removeMetaKeywordTag(this)">&times;</button>
    `;
    
    container.appendChild(tag);
}

function removeMetaKeywordTag(button) {
    button.closest('.tag-item').remove();
}

function getMetaKeywordsData() {
    const tags = document.querySelectorAll('#meta-keywords-tags .tag-item span');
    return Array.from(tags).map(span => span.textContent);
}

// ============================================
// ROLES MODAL
// ============================================

function openRoleModal(roleId = null) {
    const modal = document.getElementById('role-modal');
    const form = document.getElementById('role-form');
    const title = document.getElementById('role-modal-title');
    const roleIdInput = document.getElementById('role_id');
    
    if (!modal || !form || !title) return;
    
    if (roleId) {
        title.textContent = 'Éditer un rôle';
        roleIdInput.value = roleId;
        // TODO: Charger les données du rôle
        form.action = `${roleUpdateUrl}${roleId}/update/`;
    } else {
        title.textContent = 'Créer un rôle';
        roleIdInput.value = '';
        form.action = roleCreateUrl;
        form.reset();
    }
    
    modal.style.display = 'flex';
}

function closeRoleModal() {
    const modal = document.getElementById('role-modal');
    if (modal) {
        modal.style.display = 'none';
    }
}

function editRole(roleId) {
    openRoleModal(roleId);
}

function deleteRole(roleId) {
    if (!confirm('Êtes-vous sûr de vouloir supprimer ce rôle ?')) {
        return;
    }
    
    const formData = new FormData();
    formData.append('csrfmiddlewaretoken', csrfToken);
    
    fetch(`${roleDeleteUrl}${roleId}/delete/`, {
        method: 'POST',
        body: formData,
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showSuccessMessage(data.message || 'Rôle supprimé avec succès');
            setTimeout(() => {
                window.location.reload();
            }, 1000);
        } else {
            alert('Erreur: ' + (data.error || 'Impossible de supprimer le rôle'));
        }
    })
    .catch(error => {
        console.error('Erreur:', error);
        alert('Erreur lors de la suppression');
    });
}

// ============================================
// TEMPLATE MODAL
// ============================================

function openTemplateModal(templateId = null) {
    const modal = document.getElementById('template-modal');
    const form = document.getElementById('template-form');
    const title = document.getElementById('template-modal-title');
    const templateIdInput = document.getElementById('template_id');
    
    if (!modal || !form || !title) return;
    
    if (templateId) {
        title.textContent = 'Éditer un template';
        templateIdInput.value = templateId;
        // TODO: Charger les données du template
    } else {
        title.textContent = 'Créer un template';
        templateIdInput.value = '';
        form.reset();
    }
    
    modal.style.display = 'flex';
}

function closeTemplateModal() {
    const modal = document.getElementById('template-modal');
    if (modal) {
        modal.style.display = 'none';
    }
}

function editTemplate(templateId) {
    openTemplateModal(templateId);
}

function previewTemplate(templateId) {
    // TODO: Afficher un aperçu du template
    alert('Aperçu template non implémenté');
}

function testTemplate(templateId) {
    const email = prompt('Email pour le test:');
    if (!email) return;
    
    // TODO: Envoyer un email de test
    alert('Test email non implémenté');
}

// ============================================
// UTILITY FUNCTIONS
// ============================================

function testGoogleMaps() {
    const apiKey = document.getElementById('google_maps_api_key')?.value;
    if (!apiKey) {
        alert('Veuillez renseigner la clé API Google Maps');
        return;
    }
    
    // TODO: Tester la connexion à Google Maps
    alert('Test Google Maps non implémenté');
}

function previewInvoice() {
    // TODO: Afficher un aperçu de la facture
    alert('Aperçu facture non implémenté');
}

function viewLogDetails(logId) {
    // TODO: Afficher les détails JSON du log
    alert('Détails log non implémentés');
}

function showSuccessMessage(message) {
    const msg = document.createElement('div');
    msg.className = 'alert alert-success';
    msg.textContent = message;
    msg.style.cssText = 'position: fixed; top: 20px; right: 20px; padding: 12px 20px; background: #10B981; color: white; border-radius: 8px; z-index: 9999; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);';
    document.body.appendChild(msg);
    
    setTimeout(() => {
        msg.remove();
    }, 3000);
}

// Fermer les modals au clic sur le backdrop
document.addEventListener('click', function(e) {
    if (e.target.classList.contains('modal')) {
        e.target.style.display = 'none';
    }
});

