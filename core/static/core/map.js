// ============================================
// MAP_PHASE4_PRO.JS - JavaScript Pro Upgraded
// Avec Google Places, géolocalisation, clustering, pagination
// ============================================

let map;
let markerClusterGroup;
let userMarker = null;
let currentLogements = [];
let allLogements = [];
let searchCircle = null;
let lastSearchLat = 43.6047;
let lastSearchLng = 1.4422;
let currentRadius = 10;
let currentFilters = {};
let googleAutocompleteService;
let googlePlacesService;

// Pagination
let currentPage = 1;
let itemsPerPage = 20;

const TOULOUSE_LAT = 43.6047;
const TOULOUSE_LNG = 1.4422;

// ============================================
// INITIALISATION
// ============================================

document.addEventListener('DOMContentLoaded', function() {
    initMap();
    initGooglePlaces();
    initEventListeners();
});

function initMap() {
    map = L.map('map').setView([TOULOUSE_LAT, TOULOUSE_LNG], 13);
    
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors',
        maxZoom: 19,
    }).addTo(map);
    
    // Marker cluster group
    markerClusterGroup = L.markerClusterGroup({
        maxClusterRadius: 80,
        iconCreateFunction: function(cluster) {
            const count = cluster.getChildCount();
            let size = 'small';
            let radius = 28;
            if (count > 100) { size = 'large'; radius = 40; }
            else if (count > 50) { size = 'medium'; radius = 34; }
            
            return L.divIcon({
                html: `<div style="background: rgba(211, 88, 11, 0.8); color: white; width: ${radius*2}px; height: ${radius*2}px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: bold; font-size: 14px; box-shadow: 0 2px 8px rgba(0,0,0,0.3); border: 2px solid white;">${count}</div>`,
                iconSize: [radius*2, radius*2],
            });
        }
    });
    map.addLayer(markerClusterGroup);
    
    L.control.zoom({ position: 'bottomright' }).addTo(map);
}

function initGooglePlaces() {
    if (typeof google === 'undefined') {
        console.warn('Google Maps API non chargée');
        return;
    }
    
    googleAutocompleteService = new google.maps.places.AutocompleteService();
    googlePlacesService = new google.maps.places.PlacesService(map);
}

function initEventListeners() {
    // Geolocalisation
    const btnGeoloc = document.getElementById('btn-geoloc');
    if (btnGeoloc) {
        btnGeoloc.addEventListener('click', geolocateUser);
    }
    
    // Nouvelle barre de recherche moderne
    initModernSearchBar();
    
    // Rayon
    const radiusSelect = document.getElementById('radius-select');
    if (radiusSelect) {
        radiusSelect.addEventListener('change', function() {
            const newRadius = parseFloat(this.value);
            if (currentRadius !== newRadius) {
                currentRadius = newRadius;
                if (lastSearchLat && lastSearchLng) {
                    loadLogementsByRadius(lastSearchLat, lastSearchLng, currentRadius);
                    updateSearchCircle();
                }
            }
        });
    }
    
    // Tri
    const sortSelect = document.getElementById('sort-select');
    if (sortSelect) {
        sortSelect.addEventListener('change', function() {
            if (currentLogements.length > 0) {
                const sorted = applySortToLogements(currentLogements, this.value);
                currentPage = 1;
                displayPaginatedLogements(sorted);
            }
        });
    }
    
    // Pagination
    const btnPrevPage = document.getElementById('btn-prev-page');
    if (btnPrevPage) {
        btnPrevPage.addEventListener('click', function() {
            if (currentPage > 1) {
                currentPage--;
                displayPaginatedLogements(currentLogements);
            }
        });
    }
    
    const btnNextPage = document.getElementById('btn-next-page');
    if (btnNextPage) {
        btnNextPage.addEventListener('click', function() {
            const maxPages = Math.ceil(currentLogements.length / itemsPerPage);
            if (currentPage < maxPages) {
                currentPage++;
                displayPaginatedLogements(currentLogements);
            }
        });
    }
}

