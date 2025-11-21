/**
 * MODERATION - JavaScript pour gestion modération
 */

// ============================================
// INITIALISATION
// ============================================

function initModeration() {
    // Initialisation des tabs
    initModerationTabs();
    
    // Initialisation des sous-tabs de vérification
    initVerificationSubtabs();
}

// ============================================
// TABS
// ============================================

function switchModerationTab(tabName) {
    // Masquer tous les panels
    document.querySelectorAll('.tab-panel').forEach(panel => {
        panel.classList.remove('active');
    });
    
    // Retirer active de tous les boutons
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    
    // Afficher le panel sélectionné
    const panel = document.getElementById(`tab-${tabName}`);
    if (panel) {
        panel.classList.add('active');
    }
    
    // Activer le bouton
    const btn = document.querySelector(`[data-tab="${tabName}"]`);
    if (btn) {
        btn.classList.add('active');
    }
}

function initModerationTabs() {
    // Le premier tab est actif par défaut
    switchModerationTab('reported-contents');
}

// ============================================
// VERIFICATION SUBTABS
// ============================================

function switchVerificationSubtab(subtabName) {
    // Masquer tous les sous-panels
    document.querySelectorAll('.subtab-panel').forEach(panel => {
        panel.classList.remove('active');
    });
    
    // Retirer active de tous les boutons
    document.querySelectorAll('.subtab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    
    // Afficher le sous-panel sélectionné
    const panel = document.getElementById(`subtab-${subtabName}`);
    if (panel) {
        panel.classList.add('active');
    }
    
    // Activer le bouton
    const btn = document.querySelector(`[data-subtab="${subtabName}"]`);
    if (btn) {
        btn.classList.add('active');
    }
}

function initVerificationSubtabs() {
    // Le premier sous-tab est actif par défaut
    switchVerificationSubtab('identity');
}

// ============================================
// ACTIONS CONTENUS SIGNALÉS
// ============================================

function contentAction(contentId, action) {
    const actionTexts = {
        'approve': 'Approuver',
        'delete': 'Supprimer',
        'mark_treated': 'Marquer comme traité',
        'ignore': 'Ignorer'
    };
    
    if (action === 'delete' || action === 'ban') {
        if (!confirm(`Êtes-vous sûr de vouloir ${actionTexts[action]?.toLowerCase()} ce contenu ?`)) {
            return;
        }
    }
    
    const formData = new FormData();
    formData.append('action', action);
    formData.append('csrfmiddlewaretoken', csrfToken);
    
    fetch(`${reportedContentActionUrl}${contentId}/action/`, {
        method: 'POST',
        body: formData,
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showSuccessMessage(data.message || 'Action effectuée avec succès');
            // Recharger la page après 1 seconde
            setTimeout(() => {
                window.location.reload();
            }, 1000);
        } else {
            alert('Erreur: ' + (data.error || 'Impossible d\'effectuer l\'action'));
        }
    })
    .catch(error => {
        console.error('Erreur:', error);
        alert('Erreur lors de l\'action');
    });
}

function viewContentDetail(contentId) {
    // TODO: Charger le détail du contenu dans le modal
    // Pour l'instant, on ouvre juste le modal
    const modal = document.getElementById('content-detail-modal');
    if (modal) {
        modal.style.display = 'flex';
    }
}

function toggleActionsMenu(contentId) {
    const menu = document.getElementById(`actions-menu-${contentId}`);
    if (menu) {
        // Fermer tous les autres menus
        document.querySelectorAll('.actions-menu').forEach(m => {
            if (m.id !== menu.id) {
                m.style.display = 'none';
            }
        });
        
        // Toggle le menu actuel
        menu.style.display = menu.style.display === 'none' ? 'block' : 'none';
    }
}

// Fermer les menus au clic extérieur
document.addEventListener('click', function(e) {
    if (!e.target.closest('.actions-dropdown')) {
        document.querySelectorAll('.actions-menu').forEach(menu => {
            menu.style.display = 'none';
        });
    }
});

// ============================================
// BULK ACTIONS
// ============================================

