// ============================================
// SEARCH BAR COMPLETE - Transpareo
// ============================================

// Global state
const searchState = {
    address: null,
    lat: null,
    lng: null,
    dateDebut: null,
    dateFin: null,
    budgetMin: null,
    budgetMax: null,
    filters: {},
    activeFiltersCount: 0,
    searchHistory: JSON.parse(localStorage.getItem('search_history') || '[]'),
    quartiers: [
        { name: 'Vieux Toulouse', lat: 43.6000, lng: 1.4400 },
        { name: 'Carmes', lat: 43.6047, lng: 1.4422 },
        { name: 'Saint-Cyprien', lat: 43.5950, lng: 1.4300 },
        { name: 'Capitole', lat: 43.6047, lng: 1.4442 },
        { name: 'Matabiau', lat: 43.6100, lng: 1.4500 },
        { name: 'Balma', lat: 43.6100, lng: 1.5000 },
        { name: 'Saint-Simon', lat: 43.6200, lng: 1.4600 },
        { name: 'Fontaine Lestang', lat: 43.5800, lng: 1.4200 }
    ]
};

// Debounce utility
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// ============================================
// 1. ADDRESS AUTOCOMPLETE (BAN API)
// ============================================

let autocompleteTimeout;
let selectedAddressIndex = -1;

function initAddressAutocomplete() {
    // Support both hero and sticky versions
    const addressInput = document.getElementById('search-address-input') || document.getElementById('search-address-input-hero') || document.getElementById('hero-address-input');
    const autocompleteDiv = document.getElementById('address-autocomplete') || document.getElementById('address-autocomplete-hero') || document.getElementById('hero-address-autocomplete');
    const clearBtn = document.getElementById('address-clear') || document.getElementById('address-clear-hero') || document.getElementById('hero-address-clear');
    
    if (!addressInput) return;
    
    // Input handler with debounce
    addressInput.addEventListener('input', debounce((e) => {
        const query = e.target.value.trim();
        
        if (query.length < 2) {
            autocompleteDiv.classList.remove('active');
            if (clearBtn) clearBtn.style.display = query ? 'block' : 'none';
            return;
        }
        
        if (clearBtn) clearBtn.style.display = 'block';
        fetchBANAutocomplete(query);
    }, 300));
    
    // Focus handler - show history or popular
    addressInput.addEventListener('focus', () => {
        if (addressInput.value.length < 2) {
            showAutocompleteInitial();
        } else if (addressInput.value.length >= 2) {
            fetchBANAutocomplete(addressInput.value);
        }
    });
    
    // Keyboard navigation
    addressInput.addEventListener('keydown', (e) => {
        const items = autocompleteDiv.querySelectorAll('.autocomplete-item');
        
        if (e.key === 'ArrowDown') {
            e.preventDefault();
            selectedAddressIndex = Math.min(selectedAddressIndex + 1, items.length - 1);
            updateSelectedItem(items);
        } else if (e.key === 'ArrowUp') {
            e.preventDefault();
            selectedAddressIndex = Math.max(selectedAddressIndex - 1, -1);
            updateSelectedItem(items);
        } else if (e.key === 'Enter' && selectedAddressIndex >= 0) {
            e.preventDefault();
            items[selectedAddressIndex].click();
        } else if (e.key === 'Escape') {
            autocompleteDiv.classList.remove('active');
            selectedAddressIndex = -1;
        }
    });
    
    // Clear button
    if (clearBtn) {
        clearBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            addressInput.value = '';
            searchState.address = null;
            searchState.lat = null;
            searchState.lng = null;
            clearBtn.style.display = 'none';
            autocompleteDiv.classList.remove('active');
        });
        
        // Show/hide clear button based on input value
        addressInput.addEventListener('input', () => {
            clearBtn.style.display = addressInput.value ? 'block' : 'none';
        });
    }
    
    // Close on outside click
    document.addEventListener('click', (e) => {
        if (!addressInput.contains(e.target) && !autocompleteDiv.contains(e.target)) {
            autocompleteDiv.classList.remove('active');
        }
    });
}

function updateSelectedItem(items) {
    items.forEach((item, index) => {
        item.classList.toggle('selected', index === selectedAddressIndex);
    });
}