// Initialisation de la nouvelle barre de recherche moderne
function initModernSearchBar() {
    const input = document.getElementById('search-input-destination');
    const dropdown = document.getElementById('autocomplete-dropdown-destination');
    const display = document.getElementById('search-display-destination');
    const field = document.getElementById('search-field-destination');
    const btnSearch = document.getElementById('btn-search-modern');
    let selectedIndex = -1;
    let autocompleteResults = [];

    if (!input || !field) return;

    // Click sur le champ pour activer l'input
    field.addEventListener('click', (e) => {
        if (e.target === input) return;
        e.preventDefault();
        e.stopPropagation();
        input.focus();
        input.style.position = 'static';
        input.style.opacity = '1';
        input.style.pointerEvents = 'auto';
        if (display) display.style.display = 'none';
    });

    // Focus sur l'input
    input.addEventListener('focus', () => {
        input.style.position = 'static';
        input.style.opacity = '1';
        input.style.pointerEvents = 'auto';
        if (display) display.style.display = 'none';
    });

    // Blur sur l'input
    input.addEventListener('blur', () => {
        if (!input.value.trim()) {
            input.style.position = 'absolute';
            input.style.opacity = '0';
            input.style.pointerEvents = 'none';
            if (display) display.style.display = 'block';
        }
    });

    // Autocomplétion BAN API
    input.addEventListener('input', debounce(async (e) => {
        const query = e.target.value.trim();
        
        if (query.length < 2) {
            if (dropdown) dropdown.classList.remove('active');
            return;
        }

        try {
            const banUrl = `https://api-adresse.data.gouv.fr/search/?q=${encodeURIComponent(query)}&limit=8&type=housenumber&type=street&type=locality`;
            
            const response = await fetch(banUrl);
            const data = await response.json();
            
            if (data.features && data.features.length > 0) {
                autocompleteResults = data.features.map(feature => {
                    const props = feature.properties;
                    const coords = feature.geometry.coordinates;
                    return {
                        address: props.label,
                        latitude: coords[1],
                        longitude: coords[0],
                        display_name: props.label,
                        short_name: props.name || props.label.split(',')[0],
                        city: props.city || '',
                        postcode: props.postcode || ''
                    };
                });
                selectedIndex = -1;
                
                if (dropdown) {
                    dropdown.innerHTML = autocompleteResults.map((result, index) => {
                        const shortName = result.short_name;
                        const fullAddress = result.display_name.length > 60 ? result.display_name.substring(0, 60) + '...' : result.display_name;
                        return `<div class="autocomplete-item-modern" data-index="${index}">
                            <div class="autocomplete-item-main">
                                <div>${shortName}</div>
                                <div class="autocomplete-item-sub">${fullAddress}</div>
                            </div>
                        </div>`;
                    }).join('');
                    dropdown.classList.add('active');
                }
            } else {
                if (dropdown) dropdown.classList.remove('active');
            }
        } catch (error) {
            console.error('Autocomplete error:', error);
            if (dropdown) dropdown.classList.remove('active');
        }
    }, 300));

    // Navigation clavier
    input.addEventListener('keydown', (e) => {
        if (!dropdown || !dropdown.classList.contains('active')) return;

        if (e.key === 'ArrowDown') {
            e.preventDefault();
            selectedIndex = Math.min(selectedIndex + 1, autocompleteResults.length - 1);
            updateSelectedItem();
        } else if (e.key === 'ArrowUp') {
            e.preventDefault();
            selectedIndex = Math.max(selectedIndex - 1, -1);
            updateSelectedItem();
        } else if (e.key === 'Enter' && selectedIndex >= 0) {
            e.preventDefault();
            selectAddress(autocompleteResults[selectedIndex]);
        } else if (e.key === 'Enter') {
            e.preventDefault();
            performMapSearch();
        }
    });

    // Click sur un résultat d'autocomplétion
    if (dropdown) {
        dropdown.addEventListener('click', (e) => {
            const item = e.target.closest('.autocomplete-item-modern');
            if (item) {
                const index = parseInt(item.dataset.index);
                selectAddress(autocompleteResults[index]);
            }
        });
    }

    function updateSelectedItem() {
        if (!dropdown) return;
        dropdown.querySelectorAll('.autocomplete-item-modern').forEach((item, index) => {
            item.style.background = index === selectedIndex ? 'rgba(211, 88, 11, 0.1)' : '';
        });
    }

    function selectAddress(result) {
        const address = result.address || result.display_name || result.label || '';
        const shortName = result.short_name || address.split(',')[0] || address;
        lastSearchLat = result.latitude || result.lat;
        lastSearchLng = result.longitude || result.lng;
        if (display) display.textContent = shortName;
        input.value = shortName;
        if (dropdown) dropdown.classList.remove('active');
        
        // Centrer la carte sur l'adresse sélectionnée
        if (lastSearchLat && lastSearchLng) {
            map.setView([lastSearchLat, lastSearchLng], 14);
            updateSearchCircle();
            loadLogementsByRadius(lastSearchLat, lastSearchLng, currentRadius);
        }
    }

    // Bouton recherche
    if (btnSearch) {
        btnSearch.addEventListener('click', performMapSearch);
    }

    // Click outside to close
    document.addEventListener('click', (e) => {
        if (input && dropdown && !input.contains(e.target) && !dropdown.contains(e.target)) {
            dropdown.classList.remove('active');
        }
    });
}

