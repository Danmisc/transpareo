// ============================================
// INITIALISATION
// ============================================

function initConnectPage() {
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
    url.searchParams.delete('type');
    url.searchParams.delete('statut');
    url.searchParams.delete('auteur');
    url.searchParams.delete('groupe');
    url.searchParams.delete('date_debut');
    url.searchParams.delete('date_fin');
    url.searchParams.set('page', '1');
    window.location.href = url.toString();
}

function filterByCategory(category) {
    const url = new URL(window.location);
    
    if (category === 'recents') {
        const date = new Date();
        date.setHours(date.getHours() - 24);
        url.searchParams.set('date_debut', date.toISOString().split('T')[0]);
    } else if (category === 'populaires') {
        // TODO: Filtrer par engagement élevé
    } else if (category === 'signales') {
        url.searchParams.set('statut', 'inappropriate');
    } else {
        url.searchParams.delete('date_debut');
        url.searchParams.delete('statut');
    }
    
    url.searchParams.set('page', '1');
    window.location.href = url.toString();
}

function saveSearch() {
    const name = prompt('Nommer cette recherche :');
    if (name) {
        const filters = new URLSearchParams(window.location.search);
        localStorage.setItem('saved_search_connect_' + name, filters.toString());
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
                const form = searchInput.closest('form');
                if (form) {
                    form.submit();
                }
            }, 300);
        });
    }
}

function initFilters() {
    // Initialiser multi-selects si nécessaire
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
    document.querySelectorAll('.sortable').forEach(header => {
        header.style.cursor = 'pointer';
    });
}

// ============================================
// BULK ACTIONS
// ============================================

function toggleSelectAll(checkbox) {
    const checkboxes = document.querySelectorAll('.post-checkbox');
    checkboxes.forEach(cb => {
        cb.checked = checkbox.checked;
    });
    updateBulkActions();
}

function updateBulkActions() {
    const checked = document.querySelectorAll('.post-checkbox:checked, .groupe-checkbox:checked');
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
    document.querySelectorAll('.post-checkbox, .groupe-checkbox').forEach(cb => {
        cb.checked = false;
    });
    const selectAll = document.getElementById('select-all');
    if (selectAll) selectAll.checked = false;
    updateBulkActions();
}

function bulkChangerStatut() {
    const checked = Array.from(document.querySelectorAll('.post-checkbox:checked')).map(cb => cb.value);
    if (checked.length === 0) {
        alert('Aucun post sélectionné');
        return;
    }
    
    const statut = prompt('Nouveau statut (publier/masquer/supprimer) :');
    if (statut) {
        // TODO: Appel API
        console.log('Changer statut posts:', checked, statut);
        alert('Statut modifié');
        location.reload();
    }
}

function bulkEpingler() {
    const checked = Array.from(document.querySelectorAll('.post-checkbox:checked')).map(cb => cb.value);
    if (checked.length === 0) {
        alert('Aucun post sélectionné');
        return;
    }
    
    if (confirm(`Épingler ${checked.length} posts ?`)) {
        // TODO: Appel API
        console.log('Épingler posts:', checked);
        alert('Posts épinglés');
        location.reload();
    }
}

function bulkDesactiverCommentaires() {
    const checked = Array.from(document.querySelectorAll('.post-checkbox:checked')).map(cb => cb.value);
    if (checked.length === 0) {
        alert('Aucun post sélectionné');
        return;
    }
    
    if (confirm(`Désactiver commentaires sur ${checked.length} posts ?`)) {
        // TODO: Appel API
        console.log('Désactiver commentaires posts:', checked);
        alert('Commentaires désactivés');
        location.reload();
    }
}

function bulkExport() {
    const checked = Array.from(document.querySelectorAll('.post-checkbox:checked')).map(cb => cb.value);
    if (checked.length === 0) {
        alert('Aucun post sélectionné');
        return;
    }
    
    const url = new URL(window.location);
    url.searchParams.set('export', 'csv');
    url.searchParams.set('ids', checked.join(','));
    window.location.href = url.toString();
}

// ============================================
// DROPDOWNS
// ============================================

function toggleActionsDropdown(button) {
    const menu = button.nextElementSibling;
    if (menu) {
        document.querySelectorAll('.dropdown-menu').forEach(m => {
            if (m !== menu) m.classList.remove('show');
        });
        menu.classList.toggle('show');
    }
}

function initDropdowns() {
    document.addEventListener('click', function(e) {
        if (!e.target.closest('.actions-dropdown')) {
            document.querySelectorAll('.dropdown-menu').forEach(menu => {
                menu.classList.remove('show');
            });
        }
    });
}

// ============================================
// ACTIONS POSTS
// ============================================

