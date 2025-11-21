/**
 * SUPPORT TICKETS - JavaScript pour gestion tickets support avec drag & drop
 */

// ============================================
// VARIABLES GLOBALES
// ============================================

let draggedTicket = null;

// ============================================
// INITIALISATION
// ============================================

function initSupportTickets() {
    initDragAndDrop();
    initTicketDetail();
}

function initTicketDetail() {
    // Initialisation de la page de détail si elle existe
    if (document.getElementById('ticket-reply-form')) {
        initTicketReply();
    }
}

// ============================================
// DRAG & DROP
// ============================================

function initDragAndDrop() {
    const ticketCards = document.querySelectorAll('.ticket-card');
    const columns = document.querySelectorAll('.kanban-column');
    
    // Initialiser les cartes
    ticketCards.forEach(card => {
        card.addEventListener('dragstart', handleDragStart);
        card.addEventListener('dragend', handleDragEnd);
    });
    
    // Initialiser les colonnes
    columns.forEach(column => {
        column.addEventListener('dragover', handleDragOver);
        column.addEventListener('drop', handleDrop);
        column.addEventListener('dragleave', handleDragLeave);
        column.addEventListener('dragenter', handleDragEnter);
    });
}

function handleDragStart(e) {
    draggedTicket = this;
    this.classList.add('dragging');
    e.dataTransfer.effectAllowed = 'move';
    e.dataTransfer.setData('text/html', this.innerHTML);
}

function handleDragEnd(e) {
    this.classList.remove('dragging');
    
    // Retirer la classe drag-over de toutes les colonnes
    document.querySelectorAll('.kanban-column').forEach(col => {
        col.classList.remove('drag-over');
    });
}

function handleDragOver(e) {
    if (e.preventDefault) {
        e.preventDefault();
    }
    e.dataTransfer.dropEffect = 'move';
    return false;
}

function handleDragEnter(e) {
    this.classList.add('drag-over');
}

function handleDragLeave(e) {
    this.classList.remove('drag-over');
}

function handleDrop(e) {
    if (e.stopPropagation) {
        e.stopPropagation();
    }
    
    this.classList.remove('drag-over');
    
    if (draggedTicket !== null) {
        const column = this.querySelector('.column-cards');
        const newStatus = this.dataset.status;
        
        if (column) {
            // Déplacer la carte
            column.appendChild(draggedTicket);
            
            // Mettre à jour le statut côté serveur
            const ticketId = draggedTicket.dataset.ticketId;
            updateTicketStatus(ticketId, newStatus);
        }
    }
    
    return false;
}

// ============================================
// UPDATE STATUS
// ============================================

function updateTicketStatus(ticketId, newStatus) {
    const formData = new FormData();
    formData.append('status', newStatus);
    formData.append('csrfmiddlewaretoken', csrfToken);
    
    const url = updateStatusUrl.replace('TICKET_ID', ticketId);
    
    fetch(url, {
        method: 'POST',
        body: formData,
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Mettre à jour le compteur de la colonne
            updateColumnCounts();
            showSuccessMessage(data.message || 'Statut mis à jour');
        } else {
            // En cas d'erreur, remettre la carte à sa place
            window.location.reload();
            alert('Erreur: ' + (data.error || 'Impossible de mettre à jour le statut'));
        }
    })
    .catch(error => {
        console.error('Erreur:', error);
        window.location.reload();
        alert('Erreur lors de la mise à jour du statut');
    });
}

function updateColumnCounts() {
    document.querySelectorAll('.kanban-column').forEach(column => {
        const cards = column.querySelectorAll('.ticket-card');
        const countElement = column.querySelector('.column-count');
        if (countElement) {
            countElement.textContent = cards.length;
        }
    });
}

// ============================================
// TICKET DETAIL
// ============================================

function viewTicketDetail(ticketId) {
    const url = ticketDetailUrl.replace('TICKET_ID', ticketId);
    window.location.href = url;
}

function closeTicketModal() {
    const modal = document.getElementById('ticket-detail-modal');
    if (modal) {
        modal.style.display = 'none';
    }
}