// Fonction de recherche pour la carte
function performMapSearch() {
    const input = document.getElementById('search-input-destination');
    if (!input) return;
    
    const query = input.value.trim();
    
    if (query.length < 2) {
        alert('Veuillez entrer une adresse');
        return;
    }
    
    // Si on a déjà des coordonnées, utiliser directement
    if (lastSearchLat && lastSearchLng) {
        loadLogementsByRadius(lastSearchLat, lastSearchLng, currentRadius);
        return;
    }
    
    // Sinon, chercher l'adresse
    fetch(`https://api-adresse.data.gouv.fr/search/?q=${encodeURIComponent(query)}&limit=1`)
        .then(response => response.json())
        .then(data => {
            if (data.features && data.features.length > 0) {
                const feature = data.features[0];
                const coords = feature.geometry.coordinates;
                lastSearchLat = coords[1];
                lastSearchLng = coords[0];
                map.setView([lastSearchLat, lastSearchLng], 14);
                updateSearchCircle();
                loadLogementsByRadius(lastSearchLat, lastSearchLng, currentRadius);
            } else {
                alert('Adresse non trouvée');
            }
        })
        .catch(error => {
            console.error('Erreur recherche:', error);
            alert('Erreur lors de la recherche');
        });
}

function debounce(func, wait) {
    let timeout;
    return function(...args) {
        clearTimeout(timeout);
        timeout = setTimeout(() => func.apply(this, args), wait);
    };
}

// ============================================
// GÉOLOCALISATION
// ============================================

function geolocateUser() {
    const btn = document.getElementById('btn-geoloc');
    btn.classList.add('loading');
    
    if (!navigator.geolocation) {
        alert('Géolocalisation non supportée');
        btn.classList.remove('loading');
        return;
    }
    
    navigator.geolocation.getCurrentPosition(function(position) {
        const { latitude, longitude } = position.coords;
        
        lastSearchLat = latitude;
        lastSearchLng = longitude;
        currentPage = 1;
        
        // Ajouter marqueur utilisateur amélioré
        if (userMarker) map.removeLayer(userMarker);
        userMarker = L.marker([latitude, longitude], {
            icon: L.divIcon({
                html: `
                    <div style="
                        background: linear-gradient(135deg, #D3580B 0%, #c4510a 100%);
                        color: white;
                        width: 56px;
                        height: 56px;
                        border-radius: 50%;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        font-weight: bold;
                        font-size: 24px;
                        box-shadow: 0 0 0 4px white, 0 0 0 6px rgba(211, 88, 11, 0.3), 0 4px 12px rgba(0,0,0,0.3);
                        border: 3px solid #D3580B;
                        animation: pulse-user-marker 2s infinite;
                    ">
                        <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"></path>
                            <circle cx="12" cy="10" r="3"></circle>
                        </svg>
                    </div>
                `,
                iconSize: [56, 56],
                className: 'user-marker-wrapper'
            })
        });
        userMarker.bindPopup('<strong>Vous êtes ici</strong>').addTo(map);
        
        map.setView([latitude, longitude], 14);
        updateSearchCircle();
        loadLogementsByRadius(latitude, longitude, currentRadius);
        
        btn.classList.remove('loading');
        
        // Mettre à jour le champ d'adresse si présent
        const display = document.getElementById('search-display-destination');
        const input = document.getElementById('search-input-destination');
        if (display) display.textContent = 'Ma localisation';
        if (input) input.value = 'Ma localisation';
        
    }, function(error) {
        console.error('Erreur géolocalisation:', error);
        alert('Erreur lors de la géolocalisation');
        btn.classList.remove('loading');
    });
}

// ============================================
// GOOGLE PLACES AUTOCOMPLETE
// ============================================