function openPostDetail(postId) {
    const modal = document.getElementById('post-detail-modal');
    if (!modal) return;
    
    // Charger données post via AJAX
    fetch(`/connect-admin/posts/${postId}/detail/`)
        .then(response => response.json())
        .then(data => {
            populatePostDetail(data);
            modal.style.display = 'flex';
        })
        .catch(error => {
            console.error('Erreur chargement post:', error);
            alert('Erreur lors du chargement du post');
        });
}

function populatePostDetail(data) {
    // Header
    document.getElementById('modal-post-auteur').textContent = data.author.username;
    document.getElementById('modal-post-date').textContent = data.created_at;
    document.getElementById('modal-post-type').textContent = data.content_type_display;
    document.getElementById('modal-post-type').className = 'type-badge type-' + data.content_type;
    
    // Avatar
    if (data.author.avatar_url) {
        document.getElementById('modal-post-avatar').src = data.author.avatar_url;
        document.getElementById('widget-post-auteur-avatar').src = data.author.avatar_url;
    }
    
    // Contenu
    document.getElementById('modal-post-content').textContent = data.content;
    
    // Hashtags
    const hashtagsContainer = document.getElementById('modal-post-hashtags');
    if (data.hashtags) {
        const tags = data.hashtags.split(',').filter(t => t.trim());
        hashtagsContainer.innerHTML = tags.map(tag => 
            `<span class="hashtag">#${tag.trim()}</span>`
        ).join('');
    }
    
    // Médias
    const mediasSection = document.getElementById('modal-post-medias');
    const mediasGrid = document.getElementById('medias-grid');
    if (data.images && data.images.length > 0) {
        mediasSection.style.display = 'block';
        mediasGrid.innerHTML = data.images.map(img => `
            <div class="media-thumbnail">
                <img src="${img.url}" alt="${img.caption}" onclick="openLightbox('${img.url}')">
            </div>
        `).join('');
    } else {
        mediasSection.style.display = 'none';
    }
    
    // Engagement
    document.getElementById('engagement-likes').textContent = data.likes_count;
    document.getElementById('engagement-comments').textContent = data.comments_count;
    document.getElementById('engagement-shares').textContent = data.shares_count;
    
    // Likes avatars
    const likesGrid = document.getElementById('likes-avatars-grid');
    likesGrid.innerHTML = data.likes.map(like => `
        <div class="like-avatar" title="${like.username}">
            ${like.avatar_url ? 
                `<img src="${like.avatar_url}" alt="${like.username}">` :
                `<div class="avatar-placeholder">${like.username[0].toUpperCase()}</div>`
            }
        </div>
    `).join('');
    
    // Commentaires
    const commentsList = document.getElementById('comments-list');
    commentsList.innerHTML = data.comments.map(comment => `
        <div class="comment-item">
            <div class="comment-author">
                ${comment.author.avatar_url ? 
                    `<img src="${comment.author.avatar_url}" alt="${comment.author.username}">` :
                    `<div class="avatar-placeholder">${comment.author.username[0].toUpperCase()}</div>`
                }
                <strong>${comment.author.username}</strong>
                <span class="comment-date">${comment.created_at}</span>
            </div>
            <div class="comment-content">${comment.content}</div>
            <div class="comment-actions">
                <span>❤️ ${comment.likes_count}</span>
            </div>
        </div>
    `).join('');
    
    // Widget auteur
    document.getElementById('widget-post-auteur-nom').textContent = data.author.username;
    document.getElementById('widget-post-auteur-email').textContent = data.author.email || '-';
    
    // Widget groupe
    if (data.group) {
        const widgetGroupe = document.getElementById('widget-groupe');
        widgetGroupe.style.display = 'block';
        document.getElementById('widget-groupe-nom').textContent = data.group.name;
    }
    
    // Statut
    let statutText = 'Publié';
    let statutClass = 'statut-publie';
    if (data.is_quarantined) {
        statutText = 'Quarantaine';
        statutClass = 'statut-quarantined';
    } else if (data.is_spam) {
        statutText = 'Spam';
        statutClass = 'statut-spam';
    } else if (data.is_inappropriate) {
        statutText = 'Inapproprié';
        statutClass = 'statut-inappropriate';
    }
    document.getElementById('modal-post-statut').textContent = statutText;
    document.getElementById('modal-post-statut').className = 'statut-badge ' + statutClass;
    document.getElementById('widget-post-statut').textContent = statutText;
    document.getElementById('widget-post-date-pub').textContent = data.created_at;
    document.getElementById('widget-post-security-score').textContent = data.security_score;
    
    // Stocker l'ID du post pour les actions
    modal.dataset.postId = data.id;
}

function closePostDetailModal() {
    const modal = document.getElementById('post-detail-modal');
    if (modal) modal.style.display = 'none';
}

