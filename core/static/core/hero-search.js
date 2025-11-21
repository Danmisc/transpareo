// ============================================
// HERO SEARCH BAR - CENTERED & INNOVATIVE
// Modern implementation with all features
// ============================================

// Hero-specific state
const heroSearchState = {
    address: null,
    lat: null,
    lng: null,
    budgetMin: null,
    budgetMax: null,
    filters: {},
    activeFiltersCount: 0
};

// Initialize hero search bar
document.addEventListener('DOMContentLoaded', function() {
    initHeroSearchBar();
    initHeroAddressAutocomplete();
    initHeroBudgetModal();
    initHeroFiltersModal();
    initHeroSearchButton();
    initHeroQuickFilters();
});

// ============================================
// ADDRESS AUTOCOMPLETE
// ============================================
function initHeroAddressAutocomplete() {
    const addressInput = document.getElementById('hero-address-input');
    const autocompleteDiv = document.getElementById('hero-address-autocomplete');
    const clearBtn = document.getElementById('hero-address-clear');
    const addressField = document.getElementById('hero-search-address');
    
    if (!addressInput || !autocompleteDiv) return;
    
    let selectedIndex = -1;
    let autocompleteTimeout;
    
    // Input handler with debounce
    addressInput.addEventListener('input', debounce((e) => {
        const query = e.target.value.trim();
        
        if (query.length < 3) {
            autocompleteDiv.innerHTML = '';
            addressField.classList.remove('active');
            if (clearBtn) clearBtn.style.display = query ? 'flex' : 'none';
            return;
        }
        
        if (clearBtn) clearBtn.style.display = 'flex';
        addressField.classList.add('active');
        fetchHeroAutocomplete(query, autocompleteDiv);
    }, 300));
    
    // Focus handler
    addressInput.addEventListener('focus', () => {
        addressField.classList.add('active');
        if (addressInput.value.length < 3) {
            showHeroAutocompleteInitial(autocompleteDiv);
        } else if (addressInput.value.length >= 3) {
            fetchHeroAutocomplete(addressInput.value, autocompleteDiv);
        }
    });
    
    // Clear button
    if (clearBtn) {
        clearBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            addressInput.value = '';
            autocompleteDiv.innerHTML = '';
            addressField.classList.remove('active');
            clearBtn.style.display = 'none';
            heroSearchState.address = null;
            heroSearchState.lat = null;
            heroSearchState.lng = null;
            addressInput.focus();
        });
    }
    
    // Keyboard navigation
    addressInput.addEventListener('keydown', (e) => {
        const items = autocompleteDiv.querySelectorAll('.hero-autocomplete-item');
        
        if (e.key === 'ArrowDown') {
            e.preventDefault();
            selectedIndex = Math.min(selectedIndex + 1, items.length - 1);
            updateHeroSelectedItem(items, selectedIndex);
        } else if (e.key === 'ArrowUp') {
            e.preventDefault();
            selectedIndex = Math.max(selectedIndex - 1, -1);
            updateHeroSelectedItem(items, selectedIndex);
        } else if (e.key === 'Enter' && selectedIndex >= 0 && items[selectedIndex]) {
            e.preventDefault();
            items[selectedIndex].click();
        } else if (e.key === 'Escape') {
            addressField.classList.remove('active');
            selectedIndex = -1;
        }
    });
    
    // Close on outside click
    document.addEventListener('click', (e) => {
        if (!addressField.contains(e.target)) {
            addressField.classList.remove('active');
            selectedIndex = -1;
        }
    });
}

