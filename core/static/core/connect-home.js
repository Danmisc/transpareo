// ========== NAVBAR INTERACTIONS ==========

// Système de recherche avancé style LinkedIn
class LinkedInSearch {
    constructor() {
        this.searchInput = document.getElementById('navbar-search-input');
        this.searchDropdown = document.getElementById('search-dropdown');
        this.searchTimeout = null;
        this.debounceDelay = 300;
        this.minQueryLength = 2;
        this.isSearching = false;
        
        if (this.searchInput && this.searchDropdown) {
            this.init();
        }
    }
    
    init() {
        // Focus sur l'input
        this.searchInput.addEventListener('focus', () => {
            const query = this.searchInput.value.trim();
            if (query.length >= this.minQueryLength) {
                this.performSearch(query);
            } else {
                this.showSearchHistory();
            }
        });
        
        // Input avec debounce
        this.searchInput.addEventListener('input', (e) => {
            this.handleInput(e.target.value.trim());
        });
        
        // Gestion de la touche Enter
        this.searchInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && this.searchInput.value.trim().length >= this.minQueryLength) {
                e.preventDefault();
                this.saveToHistory(this.searchInput.value.trim());
                this.goToSearchResults();
            }
            if (e.key === 'Escape') {
                this.hideDropdown();
            }
            // Navigation avec les flèches dans l'historique
            if ((e.key === 'ArrowDown' || e.key === 'ArrowUp') && !this.isSearching) {
                this.navigateHistory(e);
            }
        });
        
        // Fermer dropdown si click outside
        document.addEventListener('click', (e) => {
            const searchContainer = document.getElementById('navbar-search-container');
            if (searchContainer && !searchContainer.contains(e.target)) {
                this.hideDropdown();
            }
        });
        
        // Lien "Voir tous les résultats"
        const viewAllLink = document.getElementById('search-view-all');
        if (viewAllLink) {
            viewAllLink.addEventListener('click', (e) => {
                e.preventDefault();
                this.saveToHistory(this.searchInput.value.trim());
                this.goToSearchResults();
            });
        }
        
        // Charger l'historique au chargement
        this.loadSearchHistory();
    }
    
    handleInput(query) {
        clearTimeout(this.searchTimeout);
        
        if (query.length < this.minQueryLength) {
            if (query.length === 0) {
                this.showSearchHistory();
            } else {
                this.hideDropdown();
            }
            return;
        }
        
        this.searchTimeout = setTimeout(() => {
            this.performSearch(query);
        }, this.debounceDelay);
    }
    
    showSearchHistory() {
        const history = this.getSearchHistory();
        const suggestions = this.getSearchSuggestions();
        
        if (history.length === 0 && suggestions.length === 0) {
            this.hideDropdown();
            return;
        }
        
        // Afficher l'historique et les suggestions
        this.displayHistory(history, suggestions);
        this.showDropdown();
    }
    
    getSearchHistory() {
        try {
            const history = JSON.parse(localStorage.getItem('transpareo_search_history') || '[]');
            return history.slice(0, 5); // Garder seulement les 5 dernières recherches
        } catch (error) {
            return [];
        }
    }
    
    getSearchSuggestions() {
        // Suggestions basées sur les hashtags populaires, groupes populaires, etc.
        // Pour l'instant, on retourne des suggestions statiques
        // TODO: Charger dynamiquement depuis l'API
        return [
            'Colocation',
            'Bail',
            'Toulouse',
            'Locataires',
            'Propriétaires'
        ];
    }
    
    saveToHistory(query) {
        if (query.length < this.minQueryLength) return;
        
        try {
            let history = this.getSearchHistory();
            // Retirer si déjà présent
            history = history.filter(q => q.toLowerCase() !== query.toLowerCase());
            // Ajouter au début
            history.unshift(query);
            // Garder seulement les 10 dernières
            history = history.slice(0, 10);
            localStorage.setItem('transpareo_search_history', JSON.stringify(history));
        } catch (error) {
            console.error('Erreur sauvegarde historique:', error);
        }
    }
    
    loadSearchHistory() {
        // Charger l'historique au chargement si nécessaire
    }
    
    displayHistory(history, suggestions) {
        const resultsContainer = document.getElementById('search-results');
        const emptyContainer = document.getElementById('search-empty');
        const loadingContainer = document.getElementById('search-loading');
        const viewAllWrapper = document.getElementById('search-view-all-wrapper');
        
        // Masquer les autres sections
        loadingContainer.style.display = 'none';
        viewAllWrapper.style.display = 'none';
        
        // Créer le contenu de l'historique
        let historyHTML = '';
        
        if (history.length > 0) {
            historyHTML += '<div class="search-results-section" style="display: block;"><div class="search-section-header"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="9 18 15 12 9 6"></polyline></svg><h4>Recherches récentes</h4></div><div class="search-results-list">';
            
            history.forEach(query => {
                const escapedQuery = this.escapeHtml(query);
                historyHTML += `<button type="button" class="search-result-item" data-query="${escapedQuery}"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="flex-shrink: 0;"><polyline points="9 18 15 12 9 6"></polyline></svg><div class="search-result-info"><div class="search-result-name">${escapedQuery}</div></div><button type="button" class="search-history-remove" data-query="${escapedQuery}" onclick="event.stopPropagation(); linkedInSearch.removeFromHistory('${escapedQuery}')" aria-label="Supprimer"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg></button></button>`;
            });
            
            historyHTML += '</div></div>';
        }
        
        if (suggestions.length > 0) {
            historyHTML += '<div class="search-results-section" style="display: block;"><div class="search-section-header"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"></circle><path d="m21 21-4.35-4.35"></path></svg><h4>Suggestions</h4></div><div class="search-results-list">';
            
            suggestions.forEach(suggestion => {
                const escapedSuggestion = this.escapeHtml(suggestion);
                historyHTML += `<button type="button" class="search-result-item" data-query="${escapedSuggestion}"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="flex-shrink: 0;"><circle cx="11" cy="11" r="8"></circle><path d="m21 21-4.35-4.35"></path></svg><div class="search-result-info"><div class="search-result-name">${escapedSuggestion}</div></div></button>`;
            });
            
            historyHTML += '</div></div>';
        }
        
        if (historyHTML) {
            resultsContainer.innerHTML = historyHTML;
            resultsContainer.style.display = 'block';
            emptyContainer.style.display = 'none';
            
            // Ajouter les event listeners pour les boutons d'historique
            resultsContainer.querySelectorAll('.search-result-item[data-query]').forEach(button => {
                button.addEventListener('click', () => {
                    const query = button.getAttribute('data-query');
                    this.searchInput.value = query;
                    this.saveToHistory(query);
                    this.performSearch(query);
                });
            });
        } else {
            resultsContainer.style.display = 'none';
            emptyContainer.style.display = 'flex';
        }
    }
    
    removeFromHistory(query) {
        try {
            let history = this.getSearchHistory();
            history = history.filter(q => q.toLowerCase() !== query.toLowerCase());
            localStorage.setItem('transpareo_search_history', JSON.stringify(history));
            this.showSearchHistory();
        } catch (error) {
            console.error('Erreur suppression historique:', error);
        }
    }
    
    navigateHistory(e) {
        // Navigation au clavier dans l'historique
        const items = document.querySelectorAll('.search-result-item[data-query]');
        if (items.length === 0) return;
        
        e.preventDefault();
        const currentIndex = Array.from(items).findIndex(item => item === document.activeElement);
        let nextIndex;
        
        if (e.key === 'ArrowDown') {
            nextIndex = currentIndex < items.length - 1 ? currentIndex + 1 : 0;
        } else {
            nextIndex = currentIndex > 0 ? currentIndex - 1 : items.length - 1;
        }
        
        items[nextIndex].focus();
    }
    
    async performSearch(query) {
        if (this.isSearching) return;
        
        this.isSearching = true;
        this.showLoading();
        
        try {
            const response = await fetch(`/api/search/?q=${encodeURIComponent(query)}&limit=5`);
            const data = await response.json();
            
            this.hideLoading();
            this.displayResults(data, query);
            
            // Sauvegarder dans l'historique si recherche réussie
            if (data.total > 0) {
                this.saveToHistory(query);
            }
            
        } catch (error) {
            console.error('Erreur recherche:', error);
            this.hideLoading();
            this.showError();
        } finally {
            this.isSearching = false;
        }
    }
    
    showLoading() {
        document.getElementById('search-loading').style.display = 'flex';
        document.getElementById('search-results').style.display = 'none';
        document.getElementById('search-empty').style.display = 'none';
        document.getElementById('search-view-all-wrapper').style.display = 'none';
        this.showDropdown();
    }
    
    hideLoading() {
        document.getElementById('search-loading').style.display = 'none';
    }
    
    displayResults(data, query) {
        const hasResults = data.total > 0;
        
        if (!hasResults) {
            this.showEmpty();
            return;
        }
        
        // Afficher les sections avec résultats
        this.displayPosts(data.posts);
        this.displayUsers(data.users);
        this.displayGroups(data.groups);
        this.displayEvents(data.events);
        this.displayHashtags(data.hashtags);
        
        // Afficher le lien "Voir tous les résultats"
        if (data.total > 5) {
            const viewAllLink = document.getElementById('search-view-all');
            if (viewAllLink) {
                viewAllLink.href = `/connect/search/?q=${encodeURIComponent(query)}`;
            }
            document.getElementById('search-view-all-wrapper').style.display = 'block';
        }
        
        document.getElementById('search-results').style.display = 'block';
        document.getElementById('search-empty').style.display = 'none';
        this.showDropdown();
    }
    
    displayPosts(posts) {
        const section = document.getElementById('search-posts-section');
        const container = document.getElementById('search-posts-results');
        
        if (posts.length === 0) {
            section.style.display = 'none';
            return;
        }
        
        section.style.display = 'block';
        container.innerHTML = '';
        
        posts.forEach(post => {
            const item = document.createElement('a');
            item.href = post.url || `/connect/posts/${post.id}/`;
            item.className = 'search-result-item';
            
            const authorName = post.author?.full_name || post.author?.username || 'Utilisateur';
            const timeAgo = this.formatTimeAgo(post.created_at);
            
            item.innerHTML = `
                <div class="search-result-info">
                    <div class="search-result-content">${this.escapeHtml(post.content)}</div>
                    <div class="search-result-meta">
                        <span>Par ${this.escapeHtml(authorName)}</span>
                        <span>•</span>
                        <span>${timeAgo}</span>
                        ${post.likes_count > 0 ? `<span>•</span><span>${post.likes_count} likes</span>` : ''}
                    </div>
                </div>
            `;
            
            container.appendChild(item);
        });
    }
    
    displayUsers(users) {
        const section = document.getElementById('search-users-section');
        const container = document.getElementById('search-users-results');
        
        if (users.length === 0) {
            section.style.display = 'none';
            return;
        }
        
        section.style.display = 'block';
        container.innerHTML = '';
        
        users.forEach(user => {
            const item = document.createElement('a');
            item.href = user.url || `/profile/${user.id}/`;
            item.className = 'search-result-item';
            
            const avatar = user.avatar 
                ? `<img src="${user.avatar}" class="search-result-avatar" alt="${this.escapeHtml(user.full_name)}">`
                : `<div class="search-result-avatar-placeholder">${(user.full_name || user.username || 'U')[0].toUpperCase()}</div>`;
            
            const profession = user.profession || '';
            const employeur = user.employeur ? ` chez ${user.employeur}` : '';
            const location = user.location ? ` • ${user.location}` : '';
            const commonConnections = user.common_connections > 0 
                ? `<span class="search-result-meta">${user.common_connections} connexion${user.common_connections > 1 ? 's' : ''} commune${user.common_connections > 1 ? 's' : ''}</span>`
                : '';
            
            item.innerHTML = `
                ${avatar}
                <div class="search-result-info">
                    <div class="search-result-name">
                        ${this.escapeHtml(user.full_name || user.username)}
                        ${user.is_verified ? '<span class="search-result-badge">✓ Vérifié</span>' : ''}
                    </div>
                    ${profession ? `<div class="search-result-subtitle">${this.escapeHtml(profession)}${employeur}</div>` : ''}
                    ${location ? `<div class="search-result-subtitle">${this.escapeHtml(location)}</div>` : ''}
                    ${commonConnections}
                </div>
            `;
            
            container.appendChild(item);
        });
    }
    
    displayGroups(groups) {
        const section = document.getElementById('search-groups-section');
        const container = document.getElementById('search-groups-results');
        
        if (groups.length === 0) {
            section.style.display = 'none';
            return;
        }
        
        section.style.display = 'block';
        container.innerHTML = '';
        
        groups.forEach(group => {
            const item = document.createElement('a');
            item.href = group.url || `/connect/groups/${group.id}/`;
            item.className = 'search-result-item';
            
            const image = group.image 
                ? `<img src="${group.image}" class="search-result-avatar" alt="${this.escapeHtml(group.name)}">`
                : `<div class="search-result-avatar-placeholder">${(group.name || 'G')[0].toUpperCase()}</div>`;
            
            item.innerHTML = `
                ${image}
                <div class="search-result-info">
                    <div class="search-result-name">${this.escapeHtml(group.name)}</div>
                    ${group.description ? `<div class="search-result-content">${this.escapeHtml(group.description)}</div>` : ''}
                    <div class="search-result-meta">
                        <span>${group.member_count} membre${group.member_count > 1 ? 's' : ''}</span>
                        ${group.posts_count > 0 ? `<span>•</span><span>${group.posts_count} posts</span>` : ''}
                        ${group.is_public ? '' : '<span>•</span><span class="search-result-badge">Privé</span>'}
                    </div>
                </div>
            `;
            
            container.appendChild(item);
        });
    }
    
    displayEvents(events) {
        const section = document.getElementById('search-events-section');
        const container = document.getElementById('search-events-results');
        
        if (events.length === 0) {
            section.style.display = 'none';
            return;
        }
        
        section.style.display = 'block';
        container.innerHTML = '';
        
        events.forEach(event => {
            const item = document.createElement('a');
            item.href = event.url || `/connect/groups/${event.group.id}/events/${event.id}/`;
            item.className = 'search-result-item';
            
            const date = new Date(event.date_start);
            const dateStr = date.toLocaleDateString('fr-FR', { day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit' });
            
            item.innerHTML = `
                <div class="search-result-info">
                    <div class="search-result-name">${this.escapeHtml(event.title)}</div>
                    ${event.description ? `<div class="search-result-content">${this.escapeHtml(event.description)}</div>` : ''}
                    <div class="search-result-meta">
                        <span>${dateStr}</span>
                        <span>•</span>
                        <span>${this.escapeHtml(event.group.name)}</span>
                        ${event.participants_count > 0 ? `<span>•</span><span>${event.participants_count} participant${event.participants_count > 1 ? 's' : ''}</span>` : ''}
                        ${event.is_live ? '<span>•</span><span class="search-result-badge">En direct</span>' : ''}
                    </div>
                </div>
            `;
            
            container.appendChild(item);
        });
    }
    
    displayHashtags(hashtags) {
        const section = document.getElementById('search-hashtags-section');
        const container = document.getElementById('search-hashtags-results');
        
        if (hashtags.length === 0) {
            section.style.display = 'none';
            return;
        }
        
        section.style.display = 'block';
        container.innerHTML = '';
        
        hashtags.forEach(hashtag => {
            const item = document.createElement('a');
            item.href = hashtag.url || `/connect/search/?q=${encodeURIComponent(hashtag.tag)}&type=hashtag`;
            item.className = 'search-result-item';
            
            item.innerHTML = `
                <div class="search-result-info">
                    <div class="search-result-name">#${this.escapeHtml(hashtag.tag)}</div>
                    <div class="search-result-meta">
                        <span>${hashtag.post_count} post${hashtag.post_count > 1 ? 's' : ''}</span>
                    </div>
                </div>
            `;
            
            container.appendChild(item);
        });
    }
    
    showEmpty() {
        document.getElementById('search-results').style.display = 'none';
        document.getElementById('search-empty').style.display = 'flex';
        document.getElementById('search-view-all-wrapper').style.display = 'none';
        this.showDropdown();
    }
    
    showError() {
        this.showEmpty();
        const emptyMsg = document.querySelector('#search-empty p');
        if (emptyMsg) {
            emptyMsg.textContent = 'Erreur lors de la recherche';
        }
    }
    
    showDropdown() {
        this.searchDropdown.style.display = 'block';
        this.searchInput.setAttribute('aria-expanded', 'true');
    }
    
    hideDropdown() {
        this.searchDropdown.style.display = 'none';
        this.searchInput.setAttribute('aria-expanded', 'false');
    }
    
    goToSearchResults() {
        const query = this.searchInput.value.trim();
        if (query.length >= this.minQueryLength) {
            window.location.href = `/connect/search/?q=${encodeURIComponent(query)}`;
        }
    }
    
    formatTimeAgo(dateString) {
        const date = new Date(dateString);
        const now = new Date();
        const diffMs = now - date;
        const diffMins = Math.floor(diffMs / 60000);
        const diffHours = Math.floor(diffMs / 3600000);
        const diffDays = Math.floor(diffMs / 86400000);
        
        if (diffMins < 1) return 'À l\'instant';
        if (diffMins < 60) return `Il y a ${diffMins} min`;
        if (diffHours < 24) return `Il y a ${diffHours}h`;
        if (diffDays < 7) return `Il y a ${diffDays}j`;
        return date.toLocaleDateString('fr-FR', { day: 'numeric', month: 'short' });
    }
    
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Initialiser la recherche
let linkedInSearch;
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        linkedInSearch = new LinkedInSearch();
    });
} else {
    linkedInSearch = new LinkedInSearch();
}

