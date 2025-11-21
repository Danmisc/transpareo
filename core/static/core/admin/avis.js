// ============================================
// INITIALISATION
// ============================================

function initAvisPage() {
    initFilters();
    initTableSorting();
    initBulkActions();
    initDropdowns();
    initSearchDebounce();
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
    
    if (content) {
        if (content.style.display === 'none') {
            content.style.display = 'block';
            if (toggleText) toggleText.textContent = 'Masquer';
        } else {
            content.style.display = 'none';
            if (toggleText) toggleText.textContent = 'Afficher';
        }
    }
}

function resetFilters() {
    const url = new URL(window.location);
    url.searchParams.delete('search');
    url.searchParams.delete('note');
    url.searchParams.delete('statut');
    url.searchParams.delete('logement');
    url.searchParams.delete('auteur');
    url.searchParams.delete('date_debut');
    url.searchParams.delete('date_fin');
    url.searchParams.delete('ville');
    url.searchParams.set('page', '1');
    window.location.href = url.toString();
}

function filterByCategory(category) {
    const url = new URL(window.location);
    
    if (category === 'recents') {
        const date = new Date();
        date.setDate(date.getDate() - 7);
        url.searchParams.set('date_debut', date.toISOString().split('T')[0]);
    } else if (category === 'bien_notes') {
        url.searchParams.set('note', '4');
        url.searchParams.append('note', '5');
    } else if (category === 'mal_notes') {
        url.searchParams.set('note', '1');
        url.searchParams.append('note', '2');
    } else {
        url.searchParams.delete('date_debut');
        url.searchParams.delete('note');
    }
    
    url.searchParams.set('page', '1');
    window.location.href = url.toString();
}

function saveSearch() {
    const name = prompt('Nommer cette recherche :');
    if (name) {
        const filters = new URLSearchParams(window.location.search);
        localStorage.setItem('saved_search_avis_' + name, filters.toString());
        alert('Recherche sauvegardée !');
    }
}

function initSearchDebounce() {
    const searchInput = document.querySelector('input[name="search"]');
    if (searchInput) {
        let timeout;
        searchInput.addEventListener('input', function() {
            clearTimeout(timeout);
            timeout = setTimeout(() => {
                // Auto-submit après 300ms d'inactivité
                const form = searchInput.closest('form');
                if (form) {
                    form.submit();
                }
            }, 300);
        });
    }
}

function initFilters() {
    // Initialiser multi-selects
    document.querySelectorAll('.multi-select').forEach(select => {
        // TODO: Implémenter multi-select custom si nécessaire
    });
}

// ============================================
// TABLE SORTING
// ============================================

function sortTable(column) {
    const url = new URL(window.location);
    const currentSort = url.searchParams.get('sort') || '-date_avis';
    
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
    document.querySelectorAll('.sortable').forEach(header => {
        header.style.cursor = 'pointer';
    });
}

// ============================================
// BULK ACTIONS
// ============================================

function toggleSelectAll(checkbox) {
    const checkboxes = document.querySelectorAll('.avis-checkbox');
    checkboxes.forEach(cb => {
        cb.checked = checkbox.checked;
    });
    updateBulkActions();
}

function updateBulkActions() {
    const checked = document.querySelectorAll('.avis-checkbox:checked');
    const bulkBar = document.getElementById('bulk-actions-bar');
    const bulkCount = document.getElementById('bulk-count');
    
    if (checked.length > 0) {
        if (bulkBar) bulkBar.style.display = 'flex';
        if (bulkCount) bulkCount.textContent = checked.length;
    } else {
        if (bulkBar) bulkBar.style.display = 'none';
    }
}

function clearSelection() {
    document.querySelectorAll('.avis-checkbox').forEach(cb => {
        cb.checked = false;
    });
    const selectAll = document.getElementById('select-all');
    if (selectAll) selectAll.checked = false;
    updateBulkActions();
}