function fetchBANAutocomplete(query) {
    const autocompleteDiv = document.getElementById('address-autocomplete') || document.getElementById('address-autocomplete-hero');
    if (!autocompleteDiv) return;
    
    // Show loading
    autocompleteDiv.innerHTML = '<div class="autocomplete-loading">Recherche en cours...</div>';
    autocompleteDiv.classList.add('active');
    
    // Use backend API which covers all of France via Nominatim
    fetch(`/api/autocomplete-address/?q=${encodeURIComponent(query)}&limit=8`)
        .then(response => response.json())
        .then(data => {
            if (data.results && data.results.length > 0) {
                displayAutocompleteResultsFromAPI(data.results, query);
            } else {
                autocompleteDiv.innerHTML = '<div class="autocomplete-empty">Aucun résultat trouvé</div>';
            }
        })
        .catch(error => {
            console.error('Erreur API:', error);
            // Fallback to BAN API
            fetch(`https://api-adresse.data.gouv.fr/search/?q=${encodeURIComponent(query)}&limit=8`)
                .then(response => response.json())
                .then(data => {
                    if (data.features && data.features.length > 0) {
                        displayAutocompleteResults(data.features, query);
                    } else {
                        autocompleteDiv.innerHTML = '<div class="autocomplete-empty">Aucun résultat trouvé</div>';
                    }
                })
                .catch(err => {
                    autocompleteDiv.innerHTML = '<div class="autocomplete-error">Erreur de connexion</div>';
                });
        });
}

function displayAutocompleteResultsFromAPI(results, query) {
    const autocompleteDiv = document.getElementById('address-autocomplete') || document.getElementById('address-autocomplete-hero');
    const addressInput = document.getElementById('search-address-input') || document.getElementById('search-address-input-hero');
    if (!autocompleteDiv || !addressInput) return;
    
    autocompleteDiv.innerHTML = '';
    selectedAddressIndex = -1;
    
    results.forEach((result, index) => {
        const item = document.createElement('div');
        item.className = 'autocomplete-item';
        item.setAttribute('data-index', index);
        
        const shortName = result.short_name || result.address.split(',')[0];
        const displayName = result.display_name || result.address;
        
        item.innerHTML = `
            <div class="autocomplete-icon">📍</div>
            <div class="autocomplete-content">
                <div class="autocomplete-title">${highlightText(shortName, query)}</div>
                <div class="autocomplete-subtitle">${displayName}</div>
            </div>
        `;
        
        item.addEventListener('click', () => {
            addressInput.value = shortName;
            searchState.address = result.address;
            searchState.lat = result.latitude;
            searchState.lng = result.longitude;
            
            // Save to history
            saveToHistory(result.address, result.latitude, result.longitude);
            
            autocompleteDiv.classList.remove('active');
            updateMapCenter(result.latitude, result.longitude);
        });
        
        autocompleteDiv.appendChild(item);
    });
    
    autocompleteDiv.classList.add('active');
}

function displayAutocompleteResults(features, query) {
    const autocompleteDiv = document.getElementById('address-autocomplete') || document.getElementById('address-autocomplete-hero');
    const addressInput = document.getElementById('search-address-input') || document.getElementById('search-address-input-hero');
    if (!autocompleteDiv || !addressInput) return;
    
    autocompleteDiv.innerHTML = '';
    selectedAddressIndex = -1;
    
    features.forEach((feature, index) => {
        const props = feature.properties;
        const coords = feature.geometry.coordinates; // [lng, lat]
        
        const item = document.createElement('div');
        item.className = 'autocomplete-item';
        item.innerHTML = `
            <div class="autocomplete-icon">📍</div>
            <div class="autocomplete-content">
                <div class="autocomplete-title">${highlightText(props.name, query)}</div>
                <div class="autocomplete-subtitle">${props.postcode} ${props.city}</div>
            </div>
        `;
        
        item.addEventListener('click', () => {
            addressInput.value = `${props.name}, ${props.postcode} ${props.city}`;
            searchState.address = addressInput.value;
            searchState.lat = coords[1];
            searchState.lng = coords[0];
            
            // Save to history
            saveToHistory(addressInput.value, coords[1], coords[0]);
            
            autocompleteDiv.classList.remove('active');
            updateMapCenter(coords[1], coords[0]);
        });
        
        autocompleteDiv.appendChild(item);
    });
    
    autocompleteDiv.classList.add('active');
}

function highlightText(text, query) {
    const regex = new RegExp(`(${query})`, 'gi');
    return text.replace(regex, '<strong>$1</strong>');
}