// Notifications dropdown
const notificationsBtn = document.getElementById('nav-notifications');
const notificationsDropdown = document.getElementById('notifications-dropdown');

if (notificationsBtn) {
    notificationsBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        notificationsDropdown.style.display = 
            notificationsDropdown.style.display === 'none' ? 'block' : 'none';
    });
}

// User menu dropdown
const userMenuBtn = document.getElementById('user-menu-btn');
const userMenu = document.getElementById('user-menu');
const userDropdown = document.getElementById('user-dropdown');

if (userMenuBtn && userMenu) {
    userMenuBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        const isOpen = userMenuBtn.getAttribute('aria-expanded') === 'true';
        userMenuBtn.setAttribute('aria-expanded', !isOpen);
        userMenu.setAttribute('data-open', !isOpen);
    });
}

// Fermer dropdowns si click outside
document.addEventListener('click', (e) => {
    if (notificationsDropdown && !notificationsBtn.contains(e.target) && !notificationsDropdown.contains(e.target)) {
        notificationsDropdown.style.display = 'none';
    }
    if (userMenuBtn && userMenu && !userMenu.contains(e.target)) {
        userMenuBtn.setAttribute('aria-expanded', 'false');
        userMenu.setAttribute('data-open', 'false');
    }
});

// ========== MODAL CRÉATION POST ==========

