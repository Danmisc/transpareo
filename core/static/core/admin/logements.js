/**
 * LOGEMENTS MANAGEMENT - JavaScript pour filtres, actions, modals
 */

// ============================================
// VARIABLES GLOBALES
// ============================================

let selectedLogements = new Set();
let currentSort = '';
let currentView = 'table';
let searchTimeout = null;

// ============================================
// INITIALISATION
// ============================================

function initLogementsTable() {
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
    currentSort = urlParams.get('sort') || '-date_creation';
    updateSortIcons();
}

function initFilters() {
    // Recherche en temps réel avec debounce
    const searchInput = document.getElementById('search');
    if (searchInput) {
        searchInput.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => {
                // Auto-submit après 500ms d'inactivité
                // document.getElementById('logements-filters-form').submit();
            }, 500);
        });
    }

    // Mise à jour des sliders de prix
    const prixMinSlider = document.getElementById('prix-slider-min');
    const prixMaxSlider = document.getElementById('prix-slider-max');
    const prixMinInput = document.getElementById('prix_min');
    const prixMaxInput = document.getElementById('prix_max');

    if (prixMinSlider && prixMaxSlider && prixMinInput && prixMaxInput) {
        prixMinSlider.addEventListener('input', function() {
            prixMinInput.value = this.value;
            if (parseInt(this.value) > parseInt(prixMaxSlider.value)) {
                prixMaxSlider.value = this.value;
                prixMaxInput.value = this.value;
            }
        });

        prixMaxSlider.addEventListener('input', function() {
            prixMaxInput.value = this.value;
            if (parseInt(this.value) < parseInt(prixMinSlider.value)) {
                prixMinSlider.value = this.value;
                prixMinInput.value = this.value;
            }
        });

        prixMinInput.addEventListener('input', function() {
            prixMinSlider.value = this.value;
        });

        prixMaxInput.addEventListener('input', function() {
            prixMaxSlider.value = this.value;
        });
    }

    // Mise à jour des sliders de surface
    const surfaceMinSlider = document.getElementById('surface-slider-min');
    const surfaceMaxSlider = document.getElementById('surface-slider-max');
    const surfaceMinInput = document.getElementById('surface_min');
    const surfaceMaxInput = document.getElementById('surface_max');

    if (surfaceMinSlider && surfaceMaxSlider && surfaceMinInput && surfaceMaxInput) {
        surfaceMinSlider.addEventListener('input', function() {
            surfaceMinInput.value = this.value;
            if (parseInt(this.value) > parseInt(surfaceMaxSlider.value)) {
                surfaceMaxSlider.value = this.value;
                surfaceMaxInput.value = this.value;
            }
        });

        surfaceMaxSlider.addEventListener('input', function() {
            surfaceMaxInput.value = this.value;
            if (parseInt(this.value) < parseInt(surfaceMinSlider.value)) {
                surfaceMinSlider.value = this.value;
                surfaceMinInput.value = this.value;
            }
        });

        surfaceMinInput.addEventListener('input', function() {
            surfaceMinSlider.value = this.value;
        });

        surfaceMaxInput.addEventListener('input', function() {
            surfaceMaxSlider.value = this.value;
        });
    }

    // Slider note
    const noteSlider = document.getElementById('note_min');
    const noteValue = document.querySelector('.note-value');
    if (noteSlider && noteValue) {
        noteSlider.addEventListener('input', function() {
            noteValue.textContent = this.value + '/5';
        });
    }
}

function initRangeSliders() {
    // Initialisation des range sliders
    // Les événements sont gérés dans initFilters()
}

// ============================================
// FILTRES
// ============================================

function toggleFilters() {
    const filtersContent = document.getElementById('filters-content');
    const toggleText = document.getElementById('filters-toggle-text');
    
    if (filtersContent.classList.contains('collapsed')) {
        filtersContent.classList.remove('collapsed');
        toggleText.textContent = 'Masquer';
    } else {
        filtersContent.classList.add('collapsed');
        toggleText.textContent = 'Afficher';
    }
}