function showAutocompleteInitial() {
    const autocompleteDiv = document.getElementById('address-autocomplete') || document.getElementById('address-autocomplete-hero');
    if (!autocompleteDiv) return;
    
    const history = searchState.searchHistory.slice(0, 5);
    
    let html = '';
    
    // History section
    if (history.length > 0) {
        html += '<div class="autocomplete-section"><div class="autocomplete-section-title">Récemment recherchées</div>';
        history.forEach(item => {
            html += `
                <div class="autocomplete-item" data-history>
                    <div class="autocomplete-icon">📍</div>
                    <div class="autocomplete-content">
                        <div class="autocomplete-title">${item.address}</div>
                    </div>
                    <button class="autocomplete-delete" onclick="deleteHistoryItem('${item.address}')" aria-label="Supprimer">✕</button>
                </div>
            `;
        });
        html += '</div>';
    }
    
    // Popular neighborhoods
    html += '<div class="autocomplete-section"><div class="autocomplete-section-title">Quartiers populaires</div>';
    searchState.quartiers.forEach(quartier => {
        html += `
            <div class="autocomplete-item" data-quartier>
                <div class="autocomplete-icon">📍</div>
                <div class="autocomplete-content">
                    <div class="autocomplete-title">${quartier.name}</div>
                    <div class="autocomplete-subtitle">Toulouse</div>
                </div>
            </div>
        `;
    });
    html += '</div>';
    
    autocompleteDiv.innerHTML = html;
    autocompleteDiv.classList.add('active');
    
    // Add click handlers
    autocompleteDiv.querySelectorAll('[data-quartier]').forEach(item => {
        item.addEventListener('click', () => {
            const title = item.querySelector('.autocomplete-title').textContent;
            const quartier = searchState.quartiers.find(q => q.name === title);
            if (quartier) {
                const addressInput = document.getElementById('search-address-input') || document.getElementById('search-address-input-hero');
                if (addressInput) {
                    addressInput.value = quartier.name;
                    searchState.address = quartier.name;
                    searchState.lat = quartier.lat;
                    searchState.lng = quartier.lng;
                    updateMapCenter(quartier.lat, quartier.lng);
                    autocompleteDiv.classList.remove('active');
                }
            }
        });
    });
    
    autocompleteDiv.querySelectorAll('[data-history]').forEach(item => {
        item.addEventListener('click', (e) => {
            if (e.target.classList.contains('autocomplete-delete')) return;
            const title = item.querySelector('.autocomplete-title').textContent;
            const historyItem = searchState.searchHistory.find(h => h.address === title);
            if (historyItem) {
                const addressInput = document.getElementById('search-address-input') || document.getElementById('search-address-input-hero');
                if (addressInput) {
                    addressInput.value = historyItem.address;
                    searchState.address = historyItem.address;
                    searchState.lat = historyItem.lat;
                    searchState.lng = historyItem.lng;
                    updateMapCenter(historyItem.lat, historyItem.lng);
                    autocompleteDiv.classList.remove('active');
                }
            }
        });
    });
}

function saveToHistory(address, lat, lng) {
    // Remove if exists
    searchState.searchHistory = searchState.searchHistory.filter(h => h.address !== address);
    
    // Add to beginning
    searchState.searchHistory.unshift({
        address,
        lat,
        lng,
        date: new Date().toISOString()
    });
    
    // Keep only 10
    searchState.searchHistory = searchState.searchHistory.slice(0, 10);
    
    // Save to localStorage
    localStorage.setItem('search_history', JSON.stringify(searchState.searchHistory));
}

function deleteHistoryItem(address) {
    searchState.searchHistory = searchState.searchHistory.filter(h => h.address !== address);
    localStorage.setItem('search_history', JSON.stringify(searchState.searchHistory));
    showAutocompleteInitial();
}

// ============================================
// 2. DATE PICKER
// ============================================

function initDatePicker() {
    const dateField = document.getElementById('search-dates-field') || document.getElementById('search-dates-field-hero');
    const dateModal = document.getElementById('date-picker-modal');
    const dateDebutInput = document.getElementById('date-debut-input');
    const dateFinInput = document.getElementById('date-fin-input');
    const dateDisplay = document.getElementById('date-display') || document.getElementById('date-display-hero');
    
    if (!dateField) return;
    
    dateField.addEventListener('click', () => {
        dateModal.classList.add('active');
    });
    
    // Close modal
    document.getElementById('date-picker-close')?.addEventListener('click', () => {
        dateModal.classList.remove('active');
    });
    
    // Preset buttons
    document.querySelectorAll('.date-preset').forEach(btn => {
        btn.addEventListener('click', () => {
            const duration = btn.getAttribute('data-duration');
            applyDatePreset(duration);
        });
    });
    
    // Date inputs
    if (dateDebutInput) {
        dateDebutInput.addEventListener('change', () => {
            if (dateFinInput.value && dateFinInput.value < dateDebutInput.value) {
                dateFinInput.value = '';
            }
            dateFinInput.min = dateDebutInput.value;
            updateDateDisplay();
        });
    }
    
    if (dateFinInput) {
        dateFinInput.addEventListener('change', () => {
            updateDateDisplay();
        });
    }
    
    // Apply button
    document.getElementById('date-picker-apply')?.addEventListener('click', () => {
        searchState.dateDebut = dateDebutInput.value;
        searchState.dateFin = dateFinInput.value;
        updateDateDisplay();
        dateModal.classList.remove('active');
    });
}

function applyDatePreset(duration) {
    const today = new Date();
    const dateDebutInput = document.getElementById('date-debut-input');
    const dateFinInput = document.getElementById('date-fin-input');
    
    let dateDebut = new Date(today);
    let dateFin = new Date(today);
    
    if (duration === '1mois') {
        dateFin.setMonth(dateFin.getMonth() + 1);
    } else if (duration === '3mois') {
        dateFin.setMonth(dateFin.getMonth() + 3);
    } else if (duration === '6mois') {
        dateFin.setMonth(dateFin.getMonth() + 6);
    } else if (duration === '12mois') {
        dateFin.setMonth(dateFin.getMonth() + 12);
    }
    
    dateDebutInput.value = formatDate(dateDebut);
    dateFinInput.value = formatDate(dateFin);
    dateFinInput.min = dateDebutInput.value;
}