function openCreatePostModal(type = null) {
    const modal = document.getElementById('create-post-modal');
    if (modal) {
        modal.style.display = 'flex';
        if (type) {
            togglePostType(type);
        }
    }
}

function closeCreatePostModal() {
    const modal = document.getElementById('create-post-modal');
    if (modal) {
        modal.style.display = 'none';
        // Reset form
        document.getElementById('post-content-textarea').value = '';
        document.getElementById('post-media-zone').style.display = 'none';
        document.getElementById('post-poll-zone').style.display = 'none';
        document.getElementById('post-event-zone').style.display = 'none';
        document.getElementById('post-article-zone').style.display = 'none';
    }
}

// Ouvrir modal au click sur input
const createPostInput = document.getElementById('create-post-input');
if (createPostInput) {
    createPostInput.addEventListener('click', () => {
        openCreatePostModal();
    });
}

// Compteur caractères
const textarea = document.getElementById('post-content-textarea');
const charCount = document.getElementById('char-count');
const publishBtn = document.getElementById('publish-post-btn');

if (textarea && charCount) {
    textarea.addEventListener('input', (e) => {
        const count = e.target.value.length;
        charCount.textContent = count;
        
        // Activer/désactiver bouton publier
        if (publishBtn) {
            publishBtn.disabled = count === 0;
        }
        
        // Warning à 2800
        if (count > 2800) {
            charCount.style.color = '#EF4444';
        } else {
            charCount.style.color = '#6B7280';
        }
    });
}