function bulkPublier() {
    const checked = Array.from(document.querySelectorAll('.avis-checkbox:checked')).map(cb => cb.value);
    if (checked.length === 0) {
        alert('Aucun avis sélectionné');
        return;
    }
    
    if (confirm(`Publier ${checked.length} avis ?`)) {
        // TODO: Appel API
        console.log('Publier avis:', checked);
        alert('Avis publiés avec succès');
        location.reload();
    }
}

function bulkMasquer() {
    const checked = Array.from(document.querySelectorAll('.avis-checkbox:checked')).map(cb => cb.value);
    if (checked.length === 0) {
        alert('Aucun avis sélectionné');
        return;
    }
    
    if (confirm(`Masquer ${checked.length} avis ?`)) {
        // TODO: Appel API
        console.log('Masquer avis:', checked);
        alert('Avis masqués avec succès');
        location.reload();
    }
}

function bulkMarquerSpam() {
    const checked = Array.from(document.querySelectorAll('.avis-checkbox:checked')).map(cb => cb.value);
    if (checked.length === 0) {
        alert('Aucun avis sélectionné');
        return;
    }
    
    if (confirm(`Marquer ${checked.length} avis comme spam ?`)) {
        // TODO: Appel API
        console.log('Marquer spam avis:', checked);
        alert('Avis marqués comme spam');
        location.reload();
    }
}

function bulkExport() {
    const checked = Array.from(document.querySelectorAll('.avis-checkbox:checked')).map(cb => cb.value);
    if (checked.length === 0) {
        alert('Aucun avis sélectionné');
        return;
    }
    
    // TODO: Export CSV avec IDs sélectionnés
    const url = new URL(window.location);
    url.searchParams.set('export', 'csv');
    url.searchParams.set('ids', checked.join(','));
    window.location.href = url.toString();
}

function bulkApprouver() {
    bulkPublier();
}

function bulkRejeter() {
    const checked = Array.from(document.querySelectorAll('.avis-checkbox:checked')).map(cb => cb.value);
    if (checked.length === 0) {
        alert('Aucun avis sélectionné');
        return;
    }
    
    if (confirm(`Rejeter ${checked.length} avis ?`)) {
        // TODO: Appel API
        console.log('Rejeter avis:', checked);
        alert('Avis rejetés avec succès');
        location.reload();
    }
}

// ============================================
// DROPDOWNS
// ============================================

function toggleActionsDropdown(button) {
    const menu = button.nextElementSibling;
    if (menu) {
        // Fermer tous les autres menus
        document.querySelectorAll('.dropdown-menu').forEach(m => {
            if (m !== menu) m.classList.remove('show');
        });
        menu.classList.toggle('show');
    }
}

function initDropdowns() {
    // Fermer dropdowns au click extérieur
    document.addEventListener('click', function(e) {
        if (!e.target.closest('.actions-dropdown')) {
            document.querySelectorAll('.dropdown-menu').forEach(menu => {
                menu.classList.remove('show');
            });
        }
    });
}

// ============================================
// MODAL DÉTAIL AVIS
// ============================================

function openAvisDetail(avisId) {
    const modal = document.getElementById('avis-detail-modal');
    if (!modal) return;
    
    // Charger données avis via AJAX
    fetch(`/connect-admin/avis/${avisId}/detail/`)
        .then(response => response.json())
        .then(data => {
            populateAvisDetail(data);
            modal.style.display = 'flex';
        })
        .catch(error => {
            console.error('Erreur chargement avis:', error);
            alert('Erreur lors du chargement de l\'avis');
        });
}

