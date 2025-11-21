// ============================================
// INITIALISATION
// ============================================

function initCandidaturesLocations() {
    initFilters();
    initTableSorting();
    initBulkActions();
}

// ============================================
// VUES
// ============================================

function switchView(view) {
    const url = new URL(window.location);
    url.searchParams.set('view', view);
    url.searchParams.set('page', '1');
    window.location.href = url.toString();
}

// ============================================
// FILTRES
// ============================================

function toggleFilters() {
    const content = document.getElementById('filters-content');
    const toggleText = document.getElementById('filters-toggle-text');
    
    if (content.style.display === 'none') {
        content.style.display = 'block';
        toggleText.textContent = 'Masquer';
    } else {
        content.style.display = 'none';
        toggleText.textContent = 'Afficher';
    }
}

function resetFilters() {
    const form = document.getElementById('filters-form');
    form.reset();
    const url = new URL(window.location);
    url.searchParams.delete('search');
    url.searchParams.delete('statut');
    url.searchParams.delete('logement');
    url.searchParams.delete('candidat');
    url.searchParams.delete('date_debut');
    url.searchParams.delete('date_fin');
    url.searchParams.delete('proprietaire');
    url.searchParams.delete('ville');
    url.searchParams.set('page', '1');
    window.location.href = url.toString();
}

function filterByStatut(statut) {
    const url = new URL(window.location);
    if (statut) {
        url.searchParams.set('statut', statut);
    } else {
        url.searchParams.delete('statut');
    }
    url.searchParams.set('page', '1');
    window.location.href = url.toString();
}

function saveSearch() {
    const name = prompt('Nommer cette recherche :');
    if (name) {
        // TODO: Sauvegarder recherche dans localStorage ou backend
        const filters = new URLSearchParams(window.location.search);
        localStorage.setItem('saved_search_' + name, filters.toString());
        alert('Recherche sauvegardée !');
    }
}

// ============================================
// TABLE SORTING
// ============================================

function sortTable(column) {
    const url = new URL(window.location);
    const currentSort = url.searchParams.get('sort') || '-created_at';
    
    if (currentSort === column) {
        url.searchParams.set('sort', '-' + column);
    } else if (currentSort === '-' + column) {
        url.searchParams.set('sort', column);
    } else {
        url.searchParams.set('sort', '-' + column);
    }
    
    url.searchParams.set('page', '1');
    window.location.href = url.toString();
}

function initTableSorting() {
    // Ajouter event listeners pour colonnes triables
    document.querySelectorAll('.sortable').forEach(header => {
        header.style.cursor = 'pointer';
    });
}

// ============================================
// BULK ACTIONS
// ============================================

let selectedCandidatures = new Set();
let selectedLocations = new Set();

function toggleSelectAll(checkbox) {
    const checkboxes = document.querySelectorAll('.candidature-checkbox, .location-checkbox');
    checkboxes.forEach(cb => {
        cb.checked = checkbox.checked;
        if (checkbox.checked) {
            if (cb.classList.contains('candidature-checkbox')) {
                selectedCandidatures.add(cb.value);
            } else {
                selectedLocations.add(cb.value);
            }
        } else {
            if (cb.classList.contains('candidature-checkbox')) {
                selectedCandidatures.delete(cb.value);
            } else {
                selectedLocations.delete(cb.value);
            }
        }
    });
    updateBulkActions();
}

function updateBulkActions() {
    selectedCandidatures.clear();
    selectedLocations.clear();
    
    document.querySelectorAll('.candidature-checkbox:checked').forEach(cb => {
        selectedCandidatures.add(cb.value);
    });
    
    document.querySelectorAll('.location-checkbox:checked').forEach(cb => {
        selectedLocations.add(cb.value);
    });
    
    const totalSelected = selectedCandidatures.size + selectedLocations.size;
    const bulkBar = document.getElementById('bulk-actions-bar');
    const bulkCount = document.getElementById('bulk-count');
    
    if (totalSelected > 0) {
        bulkBar.style.display = 'flex';
        bulkCount.textContent = totalSelected;
    } else {
        bulkBar.style.display = 'none';
    }
}

function clearSelection() {
    document.querySelectorAll('.candidature-checkbox, .location-checkbox').forEach(cb => {
        cb.checked = false;
    });
    document.getElementById('select-all').checked = false;
    selectedCandidatures.clear();
    selectedLocations.clear();
    updateBulkActions();
}

function bulkChangeStatut() {
    const statut = prompt('Choisir statut :\n1. Accepter\n2. Refuser\n3. Mettre en attente');
    if (statut) {
        // TODO: Implémenter changement statut bulk
        console.log('Changer statut pour:', Array.from(selectedCandidatures));
    }
}

function bulkSendEmail() {
    alert('Envoi email groupe - À implémenter');
}

function bulkExport() {
    const ids = Array.from(selectedCandidatures.size > 0 ? selectedCandidatures : selectedLocations);
    const url = new URL(window.location);
    url.searchParams.set('export', 'csv');
    url.searchParams.set('ids', ids.join(','));
    window.location.href = url.toString();
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
    
    // Toggle celui-ci
    if (!isActive) {
        dropdown.classList.add('active');
    }
}

// Fermer dropdowns au clic extérieur
document.addEventListener('click', function(e) {
    if (!e.target.closest('.actions-dropdown')) {
        document.querySelectorAll('.actions-dropdown').forEach(d => {
            d.classList.remove('active');
        });
    }
});

// ============================================
// CANDIDATURES ACTIONS
// ============================================

let currentCandidatureId = null;

function openCandidatureDetail(candidatureId) {
    currentCandidatureId = candidatureId;
    const modal = document.getElementById('candidature-detail-modal');
    
    // Charger les données via AJAX
    fetch(`/connect-admin/candidatures/${candidatureId}/detail/`)
        .then(response => response.json())
        .then(data => {
            populateCandidatureDetail(data);
            modal.style.display = 'flex';
            document.body.style.overflow = 'hidden';
        })
        .catch(error => {
            console.error('Erreur chargement candidature:', error);
            // Fallback: charger depuis le tableau
            loadCandidatureFromTable(candidatureId);
            modal.style.display = 'flex';
            document.body.style.overflow = 'hidden';
        });
}