function togglePostType(type) {
    // Masquer toutes les zones
    document.getElementById('post-media-zone').style.display = 'none';
    document.getElementById('post-poll-zone').style.display = 'none';
    document.getElementById('post-event-zone').style.display = 'none';
    document.getElementById('post-article-zone').style.display = 'none';
    
    // Afficher la zone correspondante
    if (type === 'photo' || type === 'video') {
        document.getElementById('post-media-zone').style.display = 'block';
    } else if (type === 'poll') {
        document.getElementById('post-poll-zone').style.display = 'block';
    } else if (type === 'event') {
        document.getElementById('post-event-zone').style.display = 'block';
    } else if (type === 'article') {
        document.getElementById('post-article-zone').style.display = 'block';
    }
}

function publishPost() {
    const content = document.getElementById('post-content-textarea').value.trim();
    const visibility = document.getElementById('post-visibility').value;
    
    if (!content) {
        alert('Veuillez saisir du contenu');
        return;
    }
    
    const publishBtn = document.getElementById('publish-post-btn');
    if (publishBtn) {
        publishBtn.disabled = true;
        publishBtn.textContent = 'Publication...';
    }
    
    fetch('/api/posts/', {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            content: content,
            visibility: visibility,
        }),
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Fermer modal
            closeCreatePostModal();
            // Recharger la page pour afficher le nouveau post
            location.reload();
        } else {
            alert('Erreur: ' + (data.error || 'Impossible de publier le post'));
            if (publishBtn) {
                publishBtn.disabled = false;
                publishBtn.textContent = 'Publier';
            }
        }
    })
    .catch(error => {
        console.error('Erreur publication:', error);
        alert('Erreur lors de la publication');
        if (publishBtn) {
            publishBtn.disabled = false;
            publishBtn.textContent = 'Publier';
        }
    });
}