function populateAvisDetail(data) {
    // Header
    document.getElementById('modal-avis-auteur').textContent = data.auteur.username;
    document.getElementById('modal-avis-date').textContent = data.date_publication;
    document.getElementById('modal-avis-statut').textContent = data.statut_display;
    
    // Avatar
    if (data.auteur.avatar_url) {
        document.getElementById('modal-avis-avatar').src = data.auteur.avatar_url;
        document.getElementById('widget-auteur-avatar').src = data.auteur.avatar_url;
    }
    
    // Note
    const noteDisplay = document.getElementById('modal-avis-note');
    noteDisplay.innerHTML = '';
    for (let i = 1; i <= 5; i++) {
        const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
        svg.setAttribute('width', '32');
        svg.setAttribute('height', '32');
        svg.setAttribute('viewBox', '0 0 24 24');
        svg.setAttribute('fill', i <= data.note ? 'currentColor' : 'none');
        svg.setAttribute('stroke', 'currentColor');
        svg.setAttribute('stroke-width', '2');
        svg.style.color = '#F59E0B';
        const polygon = document.createElementNS('http://www.w3.org/2000/svg', 'polygon');
        polygon.setAttribute('points', '12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2');
        svg.appendChild(polygon);
        noteDisplay.appendChild(svg);
    }
    const span = document.createElement('span');
    span.textContent = `${data.note}/5`;
    span.style.marginLeft = '8px';
    span.style.fontSize = '20px';
    span.style.fontWeight = '700';
    noteDisplay.appendChild(span);
    
    // Notes détaillées
    if (data.note_proprete) {
        createNoteGauge('note-proprete', data.note_proprete, 'Propreté');
    }
    if (data.note_localisation) {
        createNoteGauge('note-emplacement', data.note_localisation, 'Emplacement');
    }
    if (data.note_equipements) {
        createNoteGauge('note-qualite-prix', data.note_equipements, 'Équipements');
    }
    if (data.note_bailleur) {
        createNoteGauge('note-communication', data.note_bailleur, 'Communication');
    }
    
    // Titre et contenu
    document.getElementById('modal-avis-titre').textContent = data.titre || 'Avis';
    document.getElementById('modal-avis-contenu').textContent = data.commentaire;
    
    // Widget auteur
    document.getElementById('widget-auteur-nom').textContent = data.auteur.username;
    document.getElementById('widget-auteur-email').textContent = data.auteur.email || '-';
    
    // Widget logement
    document.getElementById('widget-logement-adresse').textContent = data.logement.adresse;
    document.getElementById('widget-logement-prix').textContent = `${data.logement.prix}€/mois`;
    
    // Statut
    document.getElementById('widget-statut').textContent = data.statut_display;
    document.getElementById('widget-date-pub').textContent = data.date_publication;
}

function createNoteGauge(id, note, label) {
    const container = document.getElementById(id);
    if (!container) return;
    
    container.innerHTML = '';
    const gauge = document.createElement('div');
    gauge.className = 'note-gauge';
    
    // Étoiles
    for (let i = 1; i <= 5; i++) {
        const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
        svg.setAttribute('width', '16');
        svg.setAttribute('height', '16');
        svg.setAttribute('viewBox', '0 0 24 24');
        svg.setAttribute('fill', i <= note ? 'currentColor' : 'none');
        svg.setAttribute('stroke', 'currentColor');
        svg.setAttribute('stroke-width', '2');
        svg.style.color = i <= note ? '#F59E0B' : '#E5E7EB';
        const polygon = document.createElementNS('http://www.w3.org/2000/svg', 'polygon');
        polygon.setAttribute('points', '12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2');
        svg.appendChild(polygon);
        gauge.appendChild(svg);
    }
    
    const span = document.createElement('span');
    span.textContent = `${note}/5`;
    span.style.marginLeft = '8px';
    span.style.fontSize = '14px';
    span.style.fontWeight = '600';
    gauge.appendChild(span);
    
    container.appendChild(gauge);
}

function closeAvisDetailModal() {
    const modal = document.getElementById('avis-detail-modal');
    if (modal) modal.style.display = 'none';
}

// Fermer modal avec Escape
document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
        closeAvisDetailModal();
    }
});

// Fermer modal au click sur overlay
document.addEventListener('click', function(e) {
    const modal = document.getElementById('avis-detail-modal');
    if (modal && e.target === modal) {
        closeAvisDetailModal();
    }
});

// ============================================
// ACTIONS AVIS
// ============================================