function openGroupeDetail(groupeId) {
    const modal = document.getElementById('groupe-detail-modal');
    if (!modal) return;
    
    fetch(`/connect-admin/groupes/${groupeId}/detail/`)
        .then(response => response.json())
        .then(data => {
            populateGroupeDetail(data);
            modal.style.display = 'flex';
        })
        .catch(error => {
            console.error('Erreur chargement groupe:', error);
            alert('Erreur lors du chargement du groupe');
        });
}

function populateGroupeDetail(data) {
    document.getElementById('modal-groupe-nom').textContent = data.name;
    document.getElementById('modal-groupe-description').textContent = data.description || data.full_description || 'Aucune description';
    document.getElementById('modal-groupe-type').textContent = data.is_public ? 'Public' : 'Privé';
    document.getElementById('modal-groupe-membres-count').textContent = data.member_count;
    document.getElementById('modal-groupe-posts-count').textContent = data.posts_count;
    document.getElementById('modal-groupe-date-creation').textContent = data.created_at;
    
    // Admins
    const adminsList = document.getElementById('admins-list');
    adminsList.innerHTML = data.admins.map(admin => `
        <div class="admin-item">
            ${admin.avatar_url ? 
                `<img src="${admin.avatar_url}" alt="${admin.username}">` :
                `<div class="avatar-placeholder">${admin.username[0].toUpperCase()}</div>`
            }
            <span>${admin.username}</span>
        </div>
    `).join('');
    
    // Membres
    const membresList = document.getElementById('membres-list');
    membresList.innerHTML = data.members.map(member => `
        <div class="membre-item">
            ${member.avatar_url ? 
                `<img src="${member.avatar_url}" alt="${member.username}">` :
                `<div class="avatar-placeholder">${member.username[0].toUpperCase()}</div>`
            }
            <span>${member.username}</span>
        </div>
    `).join('');
    
    modal.dataset.groupeId = data.id;
}

function closeGroupeDetailModal() {
    const modal = document.getElementById('groupe-detail-modal');
    if (modal) modal.style.display = 'none';
}

function switchGroupeTab(tab) {
    document.querySelectorAll('.modal-tab').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('.modal-tab-content').forEach(c => c.classList.remove('active'));
    
    document.querySelector(`.modal-tab[data-tab="${tab}"]`).classList.add('active');
    document.getElementById(`tab-${tab}`).classList.add('active');
}

function masquerPost(postId) {
    if (confirm('Masquer ce post ?')) {
        // TODO: Appel API
        console.log('Masquer post:', postId);
        alert('Post masqué');
        location.reload();
    }
}

function supprimerPost(postId) {
    const raison = prompt('Raison de la suppression :');
    if (raison) {
        if (confirm('Êtes-vous sûr de vouloir supprimer ce post ?')) {
            // TODO: Appel API
            console.log('Supprimer post:', postId, raison);
            alert('Post supprimé');
            location.reload();
        }
    }
}

// ============================================
// ACTIONS GROUPES
// ============================================

function openGroupeDetail(groupeId) {
    // TODO: Ouvrir modal détail groupe
    console.log('Ouvrir détail groupe:', groupeId);
    alert('Modal détail groupe à implémenter');
}

// ============================================
// ACTIONS MESSAGES
// ============================================

function openConversationDetail(conversationId) {
    // TODO: Ouvrir modal conversation
    console.log('Ouvrir conversation:', conversationId);
    alert('Modal conversation à implémenter');
}

// ============================================
// UTILITAIRES
// ============================================

function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        alert('ID copié : ' + text);
    });
}

function changePerPage(value) {
    const url = new URL(window.location);
    url.searchParams.set('per_page', value);
    url.searchParams.set('page', '1');
    window.location.href = url.toString();
}

function switchToFeedView() {
    const url = new URL(window.location);
    url.searchParams.set('feed', '1');
    window.location.href = url.toString();
}

function switchToTableView() {
    const url = new URL(window.location);
    url.searchParams.delete('feed');
    window.location.href = url.toString();
}

function toggleFeedActions(button) {
    const menu = button.nextElementSibling;
    if (menu) {
        document.querySelectorAll('.dropdown-menu').forEach(m => {
            if (m !== menu) m.classList.remove('show');
        });
        menu.classList.toggle('show');
    }
}

// Actions depuis modal
function masquerPostFromModal() {
    const modal = document.getElementById('post-detail-modal');
    const postId = modal ? modal.dataset.postId : null;
    if (postId) masquerPost(postId);
}

function epinglerPostFromModal() {
    const modal = document.getElementById('post-detail-modal');
    const postId = modal ? modal.dataset.postId : null;
    if (postId) {
        // TODO: Appel API
        console.log('Épingler post:', postId);
        alert('Post épinglé');
    }
}