function handleGooglePlacesInput(e) {
    const query = e.target.value;
    const autocompleteDiv = document.getElementById('search-autocomplete');
    
    if (query.length < 2) {
        autocompleteDiv.classList.remove('active');
        return;
    }
    
    if (!googleAutocompleteService) {
        fallbackAutocomplete(query);
        return;
    }
    
    googleAutocompleteService.getPlacePredictions(
        {
            input: query,
            componentRestrictions: { country: 'fr' },
            location: new google.maps.LatLng(TOULOUSE_LAT, TOULOUSE_LNG),
            radius: 50000,
        },
        function(predictions, status) {
            if (status !== google.maps.places.PlacesServiceStatus.OK || !predictions) {
                autocompleteDiv.classList.remove('active');
                return;
            }
            
            autocompleteDiv.innerHTML = predictions.map((pred, idx) => `
                <div class="autocomplete-item" onclick="selectGooglePlace('${pred.place_id}')">
                    <div class="autocomplete-title">${pred.main_text}</div>
                    <div class="autocomplete-subtitle">${pred.secondary_text || ''}</div>
                </div>
            `).join('');
            
            autocompleteDiv.classList.add('active');
        }
    );
}

function selectGooglePlace(placeId) {
    if (!googlePlacesService) return;
    
    googlePlacesService.getDetails(
        { placeId: placeId },
        function(place, status) {
            if (status !== google.maps.places.PlacesServiceStatus.OK) return;
            
            const lat = place.geometry.location.lat();
            const lng = place.geometry.location.lng();
            
            selectSearchResult(lat, lng, place.formatted_address);
        }
    );
}

function fallbackAutocomplete(query) {
    // Fallback si Google API pas disponible
    let searchQuery = query;
    if (!query.toLowerCase().includes('toulouse')) {
        searchQuery += ', Toulouse';
    }
    
    const autocompleteDiv = document.getElementById('search-autocomplete');
    
    fetch(`/api/map/search-address-advanced/?q=${encodeURIComponent(searchQuery)}&limit=5&radius=${currentRadius}`)
        .then(r => r.json())
        .then(data => {
            if (!data.results || data.results.length === 0) {
                autocompleteDiv.innerHTML = '<div class="autocomplete-item">Aucun résultat</div>';
                autocompleteDiv.classList.add('active');
                return;
            }
            
            autocompleteDiv.innerHTML = data.results.map(result => `
                <div class="autocomplete-item" onclick="selectSearchResult(${result.latitude}, ${result.longitude}, '${result.display_name.split(',')[0]}')">
                    <div class="autocomplete-title">${result.display_name.split(',')[0]}</div>
                    <div class="autocomplete-subtitle">${result.display_name}</div>
                </div>
            `).join('');
            
            autocompleteDiv.classList.add('active');
        });
}

function performSearch() {
    const query = document.getElementById('search-address').value;
    
    if (query.length < 2) {
        alert('Veuillez entrer une adresse');
        return;
    }
    
    // Si utilise Google Places
    if (googleAutocompleteService && query !== 'Ma localisation') {
        googleAutocompleteService.getPlacePredictions(
            {
                input: query,
                componentRestrictions: { country: 'fr' },
            },
            function(predictions, status) {
                if (predictions && predictions.length > 0) {
                    selectGooglePlace(predictions[0].place_id);
                } else {
                    fallbackPerformSearch(query);
                }
            }
        );
    } else if (query === 'Ma localisation') {
        // Déjà géolocalisé
    } else {
        fallbackPerformSearch(query);
    }
}

function fallbackPerformSearch(query) {
    let searchQuery = query;
    if (!query.toLowerCase().includes('toulouse')) {
        searchQuery += ', Toulouse';
    }
    
    fetch(`/api/map/search-address-advanced/?q=${encodeURIComponent(searchQuery)}&limit=1&radius=${currentRadius}`)
        .then(r => r.json())
        .then(data => {
            if (!data.center) {
                alert('Adresse non trouvée');
                return;
            }
            selectSearchResult(data.center.latitude, data.center.longitude, query);
        })
        .catch(error => {
            console.error('Erreur:', error);
            alert('Erreur lors de la recherche');
        });
}

function selectSearchResult(lat, lng, address) {
    document.getElementById('search-address').value = address;
    document.getElementById('search-autocomplete').classList.remove('active');
    
    lastSearchLat = lat;
    lastSearchLng = lng;
    currentPage = 1;
    
    map.setView([lat, lng], 14);
    updateSearchCircle();
    loadLogementsByRadius(lat, lng, currentRadius);
}

function updateSearchCircle() {
    if (searchCircle) {
        map.removeLayer(searchCircle);
    }
    
    searchCircle = L.circle([lastSearchLat, lastSearchLng], {
        color: '#D3580B',
        fill: true,
        fillColor: '#D3580B',
        fillOpacity: 0.1,
        weight: 2,
        radius: currentRadius * 1000,
        dashArray: '5, 5'
    }).addTo(map);
}

