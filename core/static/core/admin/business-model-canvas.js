/**
 * BUSINESS MODEL CANVAS - JavaScript pour édition, auto-save, etc.
 */

// ============================================
// VARIABLES GLOBALES
// ============================================

let saveTimeouts = {};
let currentEditingBlock = null;

// ============================================
// INITIALISATION
// ============================================

function initCanvas() {
    // Fermer les dropdowns au click extérieur
    document.addEventListener('click', function(e) {
        if (!e.target.closest('.actions-dropdown')) {
            const dropdowns = document.querySelectorAll('.actions-dropdown');
            dropdowns.forEach(dropdown => dropdown.classList.remove('active'));
        }
    });

    // Fermer l'indicateur de sauvegarde après 3 secondes
    const saveIndicator = document.getElementById('save-indicator');
    if (saveIndicator) {
        setTimeout(() => {
            saveIndicator.style.display = 'none';
        }, 3000);
    }
}

// ============================================
// ÉDITION DES BLOCS
// ============================================

function editBlock(blockElement) {
    // Retirer l'état d'édition des autres blocs
    document.querySelectorAll('.canvas-block').forEach(block => {
        block.classList.remove('editing');
    });

    // Ajouter l'état d'édition au bloc actuel
    blockElement.classList.add('editing');
    currentEditingBlock = blockElement;

    // Focus sur le textarea
    const textarea = blockElement.querySelector('.block-textarea');
    if (textarea) {
        textarea.focus();
        // Placer le curseur à la fin
        textarea.setSelectionRange(textarea.value.length, textarea.value.length);
    }
}

// ============================================
// SAUVEGARDE
// ============================================

function debounceSave(textarea) {
    const blockElement = textarea.closest('.canvas-block');
    const blocName = blockElement.dataset.bloc;

    // Annuler le timeout précédent pour ce bloc
    if (saveTimeouts[blocName]) {
        clearTimeout(saveTimeouts[blocName]);
    }

    // Créer un nouveau timeout (2 secondes)
    saveTimeouts[blocName] = setTimeout(() => {
        saveBlock(textarea);
    }, 2000);
}

function saveBlock(textarea) {
    const blockElement = textarea.closest('.canvas-block');
    const blocName = blockElement.dataset.bloc;
    const content = textarea.value;

    // Créer FormData
    const formData = new FormData();
    formData.append('bloc', blocName);
    formData.append('content', content);
    formData.append('csrfmiddlewaretoken', csrfToken);

    // Envoyer la requête
    fetch(saveUrl, {
        method: 'POST',
        body: formData,
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showSaveIndicator(data.message, data.updated_at);
            
            // Retirer l'état d'édition après sauvegarde
            setTimeout(() => {
                blockElement.classList.remove('editing');
            }, 100);
        } else {
            console.error('Erreur de sauvegarde:', data.error);
            alert('Erreur lors de la sauvegarde: ' + (data.error || 'Erreur inconnue'));
        }
    })
    .catch(error => {
        console.error('Erreur réseau:', error);
        alert('Erreur réseau lors de la sauvegarde');
    });

    // Nettoyer le timeout
    if (saveTimeouts[blocName]) {
        clearTimeout(saveTimeouts[blocName]);
        delete saveTimeouts[blocName];
    }
}

function showSaveIndicator(message, updatedAt) {
    const indicator = document.getElementById('save-indicator');
    const messageEl = document.getElementById('save-message');
    
    if (indicator && messageEl) {
        messageEl.textContent = message + (updatedAt ? ' - ' + updatedAt : '');
        indicator.style.display = 'flex';
        
        // Masquer après 3 secondes
        setTimeout(() => {
            indicator.style.display = 'none';
        }, 3000);
    }
}

// ============================================
// DROPDOWN VERSIONS
// ============================================

function toggleVersionsDropdown() {
    const dropdown = document.querySelector('.actions-dropdown');
    if (dropdown) {
        dropdown.classList.toggle('active');
    }
}

// ============================================
// RESTAURER VERSION
// ============================================

function restoreVersion(versionId) {
    if (!confirm('Êtes-vous sûr de vouloir restaurer cette version ? Les modifications actuelles seront perdues.')) {
        return;
    }

    fetch(`/connect-admin/business-model-canvas/restore-version/${versionId}/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrfToken,
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert(data.message);
            // Recharger la page
            location.reload();
        } else {
            alert('Erreur: ' + (data.error || 'Impossible de restaurer la version'));
        }
    })
    .catch(error => {
        console.error('Erreur:', error);
        alert('Erreur lors de la restauration');
    });

    // Fermer le dropdown
    toggleVersionsDropdown();
}

// ============================================
// PARTAGER CANVAS
// ============================================

function shareCanvas() {
    if (!shareToken) {
        alert('Token de partage non disponible');
        return;
    }

    // Activer le partage si nécessaire
    fetch('/connect-admin/business-model-canvas/share-enable/', {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrfToken,
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success || response.status === 404) {
            // Créer le lien de partage
            const shareUrl = `${window.location.origin}/canvas/share/${shareToken}/`;
            
            // Copier dans le presse-papier
            navigator.clipboard.writeText(shareUrl).then(() => {
                alert('Lien de partage copié dans le presse-papier !\n\n' + shareUrl);
            }).catch(() => {
                // Fallback: afficher le lien
                prompt('Copiez ce lien pour partager le canvas:', shareUrl);
            });
        } else {
            alert('Erreur lors de l\'activation du partage');
        }
    })
    .catch(error => {
        // Si l'endpoint n'existe pas, créer le lien directement
        const shareUrl = `${window.location.origin}/canvas/share/${shareToken}/`;
        
        navigator.clipboard.writeText(shareUrl).then(() => {
            alert('Lien de partage copié dans le presse-papier !\n\n' + shareUrl);
        }).catch(() => {
            prompt('Copiez ce lien pour partager le canvas:', shareUrl);
        });
    });
}

// ============================================
// RÉINITIALISER CANVAS
// ============================================

function resetCanvas() {
    const confirmation = prompt(
        'ATTENTION: Cette action est irréversible.\n\n' +
        'Tous les blocs du canvas seront vidés.\n\n' +
        'Tapez "RÉINITIALISER" pour confirmer:',
        ''
    );

    if (confirmation !== 'RÉINITIALISER') {
        return;
    }

    fetch('/connect-admin/business-model-canvas/reset/', {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrfToken,
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert(data.message);
            // Recharger la page
            location.reload();
        } else {
            alert('Erreur: ' + (data.error || 'Impossible de réinitialiser le canvas'));
        }
    })
    .catch(error => {
        console.error('Erreur:', error);
        alert('Erreur lors de la réinitialisation');
    });
}

// ============================================
// EXPORT PDF
// ============================================

// L'export PDF est géré par le lien href direct, pas besoin de JavaScript