function formatDate(date) {
    return date.toISOString().split('T')[0];
}

function updateDateDisplay() {
    const dateDebutInput = document.getElementById('date-debut-input');
    const dateFinInput = document.getElementById('date-fin-input');
    const dateDisplay = document.getElementById('date-display') || document.getElementById('date-display-hero');
    
    if (!dateDisplay) return;
    
    if (dateDebutInput.value && dateFinInput.value) {
        const debut = new Date(dateDebutInput.value);
        const fin = new Date(dateFinInput.value);
        dateDisplay.textContent = `${formatDateDisplay(debut)} - ${formatDateDisplay(fin)}`;
    } else {
        dateDisplay.textContent = 'Sélectionner';
    }
}

function formatDateDisplay(date) {
    const months = ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Jun', 'Jul', 'Aoû', 'Sep', 'Oct', 'Nov', 'Déc'];
    return `${date.getDate()} ${months[date.getMonth()]}`;
}

// ============================================
// 3. BUDGET RANGE SLIDER
// ============================================

function initBudgetSlider() {
    const budgetField = document.getElementById('search-budget-field') || document.getElementById('search-budget-field-hero');
    const budgetModal = document.getElementById('budget-modal');
    
    if (!budgetField) {
        console.log('Budget field not found');
        return;
    }
    
    if (!budgetModal) {
        console.log('Budget modal not found');
        return;
    }
    
    console.log('Initializing budget slider');
    
    budgetField.addEventListener('click', (e) => {
        e.stopPropagation();
        e.preventDefault();
        console.log('Budget field clicked');
        budgetModal.classList.add('active');
        document.body.style.overflow = 'hidden';
    });
    
    // Close modal
    const budgetClose = document.getElementById('budget-close');
    const budgetOverlay = document.getElementById('budget-overlay');
    
    if (budgetClose) {
        budgetClose.addEventListener('click', () => {
            budgetModal.classList.remove('active');
            document.body.style.overflow = '';
        });
    }
    
    if (budgetOverlay) {
        budgetOverlay.addEventListener('click', () => {
            budgetModal.classList.remove('active');
            document.body.style.overflow = '';
        });
    }
    
    // Get slider and input elements
    const budgetMinInput = document.getElementById('budget-min-input');
    const budgetMaxInput = document.getElementById('budget-max-input');
    const budgetMinSlider = document.getElementById('budget-min-slider');
    const budgetMaxSlider = document.getElementById('budget-max-slider');
    const budgetDisplay = document.getElementById('budget-display') || document.getElementById('budget-display-hero');
    
    // Sync sliders with inputs
    if (budgetMinSlider && budgetMinInput) {
        budgetMinSlider.addEventListener('input', (e) => {
            const value = parseInt(e.target.value);
            budgetMinInput.value = value;
            if (value >= parseInt(budgetMaxSlider.value)) {
                budgetMaxSlider.value = value + 50;
                budgetMaxInput.value = value + 50;
            }
            updateBudgetDisplay();
        });
        
        budgetMinInput.addEventListener('change', (e) => {
            const value = parseInt(e.target.value);
            budgetMinSlider.value = value;
            if (value >= parseInt(budgetMaxSlider.value)) {
                budgetMaxSlider.value = value + 50;
                budgetMaxInput.value = value + 50;
            }
            updateBudgetDisplay();
        });
    }
    
    if (budgetMaxSlider && budgetMaxInput) {
        budgetMaxSlider.addEventListener('input', (e) => {
            const value = parseInt(e.target.value);
            budgetMaxInput.value = value;
            if (value <= parseInt(budgetMinSlider.value)) {
                budgetMinSlider.value = value - 50;
                budgetMinInput.value = value - 50;
            }
            updateBudgetDisplay();
        });
        
        budgetMaxInput.addEventListener('change', (e) => {
            const value = parseInt(e.target.value);
            budgetMaxSlider.value = value;
            if (value <= parseInt(budgetMinSlider.value)) {
                budgetMinSlider.value = value - 50;
                budgetMinInput.value = value - 50;
            }
            updateBudgetDisplay();
        });
    }
    
    // Preset buttons
    document.querySelectorAll('.budget-preset').forEach(btn => {
        btn.addEventListener('click', () => {
            const range = btn.getAttribute('data-range');
            applyBudgetPreset(range);
        });
    });
    
    // Apply button
    const budgetApply = document.getElementById('budget-apply');
    if (budgetApply) {
        budgetApply.addEventListener('click', () => {
            searchState.budgetMin = budgetMinInput && budgetMinInput.value ? parseInt(budgetMinInput.value) : null;
            searchState.budgetMax = budgetMaxInput && budgetMaxInput.value ? parseInt(budgetMaxInput.value) : null;
            updateBudgetDisplay();
            updateActiveFiltersCount();
            updateActiveFiltersDisplay();
            budgetModal.classList.remove('active');
            document.body.style.overflow = '';
        });
    }
}