// ============================================
// CHARGEMENT LOGEMENTS
// ============================================

function loadLogementsByRadius(lat, lng, radius) {
    let url = `/api/map/logements-by-radius/?lat=${lat}&lng=${lng}&radius=${radius}`;
    
    if (currentFilters.price_min) url += `&price_min=${currentFilters.price_min}`;
    if (currentFilters.price_max) url += `&price_max=${currentFilters.price_max}`;
    if (currentFilters.surface_min) url += `&surface_min=${currentFilters.surface_min}`;
    if (currentFilters.rating_min) url += `&rating_min=${currentFilters.rating_min}`;
    if (currentFilters.type_logement) url += `&type_logement=${currentFilters.type_logement}`;
    if (currentFilters.chambres) url += `&chambres=${currentFilters.chambres}`;
    
    fetch(url)
        .then(response => response.json())
        .then(data => {
            if (!data.success) {
                console.error('Erreur API:', data.error);
                return;
            }
            
            const sort = document.getElementById('sort-select').value;
            allLogements = applySortToLogements(data.logements, sort);
            currentLogements = allLogements;
            
            // Mettre à jour marqueurs
            markerClusterGroup.clearLayers();
            displayAllMarkers(currentLogements);
            
            // Afficher première page
            displayPaginatedLogements(currentLogements);
        })
        .catch(error => {
            console.error('Erreur chargement:', error);
            document.getElementById('logements-list').innerHTML = '<div class="loading">Erreur lors du chargement</div>';
        });
}

function displayAllMarkers(logements) {
    logements.forEach(log => {
        // Créer un pin moderne avec SVG
        const price = Math.round(log.prix);
        const icon = L.divIcon({
            html: `
                <div class="custom-marker-map" style="
                    background: linear-gradient(135deg, #D3580B 0%, #c4510a 100%);
                    color: white;
                    width: 48px;
                    height: 48px;
                    border-radius: 50% 50% 50% 0;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    font-weight: bold;
                    font-size: 18px;
                    box-shadow: 0 4px 12px rgba(211, 88, 11, 0.4), 0 0 0 3px white;
                    border: none;
                    cursor: pointer;
                    transform: rotate(-45deg);
                    transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
                    position: relative;
                ">
                    <div style="transform: rotate(45deg); display: flex; align-items: center; justify-content: center;">
                        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path>
                            <polyline points="9 22 9 12 15 12 15 22"></polyline>
                        </svg>
                    </div>
                </div>
            `,
            iconSize: [48, 48],
            className: 'custom-marker-wrapper'
        });
        
        const marker = L.marker([log.latitude, log.longitude], { icon });
        
        // Popup améliorée
        const ratingStars = log.note > 0 ? '⭐'.repeat(Math.min(Math.round(log.note), 5)) : 'N/A';
        const popupContent = `
            <div style="font-size: 13px; width: 220px; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;">
                <div style="font-weight: 700; font-size: 15px; margin-bottom: 8px; color: #1a1a1a;">${log.titre}</div>
                <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 6px;">
                    <span style="font-weight: 700; color: #D3580B; font-size: 16px;">${price}€</span>
                    <span style="color: #666; font-size: 12px;">/mois</span>
                </div>
                <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 8px; font-size: 12px; color: #666;">
                    <span>${Math.round(log.surface)}m²</span>
                    <span>•</span>
                    <span>${log.chambres} ch.</span>
                    ${log.note > 0 ? `<span>•</span><span>${log.note.toFixed(1)} ${ratingStars}</span>` : ''}
                </div>
                ${log.distance ? `<div style="font-size: 11px; color: #999; margin-bottom: 8px;">📍 ${log.distance} km</div>` : ''}
                <a href="/logement/${log.id}/" style="
                    display: inline-block;
                    width: 100%;
                    text-align: center;
                    margin-top: 8px;
                    padding: 8px 12px;
                    background: linear-gradient(135deg, #D3580B 0%, #c4510a 100%);
                    color: white;
                    border-radius: 8px;
                    text-decoration: none;
                    font-weight: 600;
                    font-size: 12px;
                    transition: all 0.2s ease;
                " onmouseover="this.style.transform='translateY(-1px)'; this.style.boxShadow='0 4px 12px rgba(211, 88, 11, 0.4)'" onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='none'">Voir détail →</a>
            </div>
        `;
        
        marker.bindPopup(popupContent, {
            maxWidth: 250,
            className: 'custom-popup-map'
        });
        
        // Animation au survol
        marker.on('mouseover', function() {
            this.setIcon(L.divIcon({
                html: `
                    <div class="custom-marker-map" style="
                        background: linear-gradient(135deg, #D3580B 0%, #c4510a 100%);
                        color: white;
                        width: 56px;
                        height: 56px;
                        border-radius: 50% 50% 50% 0;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        font-weight: bold;
                        font-size: 20px;
                        box-shadow: 0 6px 20px rgba(211, 88, 11, 0.5), 0 0 0 3px white;
                        border: none;
                        cursor: pointer;
                        transform: rotate(-45deg) scale(1.1);
                        transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
                    ">
                        <div style="transform: rotate(45deg); display: flex; align-items: center; justify-content: center;">
                            <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path>
                                <polyline points="9 22 9 12 15 12 15 22"></polyline>
                            </svg>
                        </div>
                    </div>
                `,
                iconSize: [56, 56],
                className: 'custom-marker-wrapper'
            }));
        });
        
        marker.on('mouseout', function() {
            this.setIcon(icon);
        });
        
        marker.on('click', () => {
            selectLogement(log.id);
            marker.openPopup();
        });
        
        markerClusterGroup.addLayer(marker);
    });
}