function loadCandidatureFromTable(candidatureId) {
    const row = document.querySelector(`tr[data-candidature-id="${candidatureId}"]`);
    if (!row) return;
    
    // Extraire les données de base
    const candidatName = row.querySelector('.candidat-name strong')?.textContent || '';
    const logementTitre = row.querySelector('.logement-link')?.textContent || '';
    const statut = row.querySelector('.statut-badge')?.textContent.trim() || '';
    
    // Populer le modal avec les données de base
    document.getElementById('modal-candidature-title').textContent = `Dossier - ${candidatName}`;
    document.getElementById('modal-nom').value = candidatName;
    document.getElementById('modal-logement-titre').textContent = logementTitre;
    
    const statutBadge = document.getElementById('modal-statut-badge');
    statutBadge.textContent = statut;
    statutBadge.className = 'statut-badge ' + row.querySelector('.statut-badge')?.className.split(' ').find(c => c.startsWith('statut-')) || '';
}

function populateCandidatureDetail(data) {
    // Titre
    document.getElementById('modal-candidature-title').textContent = `Dossier - ${data.candidat?.username || ''}`;
    
    // Informations candidat
    document.getElementById('modal-nom').value = data.candidat?.username || '';
    document.getElementById('modal-email').value = data.candidat?.email || '';
    document.getElementById('modal-telephone').value = data.candidat?.phone_number || '';
    
    // Logement
    document.getElementById('modal-logement-titre').textContent = data.logement?.titre || '';
    document.getElementById('modal-logement-adresse').textContent = data.logement?.adresse || '';
    document.getElementById('modal-logement-prix').textContent = data.logement?.prix ? data.logement.prix + ' €/mois' : '-';
    document.getElementById('modal-logement-surface').textContent = data.logement?.surface ? data.logement.surface + ' m²' : '-';
    document.getElementById('modal-logement-pieces').textContent = data.logement?.chambres ? data.logement.chambres + ' pièces' : '-';
    document.getElementById('modal-logement-link').href = `/connect-admin/logements/${data.logement?.id}/`;
    
    // Propriétaire
    if (data.proprietaire) {
        const propInfo = document.getElementById('modal-proprietaire-info');
        propInfo.innerHTML = `
            <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 12px;">
                <div style="width: 48px; height: 48px; border-radius: 50%; background: linear-gradient(135deg, #D3580B 0%, #c4510a 100%); color: white; display: flex; align-items: center; justify-content: center; font-weight: 700;">
                    ${data.proprietaire.username?.[0]?.toUpperCase() || 'U'}
                </div>
                <div>
                    <div style="font-weight: 600; color: #111827;">${data.proprietaire.username || ''}</div>
                    <div style="font-size: 13px; color: #6B7280;">${data.proprietaire.email || ''}</div>
                </div>
            </div>
            <a href="/connect-admin/users/${data.proprietaire.id}/" class="btn-secondary btn-small btn-full">Voir profil</a>
        `;
    }
    
    // Statut
    const statutBadge = document.getElementById('modal-statut-badge');
    statutBadge.textContent = data.statut_display || 'En attente';
    statutBadge.className = 'statut-badge statut-' + (data.statut || 'en_attente');
    
    // Dates
    document.getElementById('modal-date-soumission').textContent = data.date_creation || '-';
    document.getElementById('modal-date-modif').textContent = data.date_modification || '-';
    
    // Revenus et ratio
    if (data.revenus_mensuels && data.logement?.prix) {
        const ratio = (data.revenus_mensuels / data.logement.prix).toFixed(1);
        document.getElementById('modal-revenus').value = data.revenus_mensuels;
        const ratioDisplay = document.getElementById('modal-ratio');
        ratioDisplay.innerHTML = `
            <span class="ratio-value">${ratio}x</span>
            <span class="ratio-status ${ratio >= 3 ? 'ratio-ok' : ratio >= 2 ? 'ratio-warning' : 'ratio-danger'}">
                ${ratio >= 3 ? 'OK' : ratio >= 2 ? 'ATTENTION' : 'INSUFFISANT'}
            </span>
        `;
    }
    
    // Score global (calculé ou depuis données)
    const score = data.score || 75;
    updateScoreDisplay(score);
}

function updateScoreDisplay(score) {
    const scoreValue = document.getElementById('score-global-value');
    const scoreCircle = document.getElementById('score-global-circle');
    const recommendation = document.getElementById('score-recommendation');
    
    scoreValue.textContent = score;
    
    // Mettre à jour le cercle de score
    const percentage = (score / 100) * 360;
    scoreCircle.style.background = `conic-gradient(
        ${score >= 85 ? '#10B981' : score >= 70 ? '#F59E0B' : score >= 50 ? '#EF4444' : '#9CA3AF'} 0deg ${percentage}deg,
        #F3F4F6 ${percentage}deg 360deg
    )`;
    
    // Recommandation
    if (score >= 85) {
        recommendation.textContent = 'Recommandation : Accepter';
        recommendation.style.color = '#10B981';
    } else if (score >= 70) {
        recommendation.textContent = 'Recommandation : Accepter avec réserves';
        recommendation.style.color = '#F59E0B';
    } else if (score >= 50) {
        recommendation.textContent = 'Recommandation : Examiner attentivement';
        recommendation.style.color = '#EF4444';
    } else {
        recommendation.textContent = 'Recommandation : Refuser';
        recommendation.style.color = '#DC2626';
    }
}

function closeCandidatureDetailModal() {
    const modal = document.getElementById('candidature-detail-modal');
    modal.style.display = 'none';
    document.body.style.overflow = '';
    currentCandidatureId = null;
}

function switchModalTab(tabName) {
    // Désactiver tous les onglets
    document.querySelectorAll('.modal-tab').forEach(tab => {
        tab.classList.remove('active');
    });
    document.querySelectorAll('.modal-tab-content').forEach(content => {
        content.classList.remove('active');
    });
    
    // Activer l'onglet sélectionné
    const tab = document.querySelector(`.modal-tab[data-tab="${tabName}"]`);
    const content = document.getElementById(`tab-${tabName}`);
    if (tab && content) {
        tab.classList.add('active');
        content.classList.add('active');
    }
}