function toggleSelectAll(checkbox) {
    const checkboxes = document.querySelectorAll('.content-checkbox');
    checkboxes.forEach(cb => {
        cb.checked = checkbox.checked;
    });
    updateBulkActions();
}

function updateBulkActions() {
    const checked = document.querySelectorAll('.content-checkbox:checked');
    const bulkBar = document.getElementById('bulk-actions-bar');
    const bulkCount = document.getElementById('bulk-count');
    
    if (checked.length > 0) {
        bulkBar.style.display = 'flex';
        bulkCount.textContent = checked.length;
    } else {
        bulkBar.style.display = 'none';
    }
}

function deselectAll() {
    document.querySelectorAll('.content-checkbox').forEach(cb => {
        cb.checked = false;
    });
    document.getElementById('select-all').checked = false;
    updateBulkActions();
}

function bulkAction(action) {
    const checked = Array.from(document.querySelectorAll('.content-checkbox:checked')).map(cb => cb.value);
    
    if (checked.length === 0) {
        alert('Veuillez sélectionner au moins un contenu');
        return;
    }
    
    if (action === 'delete') {
        if (!confirm(`Êtes-vous sûr de vouloir supprimer ${checked.length} contenu(s) ?`)) {
            return;
        }
    }
    
    // Exécuter l'action pour chaque contenu sélectionné
    checked.forEach(contentId => {
        contentAction(parseInt(contentId), action);
    });
}

// ============================================
// ACTIONS UTILISATEURS
// ============================================

function viewUserProfile(userId) {
    window.location.href = `/connect-admin/users/${userId}/`;
}

function suspendUser(userModerationId) {
    const days = prompt('Nombre de jours de suspension:', '7');
    if (days === null) return;
    
    if (isNaN(days) || days <= 0) {
        alert('Veuillez entrer un nombre valide de jours');
        return;
    }
    
    const formData = new FormData();
    formData.append('action', 'suspend');
    formData.append('days', days);
    formData.append('csrfmiddlewaretoken', csrfToken);
    
    fetch(`${userModerationActionUrl}${userModerationId}/action/`, {
        method: 'POST',
        body: formData,
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showSuccessMessage(data.message || 'Utilisateur suspendu avec succès');
            setTimeout(() => {
                window.location.reload();
            }, 1000);
        } else {
            alert('Erreur: ' + (data.error || 'Impossible de suspendre l\'utilisateur'));
        }
    })
    .catch(error => {
        console.error('Erreur:', error);
        alert('Erreur lors de la suspension');
    });
}

function banUser(userModerationId) {
    const banReason = prompt('Raison du bannissement:', '');
    if (banReason === null || banReason.trim() === '') {
        alert('La raison du bannissement est obligatoire');
        return;
    }
    
    if (!confirm('Êtes-vous sûr de vouloir bannir cet utilisateur définitivement ?')) {
        return;
    }
    
    const formData = new FormData();
    formData.append('action', 'ban');
    formData.append('ban_reason', banReason);
    formData.append('csrfmiddlewaretoken', csrfToken);
    
    fetch(`${userModerationActionUrl}${userModerationId}/action/`, {
        method: 'POST',
        body: formData,
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showSuccessMessage(data.message || 'Utilisateur banni avec succès');
            setTimeout(() => {
                window.location.reload();
            }, 1000);
        } else {
            alert('Erreur: ' + (data.error || 'Impossible de bannir l\'utilisateur'));
        }
    })
    .catch(error => {
        console.error('Erreur:', error);
        alert('Erreur lors du bannissement');
    });
}

function ignoreAlert(userModerationId) {
    const formData = new FormData();
    formData.append('action', 'ignore');
    formData.append('csrfmiddlewaretoken', csrfToken);
    
    fetch(`${userModerationActionUrl}${userModerationId}/action/`, {
        method: 'POST',
        body: formData,
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showSuccessMessage(data.message || 'Alerte ignorée');
            setTimeout(() => {
                window.location.reload();
            }, 1000);
        } else {
            alert('Erreur: ' + (data.error || 'Impossible d\'ignorer l\'alerte'));
        }
    })
    .catch(error => {
        console.error('Erreur:', error);
        alert('Erreur lors de l\'action');
    });
}