// ============================================
// AFFICHAGE PAGINÉ
// ============================================

function displayPaginatedLogements(logements) {
    if (!logements || logements.length === 0) {
        document.getElementById('logements-list').innerHTML = '<div class="loading">Aucun logement trouvé</div>';
        document.getElementById('pagination').style.display = 'none';
        return;
    }
    
    const totalPages = Math.ceil(logements.length / itemsPerPage);
    const startIdx = (currentPage - 1) * itemsPerPage;
    const endIdx = startIdx + itemsPerPage;
    const pageLogements = logements.slice(startIdx, endIdx);
    
    document.getElementById('logements-list').innerHTML = pageLogements.map(log => createLogementCard(log)).join('');
    
    // Mise à jour pagination
    document.getElementById('current-page').textContent = currentPage;
    document.getElementById('total-pages').textContent = totalPages;
    document.getElementById('btn-prev-page').disabled = currentPage === 1;
    document.getElementById('btn-next-page').disabled = currentPage === totalPages;
    document.getElementById('pagination').style.display = logements.length > itemsPerPage ? 'flex' : 'none';
}

function createLogementCard(log) {
    const stars = '⭐'.repeat(Math.round(log.note || 0));
    
    return `
        <div class="logement-card" id="card-${log.id}">
            <div class="card-header">
                <h3 class="card-title">${log.titre}</h3>
                <div class="card-price">${Math.round(log.prix)}€</div>
            </div>
            
            <div class="card-rating">
                <span class="stars">${stars}</span>
                <span>${(log.note || 0).toFixed(1)} (${log.nombre_avis || 0})</span>
            </div>
            
            <div class="card-meta">
                <span>${Math.round(log.surface)}m²</span>
                <span>${log.chambres}ch</span>
                <span>${log.type}</span>
            </div>
            
            <div class="card-distance">📍 ${log.distance} km</div>
            
            <div class="card-buttons">
                <button class="btn-small btn-favori" onclick="event.stopPropagation(); toggleFavori(${log.id})">❤️</button>
                <a href="/logement/${log.id}/" class="btn-small btn-detail">Voir plus →</a>
            </div>
        </div>
    `;
}

function selectLogement(logementId) {
    const log = allLogements.find(l => l.id === logementId);
    if (!log) return;
    
    // Scroll à la page du logement
    const pageNum = Math.ceil(allLogements.indexOf(log) / itemsPerPage + 1);
    if (currentPage !== pageNum) {
        currentPage = pageNum;
        displayPaginatedLogements(allLogements);
    }
    
    const card = document.getElementById(`card-${logementId}`);
    if (card) {
        card.classList.add('active');
        card.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }
}

// ============================================
// FILTERS_ADVANCED.JS - Gestion filtres avancés
// ============================================

class AdvancedFilters {
    constructor() {
        this.filters = {};
        this.activeFiltersCount = 0;
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.setupSectionCollapse();
        this.updateActiveCount();
    }