function saveSearch() {
    const searchName = prompt('Nommez cette recherche :');
    if (searchName) {
        // Sauvegarder dans localStorage
        const filters = new URLSearchParams(window.location.search);
        const savedSearches = JSON.parse(localStorage.getItem('saved_logement_searches') || '[]');
        savedSearches.push({
            name: searchName,
            filters: Object.fromEntries(filters),
            date: new Date().toISOString()
        });
        localStorage.setItem('saved_logement_searches', JSON.stringify(savedSearches));
        alert('Recherche sauvegardée !');
    }
}

// ============================================
// TRI
// ============================================

function toggleSort(field) {
    const urlParams = new URLSearchParams(window.location.search);
    const currentSort = urlParams.get('sort') || '-date_creation';
    
    // Si même champ, inverser le tri
    if (currentSort === field) {
        field = field.startsWith('-') ? field.substring(1) : '-' + field;
    }
    
    urlParams.set('sort', field);
    window.location.search = urlParams.toString();
}

function updateSortIcons() {
    const urlParams = new URLSearchParams(window.location.search);
    const currentSort = urlParams.get('sort') || '-date_creation';
    
    document.querySelectorAll('.sortable').forEach(header => {
        const field = header.dataset.sort;
        header.classList.remove('active');
        
        if (currentSort === field || currentSort === '-' + field) {
            header.classList.add('active');
        }
    });
}

// ============================================
// SÉLECTION
// ============================================

function toggleSelectAll(checkbox) {
    const checkboxes = document.querySelectorAll('.logement-checkbox');
    checkboxes.forEach(cb => {
        cb.checked = checkbox.checked;
        if (checkbox.checked) {
            selectedLogements.add(cb.value);
        } else {
            selectedLogements.delete(cb.value);
        }
    });
    updateBulkActions();
}

function updateBulkActions() {
    selectedLogements.clear();
    document.querySelectorAll('.logement-checkbox:checked').forEach(cb => {
        selectedLogements.add(cb.value);
    });
    
    const bulkBar = document.getElementById('bulk-actions-bar');
    const bulkCount = document.getElementById('bulk-count');
    
    if (selectedLogements.size > 0) {
        bulkBar.style.display = 'flex';
        bulkCount.textContent = selectedLogements.size;
    } else {
        bulkBar.style.display = 'none';
    }
}

function clearSelection() {
    document.querySelectorAll('.logement-checkbox').forEach(cb => {
        cb.checked = false;
    });
    document.getElementById('select-all').checked = false;
    selectedLogements.clear();
    updateBulkActions();
}

// ============================================
// VUES
// ============================================

function switchView(view) {
    currentView = view;
    
    // Mettre à jour les toggles
    document.querySelectorAll('.view-toggle').forEach(toggle => {
        toggle.classList.remove('active');
        if (toggle.dataset.view === view) {
            toggle.classList.add('active');
        }
    });
    
    // Afficher la vue correspondante
    document.querySelectorAll('.view-content').forEach(content => {
        content.classList.remove('active');
    });
    
    const viewElement = document.getElementById('view-' + view);
    if (viewElement) {
        viewElement.classList.add('active');
    }
    
    // Si vue carte, initialiser la map
    if (view === 'map') {
        initMap();
    }
}

let mapInstance = null;

function initMap() {
    const mapContainer = document.getElementById('map');
    if (!mapContainer) return;
    
    // Charger Leaflet depuis CDN si pas déjà chargé
    if (typeof L === 'undefined') {
        const link = document.createElement('link');
        link.rel = 'stylesheet';
        link.href = 'https://unpkg.com/leaflet@1.9.4/dist/leaflet.css';
        document.head.appendChild(link);
        
        const script = document.createElement('script');
        script.src = 'https://unpkg.com/leaflet@1.9.4/dist/leaflet.js';
        script.onload = function() {
            createMap();
        };
        document.body.appendChild(script);
    } else {
        createMap();
    }
}