function approuverAvis(avisId) {
    if (confirm('Approuver et publier cet avis ?')) {
        // TODO: Appel API
        fetch(`/connect-admin/avis/${avisId}/approuver/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCsrfToken(),
                'Content-Type': 'application/json'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('Avis approuvé avec succès');
                location.reload();
            } else {
                alert('Erreur : ' + (data.error || 'Erreur inconnue'));
            }
        })
        .catch(error => {
            console.error('Erreur:', error);
            alert('Erreur lors de l\'approbation');
        });
    }
}

function rejeterAvis(avisId) {
    const raison = prompt('Raison du rejet :');
    if (raison) {
        // TODO: Appel API
        console.log('Rejeter avis:', avisId, raison);
        alert('Avis rejeté');
        location.reload();
    }
}

function masquerAvis(avisId) {
    if (confirm('Masquer cet avis ? Il ne sera plus visible publiquement.')) {
        // TODO: Appel API
        console.log('Masquer avis:', avisId);
        alert('Avis masqué');
        location.reload();
    }
}

function supprimerAvis(avisId) {
    const raison = prompt('Raison de la suppression (obligatoire) :');
    if (raison) {
        if (confirm('Êtes-vous sûr de vouloir supprimer définitivement cet avis ?')) {
            // TODO: Appel API
            console.log('Supprimer avis:', avisId, raison);
            alert('Avis supprimé');
            location.reload();
        }
    }
}

function approuverAvisFromModal() {
    const avisId = getCurrentAvisId();
    if (avisId) approuverAvis(avisId);
}

function masquerAvisFromModal() {
    const avisId = getCurrentAvisId();
    if (avisId) masquerAvis(avisId);
}

function supprimerAvisFromModal() {
    const avisId = getCurrentAvisId();
    if (avisId) supprimerAvis(avisId);
}

function getCurrentAvisId() {
    // Récupérer l'ID depuis le modal ou le contexte
    const modal = document.getElementById('avis-detail-modal');
    if (modal) {
        return modal.dataset.avisId;
    }
    return null;
}

function epinglerAvis() {
    const avisId = getCurrentAvisId();
    if (avisId) {
        // TODO: Appel API
        console.log('Épingler avis:', avisId);
        alert('Avis épinglé');
    }
}

function partagerAvis() {
    const avisId = getCurrentAvisId();
    if (avisId) {
        const url = window.location.origin + '/avis/' + avisId + '/';
        navigator.clipboard.writeText(url).then(() => {
            alert('Lien copié dans le presse-papiers');
        });
    }
}

function telechargerPDFAvis() {
    const avisId = getCurrentAvisId();
    if (avisId) {
        window.open(`/connect-admin/avis/${avisId}/pdf/`, '_blank');
    }
}

function voirProfilAuteur() {
    // TODO: Récupérer ID auteur depuis modal
    console.log('Voir profil auteur');
}

function voirTousAvisAuteur() {
    // TODO: Filtrer par auteur
    console.log('Voir tous avis auteur');
}

function voirFicheLogement() {
    // TODO: Récupérer ID logement depuis modal
    console.log('Voir fiche logement');
}

function voirTousAvisLogement() {
    // TODO: Filtrer par logement
    console.log('Voir tous avis logement');
}

// ============================================
// UTILITAIRES
// ============================================

function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        alert('ID copié : ' + text);
    });
}

function getCsrfToken() {
    const cookie = document.cookie.split(';').find(c => c.trim().startsWith('csrftoken='));
    return cookie ? cookie.split('=')[1] : '';
}

function changePerPage(value) {
    const url = new URL(window.location);
    url.searchParams.set('per_page', value);
    url.searchParams.set('page', '1');
    window.location.href = url.toString();
}

function switchToCards() {
    // TODO: Implémenter vue cards
    alert('Vue cards à venir');
}

function openColumnsModal() {
    // TODO: Modal configuration colonnes
    alert('Configuration colonnes à venir');
}

function exportRapport() {
    const url = new URL(window.location);
    url.searchParams.set('export', 'csv');
    window.location.href = url.toString();
}

function openStatsGlobales() {
    switchView('analytics');
}

function openParametresNotation() {
    // TODO: Modal paramètres notation
    alert('Paramètres notation à venir');
}

// INITIALISATION
// ============================================

function initAvisPage() {
    initFilters();
    initTableSorting();
    initBulkActions();
    initDropdowns();
    initSearchDebounce();
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
    
    if (content) {
        if (content.style.display === 'none') {
            content.style.display = 'block';
            if (toggleText) toggleText.textContent = 'Masquer';
        } else {
            content.style.display = 'none';
            if (toggleText) toggleText.textContent = 'Afficher';
        }
    }
}

function resetFilters() {
    const url = new URL(window.location);
    url.searchParams.delete('search');
    url.searchParams.delete('note');
    url.searchParams.delete('statut');
    url.searchParams.delete('logement');
    url.searchParams.delete('auteur');
    url.searchParams.delete('date_debut');
    url.searchParams.delete('date_fin');
    url.searchParams.delete('ville');
    url.searchParams.set('page', '1');
    window.location.href = url.toString();
}

function filterByCategory(category) {
    const url = new URL(window.location);
    
    if (category === 'recents') {
        const date = new Date();
        date.setDate(date.getDate() - 7);
        url.searchParams.set('date_debut', date.toISOString().split('T')[0]);
    } else if (category === 'bien_notes') {
        url.searchParams.set('note', '4');
        url.searchParams.append('note', '5');
    } else if (category === 'mal_notes') {
        url.searchParams.set('note', '1');
        url.searchParams.append('note', '2');
    } else {
        url.searchParams.delete('date_debut');
        url.searchParams.delete('note');
    }
    
    url.searchParams.set('page', '1');
    window.location.href = url.toString();
}

function saveSearch() {
    const name = prompt('Nommer cette recherche :');
    if (name) {
        const filters = new URLSearchParams(window.location.search);
        localStorage.setItem('saved_search_avis_' + name, filters.toString());
        alert('Recherche sauvegardée !');
    }
}

function initSearchDebounce() {
    const searchInput = document.querySelector('input[name="search"]');
    if (searchInput) {
        let timeout;
        searchInput.addEventListener('input', function() {
            clearTimeout(timeout);
            timeout = setTimeout(() => {
                // Auto-submit après 300ms d'inactivité
                const form = searchInput.closest('form');
                if (form) {
                    form.submit();
                }
            }, 300);
        });
    }
}

function initFilters() {
    // Initialiser multi-selects
    document.querySelectorAll('.multi-select').forEach(select => {
        // TODO: Implémenter multi-select custom si nécessaire
    });
}

// ============================================
// TABLE SORTING
// ============================================

function sortTable(column) {
    const url = new URL(window.location);
    const currentSort = url.searchParams.get('sort') || '-date_avis';
    
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
    document.querySelectorAll('.sortable').forEach(header => {
        header.style.cursor = 'pointer';
    });
}

// ============================================
// BULK ACTIONS
// ============================================

function toggleSelectAll(checkbox) {
    const checkboxes = document.querySelectorAll('.avis-checkbox');
    checkboxes.forEach(cb => {
        cb.checked = checkbox.checked;
    });
    updateBulkActions();
}

function updateBulkActions() {
    const checked = document.querySelectorAll('.avis-checkbox:checked');
    const bulkBar = document.getElementById('bulk-actions-bar');
    const bulkCount = document.getElementById('bulk-count');
    
    if (checked.length > 0) {
        if (bulkBar) bulkBar.style.display = 'flex';
        if (bulkCount) bulkCount.textContent = checked.length;
    } else {
        if (bulkBar) bulkBar.style.display = 'none';
    }
}

function clearSelection() {
    document.querySelectorAll('.avis-checkbox').forEach(cb => {
        cb.checked = false;
    });
    const selectAll = document.getElementById('select-all');
    if (selectAll) selectAll.checked = false;
    updateBulkActions();
}

function bulkPublier() {
    const checked = Array.from(document.querySelectorAll('.avis-checkbox:checked')).map(cb => cb.value);
    if (checked.length === 0) {
        alert('Aucun avis sélectionné');
        return;
    }
    
    if (confirm(`Publier ${checked.length} avis ?`)) {
        // TODO: Appel API
        console.log('Publier avis:', checked);
        alert('Avis publiés avec succès');
        location.reload();
    }
}

function bulkMasquer() {
    const checked = Array.from(document.querySelectorAll('.avis-checkbox:checked')).map(cb => cb.value);
    if (checked.length === 0) {
        alert('Aucun avis sélectionné');
        return;
    }
    
    if (confirm(`Masquer ${checked.length} avis ?`)) {
        // TODO: Appel API
        console.log('Masquer avis:', checked);
        alert('Avis masqués avec succès');
        location.reload();
    }
}

function bulkMarquerSpam() {
    const checked = Array.from(document.querySelectorAll('.avis-checkbox:checked')).map(cb => cb.value);
    if (checked.length === 0) {
        alert('Aucun avis sélectionné');
        return;
    }
    
    if (confirm(`Marquer ${checked.length} avis comme spam ?`)) {
        // TODO: Appel API
        console.log('Marquer spam avis:', checked);
        alert('Avis marqués comme spam');
        location.reload();
    }
}

function bulkExport() {
    const checked = Array.from(document.querySelectorAll('.avis-checkbox:checked')).map(cb => cb.value);
    if (checked.length === 0) {
        alert('Aucun avis sélectionné');
        return;
    }
    
    // TODO: Export CSV avec IDs sélectionnés
    const url = new URL(window.location);
    url.searchParams.set('export', 'csv');
    url.searchParams.set('ids', checked.join(','));
    window.location.href = url.toString();
}

function bulkApprouver() {
    bulkPublier();
}

function bulkRejeter() {
    const checked = Array.from(document.querySelectorAll('.avis-checkbox:checked')).map(cb => cb.value);
    if (checked.length === 0) {
        alert('Aucun avis sélectionné');
        return;
    }
    
    if (confirm(`Rejeter ${checked.length} avis ?`)) {
        // TODO: Appel API
        console.log('Rejeter avis:', checked);
        alert('Avis rejetés avec succès');
        location.reload();
    }
}

// ============================================
// DROPDOWNS
// ============================================

function toggleActionsDropdown(button) {
    const menu = button.nextElementSibling;
    if (menu) {
        // Fermer tous les autres menus
        document.querySelectorAll('.dropdown-menu').forEach(m => {
            if (m !== menu) m.classList.remove('show');
        });
        menu.classList.toggle('show');
    }
}

function initDropdowns() {
    // Fermer dropdowns au click extérieur
    document.addEventListener('click', function(e) {
        if (!e.target.closest('.actions-dropdown')) {
            document.querySelectorAll('.dropdown-menu').forEach(menu => {
                menu.classList.remove('show');
            });
        }
    });
}

// ============================================
// MODAL DÉTAIL AVIS
// ============================================

function openAvisDetail(avisId) {
    const modal = document.getElementById('avis-detail-modal');
    if (!modal) return;
    
    // Charger données avis via AJAX
    fetch(`/connect-admin/avis/${avisId}/detail/`)
        .then(response => response.json())
        .then(data => {
            populateAvisDetail(data);
            modal.style.display = 'flex';
        })
        .catch(error => {
            console.error('Erreur chargement avis:', error);
            alert('Erreur lors du chargement de l\'avis');
        });
}

function populateAvisDetail(data) {
    // Header
    document.getElementById('modal-avis-auteur').textContent = data.auteur.username;
    document.getElementById('modal-avis-date').textContent = data.date_publication;
    document.getElementById('modal-avis-statut').textContent = data.statut_display;
    
    // Avatar
    if (data.auteur.avatar_url) {
        document.getElementById('modal-avis-avatar').src = data.auteur.avatar_url;
        document.getElementById('widget-auteur-avatar').src = data.auteur.avatar_url;
    }
    
    // Note
    const noteDisplay = document.getElementById('modal-avis-note');
    noteDisplay.innerHTML = '';
    for (let i = 1; i <= 5; i++) {
        const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
        svg.setAttribute('width', '32');
        svg.setAttribute('height', '32');
        svg.setAttribute('viewBox', '0 0 24 24');
        svg.setAttribute('fill', i <= data.note ? 'currentColor' : 'none');
        svg.setAttribute('stroke', 'currentColor');
        svg.setAttribute('stroke-width', '2');
        svg.style.color = '#F59E0B';
        const polygon = document.createElementNS('http://www.w3.org/2000/svg', 'polygon');
        polygon.setAttribute('points', '12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2');
        svg.appendChild(polygon);
        noteDisplay.appendChild(svg);
    }
    const span = document.createElement('span');
    span.textContent = `${data.note}/5`;
    span.style.marginLeft = '8px';
    span.style.fontSize = '20px';
    span.style.fontWeight = '700';
    noteDisplay.appendChild(span);
    
    // Notes détaillées
    if (data.note_proprete) {
        createNoteGauge('note-proprete', data.note_proprete, 'Propreté');
    }
    if (data.note_localisation) {
        createNoteGauge('note-emplacement', data.note_localisation, 'Emplacement');
    }
    if (data.note_equipements) {
        createNoteGauge('note-qualite-prix', data.note_equipements, 'Équipements');
    }
    if (data.note_bailleur) {
        createNoteGauge('note-communication', data.note_bailleur, 'Communication');
    }
    
    // Titre et contenu
    document.getElementById('modal-avis-titre').textContent = data.titre || 'Avis';
    document.getElementById('modal-avis-contenu').textContent = data.commentaire;
    
    // Widget auteur
    document.getElementById('widget-auteur-nom').textContent = data.auteur.username;
    document.getElementById('widget-auteur-email').textContent = data.auteur.email || '-';
    
    // Widget logement
    document.getElementById('widget-logement-adresse').textContent = data.logement.adresse;
    document.getElementById('widget-logement-prix').textContent = `${data.logement.prix}€/mois`;
    
    // Statut
    document.getElementById('widget-statut').textContent = data.statut_display;
    document.getElementById('widget-date-pub').textContent = data.date_publication;
}

function createNoteGauge(id, note, label) {
    const container = document.getElementById(id);
    if (!container) return;
    
    container.innerHTML = '';
    const gauge = document.createElement('div');
    gauge.className = 'note-gauge';
    
    // Étoiles
    for (let i = 1; i <= 5; i++) {
        const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
        svg.setAttribute('width', '16');
        svg.setAttribute('height', '16');
        svg.setAttribute('viewBox', '0 0 24 24');
        svg.setAttribute('fill', i <= note ? 'currentColor' : 'none');
        svg.setAttribute('stroke', 'currentColor');
        svg.setAttribute('stroke-width', '2');
        svg.style.color = i <= note ? '#F59E0B' : '#E5E7EB';
        const polygon = document.createElementNS('http://www.w3.org/2000/svg', 'polygon');
        polygon.setAttribute('points', '12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2');
        svg.appendChild(polygon);
        gauge.appendChild(svg);
    }
    
    const span = document.createElement('span');
    span.textContent = `${note}/5`;
    span.style.marginLeft = '8px';
    span.style.fontSize = '14px';
    span.style.fontWeight = '600';
    gauge.appendChild(span);
    
    container.appendChild(gauge);
}

function closeAvisDetailModal() {
    const modal = document.getElementById('avis-detail-modal');
    if (modal) modal.style.display = 'none';
}

// Fermer modal avec Escape
document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
        closeAvisDetailModal();
    }
});

// Fermer modal au click sur overlay
document.addEventListener('click', function(e) {
    const modal = document.getElementById('avis-detail-modal');
    if (modal && e.target === modal) {
        closeAvisDetailModal();
    }
});

// ============================================
// ACTIONS AVIS
// ============================================

function approuverAvis(avisId) {
    if (confirm('Approuver et publier cet avis ?')) {
        // TODO: Appel API
        fetch(`/connect-admin/avis/${avisId}/approuver/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCsrfToken(),
                'Content-Type': 'application/json'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('Avis approuvé avec succès');
                location.reload();
            } else {
                alert('Erreur : ' + (data.error || 'Erreur inconnue'));
            }
        })
        .catch(error => {
            console.error('Erreur:', error);
            alert('Erreur lors de l\'approbation');
        });
    }
}