function fetchHeroAutocomplete(query, container) {
    container.innerHTML = '<div class="hero-autocomplete-item"><div class="hero-autocomplete-content"><div class="hero-autocomplete-text">Recherche en cours...</div></div></div>';
    
    fetch(`/api/autocomplete-address/?q=${encodeURIComponent(query)}`)
        .then(response => response.json())
        .then(data => {
            if (data.success && data.addresses && data.addresses.length > 0) {
                displayHeroAutocompleteResults(data.addresses, container);
            } else {
                container.innerHTML = '<div class="hero-autocomplete-item"><div class="hero-autocomplete-content"><div class="hero-autocomplete-text">Aucun résultat trouvé</div></div></div>';
            }
        })
        .catch(error => {
            console.error('Autocomplete error:', error);
            container.innerHTML = '<div class="hero-autocomplete-item"><div class="hero-autocomplete-content"><div class="hero-autocomplete-text">Erreur de recherche</div></div></div>';
        });
}

function displayHeroAutocompleteResults(addresses, container) {
    container.innerHTML = '';
    
    addresses.slice(0, 8).forEach((addr, index) => {
        const item = document.createElement('div');
        item.className = 'hero-autocomplete-item';
        item.setAttribute('data-index', index);
        
        const icon = getAddressIcon(addr.type || 'address');
        
        item.innerHTML = `
            <svg class="hero-autocomplete-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                ${icon}
            </svg>
            <div class="hero-autocomplete-content">
                <div class="hero-autocomplete-text">${highlightMatch(addr.display_name, heroSearchState.query || '')}</div>
                ${addr.short_name ? `<div class="hero-autocomplete-subtext">${addr.short_name}</div>` : ''}
            </div>
        `;
        
        item.addEventListener('click', () => {
            selectHeroAddress(addr, container);
        });
        
        container.appendChild(item);
    });
}

function selectHeroAddress(address, container) {
    const addressInput = document.getElementById('hero-address-input');
    if (addressInput) {
        addressInput.value = address.display_name;
        heroSearchState.address = address.display_name;
        heroSearchState.lat = address.latitude;
        heroSearchState.lng = address.longitude;
        
        const addressField = document.getElementById('hero-search-address');
        if (addressField) addressField.classList.remove('active');
        
        container.innerHTML = '';
        
        // Save to history
        saveToSearchHistory(address);
    }
}

function showHeroAutocompleteInitial(container) {
    container.innerHTML = '';
    
    // Show history if exists
    const history = JSON.parse(localStorage.getItem('search_history') || '[]');
    if (history.length > 0) {
        const section = document.createElement('div');
        section.className = 'hero-autocomplete-section';
        section.textContent = 'Récemment recherchées';
        container.appendChild(section);
        
        history.slice(0, 5).forEach(item => {
            const historyItem = document.createElement('div');
            historyItem.className = 'hero-autocomplete-item';
            historyItem.innerHTML = `
                <svg class="hero-autocomplete-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <circle cx="12" cy="12" r="10"></circle>
                    <polyline points="12 6 12 12 16 14"></polyline>
                </svg>
                <div class="hero-autocomplete-content">
                    <div class="hero-autocomplete-text">${item.address}</div>
                </div>
            `;
            historyItem.addEventListener('click', () => {
                document.getElementById('hero-address-input').value = item.address;
                heroSearchState.address = item.address;
                heroSearchState.lat = item.lat;
                heroSearchState.lng = item.lng;
                const addressField = document.getElementById('hero-search-address');
                if (addressField) addressField.classList.remove('active');
            });
            container.appendChild(historyItem);
        });
    }
    
    // Show popular neighborhoods
    const quartiers = [
        'Vieux Toulouse', 'Carmes', 'Saint-Cyprien', 'Capitole',
        'Matabiau', 'Balma', 'Saint-Simon', 'Fontaine Lestang'
    ];
    
    const section = document.createElement('div');
    section.className = 'hero-autocomplete-section';
    section.textContent = 'Quartiers populaires';
    container.appendChild(section);
    
    quartiers.forEach(quartier => {
        const item = document.createElement('div');
        item.className = 'hero-autocomplete-item';
        item.innerHTML = `
            <svg class="hero-autocomplete-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"></path>
                <circle cx="12" cy="10" r="3"></circle>
            </svg>
            <div class="hero-autocomplete-content">
                <div class="hero-autocomplete-text">${quartier}, Toulouse</div>
            </div>
        `;
        item.addEventListener('click', () => {
            document.getElementById('hero-address-input').value = `${quartier}, Toulouse`;
            heroSearchState.address = `${quartier}, Toulouse`;
            const addressField = document.getElementById('hero-search-address');
            if (addressField) addressField.classList.remove('active');
        });
        container.appendChild(item);
    });
}