function acceptCandidatureFromModal() {
    if (currentCandidatureId) {
        openAcceptWorkflow(currentCandidatureId);
    } else {
        alert('Aucune candidature sélectionnée');
    }
}

function refuseCandidatureFromModal() {
    if (currentCandidatureId) {
        openRefuseWorkflow(currentCandidatureId);
    } else {
        alert('Aucune candidature sélectionnée');
    }
}

let currentWorkflowStep = 1;

function openAcceptWorkflow(candidatureId) {
    currentCandidatureId = candidatureId;
    currentWorkflowStep = 1;
    const modal = document.getElementById('accept-workflow-modal');
    
    // Charger les données de la candidature
    fetch(`/connect-admin/candidatures/${candidatureId}/detail/`)
        .then(response => response.json())
        .then(data => {
            document.getElementById('workflow-candidat-name').textContent = data.candidat?.username || '';
            document.getElementById('workflow-logement-titre').textContent = data.logement?.titre || '';
            document.getElementById('contrat-loyer').value = data.logement?.prix || '';
            document.getElementById('contrat-depot').value = (data.logement?.prix * 1.5) || ''; // 1.5 mois de loyer
        });
    
    updateWorkflowStep();
    modal.style.display = 'flex';
    document.body.style.overflow = 'hidden';
}

function closeAcceptWorkflow() {
    const modal = document.getElementById('accept-workflow-modal');
    modal.style.display = 'none';
    document.body.style.overflow = '';
    currentWorkflowStep = 1;
    updateWorkflowStep();
}

function workflowNext() {
    if (validateWorkflowStep(currentWorkflowStep)) {
        if (currentWorkflowStep < 4) {
            currentWorkflowStep++;
            updateWorkflowStep();
        }
    }
}

function workflowPrevious() {
    if (currentWorkflowStep > 1) {
        currentWorkflowStep--;
        updateWorkflowStep();
    }
}

function validateWorkflowStep(step) {
    if (step === 1) {
        const dossierVerifie = document.getElementById('confirm-dossier-verifie').checked;
        const proprietaireAccord = document.getElementById('confirm-proprietaire-accord').checked;
        if (!dossierVerifie || !proprietaireAccord) {
            alert('Veuillez confirmer toutes les conditions');
            return false;
        }
    } else if (step === 2) {
        const dateDebut = document.getElementById('contrat-date-debut').value;
        const duree = document.getElementById('contrat-duree').value;
        const loyer = document.getElementById('contrat-loyer').value;
        if (!dateDebut || !duree || !loyer) {
            alert('Veuillez remplir tous les champs obligatoires');
            return false;
        }
    }
    return true;
}

function updateWorkflowStep() {
    // Mettre à jour les steps visuels
    document.querySelectorAll('.workflow-step').forEach((step, index) => {
        if (index + 1 <= currentWorkflowStep) {
            step.classList.add('active');
        } else {
            step.classList.remove('active');
        }
    });
    
    // Afficher/masquer le contenu des étapes
    document.querySelectorAll('.workflow-step-content').forEach((content, index) => {
        if (index + 1 === currentWorkflowStep) {
            content.classList.add('active');
        } else {
            content.classList.remove('active');
        }
    });
}

function generateContrat() {
    // TODO: Générer contrat PDF côté serveur
    alert('Génération contrat - À implémenter');
    workflowNext();
}

function previewContrat() {
    alert('Prévisualisation contrat - À implémenter');
}

function sendContrat() {
    // TODO: Envoyer contrat pour signature
    alert('Envoi contrat - À implémenter');
    workflowNext();
}

function openRefuseWorkflow(candidatureId) {
    currentCandidatureId = candidatureId;
    const modal = document.getElementById('refuse-workflow-modal');
    
    // Générer message automatique
    fetch(`/connect-admin/candidatures/${candidatureId}/detail/`)
        .then(response => response.json())
        .then(data => {
            const message = `Bonjour ${data.candidat?.username || ''},\n\nNous vous informons que votre candidature pour le logement "${data.logement?.titre || ''}" n'a pas été retenue.\n\nNous vous remercions de votre intérêt et vous souhaitons bonne chance dans vos recherches.\n\nCordialement,\nL'équipe Transpareo`;
            document.getElementById('refuse-message').value = message;
        });
    
    modal.style.display = 'flex';
    document.body.style.overflow = 'hidden';
}

function closeRefuseWorkflow() {
    const modal = document.getElementById('refuse-workflow-modal');
    modal.style.display = 'none';
    document.body.style.overflow = '';
    document.getElementById('refuse-form').reset();
}

function toggleAutreRaison() {
    const raison = document.getElementById('refuse-raison').value;
    const autreField = document.getElementById('autre-raison-field');
    if (raison === 'autre') {
        autreField.style.display = 'block';
        document.getElementById('refuse-autre-detail').required = true;
    } else {
        autreField.style.display = 'none';
        document.getElementById('refuse-autre-detail').required = false;
    }
}