function applyBudgetPreset(range) {
    const budgetMinInput = document.getElementById('budget-min-input');
    const budgetMaxInput = document.getElementById('budget-max-input');
    const budgetMinSlider = document.getElementById('budget-min-slider');
    const budgetMaxSlider = document.getElementById('budget-max-slider');
    
    const presets = {
        '0-600': { min: 0, max: 600 },
        '600-800': { min: 600, max: 800 },
        '800-1000': { min: 800, max: 1000 },
        '1000-1500': { min: 1000, max: 1500 },
        '1500-2000': { min: 1500, max: 2000 },
        '2000+': { min: 2000, max: 10000 }
    };
    
    const preset = presets[range];
    if (preset) {
        budgetMinInput.value = preset.min;
        budgetMaxInput.value = preset.max;
        budgetMinSlider.value = preset.min;
        budgetMaxSlider.value = preset.max;
    }
}

function updateBudgetDisplay() {
    const budgetMinInput = document.getElementById('budget-min-input');
    const budgetMaxInput = document.getElementById('budget-max-input');
    const budgetDisplay = document.getElementById('budget-display') || document.getElementById('budget-display-hero');
    
    if (!budgetDisplay) return;
    
    if (budgetMinInput && budgetMinInput.value && budgetMaxInput && budgetMaxInput.value) {
        budgetDisplay.textContent = `${budgetMinInput.value} € - ${budgetMaxInput.value} €`;
    } else if (budgetMinInput && budgetMinInput.value) {
        budgetDisplay.textContent = `À partir de ${budgetMinInput.value} €`;
    } else if (budgetMaxInput && budgetMaxInput.value) {
        budgetDisplay.textContent = `Jusqu'à ${budgetMaxInput.value} €`;
    } else {
        budgetDisplay.textContent = 'Budget';
    }
}

// ============================================
// 4. ADVANCED FILTERS
// ============================================

function initAdvancedFilters() {
    const filtersButton = document.getElementById('search-filters-button') || document.getElementById('search-filters-button-hero');
    const filtersModal = document.getElementById('filters-modal');
    const filtersOverlay = document.getElementById('filters-overlay');
    
    if (!filtersButton) {
        console.log('Filters button not found');
        return;
    }
    
    if (!filtersModal) {
        console.log('Filters modal not found');
        return;
    }
    
    console.log('Initializing advanced filters');
    
    filtersButton.addEventListener('click', (e) => {
        e.stopPropagation();
        e.preventDefault();
        console.log('Filters button clicked');
        filtersModal.classList.add('active');
        document.body.style.overflow = 'hidden';
    });
    
    // Close modal
    const filtersClose = document.getElementById('filters-close');
    if (filtersClose) {
        filtersClose.addEventListener('click', () => {
            filtersModal.classList.remove('active');
            document.body.style.overflow = '';
        });
    }
    
    if (filtersOverlay) {
        filtersOverlay.addEventListener('click', () => {
            filtersModal.classList.remove('active');
            document.body.style.overflow = '';
        });
    }
    
    // Collapsible sections
    document.querySelectorAll('.filter-section-toggle').forEach(toggle => {
        toggle.addEventListener('click', () => {
            const section = toggle.closest('.filter-section');
            section.classList.toggle('expanded');
        });
    });
    
    // Apply button (already handled above, but ensure it works)
    const filtersApply = document.getElementById('filters-apply');
    if (filtersApply && !filtersApply.hasAttribute('data-listener-added')) {
        filtersApply.setAttribute('data-listener-added', 'true');
        filtersApply.addEventListener('click', () => {
            collectFilters();
            updateActiveFiltersCount();
            updateActiveFiltersDisplay();
            filtersModal.classList.remove('active');
            document.body.style.overflow = '';
        });
    }
    
    // Reset button
    const filtersReset = document.getElementById('filters-reset');
    if (filtersReset) {
        filtersReset.addEventListener('click', () => {
            resetFilters();
        });
    }
}

