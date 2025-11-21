/**
 * USERS MANAGEMENT - JavaScript pour filtres, sélection bulk et actions
 */

// ============================================
// VARIABLES GLOBALES
// ============================================

let selectedUsers = new Set();
let currentSort = '';

// ============================================
// INITIALISATION
// ============================================

function initUsersTable() {
    // Gestion du tri
    const sortableHeaders = document.querySelectorAll('.sortable');
    sortableHeaders.forEach(header => {
        header.addEventListener('click', function() {
            const sortField = this.dataset.sort;
            toggleSort(sortField);
        });
    });

    // Fermer les dropdowns au click extérieur
    document.addEventListener('click', function(e) {
        if (!e.target.closest('.actions-dropdown')) {
            document.querySelectorAll('.actions-dropdown').forEach(dropdown => {
                dropdown.classList.remove('active');
            });
        }
    });

    // Récupérer le tri actuel
    const urlParams = new URLSearchParams(window.location.search);
    currentSort = urlParams.get('sort') || '-date_joined';
    updateSortIcons();
}

function initMultiSelect() {
    // Simulation multi-select pour les select natifs
    // Dans un vrai projet, utiliser une librairie comme Select2 ou Choices.js
    const multiSelects = document.querySelectorAll('.multi-select');
    
    multiSelects.forEach(select => {
        // Afficher le nombre d'options sélectionnées
        select.addEventListener('change', function() {
            const selected = Array.from(this.selectedOptions).map(opt => opt.text);
            if (selected.length > 0) {
                this.title = selected.join(', ');
            }
        });
        
        // Trigger change au chargement pour afficher les valeurs sélectionnées
        if (select.selectedOptions.length > 0) {
            select.dispatchEvent(new Event('change'));
        }
    });
}

function initDateRange() {
    // Date picker validation
    const dateInputs = document.querySelectorAll('.date-input');
    dateInputs.forEach(input => {
        input.addEventListener('change', function() {
            const dateFrom = document.querySelector('input[name="date_from"]');
            const dateTo = document.querySelector('input[name="date_to"]');
            
            if (dateFrom.value && dateTo.value) {
                if (new Date(dateFrom.value) > new Date(dateTo.value)) {
                    alert('La date de début doit être antérieure à la date de fin');
                    this.value = '';
                }
            }
        });
    });
}

// ============================================
// SÉLECTION BULK
// ============================================

function toggleSelectAll(checkbox) {
    const userCheckboxes = document.querySelectorAll('.user-checkbox');
    userCheckboxes.forEach(cb => {
        cb.checked = checkbox.checked;
        if (checkbox.checked) {
            selectedUsers.add(cb.value);
        } else {
            selectedUsers.delete(cb.value);
        }
    });
    updateBulkActions();
}

function updateBulkActions() {
    selectedUsers.clear();
    document.querySelectorAll('.user-checkbox:checked').forEach(cb => {
        selectedUsers.add(cb.value);
    });

    const bulkBar = document.getElementById('bulk-actions-bar');
    const bulkCount = document.getElementById('bulk-count');
    
    if (selectedUsers.size > 0) {
        bulkBar.style.display = 'flex';
        bulkCount.textContent = selectedUsers.size;
        
        // Update select-all checkbox
        const selectAll = document.getElementById('select-all');
        const totalCheckboxes = document.querySelectorAll('.user-checkbox').length;
        const checkedCheckboxes = document.querySelectorAll('.user-checkbox:checked').length;
        selectAll.checked = checkedCheckboxes === totalCheckboxes;
        selectAll.indeterminate = checkedCheckboxes > 0 && checkedCheckboxes < totalCheckboxes;
    } else {
        bulkBar.style.display = 'none';
        document.getElementById('select-all').checked = false;
        document.getElementById('select-all').indeterminate = false;
    }
}

function clearSelection() {
    selectedUsers.clear();
    document.querySelectorAll('.user-checkbox, #select-all').forEach(cb => {
        cb.checked = false;
        cb.indeterminate = false;
    });
    updateBulkActions();
}

// ============================================
// ACTIONS BULK
// ============================================

function bulkAction(action) {
    if (selectedUsers.size === 0) {
        alert('Veuillez sélectionner au moins un utilisateur');
        return;
    }

    const userIds = Array.from(selectedUsers).map(id => parseInt(id));

    switch(action) {
        case 'suspend':
            bulkSuspendUsers(userIds);
            break;
        case 'email':
            bulkSendEmail(userIds);
            break;
        case 'export':
            bulkExportUsers(userIds);
            break;
        default:
            console.error('Action bulk inconnue:', action);
    }
}