function updateHeroSelectedItem(items, index) {
    items.forEach((item, i) => {
        item.classList.toggle('active', i === index);
    });
    if (index >= 0 && items[index]) {
        items[index].scrollIntoView({ block: 'nearest', behavior: 'smooth' });
    }
}

function highlightMatch(text, query) {
    if (!query) return text;
    const regex = new RegExp(`(${query})`, 'gi');
    return text.replace(regex, '<strong>$1</strong>');
}

function getAddressIcon(type) {
    const icons = {
        address: '<path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"></path><circle cx="12" cy="10" r="3"></circle>',
        neighborhood: '<path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"></path><circle cx="12" cy="10" r="3"></circle>',
        city: '<circle cx="12" cy="12" r="10"></circle><path d="M12 2a15.3 15.3 0 0 0 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 0 4-10z"></path>',
        history: '<circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline>'
    };
    return icons[type] || icons.address;
}

function saveToSearchHistory(address) {
    const history = JSON.parse(localStorage.getItem('search_history') || '[]');
    const newItem = {
        address: address.display_name,
        lat: address.latitude,
        lng: address.longitude,
        date: new Date().toISOString()
    };
    
    // Remove if already exists
    const filtered = history.filter(item => item.address !== newItem.address);
    filtered.unshift(newItem);
    
    // Keep only last 10
    localStorage.setItem('search_history', JSON.stringify(filtered.slice(0, 10)));
}

// ============================================
// BUDGET MODAL
// ============================================
function initHeroBudgetModal() {
    const budgetTrigger = document.getElementById('hero-budget-trigger');
    const budgetDisplay = document.getElementById('hero-budget-display');
    const budgetField = document.getElementById('hero-search-budget');
    
    if (!budgetTrigger) return;
    
    budgetTrigger.addEventListener('click', (e) => {
        e.stopPropagation();
        openHeroBudgetModal();
    });
    
    // Update display when budget changes
    updateHeroBudgetDisplay();
}