function collectFilters() {
    searchState.filters = {};
    
    // Type de bien
    const typeCheckboxes = document.querySelectorAll('#filters-modal input[type="checkbox"][id^="filter-type"]:checked');
    if (typeCheckboxes.length > 0) {
        searchState.filters.type_bien = Array.from(typeCheckboxes).map(cb => cb.value);
    }
    
    // Pièces (from filter pills)
    const piecesPill = document.querySelector('.filter-pill.active[data-value]');
    if (piecesPill) {
        const value = piecesPill.getAttribute('data-value');
        if (value) searchState.filters.nb_pieces = value;
    }
    
    // Chambres (from slider)
    const chambresSlider = document.querySelector('#filter-chambres-slider');
    if (chambresSlider && chambresSlider.value > 0) {
        searchState.filters.nb_chambres = parseInt(chambresSlider.value);
    }
    
    // Surface
    const surfaceMin = document.querySelector('#filter-surface-min');
    if (surfaceMin && surfaceMin.value) {
        searchState.filters.surface_min = parseInt(surfaceMin.value);
    }
    
    // Équipements
    const equipements = document.querySelectorAll('#filters-equipements input[type="checkbox"]:checked');
    if (equipements.length > 0) {
        searchState.filters.equipements = Array.from(equipements).map(cb => cb.value);
    }
    
    // Animaux (from filter pills)
    const animauxPill = document.querySelector('#filters-animaux .filter-pill.active');
    if (animauxPill) {
        const value = animauxPill.getAttribute('data-value');
        if (value) searchState.filters.animaux = value;
    }
    
    // Tri
    if (searchState.filters.tri) {
        // Already set
    }
    
    // Rating min
    if (searchState.filters.rating_min) {
        // Already set
    }
}

function resetFilters() {
    document.querySelectorAll('#filters-modal input[type="checkbox"]').forEach(cb => cb.checked = false);
    document.querySelectorAll('#filters-modal input[type="radio"]').forEach(radio => radio.checked = false);
    document.querySelectorAll('#filters-modal input[type="number"]').forEach(input => input.value = '');
    searchState.filters = {};
    updateActiveFiltersCount();
    updateActiveFiltersDisplay();
}

function updateActiveFiltersCount() {
    let count = 0;
    
    if (searchState.budgetMin) count++;
    if (searchState.budgetMax) count++;
    if (searchState.filters.type_bien) count += searchState.filters.type_bien.length;
    if (searchState.filters.nb_pieces) count++;
    if (searchState.filters.nb_chambres) count++;
    if (searchState.filters.surface_min) count++;
    if (searchState.filters.equipements) count += searchState.filters.equipements.length;
    if (searchState.filters.animaux) count++;
    if (searchState.filters.rating_min) count++;
    if (searchState.filters.tri) count++;
    
    searchState.activeFiltersCount = count;
    
    const badge = document.getElementById('filters-badge') || document.getElementById('filters-badge-hero');
    if (badge) {
        badge.textContent = count > 0 ? `(${count})` : '';
        badge.style.display = count > 0 ? 'inline' : 'none';
    }
}

function updateActiveFiltersDisplay() {
    const container = document.getElementById('active-filters-container') || document.getElementById('active-filters-container-hero');
    const bar = document.getElementById('active-filters-bar') || document.getElementById('active-filters-bar-hero');
    if (!container) return;
    
    container.innerHTML = '';
    
    // Add budget badges
    if (searchState.budgetMin) {
        const badge = document.createElement('div');
        badge.className = 'filter-badge';
        badge.innerHTML = `
            <span>Budget min: ${searchState.budgetMin}€</span>
            <button onclick="removeBudgetFilter('min')" aria-label="Supprimer">×</button>
        `;
        container.appendChild(badge);
    }
    
    if (searchState.budgetMax) {
        const badge = document.createElement('div');
        badge.className = 'filter-badge';
        badge.innerHTML = `
            <span>Budget max: ${searchState.budgetMax}€</span>
            <button onclick="removeBudgetFilter('max')" aria-label="Supprimer">×</button>
        `;
        container.appendChild(badge);
    }
    
    // Add active filter badges
    Object.entries(searchState.filters).forEach(([key, value]) => {
        if (Array.isArray(value) && value.length > 0) {
            value.forEach(v => {
                addFilterBadge(container, key, v);
            });
        } else if (value) {
            addFilterBadge(container, key, value);
        }
    });
    
    // Show/hide bar
    if (container.children.length > 0) {
        if (bar) bar.classList.add('active');
    } else {
        if (bar) bar.classList.remove('active');
    }
}

function removeBudgetFilter(type) {
    if (type === 'min') {
        searchState.budgetMin = null;
        document.getElementById('budget-display-hero').textContent = 'Budget';
    } else if (type === 'max') {
        searchState.budgetMax = null;
        document.getElementById('budget-display-hero').textContent = 'Budget';
    }
    updateActiveFiltersDisplay();
}

window.removeBudgetFilter = removeBudgetFilter;