// ============================================
// ACTIONS VÉRIFICATIONS
// ============================================

function verificationAction(verificationId, action) {
    let formData = new FormData();
    formData.append('action', action);
    formData.append('csrfmiddlewaretoken', csrfToken);
    
    if (action === 'reject') {
        const rejectionReason = prompt('Raison du refus (obligatoire):', '');
        if (!rejectionReason || rejectionReason.trim() === '') {
            alert('La raison du refus est obligatoire');
            return;
        }
        formData.append('rejection_reason', rejectionReason);
    } else if (action === 'complement_required') {
        const reviewNotes = prompt('Message pour demander un complément:', '');
        formData.append('review_notes', reviewNotes || '');
    }
    
    fetch(`${verificationActionUrl}${verificationId}/action/`, {
        method: 'POST',
        body: formData,
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showSuccessMessage(data.message || 'Action effectuée avec succès');
            setTimeout(() => {
                window.location.reload();
            }, 1000);
        } else {
            alert('Erreur: ' + (data.error || 'Impossible d\'effectuer l\'action'));
        }
    })
    .catch(error => {
        console.error('Erreur:', error);
        alert('Erreur lors de l\'action');
    });
}

// ============================================
// ACTIONS RÉCLAMATIONS
// ============================================

function claimAction(claimId, action) {
    let formData = new FormData();
    formData.append('action', action);
    formData.append('csrfmiddlewaretoken', csrfToken);
    
    if (action === 'reject') {
        const rejectionReason = prompt('Raison du refus:', '');
        if (!rejectionReason || rejectionReason.trim() === '') {
            alert('La raison du refus est obligatoire');
            return;
        }
        formData.append('rejection_reason', rejectionReason);
    } else if (action === 'information_required') {
        const reviewNotes = prompt('Message pour demander des informations:', '');
        formData.append('review_notes', reviewNotes || '');
    }
    
    fetch(`${propertyClaimActionUrl}${claimId}/action/`, {
        method: 'POST',
        body: formData,
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showSuccessMessage(data.message || 'Action effectuée avec succès');
            setTimeout(() => {
                window.location.reload();
            }, 1000);
        } else {
            alert('Erreur: ' + (data.error || 'Impossible d\'effectuer l\'action'));
        }
    })
    .catch(error => {
        console.error('Erreur:', error);
        alert('Erreur lors de l\'action');
    });
}

// ============================================
// IMAGE VIEWER
// ============================================

let currentImageRotation = 0;
let currentImageZoom = 1;

function openImageViewer(imageSrc) {
    const modal = document.getElementById('image-viewer-modal');
    const img = document.getElementById('viewer-image');
    
    if (modal && img) {
        img.src = imageSrc;
        currentImageRotation = 0;
        currentImageZoom = 1;
        img.style.transform = 'rotate(0deg) scale(1)';
        modal.style.display = 'flex';
    }
}

function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.style.display = 'none';
    }
}

function rotateImage(angle) {
    currentImageRotation += angle;
    const img = document.getElementById('viewer-image');
    if (img) {
        img.style.transform = `rotate(${currentImageRotation}deg) scale(${currentImageZoom})`;
    }
}

function zoomImage(factor) {
    currentImageZoom *= factor;
    if (currentImageZoom < 0.5) currentImageZoom = 0.5;
    if (currentImageZoom > 3) currentImageZoom = 3;
    const img = document.getElementById('viewer-image');
    if (img) {
        img.style.transform = `rotate(${currentImageRotation}deg) scale(${currentImageZoom})`;
    }
}

// Fermer les modals au clic sur le backdrop
document.addEventListener('click', function(e) {
    if (e.target.classList.contains('modal')) {
        e.target.style.display = 'none';
    }
});

// ============================================
// UTILITAIRES
// ============================================

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

function viewReports(contentId) {
    // TODO: Afficher la liste des utilisateurs qui ont signalé
    alert('Fonctionnalité à implémenter: liste des signalements');
}