function rejeterAvis(avisId) {
    const raison = prompt('Raison du rejet :');
    if (raison) {
        // TODO: Appel API
        console.log('Rejeter avis:', avisId, raison);
        alert('Avis rejeté');
        location.reload();
    }
}

function masquerAvis(avisId) {
    if (confirm('Masquer cet avis ? Il ne sera plus visible publiquement.')) {
        // TODO: Appel API
        console.log('Masquer avis:', avisId);
        alert('Avis masqué');
        location.reload();
    }
}

function supprimerAvis(avisId) {
    const raison = prompt('Raison de la suppression (obligatoire) :');
    if (raison) {
        if (confirm('Êtes-vous sûr de vouloir supprimer définitivement cet avis ?')) {
            // TODO: Appel API
            console.log('Supprimer avis:', avisId, raison);
            alert('Avis supprimé');
            location.reload();
        }
    }
}

function approuverAvisFromModal() {
    const avisId = getCurrentAvisId();
    if (avisId) approuverAvis(avisId);
}

function masquerAvisFromModal() {
    const avisId = getCurrentAvisId();
    if (avisId) masquerAvis(avisId);
}

function supprimerAvisFromModal() {
    const avisId = getCurrentAvisId();
    if (avisId) supprimerAvis(avisId);
}