function addFilterBadge(container, key, value) {
    const badge = document.createElement('div');
    badge.className = 'filter-badge';
    const label = getFilterLabel(key, value);
    const valueStr = typeof value === 'string' ? value.replace(/'/g, "\\'") : value;
    badge.innerHTML = `
        <span>${label}</span>
        <button onclick="removeFilter('${key}', '${valueStr}')" aria-label="Supprimer">×</button>
    `;
    container.appendChild(badge);
}

// Make removeFilter globally available
window.removeFilter = removeFilter;

function getFilterLabel(key, value) {
    const labels = {
        'type_bien': { 'appartement': 'Appartement', 'maison': 'Maison', 'studio': 'Studio', 'colocation': 'Colocation' },
        'nb_pieces': { '1': '1 pièce', '2': '2 pièces', '3': '3 pièces', '4+': '4+ pièces' },
        'nb_chambres': { '1': '1 chambre', '2': '2 chambres', '3': '3 chambres', '4': '4+ chambres' },
        'animaux': { 'oui': 'Animaux acceptés', 'non': 'Animaux interdits', 'nego': 'Négociable' },
        'surface_min': (v) => `Surface min: ${v}m²`,
        'rating_min': (v) => `Note min: ${v}`,
        'tri': { 'recent': 'Nouveautés' }
    };
    
    if (typeof labels[key] === 'function') {
        return labels[key](value);
    }
    return labels[key]?.[value] || `${key}: ${value}`;
}

function removeFilter(key, value) {
    if (Array.isArray(searchState.filters[key])) {
        searchState.filters[key] = searchState.filters[key].filter(v => v !== value);
        if (searchState.filters[key].length === 0) {
            delete searchState.filters[key];
        }
    } else {
        delete searchState.filters[key];
    }
    
    updateActiveFiltersCount();
    updateActiveFiltersDisplay();
    performSearch();
}

// ============================================
// 5. SEARCH BUTTON
// ============================================

function initSearchButton() {
    const searchButton = document.getElementById('search-button') || document.getElementById('search-button-hero');
    
    if (!searchButton) {
        console.log('Search button not found');
        return;
    }
    
    console.log('Initializing search button');
    
    searchButton.addEventListener('click', (e) => {
        e.preventDefault();
        e.stopPropagation();
        console.log('Search button clicked');
        performSearch();
    });
    
    // Enter key on address input
    const addressInput = document.getElementById('search-address-input') || document.getElementById('search-address-input-hero');
    if (addressInput) {
        addressInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                performSearch();
            }
        });
    }
}

function performSearch() {
    console.log('performSearch called');
    
    // Get address from input if not in state
    const addressInput = document.getElementById('search-address-input') || document.getElementById('search-address-input-hero');
    if (addressInput && addressInput.value) {
        // Si c'est "Ma localisation", ne pas écraser les coordonnées
        if (addressInput.value !== 'Ma localisation') {
            searchState.address = addressInput.value;
        }
    }
    
    // Validation : besoin d'une adresse OU de coordonnées
    if (!searchState.address && !searchState.lat) {
        // Si pas d'adresse mais un filtre rapide actif, utiliser Toulouse par défaut
        const activeQuickFilter = document.querySelector('.quick-filter-btn.active');
        if (activeQuickFilter) {
            searchState.address = 'Toulouse';
            searchState.lat = 43.6047;
            searchState.lng = 1.4422;
        } else {
            showToast('Veuillez entrer une adresse ou utiliser un filtre rapide', 'error');
            return;
        }
    }
    
    const searchButton = document.getElementById('search-button') || document.getElementById('search-button-hero');
    if (searchButton) {
        searchButton.disabled = true;
        const originalHTML = searchButton.innerHTML;
        searchButton.innerHTML = '<span style="display:inline-block;width:12px;height:12px;border:2px solid white;border-top-color:transparent;border-radius:50%;animation:spin 0.6s linear infinite;"></span> Recherche...';
        
        // Re-enable after a delay (in case of error)
        setTimeout(() => {
            searchButton.disabled = false;
            searchButton.innerHTML = originalHTML;
        }, 5000);
    }
    
    // Build search params
    const params = new URLSearchParams();
    
    if (searchState.address) params.append('address', searchState.address);
    if (searchState.lat) params.append('lat', searchState.lat);
    if (searchState.lng) params.append('lng', searchState.lng);
    if (searchState.dateDebut) params.append('date_debut', searchState.dateDebut);
    if (searchState.dateFin) params.append('date_fin', searchState.dateFin);
    if (searchState.budgetMin) params.append('price_min', searchState.budgetMin);
    if (searchState.budgetMax) params.append('price_max', searchState.budgetMax);
    
    // Add filters
    Object.entries(searchState.filters).forEach(([key, value]) => {
        if (Array.isArray(value)) {
            value.forEach(v => params.append(key, v));
        } else {
            params.append(key, value);
        }
    });
    
    // Redirect to map with params
    window.location.href = `/map/?${params.toString()}`;
}

// ============================================
// 6. MAP INTEGRATION
// ============================================

function updateMapCenter(lat, lng) {
    // This will be called by the map component
    if (window.mapInstance) {
        window.mapInstance.setView([lat, lng], 13);
        
        // Add search circle
        if (window.searchCircle) {
            window.mapInstance.removeLayer(window.searchCircle);
        }
        
        const radius = parseInt(document.getElementById('search-radius')?.value || 10);
        window.searchCircle = L.circle([lat, lng], {
            radius: radius * 1000,
            color: '#D3580B',
            fillColor: '#FFE4D6',
            fillOpacity: 0.3
        }).addTo(window.mapInstance);
    }
}