    setupEventListeners() {
        // Ouvrir/Fermer filtres
        document.getElementById('btn-filters')?.addEventListener('click', () => {
            document.getElementById('filters-panel').classList.add('active');
        });

        document.getElementById('btn-close-filters')?.addEventListener('click', () => {
            document.getElementById('filters-panel').classList.remove('active');
        });

        // Range inputs
        document.getElementById('filter-price-min')?.addEventListener('input', () => this.updatePriceDisplay());
        document.getElementById('filter-price-max')?.addEventListener('input', () => this.updatePriceDisplay());
        document.getElementById('filter-surface-min')?.addEventListener('input', () => this.updateSurfaceDisplay());
        document.getElementById('filter-surface-max')?.addEventListener('input', () => this.updateSurfaceDisplay());

        // Checkboxes/Radios change
        document.querySelectorAll('input[type="checkbox"], input[type="radio"]').forEach(input => {
            input.addEventListener('change', () => this.updateActiveCount());
        });

        // Boutons actions
        document.getElementById('btn-apply-filters')?.addEventListener('click', () => this.applyFilters());
        document.getElementById('btn-reset-filters')?.addEventListener('click', () => this.resetFilters());

        // Fermer au clic dehors
        document.addEventListener('click', (e) => {
            const panel = document.getElementById('filters-panel');
            const btnFilters = document.getElementById('btn-filters');
            if (panel && btnFilters && !panel.contains(e.target) && !btnFilters.contains(e.target)) {
                panel.classList.remove('active');
            }
        });
    }

    setupSectionCollapse() {
        document.querySelectorAll('.section-header').forEach(header => {
            header.addEventListener('click', () => {
                const section = header.closest('.filters-section');
                section.classList.toggle('collapsed');
            });
        });
    }

    updatePriceDisplay() {
        const min = document.getElementById('filter-price-min').value;
        const max = document.getElementById('filter-price-max').value;
        const display = document.getElementById('price-display');
        
        if (min || max) {
            const minText = min ? `${min}€` : '0€';
            const maxText = max ? `${max}€` : '∞€';
            display.textContent = `${minText} - ${maxText}`;
        } else {
            display.textContent = 'Tous les prix';
        }
    }

    updateSurfaceDisplay() {
        const min = document.getElementById('filter-surface-min').value;
        const max = document.getElementById('filter-surface-max').value;
        const display = document.getElementById('surface-display');
        
        if (min || max) {
            const minText = min ? `${min}m²` : '0m²';
            const maxText = max ? `${max}m²` : '∞m²';
            display.textContent = `${minText} - ${maxText}`;
        } else {
            display.textContent = 'Toutes surfaces';
        }
    }

    updateActiveCount() {
        const checkboxes = document.querySelectorAll('input[type="checkbox"]:checked, input[type="radio"]:checked');
        this.activeFiltersCount = checkboxes.length;
        
        // Range inputs
        if (document.getElementById('filter-price-min').value) this.activeFiltersCount++;
        if (document.getElementById('filter-price-max').value) this.activeFiltersCount++;
        if (document.getElementById('filter-surface-min').value) this.activeFiltersCount++;
        if (document.getElementById('filter-surface-max').value) this.activeFiltersCount++;

        const counter = document.getElementById('filters-count');
        if (counter) {
            counter.textContent = this.activeFiltersCount > 0 
                ? `${this.activeFiltersCount} filtres actifs`
                : '0 filtres actifs';
        }
    }

    gatherFilters() {
        this.filters = {
            types: Array.from(document.querySelectorAll('input[name="type"]:checked')).map(el => el.value),
            price_min: document.getElementById('filter-price-min').value,
            price_max: document.getElementById('filter-price-max').value,
            surface_min: document.getElementById('filter-surface-min').value,
            surface_max: document.getElementById('filter-surface-max').value,
            pieces: document.querySelector('input[name="pieces"]:checked')?.value,
            chambres: document.querySelector('input[name="chambres"]:checked')?.value,
            rating_min: document.querySelector('input[name="rating"]:checked')?.value,
            reviews_min: document.querySelector('input[name="reviews-min"]:checked')?.value,
            amenities: Array.from(document.querySelectorAll('input[name="amenities"]:checked')).map(el => el.value),
            exteriors: Array.from(document.querySelectorAll('input[name="exteriors"]:checked')).map(el => el.value),
            criteria: Array.from(document.querySelectorAll('input[name="criteria"]:checked')).map(el => el.value),
            dpe: Array.from(document.querySelectorAll('input[name="dpe"]:checked')).map(el => el.value),
        };
        
        return this.filters;
    }

    applyFilters() {
        this.gatherFilters();
        document.getElementById('filters-panel').classList.remove('active');
        
        // Trigger search avec les filtres
        if (window.loadLogements) {
            window.loadLogements();
        }
    }