function createMap() {
    if (mapInstance) {
        mapInstance.remove();
    }
    
    mapInstance = L.map('map').setView([46.6034, 1.8883], 6);
    
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors',
        maxZoom: 19
    }).addTo(mapInstance);
    
    // Charger les logements depuis le tableau
    const logements = document.querySelectorAll('.table-row[data-logement-id]');
    const markers = [];
    
    logements.forEach(row => {
        const logementId = row.dataset.logementId;
        const adresse = row.querySelector('.adresse-text')?.textContent || '';
        const prix = row.querySelector('.col-prix strong')?.textContent || '';
        const titre = row.querySelector('.logement-title-link strong')?.textContent || '';
        
        // Récupérer les coordonnées via AJAX ou depuis data attributes
        fetch(`/connect-admin/logements/${logementId}/detail/`)
            .then(response => response.json())
            .then(data => {
                if (data.latitude && data.longitude) {
                    const marker = L.marker([data.latitude, data.longitude]).addTo(mapInstance);
                    marker.bindPopup(`
                        <div style="min-width: 200px;">
                            <strong>${data.titre}</strong><br>
                            ${data.adresse}<br>
                            ${data.prix} €/mois<br>
                            <button onclick="openLogementDetail(${data.id})" style="margin-top: 8px; padding: 4px 12px; background: #D3580B; color: white; border: none; border-radius: 4px; cursor: pointer;">Voir détail</button>
                        </div>
                    `);
                    markers.push(marker);
                    
                    // Ajuster la vue si c'est le premier marqueur
                    if (markers.length === 1) {
                        mapInstance.setView([data.latitude, data.longitude], 10);
                    }
                }
            })
            .catch(error => {
                console.error('Erreur chargement coordonnées:', error);
            });
    });
    
    // Ajuster la vue pour voir tous les marqueurs
    if (markers.length > 0) {
        const group = new L.featureGroup(markers);
        mapInstance.fitBounds(group.getBounds().pad(0.1));
    }
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

// ============================================
// ACTIONS LOGEMENT
// ============================================

function openLogementDetail(logementId) {
    // Ouvrir modal détail
    console.log('Ouvrir détail logement', logementId);
    // TODO: Implémenter modal détail
}

function editLogement(logementId) {
    // Ouvrir modal édition
    console.log('Éditer logement', logementId);
    // TODO: Implémenter modal édition
}

function duplicateLogement(logementId) {
    if (confirm('Dupliquer ce logement ?')) {
        // TODO: Implémenter duplication
        console.log('Dupliquer logement', logementId);
    }
}

function boostLogement(logementId) {
    // Mettre en avant
    console.log('Mettre en avant logement', logementId);
    // TODO: Implémenter boost
}

function deleteLogement(logementId) {
    if (confirm('Êtes-vous sûr de vouloir supprimer ce logement ? Cette action est irréversible.')) {
        // TODO: Implémenter suppression
        console.log('Supprimer logement', logementId);
    }
}

// ============================================
// ACTIONS BULK
// ============================================

function bulkChangeStatus() {
    const status = prompt('Nouveau statut (disponible/reclame/verifie) :');
    if (status && ['disponible', 'reclame', 'verifie'].includes(status)) {
        // TODO: Implémenter changement statut bulk
        console.log('Changer statut pour', Array.from(selectedLogements), 'vers', status);
    }
}

function bulkExport() {
    const ids = Array.from(selectedLogements).join(',');
    window.location.href = '?export=csv&ids=' + ids;
}

function bulkEmail() {
    // Ouvrir modal email
    console.log('Envoyer email aux propriétaires de', Array.from(selectedLogements));
    // TODO: Implémenter modal email
}

function bulkDelete() {
    if (confirm(`Êtes-vous sûr de vouloir supprimer ${selectedLogements.size} logement(s) ? Cette action est irréversible.`)) {
        // TODO: Implémenter suppression bulk
        console.log('Supprimer logements', Array.from(selectedLogements));
    }
}

// ============================================
// MODAL DÉTAIL LOGEMENT
// ============================================

let currentLogementId = null;
let currentWizardStep = 1;
const totalWizardSteps = 5;