function submitRefuse(event) {
    event.preventDefault();
    
    const raison = document.getElementById('refuse-raison').value;
    const autreDetail = document.getElementById('refuse-autre-detail').value;
    const message = document.getElementById('refuse-message').value;
    const sendEmail = document.getElementById('refuse-send-email').checked;
    
    if (raison === 'autre' && !autreDetail.trim()) {
        alert('Veuillez préciser la raison');
        return;
    }
    
    fetch(`/connect-admin/candidatures/${currentCandidatureId}/refuse/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCsrfToken()
        },
        body: JSON.stringify({
            raison: raison === 'autre' ? autreDetail : raison,
            message: message,
            send_email: sendEmail
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('Candidature refusée avec succès');
            closeRefuseWorkflow();
            closeCandidatureDetailModal();
            window.location.reload();
        } else {
            alert('Erreur : ' + (data.error || 'Erreur inconnue'));
        }
    })
    .catch(error => {
        console.error('Erreur refus candidature:', error);
        alert('Erreur lors du refus de la candidature');
    });
}

function getCsrfToken() {
    return document.querySelector('[name=csrfmiddlewaretoken]')?.value || '';
}

function demanderInfos() {
    alert('Demander informations - À implémenter');
}

function addGarant() {
    alert('Ajouter garant - À implémenter');
}

function uploadDocuments() {
    alert('Upload documents - À implémenter');
}

function sendEmailCandidat() {
    alert('Envoyer email - À implémenter');
}

function sendSMSCandidat() {
    alert('Envoyer SMS - À implémenter');
}

function shareWithProprietaire() {
    alert('Partager avec propriétaire - À implémenter');
}

function saveNote() {
    const noteText = document.getElementById('note-input').value;
    if (!noteText.trim()) return;
    
    if (currentCandidatureId) {
        // TODO: Sauvegarder note via AJAX
        const notesList = document.getElementById('notes-list');
        const noteItem = document.createElement('div');
        noteItem.className = 'note-item';
        noteItem.innerHTML = `
            <div class="note-item-header">
                <span>${new Date().toLocaleDateString('fr-FR')}</span>
                <span>Admin</span>
            </div>
            <div class="note-item-text">${noteText}</div>
        `;
        
        if (notesList.querySelector('.no-data')) {
            notesList.innerHTML = '';
        }
        notesList.insertBefore(noteItem, notesList.firstChild);
        document.getElementById('note-input').value = '';
    }
}

// Fermer modals avec Escape
document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
        closeCandidatureDetailModal();
        closeLocationDetailModal();
        closeAcceptWorkflow();
        closeRefuseWorkflow();
    }
});

// Fermer modals au clic sur overlay
document.addEventListener('click', function(e) {
    if (e.target.classList.contains('modal-overlay')) {
        closeCandidatureDetailModal();
        closeLocationDetailModal();
        closeAcceptWorkflow();
        closeRefuseWorkflow();
    }
});

function acceptCandidature(candidatureId) {
    openCandidatureDetail(candidatureId);
    setTimeout(() => {
        acceptCandidatureFromModal();
    }, 500);
}

function refuseCandidature(candidatureId) {
    openCandidatureDetail(candidatureId);
    setTimeout(() => {
        refuseCandidatureFromModal();
    }, 500);
}

function downloadDossierPDF(candidatureId) {
    window.location.href = `/connect-admin/candidatures/${candidatureId}/pdf/`;
}

// ============================================
// LOCATIONS ACTIONS
// ============================================

let currentLocationId = null;

function openLocationDetail(locationId) {
    currentLocationId = locationId;
    const modal = document.getElementById('location-detail-modal');
    
    // Charger les données via AJAX ou depuis le tableau
    const row = document.querySelector(`tr[data-location-id="${locationId}"]`);
    if (row) {
        loadLocationFromTable(locationId);
    }
    
    modal.style.display = 'flex';
    document.body.style.overflow = 'hidden';
}

function loadLocationFromTable(locationId) {
    const row = document.querySelector(`tr[data-location-id="${locationId}"]`);
    if (!row) return;
    
    // Extraire les données de base
    const locataireName = row.querySelector('.candidat-name strong')?.textContent || '';
    const logementTitre = row.querySelector('.logement-link')?.textContent || '';
    const statut = row.querySelector('.statut-badge')?.textContent.trim() || '';
    
    document.getElementById('modal-location-title').textContent = `Location - ${locataireName}`;
    document.getElementById('location-statut-badge').textContent = statut;
    document.getElementById('location-statut-badge').className = 'statut-badge ' + row.querySelector('.statut-badge')?.className.split(' ').find(c => c.startsWith('statut-')) || '';
}

function closeLocationDetailModal() {
    const modal = document.getElementById('location-detail-modal');
    modal.style.display = 'none';
    document.body.style.overflow = '';
    currentLocationId = null;
}

function switchLocationTab(tabName) {
    document.querySelectorAll('#location-detail-modal .modal-tab').forEach(tab => {
        tab.classList.remove('active');
    });
    document.querySelectorAll('#location-detail-modal .modal-tab-content').forEach(content => {
        content.classList.remove('active');
    });
    
    const tab = document.querySelector(`#location-detail-modal .modal-tab[data-tab="${tabName}"]`);
    const content = document.getElementById(`location-tab-${tabName}`);
    if (tab && content) {
        tab.classList.add('active');
        content.classList.add('active');
    }
}

function enregistrerPaiement() {
    alert('Enregistrer paiement - À implémenter');
}

function creerIncident() {
    alert('Créer incident - À implémenter');
}

function viewPaiements(locationId) {
    alert('Historique paiements - À implémenter');
}

function generateQuittance(locationId) {
    const mois = prompt('Mois (format MM/YYYY) :');
    if (mois) {
        window.location.href = `/connect-admin/locations/${locationId}/quittance/?mois=${mois}`;
    }
}

function downloadContratPDF(locationId) {
    window.location.href = `/connect-admin/locations/${locationId}/contrat-pdf/`;
}

// ============================================
// UTILITAIRES
// ============================================

function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        // Afficher notification
        const notification = document.createElement('div');
        notification.textContent = 'ID copié : ' + text;
        notification.style.cssText = 'position: fixed; top: 20px; right: 20px; background: #10B981; color: white; padding: 12px 20px; border-radius: 8px; z-index: 10000;';
        document.body.appendChild(notification);
        setTimeout(() => notification.remove(), 2000);
    });
}

function changePerPage(value) {
    const url = new URL(window.location);
    url.searchParams.set('per_page', value);
    url.searchParams.set('page', '1');
    window.location.href = url.toString();
}

function exportRapport() {
    const url = new URL(window.location);
    url.searchParams.set('export', 'csv');
    window.location.href = url.toString();
}

function openStatsModal() {
    alert('Modal statistiques - À implémenter');
}

function openWorkflowSettings() {
    alert('Paramètres workflow - À implémenter');
}

function openColumnsModal() {
    alert('Configuration colonnes - À implémenter');
}

function switchToKanban() {
    alert('Vue Kanban - À implémenter');
}

// ============================================
// INIT FILTERS
// ============================================

function initFilters() {
    // Debounce pour recherche
    const searchInput = document.querySelector('input[name="search"]');
    if (searchInput) {
        let timeout;
        searchInput.addEventListener('input', function() {
            clearTimeout(timeout);
            timeout = setTimeout(() => {
                // Auto-submit après 500ms d'inactivité
                // document.getElementById('filters-form').submit();
            }, 500);
        });
    }
}