// ============================================
// TICKET REPLY
// ============================================

function initTicketReply() {
    const form = document.getElementById('ticket-reply-form');
    if (form) {
        form.addEventListener('submit', handleTicketReply);
    }
}

function handleTicketReply(e) {
    e.preventDefault();
    
    const formData = new FormData(this);
    
    fetch(replyUrl, {
        method: 'POST',
        body: formData,
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showSuccessMessage(data.message || 'Réponse envoyée avec succès');
            // Recharger la page après 1 seconde
            setTimeout(() => {
                window.location.reload();
            }, 1000);
        } else {
            alert('Erreur: ' + (data.error || 'Impossible d\'envoyer la réponse'));
        }
    })
    .catch(error => {
        console.error('Erreur:', error);
        alert('Erreur lors de l\'envoi de la réponse');
    });
}

// ============================================
// LOAD TEMPLATE
// ============================================

function loadTemplate(templateId) {
    if (!templateId || !templates || !templates[templateId]) {
        return;
    }
    
    const textarea = document.getElementById('reply-content');
    if (textarea) {
        let templateContent = templates[templateId];
        
        // Remplacer les variables
        if (typeof ticket !== 'undefined') {
            templateContent = templateContent.replace(/\{user_name\}/g, ticket.user.username || '');
            templateContent = templateContent.replace(/\{ticket_id\}/g, ticket.ticket_id || '');
        }
        
        textarea.value = templateContent;
    }
}

// ============================================
// ASSIGN TICKET
// ============================================

function assignTicket(ticketId, assignedToId) {
    const formData = new FormData();
    if (assignedToId) {
        formData.append('assigned_to_id', assignedToId);
    }
    formData.append('csrfmiddlewaretoken', csrfToken);
    
    fetch(assignUrl, {
        method: 'POST',
        body: formData,
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showSuccessMessage(data.message || 'Ticket assigné avec succès');
        } else {
            alert('Erreur: ' + (data.error || 'Impossible d\'assigner le ticket'));
        }
    })
    .catch(error => {
        console.error('Erreur:', error);
        alert('Erreur lors de l\'assignation');
    });
}

// ============================================
// UPDATE TICKET STATUS (détail page)
// ============================================

function updateTicketStatus(ticketId, newStatus) {
    const formData = new FormData();
    formData.append('status', newStatus);
    formData.append('csrfmiddlewaretoken', csrfToken);
    
    fetch(updateStatusUrl.replace('TICKET_ID', ticketId), {
        method: 'POST',
        body: formData,
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showSuccessMessage(data.message || 'Statut mis à jour');
            // Optionnel: mettre à jour l'UI sans recharger
            // window.location.reload();
        } else {
            alert('Erreur: ' + (data.error || 'Impossible de mettre à jour le statut'));
            // Restaurer l'ancienne valeur
            const select = document.getElementById('ticket-status');
            if (select) {
                // TODO: stocker l'ancienne valeur
            }
        }
    })
    .catch(error => {
        console.error('Erreur:', error);
        alert('Erreur lors de la mise à jour du statut');
    });
}

// ============================================
// FILTERS
// ============================================

function filterTickets() {
    const priority = document.getElementById('filter-priority')?.value || '';
    const category = document.getElementById('filter-category')?.value || '';
    const assigned = document.getElementById('filter-assigned')?.value || '';
    
    const params = new URLSearchParams();
    if (priority) params.append('priority', priority);
    if (category) params.append('category', category);
    if (assigned) params.append('assigned', assigned);
    
    window.location.href = window.location.pathname + (params.toString() ? '?' + params.toString() : '');
}

// ============================================
// UTILITAIRES
// ============================================

function showSuccessMessage(message) {
    const msg = document.createElement('div');
    msg.className = 'alert alert-success';
    msg.textContent = message;
    msg.style.cssText = 'position: fixed; top: 20px; right: 20px; padding: 12px 20px; background: #10B981; color: white; border-radius: 8px; z-index: 9999; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);';
    document.body.appendChild(msg);
    
    setTimeout(() => {
        msg.remove();
    }, 3000);
}