function bulkSuspendUsers(userIds) {
    if (!confirm(`Êtes-vous sûr de vouloir suspendre ${userIds.length} utilisateur(s) ?`)) {
        return;
    }

    const duration = prompt('Durée de suspension:\n7 = 7 jours\n30 = 30 jours\nou entrez un nombre de jours personnalisé', '7');
    if (!duration) return;

    const reason = prompt('Raison de la suspension:', '');
    if (reason === null) return; // Annulé

    // Envoyer requête POST pour suspendre
    fetch('/connect-admin/users/bulk/suspend/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCsrfToken()
        },
        body: JSON.stringify({
            user_ids: userIds,
            duration: duration,
            reason: reason || ''
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert(`${userIds.length} utilisateur(s) suspendu(s) avec succès`);
            location.reload();
        } else {
            alert('Erreur: ' + (data.error || 'Impossible de suspendre les utilisateurs'));
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Erreur lors de la suspension des utilisateurs');
    });
}

function bulkSendEmail(userIds) {
    const subject = prompt('Sujet de l\'email:', '');
    if (!subject) return;

    const message = prompt('Message:', '');
    if (message === null) return;

    // Envoyer requête POST pour envoyer email
    fetch('/connect-admin/users/bulk/email/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCsrfToken()
        },
        body: JSON.stringify({
            user_ids: userIds,
            subject: subject,
            message: message
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert(`Email envoyé à ${userIds.length} utilisateur(s)`);
        } else {
            alert('Erreur: ' + (data.error || 'Impossible d\'envoyer l\'email'));
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Erreur lors de l\'envoi de l\'email');
    });
}

function bulkExportUsers(userIds) {
    const params = new URLSearchParams(window.location.search);
    params.set('export', 'csv');
    params.set('user_ids', userIds.join(','));
    
    window.location.href = window.location.pathname + '?' + params.toString();
}

// ============================================
// TRI
// ============================================

function toggleSort(sortField) {
    const urlParams = new URLSearchParams(window.location.search);
    const currentSortParam = urlParams.get('sort') || '-date_joined';
    
    // Déterminer le nouveau tri
    let newSort;
    if (currentSortParam === sortField) {
        // Inverser le tri
        newSort = sortField.startsWith('-') ? sortField.slice(1) : '-' + sortField;
    } else if (currentSortParam === '-' + sortField) {
        // Déjà en ordre inverse, revenir à l'ordre normal
        newSort = sortField;
    } else {
        // Nouveau tri, ordre décroissant par défaut
        newSort = '-' + sortField;
    }
    
    urlParams.set('sort', newSort);
    window.location.search = urlParams.toString();
}

function updateSortIcons() {
    const urlParams = new URLSearchParams(window.location.search);
    const currentSortParam = urlParams.get('sort') || '-date_joined';
    const sortField = currentSortParam.startsWith('-') ? currentSortParam.slice(1) : currentSortParam;
    const isDesc = currentSortParam.startsWith('-');
    
    document.querySelectorAll('.sortable').forEach(header => {
        header.classList.remove('active');
        const icon = header.querySelector('.sort-icon');
        if (icon) {
            icon.style.transform = 'translateY(-50%)';
        }
        
        if (header.dataset.sort === sortField) {
            header.classList.add('active');
            if (icon) {
                icon.style.transform = isDesc ? 'translateY(-50%) rotate(180deg)' : 'translateY(-50%)';
            }
        }
    });
}

// ============================================
// ACTIONS DROPDOWN
// ============================================

function toggleActionsDropdown(button) {
    const dropdown = button.closest('.actions-dropdown');
    const isActive = dropdown.classList.contains('active');
    
    // Fermer tous les autres dropdowns
    document.querySelectorAll('.actions-dropdown').forEach(d => {
        d.classList.remove('active');
    });
    
    // Toggle le dropdown actuel
    if (!isActive) {
        dropdown.classList.add('active');
    }
}

// ============================================
// ACTIONS UTILISATEUR
// ============================================

function suspendUser(userId) {
    const duration = prompt('Durée de suspension:\n7 = 7 jours\n30 = 30 jours\nou entrez un nombre de jours personnalisé', '7');
    if (!duration) return;

    const reason = prompt('Raison de la suspension:', '');
    if (reason === null) return;

    // Rediriger vers l'action suspend
    const form = document.createElement('form');
    form.method = 'POST';
    form.action = `/connect-admin/users/${userId}/suspend/`;
    
    const csrf = document.createElement('input');
    csrf.type = 'hidden';
    csrf.name = 'csrfmiddlewaretoken';
    csrf.value = getCsrfToken();
    form.appendChild(csrf);
    
    const durationInput = document.createElement('input');
    durationInput.type = 'hidden';
    durationInput.name = 'duration';
    durationInput.value = duration;
    form.appendChild(durationInput);
    
    const reasonInput = document.createElement('input');
    reasonInput.type = 'hidden';
    reasonInput.name = 'reason';
    reasonInput.value = reason;
    form.appendChild(reasonInput);
    
    document.body.appendChild(form);
    form.submit();
}