// ============================================

function initCandidaturesLocations() {
    initFilters();
    initTableSorting();
    initBulkActions();
}

// ============================================
// VUES
// ============================================

function switchView(view) {
    const url = new URL(window.location);
    url.searchParams.set('view', view);
    url.searchParams.set('page', '1');
    window.location.href = url.toString();
}

// ============================================
// FILTRES
// ============================================

function toggleFilters() {
    const content = document.getElementById('filters-content');
    const toggleText = document.getElementById('filters-toggle-text');
    
    if (content.style.display === 'none') {
        content.style.display = 'block';
        toggleText.textContent = 'Masquer';
    } else {
        content.style.display = 'none';
        toggleText.textContent = 'Afficher';
    }
}

function resetFilters() {
    const form = document.getElementById('filters-form');
    form.reset();
    const url = new URL(window.location);
    url.searchParams.delete('search');
    url.searchParams.delete('statut');
    url.searchParams.delete('logement');
    url.searchParams.delete('candidat');
    url.searchParams.delete('date_debut');
    url.searchParams.delete('date_fin');
    url.searchParams.delete('proprietaire');
    url.searchParams.delete('ville');
    url.searchParams.set('page', '1');
    window.location.href = url.toString();
}

function filterByStatut(statut) {
    const url = new URL(window.location);
    if (statut) {
        url.searchParams.set('statut', statut);
    } else {
        url.searchParams.delete('statut');
    }
    url.searchParams.set('page', '1');
    window.location.href = url.toString();
}

function saveSearch() {
    const name = prompt('Nommer cette recherche :');
    if (name) {
        // TODO: Sauvegarder recherche dans localStorage ou backend
        const filters = new URLSearchParams(window.location.search);
        localStorage.setItem('saved_search_' + name, filters.toString());
        alert('Recherche sauvegardée !');
    }
}

// ============================================
// TABLE SORTING
// ============================================

function sortTable(column) {
    const url = new URL(window.location);
    const currentSort = url.searchParams.get('sort') || '-created_at';
    
    if (currentSort === column) {
        url.searchParams.set('sort', '-' + column);
    } else if (currentSort === '-' + column) {
        url.searchParams.set('sort', column);
    } else {
        url.searchParams.set('sort', '-' + column);
    }
    
    url.searchParams.set('page', '1');
    window.location.href = url.toString();
}

function initTableSorting() {
    // Ajouter event listeners pour colonnes triables
    document.querySelectorAll('.sortable').forEach(header => {
        header.style.cursor = 'pointer';
    });
}

// ============================================
// BULK ACTIONS
// ============================================

let selectedCandidatures = new Set();
let selectedLocations = new Set();

function toggleSelectAll(checkbox) {
    const checkboxes = document.querySelectorAll('.candidature-checkbox, .location-checkbox');
    checkboxes.forEach(cb => {
        cb.checked = checkbox.checked;
        if (checkbox.checked) {
            if (cb.classList.contains('candidature-checkbox')) {
                selectedCandidatures.add(cb.value);
            } else {
                selectedLocations.add(cb.value);
            }
        } else {
            if (cb.classList.contains('candidature-checkbox')) {
                selectedCandidatures.delete(cb.value);
            } else {
                selectedLocations.delete(cb.value);
            }
        }
    });
    updateBulkActions();
}

function updateBulkActions() {
    selectedCandidatures.clear();
    selectedLocations.clear();
    
    document.querySelectorAll('.candidature-checkbox:checked').forEach(cb => {
        selectedCandidatures.add(cb.value);
    });
    
    document.querySelectorAll('.location-checkbox:checked').forEach(cb => {
        selectedLocations.add(cb.value);
    });
    
    const totalSelected = selectedCandidatures.size + selectedLocations.size;
    const bulkBar = document.getElementById('bulk-actions-bar');
    const bulkCount = document.getElementById('bulk-count');
    
    if (totalSelected > 0) {
        bulkBar.style.display = 'flex';
        bulkCount.textContent = totalSelected;
    } else {
        bulkBar.style.display = 'none';
    }
}

function clearSelection() {
    document.querySelectorAll('.candidature-checkbox, .location-checkbox').forEach(cb => {
        cb.checked = false;
    });
    document.getElementById('select-all').checked = false;
    selectedCandidatures.clear();
    selectedLocations.clear();
    updateBulkActions();
}

function bulkChangeStatut() {
    const statut = prompt('Choisir statut :\n1. Accepter\n2. Refuser\n3. Mettre en attente');
    if (statut) {
        // TODO: Implémenter changement statut bulk
        console.log('Changer statut pour:', Array.from(selectedCandidatures));
    }
}

function bulkSendEmail() {
    alert('Envoi email groupe - À implémenter');
}

function bulkExport() {
    const ids = Array.from(selectedCandidatures.size > 0 ? selectedCandidatures : selectedLocations);
    const url = new URL(window.location);
    url.searchParams.set('export', 'csv');
    url.searchParams.set('ids', ids.join(','));
    window.location.href = url.toString();
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
    
    // Toggle celui-ci
    if (!isActive) {
        dropdown.classList.add('active');
    }
}

// Fermer dropdowns au clic extérieur
document.addEventListener('click', function(e) {
    if (!e.target.closest('.actions-dropdown')) {
        document.querySelectorAll('.actions-dropdown').forEach(d => {
            d.classList.remove('active');
        });
    }
});

// ============================================
// CANDIDATURES ACTIONS
// ============================================

let currentCandidatureId = null;

function openCandidatureDetail(candidatureId) {
    currentCandidatureId = candidatureId;
    const modal = document.getElementById('candidature-detail-modal');
    
    // Charger les données via AJAX
    fetch(`/connect-admin/candidatures/${candidatureId}/detail/`)
        .then(response => response.json())
        .then(data => {
            populateCandidatureDetail(data);
            modal.style.display = 'flex';
            document.body.style.overflow = 'hidden';
        })
        .catch(error => {
            console.error('Erreur chargement candidature:', error);
            // Fallback: charger depuis le tableau
            loadCandidatureFromTable(candidatureId);
            modal.style.display = 'flex';
            document.body.style.overflow = 'hidden';
        });
}