function desactiverCommentairesPost() {
    const modal = document.getElementById('post-detail-modal');
    const postId = modal ? modal.dataset.postId : null;
    if (postId) {
        // TODO: Appel API
        console.log('Désactiver commentaires post:', postId);
        alert('Commentaires désactivés');
    }
}

function supprimerPostFromModal() {
    const modal = document.getElementById('post-detail-modal');
    const postId = modal ? modal.dataset.postId : null;
    if (postId) supprimerPost(postId);
}

function partagerPost() {
    const modal = document.getElementById('post-detail-modal');
    const postId = modal ? modal.dataset.postId : null;
    if (postId) {
        const url = window.location.origin + '/connect/post/' + postId + '/';
        navigator.clipboard.writeText(url).then(() => {
            alert('Lien copié dans le presse-papiers');
        });
    }
}

function voirProfilAuteurPost() {
    const modal = document.getElementById('post-detail-modal');
    const postId = modal ? modal.dataset.postId : null;
    if (postId) {
        // TODO: Récupérer ID auteur depuis modal
        console.log('Voir profil auteur');
    }
}

function voirGroupePost() {
    const modal = document.getElementById('post-detail-modal');
    const postId = modal ? modal.dataset.postId : null;
    if (postId) {
        // TODO: Récupérer ID groupe depuis modal
        console.log('Voir groupe');
    }
}

function voirTousLikes() {
    alert('Liste complète des likes à implémenter');
}

function ajouterCommentaire() {
    const input = document.getElementById('new-comment-input');
    const modal = document.getElementById('post-detail-modal');
    const postId = modal ? modal.dataset.postId : null;
    
    if (!input.value.trim() || !postId) return;
    
    // TODO: Appel API pour ajouter commentaire
    console.log('Ajouter commentaire:', input.value, 'au post:', postId);
    alert('Commentaire ajouté');
    input.value = '';
    // Recharger les commentaires
}

function openLightbox(imageUrl) {
    // TODO: Implémenter lightbox
    window.open(imageUrl, '_blank');
}

// Actions groupes
function modifierGroupe() {
    const modal = document.getElementById('groupe-detail-modal');
    const groupeId = modal ? modal.dataset.groupeId : null;
    if (groupeId) {
        alert('Modification groupe à implémenter');
    }
}

function gererMembres() {
    switchGroupeTab('membres');
}

function gererAdmins() {
    alert('Gestion admins à implémenter');
}

function archiverGroupe() {
    const modal = document.getElementById('groupe-detail-modal');
    const groupeId = modal ? modal.dataset.groupeId : null;
    if (groupeId && confirm('Archiver ce groupe ?')) {
        // TODO: Appel API
        console.log('Archiver groupe:', groupeId);
        alert('Groupe archivé');
        location.reload();
    }
}

function supprimerGroupe() {
    const modal = document.getElementById('groupe-detail-modal');
    const groupeId = modal ? modal.dataset.groupeId : null;
    if (groupeId && confirm('Êtes-vous sûr de vouloir supprimer ce groupe ? Cette action est irréversible.')) {
        // TODO: Appel API
        console.log('Supprimer groupe:', groupeId);
        alert('Groupe supprimé');
        location.reload();
    }
}

function openColumnsModal() {
    alert('Configuration colonnes à venir');
}

function exportDonnees() {
    const url = new URL(window.location);
    url.searchParams.set('export', 'csv');
    window.location.href = url.toString();
}

function openStatsEngagement() {
    switchView('analytics');
}

function openModerationAvancee() {
    alert('Modération avancée à venir');
}

function openBadgesPage() {
    window.location.href = '/connect-admin/badges/';
}

// Événements
function creerEvenement() {
    const modal = document.getElementById('evenement-modal');
    if (modal) {
        modal.style.display = 'flex';
        document.getElementById('modal-evenement-title').textContent = 'Créer événement';
    }
}

function closeEvenementModal() {
    const modal = document.getElementById('evenement-modal');
    if (modal) modal.style.display = 'none';
}

// Fermer modals avec Escape
document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
        closePostDetailModal();
        closeGroupeDetailModal();
        closeEvenementModal();
    }
});

// Fermer modals au click sur overlay
document.addEventListener('click', function(e) {
    const modals = ['post-detail-modal', 'groupe-detail-modal', 'evenement-modal'];
    modals.forEach(modalId => {
        const modal = document.getElementById(modalId);
        if (modal && e.target === modal) {
            if (modalId === 'post-detail-modal') closePostDetailModal();
            else if (modalId === 'groupe-detail-modal') closeGroupeDetailModal();
            else if (modalId === 'evenement-modal') closeEvenementModal();
        }
    });
});