function openHeroBudgetModal() {
    // Check if modal already exists
    let modal = document.getElementById('hero-budget-modal');
    if (modal) {
        modal.style.display = 'flex';
        return;
    }
    
    // Create modal
    modal = document.createElement('div');
    modal.id = 'hero-budget-modal';
    modal.className = 'hero-modal-overlay';
    modal.innerHTML = `
        <div class="hero-modal-content hero-budget-modal">
            <div class="hero-modal-header">
                <h3>Budget mensuel</h3>
                <button class="hero-modal-close" onclick="closeHeroBudgetModal()">
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <line x1="18" y1="6" x2="6" y2="18"></line>
                        <line x1="6" y1="6" x2="18" y2="18"></line>
                    </svg>
                </button>
            </div>
            <div class="hero-modal-body">
                <div class="hero-budget-inputs">
                    <div class="hero-budget-input-group">
                        <label>De</label>
                        <input type="number" id="hero-budget-min" min="0" max="10000" step="50" placeholder="0">
                        <span>€</span>
                    </div>
                    <div class="hero-budget-input-group">
                        <label>À</label>
                        <input type="number" id="hero-budget-max" min="0" max="10000" step="50" placeholder="10000">
                        <span>€</span>
                    </div>
                </div>
                <div class="hero-budget-slider-container">
                    <div class="hero-budget-slider" id="hero-budget-slider"></div>
                </div>
                <div class="hero-budget-presets">
                    <div class="hero-budget-presets-title">Budgets populaires</div>
                    <div class="hero-budget-presets-grid">
                        <button class="hero-budget-preset" data-min="0" data-max="600">Jusqu'à 600€</button>
                        <button class="hero-budget-preset" data-min="600" data-max="800">600€ - 800€</button>
                        <button class="hero-budget-preset" data-min="800" data-max="1000">800€ - 1000€</button>
                        <button class="hero-budget-preset" data-min="1000" data-max="1500">1000€ - 1500€</button>
                        <button class="hero-budget-preset" data-min="1500" data-max="2000">1500€ - 2000€</button>
                        <button class="hero-budget-preset" data-min="2000" data-max="10000">2000€+</button>
                    </div>
                </div>
            </div>
            <div class="hero-modal-footer">
                <button class="hero-modal-btn-secondary" onclick="resetHeroBudget()">Réinitialiser</button>
                <button class="hero-modal-btn-primary" onclick="applyHeroBudget()">Appliquer</button>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    
    // Initialize slider
    initHeroBudgetSlider();
    
    // Preset buttons
    modal.querySelectorAll('.hero-budget-preset').forEach(btn => {
        btn.addEventListener('click', () => {
            const min = parseInt(btn.dataset.min);
            const max = parseInt(btn.dataset.max);
            document.getElementById('hero-budget-min').value = min;
            document.getElementById('hero-budget-max').value = max;
            heroSearchState.budgetMin = min;
            heroSearchState.budgetMax = max;
            updateHeroBudgetSlider();
            updateHeroBudgetDisplay();
        });
    });
    
    // Close on overlay click
    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            closeHeroBudgetModal();
        }
    });
    
    // Close on Escape
    document.addEventListener('keydown', function escapeHandler(e) {
        if (e.key === 'Escape' && modal.style.display === 'flex') {
            closeHeroBudgetModal();
            document.removeEventListener('keydown', escapeHandler);
        }
    });
}

function initHeroBudgetSlider() {
    // Simple range slider implementation
    const slider = document.getElementById('hero-budget-slider');
    if (!slider) return;
    
    const minInput = document.getElementById('hero-budget-min');
    const maxInput = document.getElementById('hero-budget-max');
    
    if (!minInput || !maxInput) return;
    
    // Sync inputs with state
    if (heroSearchState.budgetMin !== null) {
        minInput.value = heroSearchState.budgetMin;
    }
    if (heroSearchState.budgetMax !== null) {
        maxInput.value = heroSearchState.budgetMax;
    }
    
    // Input handlers
    minInput.addEventListener('input', () => {
        const min = parseInt(minInput.value) || 0;
        const max = parseInt(maxInput.value) || 10000;
        if (min > max) minInput.value = max;
        heroSearchState.budgetMin = parseInt(minInput.value) || null;
        updateHeroBudgetDisplay();
    });
    
    maxInput.addEventListener('input', () => {
        const min = parseInt(minInput.value) || 0;
        const max = parseInt(maxInput.value) || 10000;
        if (max < min) maxInput.value = min;
        heroSearchState.budgetMax = parseInt(maxInput.value) || null;
        updateHeroBudgetDisplay();
    });
}

function updateHeroBudgetSlider() {
    // Update slider visual if needed
}

function applyHeroBudget() {
    const minInput = document.getElementById('hero-budget-min');
    const maxInput = document.getElementById('hero-budget-max');
    
    if (minInput && maxInput) {
        heroSearchState.budgetMin = minInput.value ? parseInt(minInput.value) : null;
        heroSearchState.budgetMax = maxInput.value ? parseInt(maxInput.value) : null;
    }
    
    updateHeroBudgetDisplay();
    closeHeroBudgetModal();
}

function resetHeroBudget() {
    heroSearchState.budgetMin = null;
    heroSearchState.budgetMax = null;
    const minInput = document.getElementById('hero-budget-min');
    const maxInput = document.getElementById('hero-budget-max');
    if (minInput) minInput.value = '';
    if (maxInput) maxInput.value = '';
    updateHeroBudgetDisplay();
}

function closeHeroBudgetModal() {
    const modal = document.getElementById('hero-budget-modal');
    if (modal) {
        modal.style.display = 'none';
    }
    const budgetField = document.getElementById('hero-search-budget');
    if (budgetField) budgetField.classList.remove('active');
}

function updateHeroBudgetDisplay() {
    const display = document.getElementById('hero-budget-display');
    if (!display) return;
    
    if (heroSearchState.budgetMin !== null && heroSearchState.budgetMax !== null) {
        display.textContent = `${heroSearchState.budgetMin}€ - ${heroSearchState.budgetMax}€`;
        display.classList.remove('empty');
    } else if (heroSearchState.budgetMin !== null) {
        display.textContent = `À partir de ${heroSearchState.budgetMin}€`;
        display.classList.remove('empty');
    } else if (heroSearchState.budgetMax !== null) {
        display.textContent = `Jusqu'à ${heroSearchState.budgetMax}€`;
        display.classList.remove('empty');
    } else {
        display.textContent = 'Sélectionner';
        display.classList.add('empty');
    }
}