function reactivateUser(userId) {
    if (!confirm('Êtes-vous sûr de vouloir réactiver cet utilisateur ?')) {
        return;
    }

    // TODO: Implémenter réactivation
    alert('Fonctionnalité de réactivation à implémenter');
}

function banUser(userId) {
    const reason = prompt('Raison du bannissement:', '');
    if (reason === null || !reason.trim()) {
        alert('Une raison est requise pour bannir un utilisateur');
        return;
    }

    if (!confirm(`Êtes-vous sûr de vouloir bannir définitivement cet utilisateur ?\n\nRaison: ${reason}`)) {
        return;
    }

    // Rediriger vers l'action ban
    const form = document.createElement('form');
    form.method = 'POST';
    form.action = `/connect-admin/users/${userId}/ban/`;
    
    const csrf = document.createElement('input');
    csrf.type = 'hidden';
    csrf.name = 'csrfmiddlewaretoken';
    csrf.value = getCsrfToken();
    form.appendChild(csrf);
    
    const reasonInput = document.createElement('input');
    reasonInput.type = 'hidden';
    reasonInput.name = 'reason';
    reasonInput.value = reason;
    form.appendChild(reasonInput);
    
    document.body.appendChild(form);
    form.submit();
}

function revokeBadges(userId) {
    // TODO: Ouvrir modal pour sélectionner badges à révoquer
    alert('Fonctionnalité de révocation de badges à implémenter');
}

function deleteUser(userId) {
    const confirmation1 = prompt('ATTENTION: Cette action est irréversible.\n\nTapez SUPPRIMER pour confirmer:', '');
    if (confirmation1 !== 'SUPPRIMER') {
        return;
    }

    const confirmation2 = prompt('Tapez SUPPRIMER une deuxième fois pour confirmer:', '');
    if (confirmation2 !== 'SUPPRIMER') {
        return;
    }

    // Rediriger vers l'action delete
    const form = document.createElement('form');
    form.method = 'POST';
    form.action = `/connect-admin/users/${userId}/delete/`;
    
    const csrf = document.createElement('input');
    csrf.type = 'hidden';
    csrf.name = 'csrfmiddlewaretoken';
    csrf.value = getCsrfToken();
    form.appendChild(csrf);
    
    const confirm1Input = document.createElement('input');
    confirm1Input.type = 'hidden';
    confirm1Input.name = 'confirmation';
    confirm1Input.value = confirmation1;
    form.appendChild(confirm1Input);
    
    const confirm2Input = document.createElement('input');
    confirm2Input.type = 'hidden';
    confirm2Input.name = 'confirmation2';
    confirm2Input.value = confirmation2;
    form.appendChild(confirm2Input);
    
    document.body.appendChild(form);
    form.submit();
}

function editUser(userId) {
    // TODO: Ouvrir modal d'édition
    alert('Fonctionnalité d\'édition à implémenter');
}

// ============================================
// UTILITAIRES
// ============================================

function copyEmail(email) {
    navigator.clipboard.writeText(email).then(() => {
        // Feedback visuel
        const tooltip = document.createElement('div');
        tooltip.textContent = 'Email copié !';
        tooltip.style.cssText = 'position: fixed; top: 20px; right: 20px; background: #10B981; color: white; padding: 12px 20px; border-radius: 8px; z-index: 10000; box-shadow: 0 4px 12px rgba(0,0,0,0.15);';
        document.body.appendChild(tooltip);
        
        setTimeout(() => {
            tooltip.remove();
        }, 2000);
    }).catch(err => {
        console.error('Erreur lors de la copie:', err);
        alert('Impossible de copier l\'email');
    });
}

function getCsrfToken() {
    const token = document.querySelector('[name=csrfmiddlewaretoken]');
    return token ? token.value : '';
}

// ============================================
// MODAL
// ============================================

function openAddUserModal() {
    const modal = document.getElementById('add-user-modal');
    if (modal) {
        modal.style.display = 'flex';
    }
}

function closeAddUserModal() {
    const modal = document.getElementById('add-user-modal');
    if (modal) {
        modal.style.display = 'none';
    }
}

// Fermer modal au click sur overlay
document.addEventListener('DOMContentLoaded', function() {
    const modalOverlay = document.getElementById('add-user-modal');
    if (modalOverlay) {
        modalOverlay.addEventListener('click', function(e) {
            if (e.target === modalOverlay) {
                closeAddUserModal();
            }
        });
    }

    // Fermer modal avec Escape
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            closeAddUserModal();
        }
    });
});