// ============================================

function initConnectPage() {
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
    url.searchParams.delete('type');
    url.searchParams.delete('statut');
    url.searchParams.delete('auteur');
    url.searchParams.delete('groupe');
    url.searchParams.delete('date_debut');
    url.searchParams.delete('date_fin');
    url.searchParams.set('page', '1');
    window.location.href = url.toString();
}

function filterByCategory(category) {
    const url = new URL(window.location);
    
    if (category === 'recents') {
        const date = new Date();
        date.setHours(date.getHours() - 24);
        url.searchParams.set('date_debut', date.toISOString().split('T')[0]);
    } else if (category === 'populaires') {
        // TODO: Filtrer par engagement élevé
    } else if (category === 'signales') {
        url.searchParams.set('statut', 'inappropriate');
    } else {
        url.searchParams.delete('date_debut');
        url.searchParams.delete('statut');
    }
    
    url.searchParams.set('page', '1');
    window.location.href = url.toString();
}

function saveSearch() {
    const name = prompt('Nommer cette recherche :');
    if (name) {
        const filters = new URLSearchParams(window.location.search);
        localStorage.setItem('saved_search_connect_' + name, filters.toString());
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
                const form = searchInput.closest('form');
                if (form) {
                    form.submit();
                }
            }, 300);
        });
    }
}

function initFilters() {
    // Initialiser multi-selects si nécessaire
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
    document.querySelectorAll('.sortable').forEach(header => {
        header.style.cursor = 'pointer';
    });
}

// ============================================
// BULK ACTIONS
// ============================================

function toggleSelectAll(checkbox) {
    const checkboxes = document.querySelectorAll('.post-checkbox');
    checkboxes.forEach(cb => {
        cb.checked = checkbox.checked;
    });
    updateBulkActions();
}

function updateBulkActions() {
    const checked = document.querySelectorAll('.post-checkbox:checked, .groupe-checkbox:checked');
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
    document.querySelectorAll('.post-checkbox, .groupe-checkbox').forEach(cb => {
        cb.checked = false;
    });
    const selectAll = document.getElementById('select-all');
    if (selectAll) selectAll.checked = false;
    updateBulkActions();
}

function bulkChangerStatut() {
    const checked = Array.from(document.querySelectorAll('.post-checkbox:checked')).map(cb => cb.value);
    if (checked.length === 0) {
        alert('Aucun post sélectionné');
        return;
    }
    
    const statut = prompt('Nouveau statut (publier/masquer/supprimer) :');
    if (statut) {
        // TODO: Appel API
        console.log('Changer statut posts:', checked, statut);
        alert('Statut modifié');
        location.reload();
    }
}

function bulkEpingler() {
    const checked = Array.from(document.querySelectorAll('.post-checkbox:checked')).map(cb => cb.value);
    if (checked.length === 0) {
        alert('Aucun post sélectionné');
        return;
    }
    
    if (confirm(`Épingler ${checked.length} posts ?`)) {
        // TODO: Appel API
        console.log('Épingler posts:', checked);
        alert('Posts épinglés');
        location.reload();
    }
}

function bulkDesactiverCommentaires() {
    const checked = Array.from(document.querySelectorAll('.post-checkbox:checked')).map(cb => cb.value);
    if (checked.length === 0) {
        alert('Aucun post sélectionné');
        return;
    }
    
    if (confirm(`Désactiver commentaires sur ${checked.length} posts ?`)) {
        // TODO: Appel API
        console.log('Désactiver commentaires posts:', checked);
        alert('Commentaires désactivés');
        location.reload();
    }
}

function bulkExport() {
    const checked = Array.from(document.querySelectorAll('.post-checkbox:checked')).map(cb => cb.value);
    if (checked.length === 0) {
        alert('Aucun post sélectionné');
        return;
    }
    
    const url = new URL(window.location);
    url.searchParams.set('export', 'csv');
    url.searchParams.set('ids', checked.join(','));
    window.location.href = url.toString();
}

// ============================================
// DROPDOWNS
// ============================================

function toggleActionsDropdown(button) {
    const menu = button.nextElementSibling;
    if (menu) {
        document.querySelectorAll('.dropdown-menu').forEach(m => {
            if (m !== menu) m.classList.remove('show');
        });
        menu.classList.toggle('show');
    }
}

function initDropdowns() {
    document.addEventListener('click', function(e) {
        if (!e.target.closest('.actions-dropdown')) {
            document.querySelectorAll('.dropdown-menu').forEach(menu => {
                menu.classList.remove('show');
            });
        }
    });
}

// ============================================
// ACTIONS POSTS
// ============================================