function openLogementDetail(logementId) {
    currentLogementId = logementId;
    const modal = document.getElementById('logement-detail-modal');
    
    // Charger les données du logement via AJAX
    fetch(`/connect-admin/logements/${logementId}/detail/`)
        .then(response => response.json())
        .then(data => {
            populateLogementDetail(data);
            modal.style.display = 'flex';
            document.body.style.overflow = 'hidden';
        })
        .catch(error => {
            console.error('Erreur chargement logement:', error);
            // Fallback: charger depuis les données du tableau
            loadLogementFromTable(logementId);
            modal.style.display = 'flex';
            document.body.style.overflow = 'hidden';
        });
}

function loadLogementFromTable(logementId) {
    // Récupérer les données depuis la ligne du tableau
    const row = document.querySelector(`tr[data-logement-id="${logementId}"]`);
    if (!row) return;
    
    // Extraire les données de base depuis le DOM
    const titre = row.querySelector('.logement-title-link strong')?.textContent || '';
    const adresse = row.querySelector('.adresse-text')?.textContent || '';
    const codePostal = row.querySelector('.adresse-city')?.textContent || '';
    const prix = row.querySelector('.col-prix strong')?.textContent?.replace(/[^\d,]/g, '').replace(',', '') || '0';
    const surface = row.querySelector('.col-surface')?.textContent?.replace(/[^\d,]/g, '').replace(',', '') || '0';
    const pieces = row.querySelector('.pieces-count')?.textContent || '0';
    const type = row.querySelector('.type-badge')?.textContent.trim() || '';
    const statut = row.querySelector('.statut-badge')?.textContent.trim() || '';
    
    // Populer le modal avec les données de base
    document.getElementById('modal-titre').value = titre;
    document.getElementById('modal-adresse').value = adresse;
    document.getElementById('modal-code-postal').value = codePostal;
    document.getElementById('modal-prix').value = prix;
    document.getElementById('modal-surface').value = surface;
    document.getElementById('modal-pieces').value = pieces;
    document.getElementById('modal-logement-title').textContent = titre;
    
    // Mettre à jour le badge statut
    const statutBadge = document.getElementById('modal-statut-badge');
    statutBadge.textContent = statut;
    statutBadge.className = 'statut-badge statut-' + (row.querySelector('.statut-badge')?.classList.contains('statut-disponible') ? 'disponible' : 
                                                      row.querySelector('.statut-badge')?.classList.contains('statut-reclame') ? 'reclame' : 'verifie');
}