// ============================================
// 7. UTILITIES
// ============================================

function showToast(message, type = 'info') {
    // Simple toast implementation
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.classList.add('show');
    }, 10);
    
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// ============================================
// INITIALIZATION
// ============================================

// ============================================
// QUICK FILTERS
// ============================================

function applyQuickFilter(filterType) {
    // Toggle active state
    const clickedBtn = document.querySelector(`[data-filter="${filterType}"]`);
    if (clickedBtn && clickedBtn.classList.contains('active')) {
        // Si déjà actif, désactiver
        clickedBtn.classList.remove('active');
        // Réinitialiser les filtres de ce type
        resetQuickFilter(filterType);
        updateActiveFiltersCount();
        updateActiveFiltersDisplay();
        return;
    }
    
    // Désactiver tous les autres
    const buttons = document.querySelectorAll('.quick-filter-btn');
    buttons.forEach(btn => btn.classList.remove('active'));
    
    if (clickedBtn) {
        clickedBtn.classList.add('active');
    }
    
    // Reset previous filters (but keep address if set)
    const previousAddress = searchState.address;
    const previousLat = searchState.lat;
    const previousLng = searchState.lng;
    
    searchState.filters = {};
    searchState.budgetMin = null;
    searchState.budgetMax = null;
    
    // Restore address if it was set
    if (previousAddress || previousLat) {
        searchState.address = previousAddress;
        searchState.lat = previousLat;
        searchState.lng = previousLng;
    }
    
    switch(filterType) {
        case 'affordable':
            // Logements abordables : prix max 600€
            searchState.budgetMin = null;
            searchState.budgetMax = 600;
            const budgetDisplayAffordable = document.getElementById('budget-display-hero');
            if (budgetDisplayAffordable) {
                budgetDisplayAffordable.textContent = 'Jusqu\'à 600€';
            }
            break;
            
        case 'nearby':
            // Proche de moi : géolocalisation
            if (navigator.geolocation) {
                navigator.geolocation.getCurrentPosition(
                    (position) => {
                        searchState.lat = position.coords.latitude;
                        searchState.lng = position.coords.longitude;
                        searchState.address = 'Ma localisation';
                        document.getElementById('search-address-input-hero').value = 'Ma localisation';
                        showToast('Localisation détectée', 'success');
                    },
                    (error) => {
                        showToast('Impossible d\'obtenir votre localisation', 'error');
                    }
                );
            } else {
                showToast('Géolocalisation non supportée', 'error');
            }
            break;
            
        case 'premium':
            // Logements premium : prix min 1500€
            searchState.budgetMin = 1500;
            searchState.budgetMax = null;
            const budgetDisplayPremium = document.getElementById('budget-display-hero');
            if (budgetDisplayPremium) {
                budgetDisplayPremium.textContent = 'À partir de 1500€';
            }
            break;
            
        case 'recent':
            // Nouveautés : tri par date récente
            searchState.filters.tri = 'recent';
            break;
            
        case 'high-rated':
            // Bien notés : note min 4.5
            searchState.filters.rating_min = 4.5;
            break;
            
        case 'large':
            // Grandes surfaces : surface min 80m²
            searchState.filters.surface_min = 80;
            break;
    }
    
    // Update active filters display
    updateActiveFiltersCount();
    updateActiveFiltersDisplay();
}

function resetQuickFilter(filterType) {
    switch(filterType) {
        case 'affordable':
            searchState.budgetMax = null;
            const budgetDisplay1 = document.getElementById('budget-display-hero');
            if (budgetDisplay1) budgetDisplay1.textContent = 'Budget';
            break;
        case 'premium':
            searchState.budgetMin = null;
            const budgetDisplay2 = document.getElementById('budget-display-hero');
            if (budgetDisplay2) budgetDisplay2.textContent = 'Budget';
            break;
        case 'recent':
            delete searchState.filters.tri;
            break;
        case 'high-rated':
            delete searchState.filters.rating_min;
            break;
        case 'large':
            delete searchState.filters.surface_min;
            break;
        case 'nearby':
            if (searchState.address === 'Ma localisation') {
                searchState.address = null;
                searchState.lat = null;
                searchState.lng = null;
                const addressInput = document.getElementById('search-address-input-hero');
                if (addressInput) addressInput.value = '';
            }
            break;
    }
}

// Make function globally available
window.applyQuickFilter = applyQuickFilter;

// ============================================
// INITIALIZATION
// ============================================

document.addEventListener('DOMContentLoaded', () => {
    console.log('Initializing search bar...');
    initAddressAutocomplete();
    initBudgetSlider();
    initAdvancedFilters();
    initSearchButton();
    console.log('Search bar initialized');
});