// ============================================
// FILTERS MODAL
// ============================================
function initHeroFiltersModal() {
    const filtersTrigger = document.getElementById('hero-filters-trigger');
    const filtersField = document.getElementById('hero-search-filters');
    
    if (!filtersTrigger) return;
    
    filtersTrigger.addEventListener('click', (e) => {
        e.stopPropagation();
        openHeroFiltersModal();
    });
    
    updateHeroFiltersBadge();
}

function openHeroFiltersModal() {
    // Check if modal already exists
    let modal = document.getElementById('hero-filters-modal');
    if (modal) {
        modal.style.display = 'flex';
        return;
    }
    
    // Create comprehensive filters modal
    modal = document.createElement('div');
    modal.id = 'hero-filters-modal';
    modal.className = 'hero-modal-overlay';
    modal.innerHTML = `
        <div class="hero-modal-content hero-filters-modal">
            <div class="hero-modal-header">
                <h3>Filtres avancés</h3>
                <button class="hero-modal-close" onclick="closeHeroFiltersModal()">
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <line x1="18" y1="6" x2="6" y2="18"></line>
                        <line x1="6" y1="6" x2="18" y2="18"></line>
                    </svg>
                </button>
            </div>
            <div class="hero-modal-body hero-filters-body">
                <div class="hero-filters-grid">
                    <!-- Type de bien -->
                    <div class="hero-filters-column">
                        <div class="hero-filters-title">Type de bien</div>
                        <label class="hero-filter-checkbox">
                            <input type="checkbox" data-filter="type" value="appartement">
                            <span>Appartement</span>
                        </label>
                        <label class="hero-filter-checkbox">
                            <input type="checkbox" data-filter="type" value="maison">
                            <span>Maison</span>
                        </label>
                        <label class="hero-filter-checkbox">
                            <input type="checkbox" data-filter="type" value="studio">
                            <span>Studio</span>
                        </label>
                        <label class="hero-filter-checkbox">
                            <input type="checkbox" data-filter="type" value="loft">
                            <span>Loft</span>
                        </label>
                    </div>
                    
                    <!-- Caractéristiques -->
                    <div class="hero-filters-column">
                        <div class="hero-filters-title">Caractéristiques</div>
                        <div class="hero-filter-group">
                            <label>Pièces</label>
                            <div class="hero-filter-pills">
                                <button class="hero-filter-pill" data-filter="pieces" value="1">1</button>
                                <button class="hero-filter-pill" data-filter="pieces" value="2">2</button>
                                <button class="hero-filter-pill" data-filter="pieces" value="3">3</button>
                                <button class="hero-filter-pill" data-filter="pieces" value="4">4+</button>
                            </div>
                        </div>
                        <div class="hero-filter-group">
                            <label>Chambres</label>
                            <div class="hero-filter-pills">
                                <button class="hero-filter-pill" data-filter="chambres" value="1">1</button>
                                <button class="hero-filter-pill" data-filter="chambres" value="2">2</button>
                                <button class="hero-filter-pill" data-filter="chambres" value="3">3+</button>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Équipements -->
                    <div class="hero-filters-column">
                        <div class="hero-filters-title">Équipements</div>
                        <label class="hero-filter-checkbox">
                            <input type="checkbox" data-filter="equipement" value="parking">
                            <span>Parking</span>
                        </label>
                        <label class="hero-filter-checkbox">
                            <input type="checkbox" data-filter="equipement" value="balcon">
                            <span>Balcon / Terrasse</span>
                        </label>
                        <label class="hero-filter-checkbox">
                            <input type="checkbox" data-filter="equipement" value="wifi">
                            <span>WiFi</span>
                        </label>
                        <label class="hero-filter-checkbox">
                            <input type="checkbox" data-filter="equipement" value="climatisation">
                            <span>Climatisation</span>
                        </label>
                        <label class="hero-filter-checkbox">
                            <input type="checkbox" data-filter="equipement" value="ascenseur">
                            <span>Ascenseur</span>
                        </label>
                    </div>
                </div>
            </div>
            <div class="hero-modal-footer">
                <button class="hero-modal-btn-secondary" onclick="resetHeroFilters()">Réinitialiser</button>
                <button class="hero-modal-btn-primary" onclick="applyHeroFilters()">Appliquer</button>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    
    // Initialize filter interactions
    initHeroFilterInteractions(modal);
    
    // Close handlers
    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            closeHeroFiltersModal();
        }
    });
    
    document.addEventListener('keydown', function escapeHandler(e) {
        if (e.key === 'Escape' && modal.style.display === 'flex') {
            closeHeroFiltersModal();
            document.removeEventListener('keydown', escapeHandler);
        }
    });
}

function initHeroFilterInteractions(modal) {
    // Checkboxes
    modal.querySelectorAll('input[type="checkbox"]').forEach(checkbox => {
        checkbox.addEventListener('change', () => {
            updateHeroFiltersBadge();
        });
    });
    
    // Pills (buttons)
    modal.querySelectorAll('.hero-filter-pill').forEach(pill => {
        pill.addEventListener('click', () => {
            pill.classList.toggle('active');
            updateHeroFiltersBadge();
        });
    });
}

function applyHeroFilters() {
    const modal = document.getElementById('hero-filters-modal');
    if (!modal) return;
    
    heroSearchState.filters = {};
    heroSearchState.activeFiltersCount = 0;
    
    // Collect checkbox filters
    modal.querySelectorAll('input[type="checkbox"]:checked').forEach(checkbox => {
        const filterType = checkbox.dataset.filter;
        const value = checkbox.value;
        
        if (!heroSearchState.filters[filterType]) {
            heroSearchState.filters[filterType] = [];
        }
        heroSearchState.filters[filterType].push(value);
        heroSearchState.activeFiltersCount++;
    });
    
    // Collect pill filters
    modal.querySelectorAll('.hero-filter-pill.active').forEach(pill => {
        const filterType = pill.dataset.filter;
        const value = pill.value;
        
        if (!heroSearchState.filters[filterType]) {
            heroSearchState.filters[filterType] = [];
        }
        heroSearchState.filters[filterType].push(value);
        heroSearchState.activeFiltersCount++;
    });
    
    updateHeroFiltersBadge();
    closeHeroFiltersModal();
}

function resetHeroFilters() {
    const modal = document.getElementById('hero-filters-modal');
    if (!modal) return;
    
    modal.querySelectorAll('input[type="checkbox"]').forEach(checkbox => {
        checkbox.checked = false;
    });
    
    modal.querySelectorAll('.hero-filter-pill').forEach(pill => {
        pill.classList.remove('active');
    });
    
    heroSearchState.filters = {};
    heroSearchState.activeFiltersCount = 0;
    updateHeroFiltersBadge();
}

function closeHeroFiltersModal() {
    const modal = document.getElementById('hero-filters-modal');
    if (modal) {
        modal.style.display = 'none';
    }
    const filtersField = document.getElementById('hero-search-filters');
    if (filtersField) filtersField.classList.remove('active');
}

function updateHeroFiltersBadge() {
    const badge = document.getElementById('hero-filters-badge');
    if (!badge) return;
    
    if (heroSearchState.activeFiltersCount > 0) {
        badge.textContent = heroSearchState.activeFiltersCount;
        badge.style.display = 'inline-flex';
    } else {
        badge.textContent = '';
        badge.style.display = 'none';
    }
}

// ============================================
// SEARCH BUTTON
// ============================================
function initHeroSearchButton() {
    const searchButton = document.getElementById('hero-search-button');
    if (!searchButton) return;
    
    searchButton.addEventListener('click', performHeroSearch);
    
    // Enter key on address input
    const addressInput = document.getElementById('hero-address-input');
    if (addressInput) {
        addressInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                performHeroSearch();
            }
        });
    }
}

function performHeroSearch() {
    const searchButton = document.getElementById('hero-search-button');
    if (!searchButton) return;
    
    // Validation
    if (!heroSearchState.address && !heroSearchState.lat) {
        // Default to Toulouse if no address
        heroSearchState.address = 'Toulouse, France';
        heroSearchState.lat = 43.6047;
        heroSearchState.lng = 1.4442;
    }
    
    // Loading state
    searchButton.disabled = true;
    searchButton.classList.add('loading');
    const originalText = searchButton.querySelector('span').textContent;
    searchButton.querySelector('span').textContent = 'Recherche...';
    
    // Build URL params
    const params = new URLSearchParams();
    if (heroSearchState.address) params.append('address', heroSearchState.address);
    if (heroSearchState.lat) params.append('lat', heroSearchState.lat);
    if (heroSearchState.lng) params.append('lng', heroSearchState.lng);
    if (heroSearchState.budgetMin) params.append('price_min', heroSearchState.budgetMin);
    if (heroSearchState.budgetMax) params.append('price_max', heroSearchState.budgetMax);
    
    // Add filters
    Object.keys(heroSearchState.filters).forEach(key => {
        heroSearchState.filters[key].forEach(value => {
            params.append(key, value);
        });
    });
    
    // Redirect to map
    setTimeout(() => {
        window.location.href = `/map/?${params.toString()}`;
    }, 500);
}

// ============================================
// QUICK FILTERS
// ============================================
function initHeroQuickFilters() {
    document.querySelectorAll('.hero-quick-filter').forEach(btn => {
        btn.addEventListener('click', function() {
            const filter = this.dataset.filter;
            applyQuickFilter(filter);
        });
    });
}

function applyQuickFilter(filter) {
    // Remove active class from all
    document.querySelectorAll('.hero-quick-filter').forEach(btn => {
        btn.classList.remove('active');
    });
    
    // Add active to clicked
    const clicked = document.querySelector(`.hero-quick-filter[data-filter="${filter}"]`);
    if (clicked) clicked.classList.add('active');
    
    // Apply filter logic
    switch(filter) {
        case 'affordable':
            heroSearchState.budgetMin = null;
            heroSearchState.budgetMax = 600;
            updateHeroBudgetDisplay();
            break;
        case 'nearby':
            // Use geolocation
            if (navigator.geolocation) {
                navigator.geolocation.getCurrentPosition((position) => {
                    heroSearchState.lat = position.coords.latitude;
                    heroSearchState.lng = position.coords.longitude;
                    document.getElementById('hero-address-input').value = 'Proche de moi';
                });
            }
            break;
        case 'premium':
            heroSearchState.budgetMin = 2000;
            heroSearchState.budgetMax = null;
            updateHeroBudgetDisplay();
            break;
        case 'high-rated':
            // Add rating filter
            if (!heroSearchState.filters.rating) {
                heroSearchState.filters.rating = [];
            }
            heroSearchState.filters.rating.push('4+');
            updateHeroFiltersBadge();
            break;
    }
}

// ============================================
// UTILITIES
// ============================================
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

function initHeroSearchBar() {
    // Initialize any additional hero search bar functionality
    console.log('Hero search bar initialized');
}