function loadCandidatureFromTable(candidatureId) {
    const row = document.querySelector(`tr[data-candidature-id="${candidatureId}"]`);
    if (!row) return;
    
    // Extraire les données de base
    const candidatName = row.querySelector('.candidat-name strong')?.textContent || '';
    const logementTitre = row.querySelector('.logement-link')?.textContent || '';
    const statut = row.querySelector('.statut-badge')?.textContent.trim() || '';
    
    // Populer le modal avec les données de base
    document.getElementById('modal-candidature-title').textContent = `Dossier - ${candidatName}`;
    document.getElementById('modal-nom').value = candidatName;
    document.getElementById('modal-logement-titre').textContent = logementTitre;
    
    const statutBadge = document.getElementById('modal-statut-badge');
    statutBadge.textContent = statut;
    statutBadge.className = 'statut-badge ' + row.querySelector('.statut-badge')?.className.split(' ').find(c => c.startsWith('statut-')) || '';
}

function populateCandidatureDetail(data) {
    // Titre
    document.getElementById('modal-candidature-title').textContent = `Dossier - ${data.candidat?.username || ''}`;
    
    // Informations candidat
    document.getElementById('modal-nom').value = data.candidat?.username || '';
    document.getElementById('modal-email').value = data.candidat?.email || '';
    document.getElementById('modal-telephone').value = data.candidat?.phone_number || '';
    
    // Logement
    document.getElementById('modal-logement-titre').textContent = data.logement?.titre || '';
    document.getElementById('modal-logement-adresse').textContent = data.logement?.adresse || '';
    document.getElementById('modal-logement-prix').textContent = data.logement?.prix ? data.logement.prix + ' €/mois' : '-';
    document.getElementById('modal-logement-surface').textContent = data.logement?.surface ? data.logement.surface + ' m²' : '-';
    document.getElementById('modal-logement-pieces').textContent = data.logement?.chambres ? data.logement.chambres + ' pièces' : '-';
    document.getElementById('modal-logement-link').href = `/connect-admin/logements/${data.logement?.id}/`;
    
    // Propriétaire
    if (data.proprietaire) {
        const propInfo = document.getElementById('modal-proprietaire-info');
        propInfo.innerHTML = `
            <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 12px;">
                <div style="width: 48px; height: 48px; border-radius: 50%; background: linear-gradient(135deg, #D3580B 0%, #c4510a 100%); color: white; display: flex; align-items: center; justify-content: center; font-weight: 700;">
                    ${data.proprietaire.username?.[0]?.toUpperCase() || 'U'}
                </div>
                <div>
                    <div style="font-weight: 600; color: #111827;">${data.proprietaire.username || ''}</div>
                    <div style="font-size: 13px; color: #6B7280;">${data.proprietaire.email || ''}</div>
                </div>
            </div>
            <a href="/connect-admin/users/${data.proprietaire.id}/" class="btn-secondary btn-small btn-full">Voir profil</a>
        `;
    }
    
    // Statut
    const statutBadge = document.getElementById('modal-statut-badge');
    statutBadge.textContent = data.statut_display || 'En attente';
    statutBadge.className = 'statut-badge statut-' + (data.statut || 'en_attente');
    
    // Dates
    document.getElementById('modal-date-soumission').textContent = data.date_creation || '-';
    document.getElementById('modal-date-modif').textContent = data.date_modification || '-';
    
    // Revenus et ratio
    if (data.revenus_mensuels && data.logement?.prix) {
        const ratio = (data.revenus_mensuels / data.logement.prix).toFixed(1);
        document.getElementById('modal-revenus').value = data.revenus_mensuels;
        const ratioDisplay = document.getElementById('modal-ratio');
        ratioDisplay.innerHTML = `
            <span class="ratio-value">${ratio}x</span>
            <span class="ratio-status ${ratio >= 3 ? 'ratio-ok' : ratio >= 2 ? 'ratio-warning' : 'ratio-danger'}">
                ${ratio >= 3 ? 'OK' : ratio >= 2 ? 'ATTENTION' : 'INSUFFISANT'}
            </span>
        `;
    }
    
    // Score global (calculé ou depuis données)
    const score = data.score || 75;
    updateScoreDisplay(score);
}

function updateScoreDisplay(score) {
    const scoreValue = document.getElementById('score-global-value');
    const scoreCircle = document.getElementById('score-global-circle');
    const recommendation = document.getElementById('score-recommendation');
    
    scoreValue.textContent = score;
    
    // Mettre à jour le cercle de score
    const percentage = (score / 100) * 360;
    scoreCircle.style.background = `conic-gradient(
        ${score >= 85 ? '#10B981' : score >= 70 ? '#F59E0B' : score >= 50 ? '#EF4444' : '#9CA3AF'} 0deg ${percentage}deg,
        #F3F4F6 ${percentage}deg 360deg
    )`;
    
    // Recommandation
    if (score >= 85) {
        recommendation.textContent = 'Recommandation : Accepter';
        recommendation.style.color = '#10B981';
    } else if (score >= 70) {
        recommendation.textContent = 'Recommandation : Accepter avec réserves';
        recommendation.style.color = '#F59E0B';
    } else if (score >= 50) {
        recommendation.textContent = 'Recommandation : Examiner attentivement';
        recommendation.style.color = '#EF4444';
    } else {
        recommendation.textContent = 'Recommandation : Refuser';
        recommendation.style.color = '#DC2626';
    }
}

function closeCandidatureDetailModal() {
    const modal = document.getElementById('candidature-detail-modal');
    modal.style.display = 'none';
    document.body.style.overflow = '';
    currentCandidatureId = null;
}

function switchModalTab(tabName) {
    // Désactiver tous les onglets
    document.querySelectorAll('.modal-tab').forEach(tab => {
        tab.classList.remove('active');
    });
    document.querySelectorAll('.modal-tab-content').forEach(content => {
        content.classList.remove('active');
    });
    
    // Activer l'onglet sélectionné
    const tab = document.querySelector(`.modal-tab[data-tab="${tabName}"]`);
    const content = document.getElementById(`tab-${tabName}`);
    if (tab && content) {
        tab.classList.add('active');
        content.classList.add('active');
    }
}