function openPostDetail(postId) {
    const modal = document.getElementById('post-detail-modal');
    if (!modal) return;
    
    // Charger données post via AJAX
    fetch(`/connect-admin/posts/${postId}/detail/`)
        .then(response => response.json())
        .then(data => {
            populatePostDetail(data);
            modal.style.display = 'flex';
        })
        .catch(error => {
            console.error('Erreur chargement post:', error);
            alert('Erreur lors du chargement du post');
        });
}

function populatePostDetail(data) {
    // Header
    document.getElementById('modal-post-auteur').textContent = data.author.username;
    document.getElementById('modal-post-date').textContent = data.created_at;
    document.getElementById('modal-post-type').textContent = data.content_type_display;
    document.getElementById('modal-post-type').className = 'type-badge type-' + data.content_type;
    
    // Avatar
    if (data.author.avatar_url) {
        document.getElementById('modal-post-avatar').src = data.author.avatar_url;
        document.getElementById('widget-post-auteur-avatar').src = data.author.avatar_url;
    }
    
    // Contenu
    document.getElementById('modal-post-content').textContent = data.content;
    
    // Hashtags
    const hashtagsContainer = document.getElementById('modal-post-hashtags');
    if (data.hashtags) {
        const tags = data.hashtags.split(',').filter(t => t.trim());
        hashtagsContainer.innerHTML = tags.map(tag => 
            `<span class="hashtag">#${tag.trim()}</span>`
        ).join('');
    }
    
    // Médias
    const mediasSection = document.getElementById('modal-post-medias');
    const mediasGrid = document.getElementById('medias-grid');
    if (data.images && data.images.length > 0) {
        mediasSection.style.display = 'block';
        mediasGrid.innerHTML = data.images.map(img => `
            <div class="media-thumbnail">
                <img src="${img.url}" alt="${img.caption}" onclick="openLightbox('${img.url}')">
            </div>
        `).join('');
    } else {
        mediasSection.style.display = 'none';
    }
    
    // Engagement
    document.getElementById('engagement-likes').textContent = data.likes_count;
    document.getElementById('engagement-comments').textContent = data.comments_count;
    document.getElementById('engagement-shares').textContent = data.shares_count;
    
    // Likes avatars
    const likesGrid = document.getElementById('likes-avatars-grid');
    likesGrid.innerHTML = data.likes.map(like => `
        <div class="like-avatar" title="${like.username}">
            ${like.avatar_url ? 
                `<img src="${like.avatar_url}" alt="${like.username}">` :
                `<div class="avatar-placeholder">${like.username[0].toUpperCase()}</div>`
            }
        </div>
    `).join('');
    
    // Commentaires
    const commentsList = document.getElementById('comments-list');
    commentsList.innerHTML = data.comments.map(comment => `
        <div class="comment-item">
            <div class="comment-author">
                ${comment.author.avatar_url ? 
                    `<img src="${comment.author.avatar_url}" alt="${comment.author.username}">` :
                    `<div class="avatar-placeholder">${comment.author.username[0].toUpperCase()}</div>`
                }
                <strong>${comment.author.username}</strong>
                <span class="comment-date">${comment.created_at}</span>
            </div>
            <div class="comment-content">${comment.content}</div>
            <div class="comment-actions">
                <span>❤️ ${comment.likes_count}</span>
            </div>
        </div>
    `).join('');
    
    // Widget auteur
    document.getElementById('widget-post-auteur-nom').textContent = data.author.username;
    document.getElementById('widget-post-auteur-email').textContent = data.author.email || '-';
    
    // Widget groupe
    if (data.group) {
        const widgetGroupe = document.getElementById('widget-groupe');
        widgetGroupe.style.display = 'block';
        document.getElementById('widget-groupe-nom').textContent = data.group.name;
    }
    
    // Statut
    let statutText = 'Publié';
    let statutClass = 'statut-publie';
    if (data.is_quarantined) {
        statutText = 'Quarantaine';
        statutClass = 'statut-quarantined';
    } else if (data.is_spam) {
        statutText = 'Spam';
        statutClass = 'statut-spam';
    } else if (data.is_inappropriate) {
        statutText = 'Inapproprié';
        statutClass = 'statut-inappropriate';
    }
    document.getElementById('modal-post-statut').textContent = statutText;
    document.getElementById('modal-post-statut').className = 'statut-badge ' + statutClass;
    document.getElementById('widget-post-statut').textContent = statutText;
    document.getElementById('widget-post-date-pub').textContent = data.created_at;
    document.getElementById('widget-post-security-score').textContent = data.security_score;
    
    // Stocker l'ID du post pour les actions
    modal.dataset.postId = data.id;
}

function closePostDetailModal() {
    const modal = document.getElementById('post-detail-modal');
    if (modal) modal.style.display = 'none';
}