// ========== FEED FILTERS ==========

function changeFeedFilter(filter) {
    const url = new URL(window.location);
    url.searchParams.set('filter', filter);
    window.location.href = url.toString();
}

// ========== POST INTERACTIONS ==========

function toggleLike(postId) {
    const btn = event.currentTarget;
    
    fetch(`/api/posts/${postId}/like/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
            'Content-Type': 'application/json',
        },
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            btn.classList.toggle('liked', data.liked);
            
            // Mettre à jour le compteur
            const countElement = btn.closest('.post-footer').querySelector('.metric-item');
            if (countElement) {
                const countText = countElement.textContent.trim();
                const currentCount = parseInt(countText) || 0;
                countElement.innerHTML = `
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"></path>
                    </svg>
                    ${data.likes_count}
                `;
            }
            
            // Animation
            btn.style.transform = 'scale(1.3)';
            setTimeout(() => {
                btn.style.transform = 'scale(1)';
            }, 200);
        }
    })
    .catch(error => {
        console.error('Erreur like:', error);
    });
}

function togglePostMenu(postId) {
    const menu = document.getElementById(`post-menu-${postId}`);
    if (menu) {
        menu.style.display = menu.style.display === 'none' ? 'block' : 'none';
    }
}

function focusComments(postId) {
    const commentsSection = document.getElementById(`comments-${postId}`);
    if (commentsSection) {
        commentsSection.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        const input = commentsSection.querySelector('.comment-input');
        if (input) {
            input.focus();
        }
    }
}

function sharePost(postId) {
    // TODO: Ouvrir modal partage
    console.log('Partager post:', postId);
}

function sendPost(postId) {
    // TODO: Ouvrir modal envoi message
    console.log('Envoyer post:', postId);
}

function handleCommentKeypress(event, postId) {
    if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        const input = event.target;
        const content = input.value.trim();
        
        if (!content) return;
        
        // Désactiver l'input pendant l'envoi
        input.disabled = true;
        
        fetch(`/api/posts/${postId}/comments/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                content: content,
            }),
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                input.value = '';
                // Recharger les commentaires ou ajouter le nouveau
                location.reload(); // Simple pour l'instant, peut être amélioré avec DOM manipulation
            } else {
                alert('Erreur: ' + (data.error || 'Impossible d\'ajouter le commentaire'));
            }
            input.disabled = false;
        })
        .catch(error => {
            console.error('Erreur commentaire:', error);
            alert('Erreur lors de l\'ajout du commentaire');
            input.disabled = false;
        });
    }
}