function acceptCandidatureFromModal() {
    if (currentCandidatureId) {
        openAcceptWorkflow(currentCandidatureId);
    } else {
        alert('Aucune candidature sélectionnée');
    }
}

function refuseCandidatureFromModal() {
    if (currentCandidatureId) {
        openRefuseWorkflow(currentCandidatureId);
    } else {
        alert('Aucune candidature sélectionnée');
    }
}

let currentWorkflowStep = 1;

function openAcceptWorkflow(candidatureId) {
    currentCandidatureId = candidatureId;
    currentWorkflowStep = 1;
    const modal = document.getElementById('accept-workflow-modal');
    
    // Charger les données de la candidature
    fetch(`/connect-admin/candidatures/${candidatureId}/detail/`)
        .then(response => response.json())
        .then(data => {
            document.getElementById('workflow-candidat-name').textContent = data.candidat?.username || '';
            document.getElementById('workflow-logement-titre').textContent = data.logement?.titre || '';
            document.getElementById('contrat-loyer').value = data.logement?.prix || '';
            document.getElementById('contrat-depot').value = (data.logement?.prix * 1.5) || ''; // 1.5 mois de loyer
        });
    
    updateWorkflowStep();
    modal.style.display = 'flex';
    document.body.style.overflow = 'hidden';
}

function closeAcceptWorkflow() {
    const modal = document.getElementById('accept-workflow-modal');
    modal.style.display = 'none';
    document.body.style.overflow = '';
    currentWorkflowStep = 1;
    updateWorkflowStep();
}

function workflowNext() {
    if (validateWorkflowStep(currentWorkflowStep)) {
        if (currentWorkflowStep < 4) {
            currentWorkflowStep++;
            updateWorkflowStep();
        }
    }
}

function workflowPrevious() {
    if (currentWorkflowStep > 1) {
        currentWorkflowStep--;
        updateWorkflowStep();
    }
}

function validateWorkflowStep(step) {
    if (step === 1) {
        const dossierVerifie = document.getElementById('confirm-dossier-verifie').checked;
        const proprietaireAccord = document.getElementById('confirm-proprietaire-accord').checked;
        if (!dossierVerifie || !proprietaireAccord) {
            alert('Veuillez confirmer toutes les conditions');
            return false;
        }
    } else if (step === 2) {
        const dateDebut = document.getElementById('contrat-date-debut').value;
        const duree = document.getElementById('contrat-duree').value;
        const loyer = document.getElementById('contrat-loyer').value;
        if (!dateDebut || !duree || !loyer) {
            alert('Veuillez remplir tous les champs obligatoires');
            return false;
        }
    }
    return true;
}

function updateWorkflowStep() {
    // Mettre à jour les steps visuels
    document.querySelectorAll('.workflow-step').forEach((step, index) => {
        if (index + 1 <= currentWorkflowStep) {
            step.classList.add('active');
        } else {
            step.classList.remove('active');
        }
    });
    
    // Afficher/masquer le contenu des étapes
    document.querySelectorAll('.workflow-step-content').forEach((content, index) => {
        if (index + 1 === currentWorkflowStep) {
            content.classList.add('active');
        } else {
            content.classList.remove('active');
        }
    });
}

function generateContrat() {
    // TODO: Générer contrat PDF côté serveur
    alert('Génération contrat - À implémenter');
    workflowNext();
}

function previewContrat() {
    alert('Prévisualisation contrat - À implémenter');
}

function sendContrat() {
    // TODO: Envoyer contrat pour signature
    alert('Envoi contrat - À implémenter');
    workflowNext();
}

function openRefuseWorkflow(candidatureId) {
    currentCandidatureId = candidatureId;
    const modal = document.getElementById('refuse-workflow-modal');
    
    // Générer message automatique
    fetch(`/connect-admin/candidatures/${candidatureId}/detail/`)
        .then(response => response.json())
        .then(data => {
            const message = `Bonjour ${data.candidat?.username || ''},\n\nNous vous informons que votre candidature pour le logement "${data.logement?.titre || ''}" n'a pas été retenue.\n\nNous vous remercions de votre intérêt et vous souhaitons bonne chance dans vos recherches.\n\nCordialement,\nL'équipe Transpareo`;
            document.getElementById('refuse-message').value = message;
        });
    
    modal.style.display = 'flex';
    document.body.style.overflow = 'hidden';
}

function closeRefuseWorkflow() {
    const modal = document.getElementById('refuse-workflow-modal');
    modal.style.display = 'none';
    document.body.style.overflow = '';
    document.getElementById('refuse-form').reset();
}

function toggleAutreRaison() {
    const raison = document.getElementById('refuse-raison').value;
    const autreField = document.getElementById('autre-raison-field');
    if (raison === 'autre') {
        autreField.style.display = 'block';
        document.getElementById('refuse-autre-detail').required = true;
    } else {
        autreField.style.display = 'none';
        document.getElementById('refuse-autre-detail').required = false;
    }
}