function openGroupeDetail(groupeId) {
    const modal = document.getElementById('groupe-detail-modal');
    if (!modal) return;
    
    fetch(`/connect-admin/groupes/${groupeId}/detail/`)
        .then(response => response.json())
        .then(data => {
            populateGroupeDetail(data);
            modal.style.display = 'flex';
        })
        .catch(error => {
            console.error('Erreur chargement groupe:', error);
            alert('Erreur lors du chargement du groupe');
        });
}

function populateGroupeDetail(data) {
    document.getElementById('modal-groupe-nom').textContent = data.name;
    document.getElementById('modal-groupe-description').textContent = data.description || data.full_description || 'Aucune description';
    document.getElementById('modal-groupe-type').textContent = data.is_public ? 'Public' : 'Privé';
    document.getElementById('modal-groupe-membres-count').textContent = data.member_count;
    document.getElementById('modal-groupe-posts-count').textContent = data.posts_count;
    document.getElementById('modal-groupe-date-creation').textContent = data.created_at;
    
    // Admins
    const adminsList = document.getElementById('admins-list');
    adminsList.innerHTML = data.admins.map(admin => `
        <div class="admin-item">
            ${admin.avatar_url ? 
                `<img src="${admin.avatar_url}" alt="${admin.username}">` :
                `<div class="avatar-placeholder">${admin.username[0].toUpperCase()}</div>`
            }
            <span>${admin.username}</span>
        </div>
    `).join('');
    
    // Membres
    const membresList = document.getElementById('membres-list');
    membresList.innerHTML = data.members.map(member => `
        <div class="membre-item">
            ${member.avatar_url ? 
                `<img src="${member.avatar_url}" alt="${member.username}">` :
                `<div class="avatar-placeholder">${member.username[0].toUpperCase()}</div>`
            }
            <span>${member.username}</span>
        </div>
    `).join('');
    
    modal.dataset.groupeId = data.id;
}

function closeGroupeDetailModal() {
    const modal = document.getElementById('groupe-detail-modal');
    if (modal) modal.style.display = 'none';
}

function switchGroupeTab(tab) {
    document.querySelectorAll('.modal-tab').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('.modal-tab-content').forEach(c => c.classList.remove('active'));
    
    document.querySelector(`.modal-tab[data-tab="${tab}"]`).classList.add('active');
    document.getElementById(`tab-${tab}`).classList.add('active');
}

function masquerPost(postId) {
    if (confirm('Masquer ce post ?')) {
        // TODO: Appel API
        console.log('Masquer post:', postId);
        alert('Post masqué');
        location.reload();
    }
}

function supprimerPost(postId) {
    const raison = prompt('Raison de la suppression :');
    if (raison) {
        if (confirm('Êtes-vous sûr de vouloir supprimer ce post ?')) {
            // TODO: Appel API
            console.log('Supprimer post:', postId, raison);
            alert('Post supprimé');
            location.reload();
        }
    }
}

// ============================================
// ACTIONS GROUPES
// ============================================

function openGroupeDetail(groupeId) {
    // TODO: Ouvrir modal détail groupe
    console.log('Ouvrir détail groupe:', groupeId);
    alert('Modal détail groupe à implémenter');
}

// ============================================
// ACTIONS MESSAGES
// ============================================

function openConversationDetail(conversationId) {
    // TODO: Ouvrir modal conversation
    console.log('Ouvrir conversation:', conversationId);
    alert('Modal conversation à implémenter');
}

// ============================================
// UTILITAIRES
// ============================================

function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        alert('ID copié : ' + text);
    });
}

function changePerPage(value) {
    const url = new URL(window.location);
    url.searchParams.set('per_page', value);
    url.searchParams.set('page', '1');
    window.location.href = url.toString();
}

function switchToFeedView() {
    const url = new URL(window.location);
    url.searchParams.set('feed', '1');
    window.location.href = url.toString();
}

function switchToTableView() {
    const url = new URL(window.location);
    url.searchParams.delete('feed');
    window.location.href = url.toString();
}

function toggleFeedActions(button) {
    const menu = button.nextElementSibling;
    if (menu) {
        document.querySelectorAll('.dropdown-menu').forEach(m => {
            if (m !== menu) m.classList.remove('show');
        });
        menu.classList.toggle('show');
    }
}

// Actions depuis modal
function masquerPostFromModal() {
    const modal = document.getElementById('post-detail-modal');
    const postId = modal ? modal.dataset.postId : null;
    if (postId) masquerPost(postId);
}

function epinglerPostFromModal() {
    const modal = document.getElementById('post-detail-modal');
    const postId = modal ? modal.dataset.postId : null;
    if (postId) {
        // TODO: Appel API
        console.log('Épingler post:', postId);
        alert('Post épinglé');
    }
}