    resetFilters() {
        // Reset range inputs
        document.getElementById('filter-price-min').value = '';
        document.getElementById('filter-price-max').value = '';
        document.getElementById('filter-surface-min').value = '';
        document.getElementById('filter-surface-max').value = '';

        // Reset checkboxes/radios
        document.querySelectorAll('input[type="checkbox"], input[type="radio"]').forEach(input => {
            input.checked = false;
        });

        // Reset displays
        this.updatePriceDisplay();
        this.updateSurfaceDisplay();
        this.updateActiveCount();

        // Reset filters object
        this.filters = {};
    }

    getFiltersForAPI() {
        return this.filters;
    }
}

// ============================================
// CLUSTERS OPTIMISÉS
// ============================================

class OptimizedClusters {
    static createClusterIcon(cluster) {
        const count = cluster.getChildCount();
        let size = 32;
        let className = 'marker-cluster-small';

        if (count > 50) {
            size = 48;
            className = 'marker-cluster-large';
        } else if (count > 20) {
            size = 40;
            className = 'marker-cluster-medium';
        }

        return L.divIcon({
            html: `<div class="marker-cluster ${className}"><div>${count}</div></div>`,
            iconSize: [size, size],
            className: 'cluster-marker',
        });
    }

    static initClusterGroup(map) {
        const clusterGroup = L.markerClusterGroup({
            maxClusterRadius: 50, // Plus petit rayon pour plus de clustering
            iconCreateFunction: this.createClusterIcon,
            chunkedLoading: true,
        });

        map.addLayer(clusterGroup);
        return clusterGroup;
    }
}

// ============================================
// MAP MARKERS CUSTOM
// ============================================

class CustomMarkers {
    static createMarker(logement) {
        const icon = L.divIcon({
            html: `<div class="custom-marker">🏠</div>`,
            iconSize: [40, 40],
            className: 'custom-marker-container',
        });

        const marker = L.marker([logement.latitude, logement.longitude], { icon });

        // Popup content
        const popupContent = `
            <div class="marker-popup">
                <strong>${logement.titre}</strong><br>
                <span class="popup-price">${Math.round(logement.prix)}€/mois</span><br>
                <small>${Math.round(logement.surface)}m² • ${logement.chambres}ch</small><br>
                <small>⭐ ${(logement.note || 0).toFixed(1)} (${logement.nombre_avis || 0} avis)</small><br>
                <a href="/logement/${logement.id}/" class="popup-link">Voir détail →</a>
            </div>
        `;

        marker.bindPopup(popupContent, {
            maxWidth: 200,
            className: 'custom-popup',
        });

        marker.on('click', () => {
            if (window.selectLogement) {
                window.selectLogement(logement.id);
            }
        });

        return marker;
    }

    static createUserMarker(lat, lng, map) {
        const icon = L.divIcon({
            html: `<div class="user-marker">📍</div>`,
            iconSize: [50, 50],
            className: 'user-marker-container',
        });

        const marker = L.marker([lat, lng], { icon });
        marker.bindPopup('<strong>Votre position</strong>');
        marker.addTo(map);

        return marker;
    }
}

// ============================================
// INIT
// ============================================

let filtersManager;

document.addEventListener('DOMContentLoaded', () => {
    filtersManager = new AdvancedFilters();
});

// Export pour utilisation externe
window.AdvancedFilters = AdvancedFilters;
window.OptimizedClusters = OptimizedClusters;
window.CustomMarkers = CustomMarkers;

// ============================================
// TRI
// ============================================

function applySortToLogements(logements, sort) {
    const sorted = [...logements];
    
    switch(sort) {
        case 'notes':
            return sorted.sort((a, b) => (b.note || 0) - (a.note || 0));
        case 'prix-bas':
            return sorted.sort((a, b) => a.prix - b.prix);
        case 'prix-haut':
            return sorted.sort((a, b) => b.prix - a.prix);
        case 'proches':
            return sorted.sort((a, b) => a.distance - b.distance);
        case 'recents':
        default:
            return sorted;
    }
}

// ============================================
// FAVORIS
// ============================================

function toggleFavori(logementId) {
    fetch(`/api/map/logement/${logementId}/favori/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
            'Content-Type': 'application/json',
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            const btn = document.querySelector(`#card-${logementId} .btn-favori`);
            if (btn) {
                btn.textContent = data.is_favori ? '❤️' : '🤍';
                btn.classList.toggle('active', data.is_favori);
            }
        }
    })
    .catch(error => console.error('Erreur favori:', error));
}

// ============================================
// UTILITAIRES
// ============================================

function getCookie(name) {
    let value = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                value = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return value;
}