// ========== INFINITE SCROLL ==========

let isLoading = false;
let currentPage = 1;

window.addEventListener('scroll', () => {
    if (isLoading) return;
    
    const scrollHeight = document.documentElement.scrollHeight;
    const scrollTop = document.documentElement.scrollTop;
    const clientHeight = document.documentElement.clientHeight;
    
    if (scrollTop + clientHeight >= scrollHeight - 500) {
        loadMorePosts();
    }
});

function loadMorePosts() {
    if (isLoading) return;
    
    isLoading = true;
    const loader = document.getElementById('feed-loader');
    if (loader) {
        loader.style.display = 'block';
    }
    
    currentPage++;
    const filter = new URLSearchParams(window.location.search).get('filter') || 'for_you';
    
    fetch(`/api/feed/?page=${currentPage}&filter=${filter}&limit=10`)
        .then(response => response.json())
        .then(data => {
            const feed = document.getElementById('posts-feed');
            if (feed && data.posts && data.posts.length > 0) {
                // Pour l'instant, recharger la page pour afficher les nouveaux posts
                // TODO: Implémenter rendu dynamique des posts
                if (data.has_more) {
                    // Recharger la page avec la nouvelle page
                    const url = new URL(window.location);
                    url.searchParams.set('page', currentPage);
                    window.location.href = url.toString();
                }
            }
            isLoading = false;
            if (loader) {
                loader.style.display = 'none';
            }
        })
        .catch(error => {
            console.error('Erreur chargement posts:', error);
            isLoading = false;
            if (loader) {
                loader.style.display = 'none';
            }
        });
}