function populateLogementDetail(data) {
    // Populer tous les champs du modal avec les données
    document.getElementById('modal-logement-title').textContent = data.titre || 'Détail du logement';
    document.getElementById('modal-titre').value = data.titre || '';
    document.getElementById('modal-type').value = data.type_logement || 'appartement';
    document.getElementById('modal-description').value = data.description || '';
    document.getElementById('modal-adresse').value = data.adresse || '';
    document.getElementById('modal-code-postal').value = data.code_postal || '';
    document.getElementById('modal-prix').value = data.prix || '0';
    document.getElementById('modal-surface').value = data.surface || '0';
    document.getElementById('modal-pieces').value = data.chambres || '0';
    document.getElementById('modal-chambres').value = data.chambres || '0';
    document.getElementById('modal-etage').value = data.etage || 'etage';
    
    // Statut
    const statutBadge = document.getElementById('modal-statut-badge');
    statutBadge.textContent = data.statut_display || 'Disponible';
    statutBadge.className = 'statut-badge statut-' + (data.statut || 'disponible');
    
    // Images
    const mainImage = document.getElementById('modal-main-image');
    const thumbnails = document.getElementById('modal-thumbnails');
    
    if (data.images && data.images.length > 0) {
        const mainImg = data.images.find(img => img.est_principale) || data.images[0];
        mainImage.innerHTML = `<img src="${mainImg.url}" alt="${mainImg.titre}" style="width: 100%; height: 100%; object-fit: cover;">`;
        
        thumbnails.innerHTML = '';
        data.images.forEach((img, index) => {
            const thumb = document.createElement('div');
            thumb.className = 'modal-thumbnail' + (index === 0 ? ' active' : '');
            thumb.innerHTML = `<img src="${img.url}" alt="${img.titre}" style="width: 100%; height: 100%; object-fit: cover;">`;
            thumb.onclick = () => {
                mainImage.innerHTML = `<img src="${img.url}" alt="${img.titre}" style="width: 100%; height: 100%; object-fit: cover;">`;
                document.querySelectorAll('.modal-thumbnail').forEach(t => t.classList.remove('active'));
                thumb.classList.add('active');
            };
            thumbnails.appendChild(thumb);
        });
    }
    
    // Propriétaire
    if (data.proprietaire) {
        const propInfo = document.getElementById('modal-proprietaire-info');
        const avatarHtml = data.proprietaire.avatar_url 
            ? `<img src="${data.proprietaire.avatar_url}" alt="${data.proprietaire.username}" style="width: 60px; height: 60px; border-radius: 50%; object-fit: cover;">`
            : `<div style="width: 60px; height: 60px; border-radius: 50%; background: linear-gradient(135deg, #D3580B 0%, #c4510a 100%); color: white; display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 20px;">${data.proprietaire.username?.[0]?.toUpperCase() || 'U'}</div>`;
        
        propInfo.innerHTML = `
            <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 12px;">
                ${avatarHtml}
                <div>
                    <div style="font-weight: 600; color: #111827;">${data.proprietaire.username || 'Utilisateur'}</div>
                    <div style="font-size: 13px; color: #6B7280;">${data.proprietaire.email || ''}</div>
                </div>
            </div>
            <a href="/connect-admin/users/${data.proprietaire.id}/" style="display: inline-block; padding: 8px 16px; background: #F9FAFB; border: 1px solid #E5E7EB; border-radius: 6px; color: #111827; text-decoration: none; font-size: 13px; font-weight: 500; margin-top: 8px;">Voir profil complet</a>
        `;
    }
    
    // Statistiques
    document.getElementById('modal-vues').textContent = data.vues || '0';
    document.getElementById('modal-candidatures').textContent = data.candidatures || '0';
    document.getElementById('modal-note').textContent = (data.note_moyenne || 0).toFixed(1) + '/5';
}

function closeLogementDetailModal() {
    const modal = document.getElementById('logement-detail-modal');
    modal.style.display = 'none';
    document.body.style.overflow = '';
    currentLogementId = null;
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
    document.querySelector(`.modal-tab[data-tab="${tabName}"]`).classList.add('active');
    document.getElementById(`tab-${tabName}`).classList.add('active');
}

function toggleEditMode() {
    const inputs = document.querySelectorAll('#tab-infos .modal-input, #tab-infos .modal-select, #tab-infos .modal-textarea');
    const isReadonly = inputs[0].readOnly;
    
    inputs.forEach(input => {
        input.readOnly = !isReadonly;
        input.disabled = !isReadonly;
    });
    
    const btn = document.getElementById('btn-edit-mode');
    if (isReadonly) {
        btn.textContent = 'Enregistrer';
        btn.classList.remove('btn-primary');
        btn.classList.add('btn-success');
    } else {
        btn.textContent = 'Modifier';
        btn.classList.remove('btn-success');
        btn.classList.add('btn-primary');
        // TODO: Sauvegarder les modifications
    }
}

// ============================================
// MODAL AJOUTER LOGEMENT (WIZARD)
// ============================================

function openAddLogementModal() {
    const modal = document.getElementById('add-logement-modal');
    currentWizardStep = 1;
    updateWizardProgress();
    modal.style.display = 'flex';
    document.body.style.overflow = 'hidden';
}

function closeAddLogementModal() {
    const modal = document.getElementById('add-logement-modal');
    modal.style.display = 'none';
    document.body.style.overflow = '';
    currentWizardStep = 1;
    updateWizardProgress();
    document.getElementById('add-logement-form').reset();
}

function wizardNext() {
    if (validateWizardStep(currentWizardStep)) {
        if (currentWizardStep < totalWizardSteps) {
            currentWizardStep++;
            updateWizardProgress();
        }
    }
}

function wizardPrevious() {
    if (currentWizardStep > 1) {
        currentWizardStep--;
        updateWizardProgress();
    }
}