function submitRefuse(event) {
    event.preventDefault();
    
    const raison = document.getElementById('refuse-raison').value;
    const autreDetail = document.getElementById('refuse-autre-detail').value;
    const message = document.getElementById('refuse-message').value;
    const sendEmail = document.getElementById('refuse-send-email').checked;
    
    if (raison === 'autre' && !autreDetail.trim()) {
        alert('Veuillez préciser la raison');
        return;
    }
    
    fetch(`/connect-admin/candidatures/${currentCandidatureId}/refuse/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCsrfToken()
        },
        body: JSON.stringify({
            raison: raison === 'autre' ? autreDetail : raison,
            message: message,
            send_email: sendEmail
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('Candidature refusée avec succès');
            closeRefuseWorkflow();
            closeCandidatureDetailModal();
            window.location.reload();
        } else {
            alert('Erreur : ' + (data.error || 'Erreur inconnue'));
        }
    })
    .catch(error => {
        console.error('Erreur refus candidature:', error);
        alert('Erreur lors du refus de la candidature');
    });
}

function getCsrfToken() {
    return document.querySelector('[name=csrfmiddlewaretoken]')?.value || '';
}

function demanderInfos() {
    alert('Demander informations - À implémenter');
}

function addGarant() {
    alert('Ajouter garant - À implémenter');
}

function uploadDocuments() {
    alert('Upload documents - À implémenter');
}

function sendEmailCandidat() {
    alert('Envoyer email - À implémenter');
}

function sendSMSCandidat() {
    alert('Envoyer SMS - À implémenter');
}

function shareWithProprietaire() {
    alert('Partager avec propriétaire - À implémenter');
}

function saveNote() {
    const noteText = document.getElementById('note-input').value;
    if (!noteText.trim()) return;
    
    if (currentCandidatureId) {
        // TODO: Sauvegarder note via AJAX
        const notesList = document.getElementById('notes-list');
        const noteItem = document.createElement('div');
        noteItem.className = 'note-item';
        noteItem.innerHTML = `
            <div class="note-item-header">
                <span>${new Date().toLocaleDateString('fr-FR')}</span>
                <span>Admin</span>
            </div>
            <div class="note-item-text">${noteText}</div>
        `;
        
        if (notesList.querySelector('.no-data')) {
            notesList.innerHTML = '';
        }
        notesList.insertBefore(noteItem, notesList.firstChild);
        document.getElementById('note-input').value = '';
    }
}

// Fermer modals avec Escape
document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
        closeCandidatureDetailModal();
        closeLocationDetailModal();
        closeAcceptWorkflow();
        closeRefuseWorkflow();
    }
});

// Fermer modals au clic sur overlay
document.addEventListener('click', function(e) {
    if (e.target.classList.contains('modal-overlay')) {
        closeCandidatureDetailModal();
        closeLocationDetailModal();
        closeAcceptWorkflow();
        closeRefuseWorkflow();
    }
});

function acceptCandidature(candidatureId) {
    openCandidatureDetail(candidatureId);
    setTimeout(() => {
        acceptCandidatureFromModal();
    }, 500);
}

function refuseCandidature(candidatureId) {
    openCandidatureDetail(candidatureId);
    setTimeout(() => {
        refuseCandidatureFromModal();
    }, 500);
}

function downloadDossierPDF(candidatureId) {
    window.location.href = `/connect-admin/candidatures/${candidatureId}/pdf/`;
}

// ============================================
// LOCATIONS ACTIONS
// ============================================

let currentLocationId = null;

function openLocationDetail(locationId) {
    currentLocationId = locationId;
    const modal = document.getElementById('location-detail-modal');
    
    // Charger les données via AJAX ou depuis le tableau
    const row = document.querySelector(`tr[data-location-id="${locationId}"]`);
    if (row) {
        loadLocationFromTable(locationId);
    }
    
    modal.style.display = 'flex';
    document.body.style.overflow = 'hidden';
}

function loadLocationFromTable(locationId) {
    const row = document.querySelector(`tr[data-location-id="${locationId}"]`);
    if (!row) return;
    
    // Extraire les données de base
    const locataireName = row.querySelector('.candidat-name strong')?.textContent || '';
    const logementTitre = row.querySelector('.logement-link')?.textContent || '';
    const statut = row.querySelector('.statut-badge')?.textContent.trim() || '';
    
    document.getElementById('modal-location-title').textContent = `Location - ${locataireName}`;
    document.getElementById('location-statut-badge').textContent = statut;
    document.getElementById('location-statut-badge').className = 'statut-badge ' + row.querySelector('.statut-badge')?.className.split(' ').find(c => c.startsWith('statut-')) || '';
}

function closeLocationDetailModal() {
    const modal = document.getElementById('location-detail-modal');
    modal.style.display = 'none';
    document.body.style.overflow = '';
    currentLocationId = null;
}

function switchLocationTab(tabName) {
    document.querySelectorAll('#location-detail-modal .modal-tab').forEach(tab => {
        tab.classList.remove('active');
    });
    document.querySelectorAll('#location-detail-modal .modal-tab-content').forEach(content => {
        content.classList.remove('active');
    });
    
    const tab = document.querySelector(`#location-detail-modal .modal-tab[data-tab="${tabName}"]`);
    const content = document.getElementById(`location-tab-${tabName}`);
    if (tab && content) {
        tab.classList.add('active');
        content.classList.add('active');
    }
}

function enregistrerPaiement() {
    alert('Enregistrer paiement - À implémenter');
}

function creerIncident() {
    alert('Créer incident - À implémenter');
}

function viewPaiements(locationId) {
    alert('Historique paiements - À implémenter');
}

function generateQuittance(locationId) {
    const mois = prompt('Mois (format MM/YYYY) :');
    if (mois) {
        window.location.href = `/connect-admin/locations/${locationId}/quittance/?mois=${mois}`;
    }
}

function downloadContratPDF(locationId) {
    window.location.href = `/connect-admin/locations/${locationId}/contrat-pdf/`;
}

// ============================================
// UTILITAIRES
// ============================================

function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        // Afficher notification
        const notification = document.createElement('div');
        notification.textContent = 'ID copié : ' + text;
        notification.style.cssText = 'position: fixed; top: 20px; right: 20px; background: #10B981; color: white; padding: 12px 20px; border-radius: 8px; z-index: 10000;';
        document.body.appendChild(notification);
        setTimeout(() => notification.remove(), 2000);
    });
}

function changePerPage(value) {
    const url = new URL(window.location);
    url.searchParams.set('per_page', value);
    url.searchParams.set('page', '1');
    window.location.href = url.toString();
}

function exportRapport() {
    const url = new URL(window.location);
    url.searchParams.set('export', 'csv');
    window.location.href = url.toString();
}

function openStatsModal() {
    alert('Modal statistiques - À implémenter');
}

function openWorkflowSettings() {
    alert('Paramètres workflow - À implémenter');
}

function openColumnsModal() {
    alert('Configuration colonnes - À implémenter');
}

function switchToKanban() {
    alert('Vue Kanban - À implémenter');
}

// ============================================
// INIT FILTERS
// ============================================

function initFilters() {
    // Debounce pour recherche
    const searchInput = document.querySelector('input[name="search"]');
    if (searchInput) {
        let timeout;
        searchInput.addEventListener('input', function() {
            clearTimeout(timeout);
            timeout = setTimeout(() => {
                // Auto-submit après 500ms d'inactivité
                // document.getElementById('filters-form').submit();
            }, 500);
        });
    }
}

