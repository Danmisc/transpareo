// ============================================
// BADGES MANAGEMENT
// ============================================

function creerBadge() {
    const modal = document.getElementById('badge-modal');
    if (modal) {
        modal.style.display = 'flex';
        document.getElementById('modal-badge-title').textContent = 'Créer badge';
        document.getElementById('badge-form').reset();
    }
}

function closeBadgeModal() {
    const modal = document.getElementById('badge-modal');
    if (modal) modal.style.display = 'none';
}

function modifierBadge(badgeId) {
    // TODO: Charger données badge et ouvrir modal
    alert('Modification badge à implémenter');
}

function attribuerBadge(badgeId) {
    const userId = prompt('ID utilisateur :');
    if (userId) {
        // TODO: Appel API
        console.log('Attribuer badge', badgeId, 'à user', userId);
        alert('Badge attribué');
    }
}

function supprimerBadge(badgeId) {
    if (confirm('Êtes-vous sûr de vouloir supprimer ce badge ?')) {
        // TODO: Appel API
        console.log('Supprimer badge:', badgeId);
        alert('Badge supprimé');
        location.reload();
    }
}

// Gestion formulaire
document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('badge-form');
    if (form) {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            // TODO: Appel API pour créer badge
            const formData = new FormData(form);
            console.log('Créer badge:', Object.fromEntries(formData));
            alert('Badge créé');
            closeBadgeModal();
            location.reload();
        });
    }
});

// BADGES MANAGEMENT
// ============================================

function creerBadge() {
    const modal = document.getElementById('badge-modal');
    if (modal) {
        modal.style.display = 'flex';
        document.getElementById('modal-badge-title').textContent = 'Créer badge';
        document.getElementById('badge-form').reset();
    }
}

function closeBadgeModal() {
    const modal = document.getElementById('badge-modal');
    if (modal) modal.style.display = 'none';
}

function modifierBadge(badgeId) {
    // TODO: Charger données badge et ouvrir modal
    alert('Modification badge à implémenter');
}

function attribuerBadge(badgeId) {
    const userId = prompt('ID utilisateur :');
    if (userId) {
        // TODO: Appel API
        console.log('Attribuer badge', badgeId, 'à user', userId);
        alert('Badge attribué');
    }
}

function supprimerBadge(badgeId) {
    if (confirm('Êtes-vous sûr de vouloir supprimer ce badge ?')) {
        // TODO: Appel API
        console.log('Supprimer badge:', badgeId);
        alert('Badge supprimé');
        location.reload();
    }
}

// Gestion formulaire
document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('badge-form');
    if (form) {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            // TODO: Appel API pour créer badge
            const formData = new FormData(form);
            console.log('Créer badge:', Object.fromEntries(formData));
            alert('Badge créé');
            closeBadgeModal();
            location.reload();
        });
    }
});