function getCurrentAvisId() {
    // Récupérer l'ID depuis le modal ou le contexte
    const modal = document.getElementById('avis-detail-modal');
    if (modal) {
        return modal.dataset.avisId;
    }
    return null;
}

function epinglerAvis() {
    const avisId = getCurrentAvisId();
    if (avisId) {
        // TODO: Appel API
        console.log('Épingler avis:', avisId);
        alert('Avis épinglé');
    }
}

function partagerAvis() {
    const avisId = getCurrentAvisId();
    if (avisId) {
        const url = window.location.origin + '/avis/' + avisId + '/';
        navigator.clipboard.writeText(url).then(() => {
            alert('Lien copié dans le presse-papiers');
        });
    }
}

function telechargerPDFAvis() {
    const avisId = getCurrentAvisId();
    if (avisId) {
        window.open(`/connect-admin/avis/${avisId}/pdf/`, '_blank');
    }
}

function voirProfilAuteur() {
    // TODO: Récupérer ID auteur depuis modal
    console.log('Voir profil auteur');
}

function voirTousAvisAuteur() {
    // TODO: Filtrer par auteur
    console.log('Voir tous avis auteur');
}

function voirFicheLogement() {
    // TODO: Récupérer ID logement depuis modal
    console.log('Voir fiche logement');
}

function voirTousAvisLogement() {
    // TODO: Filtrer par logement
    console.log('Voir tous avis logement');
}

// ============================================
// UTILITAIRES
// ============================================

function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        alert('ID copié : ' + text);
    });
}

function getCsrfToken() {
    const cookie = document.cookie.split(';').find(c => c.trim().startsWith('csrftoken='));
    return cookie ? cookie.split('=')[1] : '';
}

function changePerPage(value) {
    const url = new URL(window.location);
    url.searchParams.set('per_page', value);
    url.searchParams.set('page', '1');
    window.location.href = url.toString();
}

function switchToCards() {
    // TODO: Implémenter vue cards
    alert('Vue cards à venir');
}

function openColumnsModal() {
    // TODO: Modal configuration colonnes
    alert('Configuration colonnes à venir');
}

function exportRapport() {
    const url = new URL(window.location);
    url.searchParams.set('export', 'csv');
    window.location.href = url.toString();
}

function openStatsGlobales() {
    switchView('analytics');
}

function openParametresNotation() {
    // TODO: Modal paramètres notation
    alert('Paramètres notation à venir');
}