function validateWizardStep(step) {
    const stepContent = document.getElementById(`wizard-step-${step}`);
    const requiredFields = stepContent.querySelectorAll('[required]');
    
    for (let field of requiredFields) {
        if (!field.value.trim()) {
            field.focus();
            alert(`Le champ "${field.previousElementSibling?.textContent || field.name}" est obligatoire`);
            return false;
        }
    }
    return true;
}

function updateWizardProgress() {
    // Mettre à jour la barre de progression
    const progress = (currentWizardStep / totalWizardSteps) * 100;
    document.getElementById('wizard-progress-bar').style.width = progress + '%';
    
    // Mettre à jour les étapes
    document.querySelectorAll('.wizard-step').forEach((step, index) => {
        if (index + 1 <= currentWizardStep) {
            step.classList.add('active');
        } else {
            step.classList.remove('active');
        }
    });
    
    // Afficher/masquer le contenu des étapes
    document.querySelectorAll('.wizard-step-content').forEach((content, index) => {
        if (index + 1 === currentWizardStep) {
            content.classList.add('active');
        } else {
            content.classList.remove('active');
        }
    });
    
    // Gérer les boutons navigation
    document.getElementById('wizard-prev').style.display = currentWizardStep > 1 ? 'flex' : 'none';
    document.getElementById('wizard-next').style.display = currentWizardStep < totalWizardSteps ? 'flex' : 'none';
    document.getElementById('wizard-submit').style.display = currentWizardStep === totalWizardSteps ? 'flex' : 'none';
}

// Compteur de caractères
document.addEventListener('DOMContentLoaded', function() {
    const titreInput = document.getElementById('wizard-titre');
    const descriptionInput = document.getElementById('wizard-description');
    
    if (titreInput) {
        titreInput.addEventListener('input', function() {
            document.getElementById('titre-count').textContent = this.value.length;
        });
    }
    
    if (descriptionInput) {
        descriptionInput.addEventListener('input', function() {
            document.getElementById('description-count').textContent = this.value.length;
        });
    }
    
    // Preview images
    const imageInput = document.getElementById('wizard-images');
    if (imageInput) {
        imageInput.addEventListener('change', function(e) {
            const previewGrid = document.getElementById('image-preview-grid');
            previewGrid.innerHTML = '';
            
            Array.from(e.target.files).forEach((file, index) => {
                const reader = new FileReader();
                reader.onload = function(e) {
                    const item = document.createElement('div');
                    item.className = 'image-preview-item';
                    item.innerHTML = `
                        <img src="${e.target.result}" alt="Preview ${index + 1}">
                        <button type="button" class="image-preview-remove" onclick="removeImagePreview(${index})">×</button>
                    `;
                    previewGrid.appendChild(item);
                };
                reader.readAsDataURL(file);
            });
        });
    }
});

function removeImagePreview(index) {
    // TODO: Implémenter suppression preview
    console.log('Supprimer image preview', index);
}

// ============================================
// UTILITAIRES
// ============================================

function copyId(id) {
    navigator.clipboard.writeText(id.toString()).then(() => {
        alert('ID copié : ' + id);
    });
}

function changePerPage(value) {
    const urlParams = new URLSearchParams(window.location.search);
    urlParams.set('per_page', value);
    urlParams.set('page', '1'); // Reset à la première page
    window.location.search = urlParams.toString();
}

function exportPDF() {
    // Export PDF côté serveur
    const filters = new URLSearchParams(window.location.search);
    filters.set('export', 'pdf');
    window.location.href = '?' + filters.toString();
}

function openColumnsModal() {
    // Modal pour configurer les colonnes affichées
    alert('Configuration des colonnes - Fonctionnalité à venir');
    // TODO: Implémenter modal avec checkboxes pour chaque colonne
}

function shareLogement(logementId) {
    const url = window.location.origin + '/logements/' + logementId + '/';
    navigator.clipboard.writeText(url).then(() => {
        alert('Lien copié dans le presse-papiers !');
    });
}

function previewLogement(logementId) {
    const url = window.location.origin + '/logements/' + logementId + '/';
    window.open(url, '_blank');
}

// ============================================
// EXPORT
// ============================================

// Les exports CSV sont gérés côté serveur via l'URL ?export=csv