function desactiverCommentairesPost() {
    const modal = document.getElementById('post-detail-modal');
    const postId = modal ? modal.dataset.postId : null;
    if (postId) {
        // TODO: Appel API
        console.log('Désactiver commentaires post:', postId);
        alert('Commentaires désactivés');
    }
}

function supprimerPostFromModal() {
    const modal = document.getElementById('post-detail-modal');
    const postId = modal ? modal.dataset.postId : null;
    if (postId) supprimerPost(postId);
}

function partagerPost() {
    const modal = document.getElementById('post-detail-modal');
    const postId = modal ? modal.dataset.postId : null;
    if (postId) {
        const url = window.location.origin + '/connect/post/' + postId + '/';
        navigator.clipboard.writeText(url).then(() => {
            alert('Lien copié dans le presse-papiers');
        });
    }
}

function voirProfilAuteurPost() {
    const modal = document.getElementById('post-detail-modal');
    const postId = modal ? modal.dataset.postId : null;
    if (postId) {
        // TODO: Récupérer ID auteur depuis modal
        console.log('Voir profil auteur');
    }
}

function voirGroupePost() {
    const modal = document.getElementById('post-detail-modal');
    const postId = modal ? modal.dataset.postId : null;
    if (postId) {
        // TODO: Récupérer ID groupe depuis modal
        console.log('Voir groupe');
    }
}

function voirTousLikes() {
    alert('Liste complète des likes à implémenter');
}

function ajouterCommentaire() {
    const input = document.getElementById('new-comment-input');
    const modal = document.getElementById('post-detail-modal');
    const postId = modal ? modal.dataset.postId : null;
    
    if (!input.value.trim() || !postId) return;
    
    // TODO: Appel API pour ajouter commentaire
    console.log('Ajouter commentaire:', input.value, 'au post:', postId);
    alert('Commentaire ajouté');
    input.value = '';
    // Recharger les commentaires
}

function openLightbox(imageUrl) {
    // TODO: Implémenter lightbox
    window.open(imageUrl, '_blank');
}

// Actions groupes
function modifierGroupe() {
    const modal = document.getElementById('groupe-detail-modal');
    const groupeId = modal ? modal.dataset.groupeId : null;
    if (groupeId) {
        alert('Modification groupe à implémenter');
    }
}

function gererMembres() {
    switchGroupeTab('membres');
}

function gererAdmins() {
    alert('Gestion admins à implémenter');
}

function archiverGroupe() {
    const modal = document.getElementById('groupe-detail-modal');
    const groupeId = modal ? modal.dataset.groupeId : null;
    if (groupeId && confirm('Archiver ce groupe ?')) {
        // TODO: Appel API
        console.log('Archiver groupe:', groupeId);
        alert('Groupe archivé');
        location.reload();
    }
}

function supprimerGroupe() {
    const modal = document.getElementById('groupe-detail-modal');
    const groupeId = modal ? modal.dataset.groupeId : null;
    if (groupeId && confirm('Êtes-vous sûr de vouloir supprimer ce groupe ? Cette action est irréversible.')) {
        // TODO: Appel API
        console.log('Supprimer groupe:', groupeId);
        alert('Groupe supprimé');
        location.reload();
    }
}

function openColumnsModal() {
    alert('Configuration colonnes à venir');
}

function exportDonnees() {
    const url = new URL(window.location);
    url.searchParams.set('export', 'csv');
    window.location.href = url.toString();
}

function openStatsEngagement() {
    switchView('analytics');
}

function openModerationAvancee() {
    alert('Modération avancée à venir');
}

function openBadgesPage() {
    window.location.href = '/connect-admin/badges/';
}

// Événements
function creerEvenement() {
    const modal = document.getElementById('evenement-modal');
    if (modal) {
        modal.style.display = 'flex';
        document.getElementById('modal-evenement-title').textContent = 'Créer événement';
    }
}

function closeEvenementModal() {
    const modal = document.getElementById('evenement-modal');
    if (modal) modal.style.display = 'none';
}

// Fermer modals avec Escape
document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
        closePostDetailModal();
        closeGroupeDetailModal();
        closeEvenementModal();
    }
});

// Fermer modals au click sur overlay
document.addEventListener('click', function(e) {
    const modals = ['post-detail-modal', 'groupe-detail-modal', 'evenement-modal'];
    modals.forEach(modalId => {
        const modal = document.getElementById(modalId);
        if (modal && e.target === modal) {
            if (modalId === 'post-detail-modal') closePostDetailModal();
            else if (modalId === 'groupe-detail-modal') closeGroupeDetailModal();
            else if (modalId === 'evenement-modal') closeEvenementModal();
        }
    });
});