// Fonction helper pour récupérer le cookie CSRF
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// ========== SCROLL TO TOP ==========

const scrollToTopBtn = document.getElementById('scroll-to-top');

window.addEventListener('scroll', () => {
    if (window.scrollY > 500) {
        if (scrollToTopBtn) {
            scrollToTopBtn.style.display = 'block';
        }
    } else {
        if (scrollToTopBtn) {
            scrollToTopBtn.style.display = 'none';
        }
    }
});

function scrollToTop() {
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

// ========== SUGGESTIONS ==========

function toggleFollow(userId) {
    // TODO: Appel API pour follow/unfollow
    const btn = event.currentTarget;
    if (btn.textContent === 'Suivre') {
        btn.textContent = 'Suivi';
        btn.style.background = '#E5E7EB';
        btn.style.color = '#111827';
    } else {
        btn.textContent = 'Suivre';
        btn.style.background = '#D3580B';
        btn.style.color = 'white';
    }
}

function joinGroup(groupId) {
    // TODO: Appel API pour rejoindre groupe
    const btn = event.currentTarget;
    btn.textContent = 'Membre';
    btn.style.background = '#E5E7EB';
    btn.style.color = '#111827';
    btn.disabled = true;
}

// ========== INITIALISATION ==========

document.addEventListener('DOMContentLoaded', () => {
    console.log('Transpareo Connect Home initialisé');
    
    // Fermer modals au click outside
    document.addEventListener('click', (e) => {
        const modal = document.getElementById('create-post-modal');
        if (modal && e.target === modal) {
            closeCreatePostModal();
        }
    });
});

