/* ============================================
   MESSAGES COMPLETE - JAVASCRIPT
   Version reconstruite complète
   ============================================ */

// ============================================
// ÉTAT GLOBAL
// ============================================

window.messagesState = {
    currentUserId: null,
    activeConversationId: null,
    conversations: [],
    messages: {},
    unreadCounts: {},
    onlineUsers: new Set(),
    typingUsers: new Set(),
    websocket: null,
    searchDebounceTimer: null,
    typingDebounceTimer: null,
    voiceRecording: null,
    mediaRecorder: null,
    selectedMedia: [],
    selectedFiles: [],
    selectedRecipients: [],
    currentFilter: 'all',
    searchQuery: '',
    isTyping: false,
    isSending: false,
    isNearBottom: true
};

const state = window.messagesState;

// ============================================
// INITIALISATION
// ============================================

document.addEventListener('DOMContentLoaded', function() {
    console.log('✓ Messages page initializing...');
    
    // Initialiser les variables
    state.currentUserId = window.currentUserId || null;
    state.activeConversationId = window.activeConversationId || null;
    
    // Récupérer conversation active depuis URL
    const urlParams = new URLSearchParams(window.location.search);
    const conversationId = urlParams.get('conversation');
    if (conversationId) {
        state.activeConversationId = parseInt(conversationId);
    }
    
    // Initialiser l'affichage initial
    if (!state.activeConversationId) {
        // Aucune conversation sélectionnée - afficher chat-empty
        const chatEmpty = document.getElementById('chat-empty');
        if (chatEmpty) {
            chatEmpty.style.display = 'flex';
        }
        const messagesArea = document.getElementById('messages-area');
        if (messagesArea) {
            messagesArea.style.display = 'none';
        }
        const messageInputArea = document.getElementById('message-input-area');
        if (messageInputArea) {
            messageInputArea.style.display = 'none';
        }
        const chatHeader = document.getElementById('chat-header');
        if (chatHeader) {
            chatHeader.style.display = 'none';
        }
    }
    
    // Initialiser WebSocket
    initWebSocket();
    
    // Charger conversations
    loadConversations();
    
    // Charger messages si conversation active
    if (state.activeConversationId) {
            loadMessages(state.activeConversationId);
    }
    
    // Setup event listeners
    setupEventListeners();
    
    // S'assurer que le bouton détails est bien attaché
    const detailsBtn = document.querySelector('[onclick="toggleDetailsPanel()"]');
    if (detailsBtn) {
        // Retirer l'onclick inline et utiliser addEventListener
        detailsBtn.removeAttribute('onclick');
        detailsBtn.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            if (window.toggleDetailsPanel) {
                window.toggleDetailsPanel();
            }
        });
    }
    
    console.log('✓ Messages page initialized');
});

// ============================================
// WEBSOCKET - TEMPS RÉEL
// ============================================

function initWebSocket() {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws/messages/`;
    
    try {
        state.websocket = new WebSocket(wsUrl);
        
        state.websocket.onopen = function() {
            console.log('✓ WebSocket connected');
            if (state.currentUserId) {
                state.websocket.send(JSON.stringify({
                    type: 'subscribe',
                    userId: state.currentUserId
                }));
            }
            if (state.activeConversationId) {
                state.websocket.send(JSON.stringify({
                    type: 'subscribe',
                    conversation_id: state.activeConversationId
                }));
            }
        };
        
        state.websocket.onmessage = function(event) {
            try {
            const data = JSON.parse(event.data);
            handleWebSocketMessage(data);
            } catch (e) {
                console.error('Error parsing WebSocket message:', e);
            }
        };
        
        state.websocket.onerror = function(error) {
            console.error('WebSocket error:', error);
        };
        
        state.websocket.onclose = function() {
            console.log('WebSocket disconnected, reconnecting...');
            setTimeout(initWebSocket, 3000);
        };
    } catch (error) {
        console.error('WebSocket initialization error:', error);
    }
}

function handleWebSocketMessage(data) {
    switch (data.type) {
        case 'new_message':
            handleNewMessage(data.message);
            break;
        case 'message_read':
            handleMessageRead(data.messageId, data.userId);
            break;
        case 'typing_start':
            handleTypingStart(data.conversationId, data.userId);
            break;
        case 'typing_stop':
            handleTypingStop(data.conversationId, data.userId);
            break;
        case 'user_online':
            handleUserOnline(data.userId);
            break;
        case 'user_offline':
            handleUserOffline(data.userId);
            break;
        case 'reaction_update':
            handleReactionUpdate(data.reaction);
            break;
    }
}

function handleNewMessage(message) {
    if (message.conversation_id === state.activeConversationId) {
        // Ajouter message à l'UI
        addMessageToUI(message);
        scrollToBottom(false); // Auto-scroll seulement si en bas
        markMessageAsRead(message.id);
    }
    // Mettre à jour la liste des conversations
    updateConversationInList(message.conversation_id);
    loadConversations();
}

function handleMessageRead(messageId, userId) {
    const messageEl = document.querySelector(`[data-message-id="${messageId}"]`);
    if (messageEl) {
        const statusEl = messageEl.querySelector('.message-status');
        if (statusEl) {
            statusEl.innerHTML = '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/></svg>';
            statusEl.classList.add('read');
        }
    }
}

function handleTypingStart(conversationId, userId) {
    if (conversationId === state.activeConversationId) {
        showTypingIndicator(userId);
    }
}

function handleTypingStop(conversationId, userId) {
    if (conversationId === state.activeConversationId) {
        hideTypingIndicator();
    }
}

function handleUserOnline(userId) {
    state.onlineUsers.add(userId);
    updateOnlineStatus(userId, true);
}

function handleUserOffline(userId) {
    state.onlineUsers.delete(userId);
    updateOnlineStatus(userId, false);
}

function handleReactionUpdate(reaction) {
    // Mettre à jour les réactions sur le message
    const messageEl = document.querySelector(`[data-message-id="${reaction.message_id}"]`);
    if (messageEl) {
        updateMessageReactions(messageEl, reaction);
    }
}

// ============================================
// CHARGEMENT DONNÉES
// ============================================

function loadConversations() {
    const filter = state.currentFilter;
    const search = state.searchQuery;
    
    let url = '/api/connect/conversations/';
    const params = new URLSearchParams();
    if (filter !== 'all') params.append('filter', filter);
    if (search) params.append('search', search);
    if (params.toString()) url += '?' + params.toString();
    
    fetch(url, {
        credentials: 'same-origin',
        headers: {
            'X-CSRFToken': getCSRFToken()
        }
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
            state.conversations = data.conversations || [];
                state.unreadCounts = data.unread_counts || {};
            renderConversationsList();
            }
        })
        .catch(error => {
            console.error('Error loading conversations:', error);
        });
}

function loadMessages(conversationId, before = null) {
    if (!conversationId) {
        console.error('loadMessages: conversationId is required');
        return Promise.resolve();
    }
    
    console.log('Loading messages for conversation:', conversationId, 'before:', before);
    
    let url = `/api/connect/conversations/${conversationId}/messages/`;
    if (before) {
        url += `?before=${before}`;
    }
    
    // Afficher loading
    const container = document.getElementById('messages-container');
    if (container && !before) {
        container.innerHTML = '<div class="loading-messages">Chargement des messages...</div>';
    }
    
    return fetch(url, {
        method: 'GET',
        credentials: 'same-origin',
        headers: {
            'X-CSRFToken': getCSRFToken()
        }
    })
        .then(async response => {
            const contentType = response.headers.get('content-type');
            if (!contentType || !contentType.includes('application/json')) {
                const text = await response.text();
                console.error('Received HTML instead of JSON:', text.substring(0, 200));
                throw new Error('Réponse invalide du serveur. Vérifiez votre authentification.');
            }
            
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({ error: `HTTP error! status: ${response.status}` }));
                throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            console.log('Messages loaded:', data);
            if (data.success) {
                if (!state.messages[conversationId]) {
                    state.messages[conversationId] = [];
                }
                
                const newMessages = data.messages || [];
                if (before) {
                    // Ajouter au début pour historique (éviter les doublons)
                    const existingIds = new Set(state.messages[conversationId].map(m => m.id));
                    const uniqueNewMessages = newMessages.filter(m => !existingIds.has(m.id));
                    state.messages[conversationId] = [...uniqueNewMessages, ...state.messages[conversationId]];
                } else {
                    // Remplacer pour nouveau chargement
                    state.messages[conversationId] = newMessages;
                }
            
                renderMessages(before);
                if (!before) {
                    scrollToBottom(true); // Force scroll au chargement initial
                    markConversationAsRead(conversationId);
                }
            } else {
                console.error('Error loading messages:', data.error);
                if (container) {
                    container.innerHTML = `<div class="error-messages">Erreur: ${data.error || 'Impossible de charger les messages'}</div>`;
                }
            }
        })
        .catch(error => {
            console.error('Error loading messages:', error);
            if (container) {
                container.innerHTML = `<div class="error-messages">Erreur: ${error.message || 'Impossible de charger les messages'}</div>`;
            }
            throw error;
        });
}

// ============================================
// RENDU UI
// ============================================

function renderConversationsList() {
    const container = document.getElementById('conversations-list');
    if (!container) return;
    
    if (state.conversations.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <svg width="120" height="120" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                    <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
                </svg>
                <h3>Aucune conversation</h3>
                <button class="btn-primary" onclick="openNewConversationModal()">Démarrer une conversation</button>
            </div>
        `;
        return;
    }
    
    let html = '';
    state.conversations.forEach(conv => {
        const unreadCount = state.unreadCounts[conv.id] || 0;
        const isActive = conv.id === state.activeConversationId;
        const otherUser = conv.other_user || {};
        const lastMessage = conv.last_message || {};
        const convId = conv.id || conv.conversation_id || conv.conversation?.id;
        
        html += `
            <div class="conversation-item ${isActive ? 'active' : ''} ${conv.favorited ? 'favorited' : ''}" 
                 data-conversation-id="${convId}">
                <div class="conversation-avatar">
                    ${renderAvatar(conv)}
                    ${otherUser.is_online ? '<span class="online-badge"></span>' : ''}
                </div>
                <div class="conversation-content">
                    <div class="conversation-header">
                        <span class="conversation-name">
                            ${conv.favorited ? '<span class="favorite-icon">⭐</span> ' : ''}
                            ${escapeHtml(otherUser.display_name || otherUser.username || otherUser.name || 'Utilisateur')}
                        </span>
                        <span class="conversation-time">${lastMessage.created_at ? formatRelativeTime(lastMessage.created_at) : ''}</span>
                    </div>
                    <div class="conversation-preview">
                        ${lastMessage.sender_id === state.currentUserId ? '<span class="you-prefix">Vous : </span>' : ''}
                        ${escapeHtml(lastMessage.content || '')}
                    </div>
                </div>
                ${unreadCount > 0 ? `<span class="unread-badge">${unreadCount}</span>` : ''}
            </div>
        `;
    });
    
    container.innerHTML = html;
    
    // Attacher les event listeners aux conversations
    container.querySelectorAll('.conversation-item').forEach(item => {
        const conversationId = item.dataset.conversationId;
        if (conversationId) {
            item.addEventListener('click', function(e) {
                e.preventDefault();
                e.stopPropagation();
                console.log('Conversation clicked:', conversationId);
                if (window.loadConversation) {
                    window.loadConversation(parseInt(conversationId));
                } else {
                    console.error('loadConversation function not found');
                }
            });
            // Ajouter un style cursor pointer
            item.style.cursor = 'pointer';
        }
    });
}

function renderAvatar(obj) {
    // Peut recevoir conversation ou user directement
    const user = obj.other_user || obj || {};
    const avatarUrl = user.profile_picture || user.avatar;
    const username = user.username || user.display_name || 'U';
    const displayName = user.display_name || user.username || 'U';
    
    if (avatarUrl) {
        return `<img src="${escapeHtml(avatarUrl)}" alt="${escapeHtml(displayName)}">`;
    } else {
        const initial = username[0].toUpperCase();
        return `<div class="avatar-placeholder">${initial}</div>`;
    }
}

function renderMessages(before = null) {
    const container = document.getElementById('messages-container');
    if (!container) {
        console.error('Messages container not found');
        return;
    }
    
    if (!state.activeConversationId) {
        container.innerHTML = '<div class="empty-messages">Sélectionnez une conversation</div>';
        return;
    }
    
    const messages = state.messages[state.activeConversationId] || [];
    console.log('Rendering messages:', messages.length, 'before:', before);
    
    if (messages.length === 0) {
        container.innerHTML = '<div class="empty-messages">Aucun message. Commencez la conversation !</div>';
        return;
    }
    
    // Sauvegarder la position de scroll avant le rendu (pour chargement historique)
    const messagesArea = document.getElementById('messages-area');
    let savedScrollHeight = 0;
    let savedScrollTop = 0;
    if (messagesArea && before) {
        savedScrollHeight = messagesArea.scrollHeight;
        savedScrollTop = messagesArea.scrollTop;
    }
    
    let html = '';
    let lastDate = null;
    let lastSenderId = null;
    let lastMessageTime = null;
    
    messages.forEach((message, index) => {
        try {
            const messageDate = new Date(message.created_at);
            if (isNaN(messageDate.getTime())) {
                console.error('Invalid date:', message.created_at);
                return;
            }
            
            const messageDateStr = formatDate(messageDate);
            const currentDate = messageDateStr;
            
            // Séparateur de date
            if (currentDate !== lastDate) {
                html += `<div class="date-separator">${formatDateLabel(messageDate)}</div>`;
                lastDate = currentDate;
            }
        
            const isSent = message.sender_id === state.currentUserId;
            const timeDiff = lastMessageTime ? (messageDate - lastMessageTime) : Infinity;
            const isGrouped = lastSenderId === message.sender_id && timeDiff < 120000; // 2 minutes
        
            html += `
                <div class="message-wrapper ${isSent ? 'message-sent' : 'message-received'} ${isGrouped ? 'grouped' : ''}" 
                 data-message-id="${message.id}">
                    ${!isSent && !isGrouped ? `<div class="message-avatar">${renderMessageAvatar(message)}</div>` : ''}
                    <div class="message-bubble">
                        ${renderMessageContent(message)}
                        <div class="message-footer">
                            <span class="message-time">${formatTime(messageDate)}</span>
                            ${isSent ? renderMessageStatus(message) : ''}
                        </div>
                    </div>
                </div>
            `;
        
            lastSenderId = message.sender_id;
            lastMessageTime = messageDate;
        } catch (error) {
            console.error('Error rendering message:', error, message);
        }
    });
    
    // Utiliser requestAnimationFrame pour un rendu smooth
    requestAnimationFrame(() => {
        container.innerHTML = html;
        
        // Gérer le scroll après le rendu
        requestAnimationFrame(() => {
            if (!before) {
                // Nouveau chargement : scroll vers le bas
                scrollToBottom(true);
            } else {
                // Chargement historique : maintenir la position
                if (messagesArea && savedScrollHeight > 0) {
                    const newScrollHeight = messagesArea.scrollHeight;
                    const heightDiff = newScrollHeight - savedScrollHeight;
                    messagesArea.scrollTop = savedScrollTop + heightDiff;
                }
            }
        });
    });
}

function renderMessageContent(message) {
    if (message.image) {
        const imageUrl = typeof message.image === 'string' ? message.image : (message.image.url || '');
        if (imageUrl) {
            return `<div class="message-image"><img src="${escapeHtml(imageUrl)}" alt="Image" onclick="openLightbox('${escapeHtml(imageUrl)}')"></div>`;
        }
    }
    if (message.document) {
        return renderFileMessage(message);
    }
    if (message.audio) {
        return renderAudioMessage(message);
    }
    const content = message.content || '';
    if (content.trim()) {
        return `<div class="message-text">${formatMessageText(content)}</div>`;
    }
    return '<div class="message-text"><em>Message vide</em></div>';
}

function renderFileMessage(message) {
    const fileName = message.document_name || 'Fichier';
    const fileSize = formatFileSize(message.document_size || 0);
    return `
        <div class="message-file">
            <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                <polyline points="14 2 14 8 20 8"></polyline>
            </svg>
            <div class="file-info">
                <div class="file-name">${escapeHtml(fileName)}</div>
                <div class="file-size">${fileSize}</div>
            </div>
            <a href="${escapeHtml(message.document)}" download class="file-download">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
                    <polyline points="7 10 12 15 17 10"></polyline>
                    <line x1="12" y1="15" x2="12" y2="3"></line>
                </svg>
            </a>
        </div>
    `;
}

function renderAudioMessage(message) {
    return `
        <div class="message-audio">
            <button class="audio-play" onclick="playAudio('${escapeHtml(message.audio)}')">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M8 5v14l11-7z"/>
                </svg>
            </button>
            <div class="audio-waveform"></div>
            <span class="audio-duration">${formatDuration(message.audio_duration || 0)}</span>
        </div>
    `;
}

function renderMessageAvatar(message) {
    const sender = message.sender || {};
    const avatarUrl = sender.profile_picture || sender.avatar;
    const displayName = sender.display_name || sender.get_full_name || sender.username || 'Utilisateur';
    const username = sender.username || 'U';
    const initial = displayName[0].toUpperCase();
    
    if (avatarUrl) {
        return `<img src="${escapeHtml(avatarUrl)}" alt="${escapeHtml(displayName)}">`;
    } else {
        return `<div class="avatar-placeholder small">${initial}</div>`;
    }
}

function renderMessageStatus(message) {
    if (message.read) {
        return '<span class="message-status read"><svg viewBox="0 0 24 24" fill="currentColor"><path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/></svg></span>';
    } else if (message.delivered) {
        return '<span class="message-status delivered"><svg viewBox="0 0 24 24" fill="currentColor"><path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/></svg></span>';
    }
    return '<span class="message-status sent"><svg viewBox="0 0 24 24" fill="currentColor"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/></svg></span>';
}

// ============================================
// ACTIONS CONVERSATIONS
// ============================================

window.loadConversation = function(conversationId) {
    if (!conversationId) {
        console.error('loadConversation: conversationId is required');
        return;
    }
    
    console.log('Loading conversation:', conversationId);
    state.activeConversationId = parseInt(conversationId);
    
    // Trouver la conversation dans la liste
    const conversation = state.conversations.find(c => c.id === parseInt(conversationId));
    
    // Mettre à jour l'URL
    const url = new URL(window.location);
    url.searchParams.set('conversation', conversationId);
    window.history.pushState({}, '', url);
    
    // Mettre à jour l'UI - marquer conversation active
    document.querySelectorAll('.conversation-item').forEach(item => {
        const itemId = parseInt(item.dataset.conversationId);
        item.classList.toggle('active', itemId === parseInt(conversationId));
    });
    
    // Afficher le chat panel
    const chatPanel = document.getElementById('chat-panel');
    if (chatPanel) {
        chatPanel.style.display = 'flex';
        chatPanel.style.visibility = 'visible';
    }
    
    // Afficher le chat-header
    const chatHeader = document.getElementById('chat-header');
    if (chatHeader) {
        chatHeader.style.display = 'flex';
    }
    
    // Afficher la zone de messages
    const messagesArea = document.getElementById('messages-area');
    if (messagesArea) {
        messagesArea.style.display = 'flex';
        messagesArea.style.visibility = 'visible';
    }
    
    // Afficher la zone de saisie
    const messageInputArea = document.getElementById('message-input-area');
    if (messageInputArea) {
        messageInputArea.style.display = 'block';
        messageInputArea.style.visibility = 'visible';
    }
    
    // Cacher le message "Sélectionnez une conversation"
    const chatEmpty = document.getElementById('chat-empty');
    if (chatEmpty) {
        chatEmpty.style.display = 'none';
    }
    
    // Mettre à jour le chat-header avec les infos de la conversation
    if (conversation) {
        const otherUser = conversation.other_user || conversation.participants?.find(p => p.id !== state.currentUserId);
        if (otherUser) {
            // Mettre à jour l'avatar
            const chatAvatar = document.getElementById('chat-avatar');
            if (chatAvatar) {
                const avatarUrl = otherUser.avatar || otherUser.profile_picture;
                const username = otherUser.username || otherUser.get_full_name || otherUser.display_name || 'U';
                const initial = username[0].toUpperCase();
                
                // Nettoyer le contenu existant
                chatAvatar.innerHTML = '';
                
                if (avatarUrl) {
                    const img = document.createElement('img');
                    img.src = avatarUrl;
                    img.alt = username;
                    chatAvatar.appendChild(img);
                } else {
                    const placeholder = document.createElement('div');
                    placeholder.className = 'avatar-placeholder';
                    placeholder.textContent = initial;
                    chatAvatar.appendChild(placeholder);
                }
                
                // Ajouter le badge online si nécessaire
                if (otherUser.is_online) {
                    const badge = document.createElement('span');
                    badge.className = 'online-badge';
                    chatAvatar.appendChild(badge);
                }
            }
            
            // Mettre à jour le nom
            const chatName = document.getElementById('chat-name');
            if (chatName) {
                chatName.textContent = otherUser.get_full_name || otherUser.display_name || otherUser.username || 'Utilisateur';
            }
            
            // Mettre à jour le statut
            const chatStatus = document.getElementById('chat-status');
            if (chatStatus) {
                if (otherUser.is_online) {
                    chatStatus.innerHTML = '<span class="status-online">En ligne</span>';
                } else {
                    chatStatus.innerHTML = '<span class="status-offline">Hors ligne</span>';
                }
            }
            
            // S'assurer que le typing indicator est caché
            const typingIndicator = document.getElementById('typing-indicator');
            if (typingIndicator) {
                typingIndicator.style.display = 'none';
            }
        }
    }
    
    // S'abonner au WebSocket
    if (state.websocket && state.websocket.readyState === WebSocket.OPEN) {
        state.websocket.send(JSON.stringify({
            type: 'subscribe',
            conversation_id: conversationId
        }));
    }
    
    // Charger les messages
    loadMessages(conversationId);
    
    // Marquer comme lu
    markConversationAsRead(conversationId);
    
    // Recharger les conversations pour mettre à jour les badges
    setTimeout(() => {
        loadConversations();
    }, 500);
};

window.switchFilter = function(filter) {
    state.currentFilter = filter;
    document.querySelectorAll('.filter-tab').forEach(tab => {
        tab.classList.toggle('active', tab.dataset.filter === filter);
    });
    loadConversations();
};

window.archiveConversation = function(conversationId) {
    // Si pas de conversationId fourni, utiliser la conversation active
    if (!conversationId && state.activeConversationId) {
        conversationId = state.activeConversationId;
    }
    
    if (!conversationId) {
        console.error('No conversation ID provided');
        return;
    }
    
    fetch(`/api/connect/conversations/${conversationId}/archive/`, {
        method: 'POST',
        credentials: 'same-origin',
        headers: {
            'X-CSRFToken': getCSRFToken()
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            loadConversations();
            // Fermer le panel détails si la conversation active est archivée
            if (state.activeConversationId === conversationId) {
                const panel = document.getElementById('details-panel');
                if (panel) {
                    panel.classList.remove('visible');
                }
            }
        } else {
            alert('Erreur lors de l\'archivage: ' + (data.error || 'Erreur inconnue'));
        }
    })
    .catch(error => {
        console.error('Error archiving conversation:', error);
        alert('Erreur lors de l\'archivage de la conversation');
    });
};

window.deleteConversation = function(conversationId) {
    // Si pas de conversationId fourni, utiliser la conversation active
    if (!conversationId && state.activeConversationId) {
        conversationId = state.activeConversationId;
    }
    
    if (!conversationId) {
        console.error('No conversation ID provided');
        return;
    }
    
    if (!confirm('Êtes-vous sûr de vouloir supprimer cette conversation ?')) return;
    
    fetch(`/api/connect/conversations/${conversationId}/`, {
        method: 'DELETE',
        credentials: 'same-origin',
        headers: {
            'X-CSRFToken': getCSRFToken()
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            if (state.activeConversationId === conversationId) {
                state.activeConversationId = null;
                const chatPanel = document.getElementById('chat-panel');
                const chatEmpty = document.getElementById('chat-empty');
                const chatHeader = document.getElementById('chat-header');
                const messagesArea = document.getElementById('messages-area');
                const messageInputArea = document.getElementById('message-input-area');
                
                if (chatPanel) chatPanel.style.display = 'none';
                if (chatHeader) chatHeader.style.display = 'none';
                if (messagesArea) messagesArea.style.display = 'none';
                if (messageInputArea) messageInputArea.style.display = 'none';
                if (chatEmpty) chatEmpty.style.display = 'flex';
            }
            loadConversations();
        } else {
            alert('Erreur lors de la suppression: ' + (data.error || 'Erreur inconnue'));
        }
    })
    .catch(error => {
        console.error('Error deleting conversation:', error);
        alert('Erreur lors de la suppression de la conversation');
    });
};

window.toggleImportant = function(conversationId) {
    fetch(`/api/connect/conversations/${conversationId}/important/`, {
        method: 'POST',
        credentials: 'same-origin',
        headers: {
            'X-CSRFToken': getCSRFToken()
        }
    })
    .then(() => {
        loadConversations();
    })
    .catch(error => {
        console.error('Error toggling important:', error);
    });
};

// ============================================
// ENVOI MESSAGES
// ============================================

window.sendMessage = function() {
    // Empêcher l'envoi multiple
    if (state.isSending) {
        return;
    }
    
    const input = document.getElementById('message-input');
    const content = input.value.trim();
    
    if (!content && state.selectedMedia.length === 0 && state.selectedFiles.length === 0) {
        return;
    }
    
    if (!state.activeConversationId) {
        alert('Veuillez sélectionner une conversation');
        return;
    }
    
    // Marquer comme en cours d'envoi
    state.isSending = true;
    
    const sendBtn = document.getElementById('send-btn');
    if (sendBtn) {
    sendBtn.disabled = true;
        sendBtn.innerHTML = '<div class="spinner"></div>';
    }
    
    const csrfToken = getCSRFToken();
    console.log('CSRF Token:', csrfToken ? csrfToken.substring(0, 10) + '...' : 'NOT FOUND');
    
    if (!csrfToken) {
        alert('Erreur: Token CSRF introuvable. Veuillez recharger la page.');
        return;
    }
    
    const formData = new FormData();
    formData.append('conversation_id', state.activeConversationId);
    formData.append('content', content);
    
    state.selectedMedia.forEach((file, index) => {
        formData.append(`image_${index}`, file);
    });
    
    state.selectedFiles.forEach((file, index) => {
        formData.append(`file_${index}`, file);
    });
    
    fetch('/api/connect/messages/', {
        method: 'POST',
        credentials: 'same-origin',
        headers: {
            'X-CSRFToken': csrfToken
        },
        body: formData
    })
    .then(async response => {
        const contentType = response.headers.get('content-type');
        if (!contentType || !contentType.includes('application/json')) {
            const text = await response.text();
            console.error('Received HTML instead of JSON:', text.substring(0, 200));
            throw new Error('Réponse invalide du serveur. Vérifiez votre authentification.');
        }
        
        const data = await response.json();
        if (!response.ok) {
            throw new Error(data.error || `HTTP error! status: ${response.status}`);
        }
        return data;
    })
    .then(data => {
        if (data.success) {
            input.value = '';
            input.style.height = 'auto';
            state.selectedMedia = [];
            state.selectedFiles = [];
            updateMediaPreview();
            handleInputChange();
            
            if (data.message) {
                addMessageToUI(data.message);
                scrollToBottom(true); // Force scroll pour nouveau message envoyé
            }
        } else {
            throw new Error(data.error || 'Erreur lors de l\'envoi');
        }
    })
    .catch(error => {
        console.error('Error sending message:', error);
        alert('Erreur lors de l\'envoi du message: ' + error.message);
    })
    .finally(() => {
        state.isSending = false;
        if (sendBtn) {
        sendBtn.disabled = false;
        sendBtn.innerHTML = `
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <line x1="22" y1="2" x2="11" y2="13"></line>
                <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
            </svg>
        `;
}
    });
};

function addMessageToUI(message) {
    const container = document.getElementById('messages-container');
    if (!container) return;
    
    const isSent = message.sender_id === state.currentUserId;
    const messageEl = document.createElement('div');
    messageEl.className = `message-wrapper ${isSent ? 'message-sent' : 'message-received'}`;
    messageEl.dataset.messageId = message.id;
    messageEl.innerHTML = `
        <div class="message-bubble">
            ${renderMessageContent(message)}
            <div class="message-footer">
                <span class="message-time">${formatTime(new Date())}</span>
                ${isSent ? renderMessageStatus({read: false, delivered: false}) : ''}
            </div>
        </div>
    `;
    
    container.appendChild(messageEl);
    scrollToBottom(false); // Auto-scroll seulement si en bas
}

// ============================================
// MODAL NOUVELLE CONVERSATION
// ============================================

window.openNewConversationModal = function() {
    const modal = document.getElementById('new-conversation-modal');
    if (!modal) {
        console.error('Modal not found');
        return;
    }
    
    console.log('Opening new conversation modal');
    
    // Reset state
    state.selectedRecipients = [];
    const messageInput = document.getElementById('new-message-input');
    if (messageInput) {
        messageInput.value = '';
        messageInput.style.height = 'auto';
    }
    state.selectedMedia = [];
    state.selectedFiles = [];
    
    // Reset UI
    const recipientsTags = document.getElementById('recipients-tags');
    if (recipientsTags) recipientsTags.innerHTML = '';
    
    const recipientsResults = document.getElementById('recipients-results');
    if (recipientsResults) recipientsResults.innerHTML = '';
    
    const recipientsSearch = document.getElementById('recipients-search');
    if (recipientsSearch) recipientsSearch.value = '';
    
    const groupNameWrapper = document.getElementById('group-name-wrapper');
    if (groupNameWrapper) groupNameWrapper.style.display = 'none';
    
    const groupNameInput = document.getElementById('group-name-input');
    if (groupNameInput) groupNameInput.value = '';
    
    const mediaPreview = document.getElementById('new-conversation-media-preview');
    if (mediaPreview) {
        mediaPreview.style.display = 'none';
        mediaPreview.innerHTML = '';
    }
    
    updateCreateButton();
    
    // Afficher modal
    modal.style.display = 'flex';
    document.body.style.overflow = 'hidden';
    
    // Focus search après un court délai pour que le modal soit visible
    setTimeout(() => {
        const searchInput = document.getElementById('recipients-search');
        if (searchInput) {
            searchInput.focus();
            // Ajouter event listener pour la recherche
            searchInput.addEventListener('input', function(e) {
                searchRecipients(e.target.value);
            });
        }
    }, 100);
    
    // Charger suggestions
    loadSuggestions();
};

window.closeNewConversationModal = function() {
    const modal = document.getElementById('new-conversation-modal');
    if (modal) {
        modal.style.display = 'none';
    }
    document.body.style.overflow = '';
    
    // Reset state
    state.selectedRecipients = [];
    state.selectedMedia = [];
    state.selectedFiles = [];
};

function loadSuggestions() {
    fetch('/api/connect/users/suggestions/', {
        credentials: 'same-origin',
        headers: {
            'X-CSRFToken': getCSRFToken()
        }
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                renderSuggestions(data.users || []);
            }
        })
        .catch(error => {
            console.error('Error loading suggestions:', error);
        });
}

function renderSuggestions(users) {
    const container = document.getElementById('suggestions-list');
    if (!container) return;
    
    if (!users || users.length === 0) {
        container.innerHTML = '<div class="empty-results" style="padding: 20px; text-align: center; color: var(--messages-gray-500);">Aucune suggestion disponible</div>';
        return;
    }
    
    let html = '';
    users.forEach(user => {
        // Filtrer les utilisateurs déjà sélectionnés
        if (state.selectedRecipients.find(r => r.id === user.id)) {
            return;
        }
        
        const userId = user.id;
        const username = escapeHtml((user.username || '').toString());
        const profilePicture = escapeHtml((user.profile_picture || user.avatar || '').toString());
        const displayName = escapeHtml((user.display_name || user.username || 'Utilisateur').toString());
        const bio = escapeHtml((user.bio || user.title || 'Membre Transpareo').toString());
        
        html += `
            <div class="suggestion-item-modern" onclick="selectRecipient(${userId}, '${username}', '${profilePicture}', '${displayName}')">
                ${profilePicture ? `<img src="${profilePicture}" alt="${displayName}" class="suggestion-avatar-modern">` : `<div class="suggestion-avatar-modern" style="background: linear-gradient(135deg, var(--messages-orange) 0%, #c4510a 100%); display: flex; align-items: center; justify-content: center; color: white; font-weight: 600;">${displayName[0].toUpperCase()}</div>`}
                <div class="suggestion-info-modern">
                    <div class="suggestion-name-modern">${displayName}</div>
                    <div class="suggestion-username-modern">@${username}</div>
                    ${bio ? `<div class="suggestion-bio-modern">${bio}</div>` : ''}
                </div>
                <button class="add-user-btn-modern" onclick="event.stopPropagation(); selectRecipient(${userId}, '${username}', '${profilePicture}', '${displayName}')">
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <line x1="12" y1="5" x2="12" y2="19"></line>
                        <line x1="5" y1="12" x2="19" y2="12"></line>
                    </svg>
                </button>
            </div>
        `;
    });
    
    container.innerHTML = html || '<div class="empty-results" style="padding: 20px; text-align: center; color: var(--messages-gray-500);">Aucune suggestion disponible</div>';
}

window.selectRecipient = function(userId, username, profilePicture, displayName) {
    if (state.selectedRecipients.find(r => r.id === userId)) return;
    
    state.selectedRecipients.push({
        id: userId,
        username: username,
        profile_picture: profilePicture,
        display_name: displayName
    });
    
    renderRecipientTags();
    updateCreateButton();
    
    // Afficher input nom groupe si 2+ destinataires
    const groupNameWrapper = document.getElementById('group-name-wrapper');
    if (groupNameWrapper) {
        groupNameWrapper.style.display = state.selectedRecipients.length >= 2 ? 'block' : 'none';
    }
    const groupNameInput = document.getElementById('group-name-input');
    if (groupNameInput && state.selectedRecipients.length >= 2 && !groupNameInput.value) {
        const names = state.selectedRecipients.map(r => r.display_name || r.username).slice(0, 2);
        groupNameInput.value = names.join(', ') + (state.selectedRecipients.length > 2 ? ` et ${state.selectedRecipients.length - 2} autre${state.selectedRecipients.length > 3 ? 's' : ''}` : '');
    }
};

window.removeRecipient = function(index) {
    state.selectedRecipients.splice(index, 1);
    renderRecipientTags();
    updateCreateButton();
    
    const groupNameWrapper = document.getElementById('group-name-wrapper');
    if (groupNameWrapper) {
        groupNameWrapper.style.display = state.selectedRecipients.length >= 2 ? 'block' : 'none';
    }
};

function renderRecipientTags() {
    const container = document.getElementById('recipients-tags');
    if (!container) return;
    
    const selectedSection = document.getElementById('selected-recipients-section');
    if (selectedSection) {
        selectedSection.style.display = state.selectedRecipients.length > 0 ? 'block' : 'none';
    }
    
    if (state.selectedRecipients.length === 0) {
        container.innerHTML = '';
        return;
    }
    
    let html = '';
    state.selectedRecipients.forEach((recipient, index) => {
        html += `
        <div class="recipient-tag-modern">
            ${recipient.profile_picture ? 
                    `<img src="${escapeHtml(recipient.profile_picture)}" alt="${escapeHtml(recipient.display_name || recipient.username)}">` :
                    `<div style="width: 24px; height: 24px; border-radius: 50%; background: linear-gradient(135deg, var(--messages-orange) 0%, #c4510a 100%); display: flex; align-items: center; justify-content: center; color: white; font-weight: 600; font-size: 12px;">${(recipient.display_name || recipient.username)[0].toUpperCase()}</div>`
                }
                <span>${escapeHtml(recipient.display_name || recipient.username)}</span>
                <button onclick="removeRecipient(${index})" class="recipient-tag-remove-modern">
                    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <line x1="18" y1="6" x2="6" y2="18"></line>
                        <line x1="6" y1="6" x2="18" y2="18"></line>
                    </svg>
                </button>
            </div>
        `;
    });
    
    container.innerHTML = html;
}

function updateCreateButton() {
    const btn = document.getElementById('create-conversation-btn');
    if (btn) {
        btn.disabled = state.selectedRecipients.length === 0;
    }
}

window.createConversation = function() {
    if (state.selectedRecipients.length === 0) {
        alert('Veuillez sélectionner au moins un destinataire');
        return;
    }
    
    // Pour une conversation 1-to-1, ne prendre que le premier destinataire
    const recipientIds = state.selectedRecipients.length === 1 
        ? [state.selectedRecipients[0].id] 
        : state.selectedRecipients.map(r => r.id);
    
    const messageInput = document.getElementById('new-message-input');
    const content = messageInput ? messageInput.value.trim() : '';
    const groupNameInput = document.getElementById('group-name-input');
    const groupName = groupNameInput && state.selectedRecipients.length >= 2 ? groupNameInput.value.trim() : '';
    
    const btn = document.getElementById('create-conversation-btn');
    const originalBtnText = btn ? btn.innerHTML : 'Créer la conversation';
    if (btn) {
        btn.disabled = true;
        btn.innerHTML = '<div class="spinner"></div> Création...';
    }
    
    const csrfToken = getCSRFToken();
    console.log('CSRF Token for create:', csrfToken ? csrfToken.substring(0, 10) + '...' : 'NOT FOUND');
    
    if (!csrfToken) {
        alert('Erreur: Token CSRF introuvable. Veuillez recharger la page.');
        if (btn) {
            btn.disabled = false;
            btn.innerHTML = originalBtnText;
        }
        return;
    }
    
    const formData = new FormData();
    
    // Envoyer participants comme JSON string (comme attendu par l'API)
    // Pour une conversation 1-to-1, ne prendre que le premier destinataire
    formData.append('participants', JSON.stringify(recipientIds));
    
    // Message initial (optionnel)
    if (content) {
        formData.append('message', content);
    }
    
    // Nom du groupe (si plusieurs destinataires)
    if (groupName && state.selectedRecipients.length >= 2) {
        formData.append('group_name', groupName);
    }
    
    // Images
    state.selectedMedia.forEach((file, index) => {
        formData.append(`image_${index}`, file);
    });
    
    // Fichiers
    state.selectedFiles.forEach((file, index) => {
        formData.append(`file_${index}`, file);
    });
    
    console.log('Creating conversation with participants:', recipientIds);
    
    fetch('/api/connect/conversations/create/', {
        method: 'POST',
        credentials: 'same-origin',
        headers: {
            'X-CSRFToken': csrfToken
        },
        body: formData
    })
    .then(async response => {
        const contentType = response.headers.get('content-type');
        if (!contentType || !contentType.includes('application/json')) {
            const text = await response.text();
            console.error('Received HTML instead of JSON:', text.substring(0, 200));
            throw new Error('Réponse invalide du serveur. Vérifiez votre authentification.');
        }
        
        const data = await response.json();
        if (!response.ok) {
            throw new Error(data.error || `HTTP error! status: ${response.status}`);
        }
        return data;
    })
    .then(data => {
        console.log('Conversation created:', data);
        // Si la conversation est créée, même sans success: true, on continue
        if (data.success || data.conversation_id) {
            closeNewConversationModal();
            // Recharger les conversations
            loadConversations();
            // Charger la nouvelle conversation après un court délai
            if (data.conversation_id) {
                setTimeout(() => {
                loadConversation(data.conversation_id);
                }, 300);
            }
        } else {
            throw new Error(data.error || 'Erreur lors de la création');
        }
    })
    .catch(error => {
        console.error('Error creating conversation:', error);
        alert('Erreur lors de la création de la conversation: ' + error.message);
    })
    .finally(() => {
        if (btn) {
            btn.disabled = false;
            btn.innerHTML = originalBtnText;
        }
    });
};

// ============================================
// RECHERCHE RECIPIENTS
// ============================================

function searchRecipients(query) {
    const resultsContainer = document.getElementById('recipients-results');
    const resultsList = document.getElementById('results-list');
    const suggestionsContainer = document.getElementById('recipients-suggestions');
    
    if (query.length < 2) {
        if (resultsContainer) resultsContainer.style.display = 'none';
        if (suggestionsContainer) suggestionsContainer.style.display = 'block';
        return;
    }
    
    // Masquer suggestions, afficher résultats
    if (suggestionsContainer) suggestionsContainer.style.display = 'none';
    if (resultsContainer) resultsContainer.style.display = 'block';
    
    clearTimeout(state.searchDebounceTimer);
    state.searchDebounceTimer = setTimeout(() => {
        fetch(`/api/connect/users/search/?q=${encodeURIComponent(query)}`, {
            credentials: 'same-origin',
            headers: {
                'X-CSRFToken': getCSRFToken()
            }
        })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                renderRecipientResults(data.users || []);
                }
            })
            .catch(error => {
                console.error('Error searching users:', error);
            });
    }, 300);
}

function renderRecipientResults(users) {
    const container = document.getElementById('results-list');
    if (!container) return;
    
    if (users.length === 0) {
        container.innerHTML = '<div class="empty-results" style="padding: 20px; text-align: center; color: var(--messages-gray-500);">Aucun résultat trouvé</div>';
        return;
    }
    
    let html = '';
    users.forEach(user => {
        if (state.selectedRecipients.find(r => r.id === user.id)) return;
        
        const userId = user.id;
        const username = escapeHtml((user.username || '').toString());
        const profilePicture = escapeHtml((user.profile_picture || user.avatar || '').toString());
        const displayName = escapeHtml((user.display_name || user.username || 'Utilisateur').toString());
        const bio = escapeHtml((user.bio || user.title || 'Membre Transpareo').toString());
        
        html += `
            <div class="result-item-modern" onclick="selectRecipient(${userId}, '${username}', '${profilePicture}', '${displayName}')">
                ${profilePicture ? `<img src="${profilePicture}" alt="${displayName}" class="result-avatar-modern">` : `<div class="result-avatar-modern" style="background: linear-gradient(135deg, var(--messages-orange) 0%, #c4510a 100%); display: flex; align-items: center; justify-content: center; color: white; font-weight: 600;">${displayName[0].toUpperCase()}</div>`}
                <div class="result-info-modern">
                    <div class="result-name-modern">${displayName}</div>
                    <div class="result-username-modern">@${username}</div>
                    ${bio ? `<div class="result-bio-modern">${bio}</div>` : ''}
            </div>
                <button class="add-user-btn-modern" onclick="event.stopPropagation(); selectRecipient(${userId}, '${username}', '${profilePicture}', '${displayName}')">
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <line x1="12" y1="5" x2="12" y2="19"></line>
                        <line x1="5" y1="12" x2="19" y2="12"></line>
                    </svg>
                </button>
        </div>
        `;
    });
    
    container.innerHTML = html;
}

// ============================================
// INPUT HANDLERS
// ============================================

window.handleInputKeydown = function(event) {
    if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        sendMessage();
    }
};

window.handleInputChange = function() {
    const input = document.getElementById('message-input');
    const sendBtn = document.getElementById('send-btn');
    
    if (!input || !sendBtn) return;
    
    // Auto-resize
    input.style.height = 'auto';
    input.style.height = Math.min(input.scrollHeight, 200) + 'px';
    
    // Enable/disable send button
    const hasContent = input.value.trim().length > 0 || 
                       state.selectedMedia.length > 0 || 
                       state.selectedFiles.length > 0;
    sendBtn.disabled = !hasContent;
    
    // Typing indicator
    if (hasContent && state.activeConversationId && !state.isTyping) {
        state.isTyping = true;
        sendTypingIndicator(true);
    }
    
    clearTimeout(state.typingDebounceTimer);
    state.typingDebounceTimer = setTimeout(() => {
        if (state.isTyping) {
            state.isTyping = false;
            sendTypingIndicator(false);
        }
    }, 1000);
};

function sendTypingIndicator(isTyping) {
    if (!state.activeConversationId || !state.websocket || state.websocket.readyState !== WebSocket.OPEN) {
        return;
    }
    
    fetch(`/api/connect/conversations/${state.activeConversationId}/typing/`, {
        method: 'POST',
        credentials: 'same-origin',
        headers: {
            'X-CSRFToken': getCSRFToken(),
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ typing: isTyping })
    }).catch(error => {
        console.error('Error sending typing indicator:', error);
    });
}

function showTypingIndicator(userId) {
    const indicator = document.getElementById('typing-indicator');
    if (indicator) {
        indicator.style.display = 'block';
    }
}

function hideTypingIndicator() {
    const indicator = document.getElementById('typing-indicator');
    if (indicator) {
        indicator.style.display = 'none';
    }
}

// ============================================
// EVENT LISTENERS
// ============================================

function setupEventListeners() {
    // Recherche conversations
    const searchInput = document.getElementById('search-conversations');
    if (searchInput) {
        searchInput.addEventListener('input', function() {
            state.searchQuery = this.value;
            clearTimeout(state.searchDebounceTimer);
            state.searchDebounceTimer = setTimeout(() => {
                loadConversations();
            }, 300);
        });
    }
    
    // Recherche recipients
    const recipientsSearch = document.getElementById('recipients-search');
    if (recipientsSearch) {
        recipientsSearch.addEventListener('input', function() {
            searchRecipients(this.value);
        });
    }
    
    // Message input
    const messageInput = document.getElementById('message-input');
    if (messageInput) {
        messageInput.addEventListener('keydown', handleInputKeydown);
        messageInput.addEventListener('input', handleInputChange);
    }
    
    // Send button
    const sendBtn = document.getElementById('send-btn');
    if (sendBtn) {
        sendBtn.addEventListener('click', sendMessage);
    }
    
    // Details button
    const detailsBtn = document.getElementById('btn-details');
    if (detailsBtn) {
        detailsBtn.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            if (window.toggleDetailsPanel) {
                window.toggleDetailsPanel();
            }
        });
    }
    
    // Voice call button
    const voiceCallBtn = document.getElementById('btn-voice-call');
    if (voiceCallBtn) {
        voiceCallBtn.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            if (window.startVoiceCall) {
                window.startVoiceCall();
            }
        });
    }
    
    // Video call button
    const videoCallBtn = document.getElementById('btn-video-call');
    if (videoCallBtn) {
        videoCallBtn.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            if (window.startVideoCall) {
                window.startVideoCall();
            }
        });
    }
    
    // Filter tabs
    document.querySelectorAll('.filter-tab').forEach(tab => {
        tab.addEventListener('click', function() {
            const filter = this.dataset.filter;
            if (filter) {
                switchFilter(filter);
            }
        });
    });
    
    // Scroll messages avec debounce pour éviter les clignotements
    const messagesArea = document.getElementById('messages-area');
    if (messagesArea) {
        let isLoadingMore = false;
        let scrollTimeout = null;
        
        messagesArea.addEventListener('scroll', function() {
            // Mettre à jour si l'utilisateur est en bas
            const isNearBottom = this.scrollHeight - this.scrollTop - this.clientHeight < 100;
            state.isNearBottom = isNearBottom;
            
            // Debounce pour éviter les appels multiples
            if (scrollTimeout) {
                clearTimeout(scrollTimeout);
            }
            
            scrollTimeout = setTimeout(() => {
                // Charger plus de messages si on scroll vers le haut
                if (this.scrollTop < 100 && state.activeConversationId && !isLoadingMore) {
                    const messages = state.messages[state.activeConversationId] || [];
                    if (messages.length > 0) {
                        isLoadingMore = true;
                        const firstMessage = messages[0];
                        loadMessages(state.activeConversationId, firstMessage.id).finally(() => {
                            isLoadingMore = false;
                        });
                    }
                }
            }, 200); // Debounce de 200ms
        });
    }
}

// ============================================
// UTILITAIRES
// ============================================

function getCSRFToken() {
    // Méthode 1: Depuis le meta tag (priorité)
    const metaTag = document.querySelector('meta[name="csrf-token"]');
    if (metaTag) {
        const token = metaTag.getAttribute('content');
        if (token) return token;
    }
    
    // Méthode 2: Depuis les cookies
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, 10) === 'csrftoken=') {
                cookieValue = decodeURIComponent(cookie.substring(10));
                break;
            }
        }
    }
    
    // Méthode 3: Depuis un input hidden si présent
    if (!cookieValue) {
        const csrfInput = document.querySelector('[name="csrfmiddlewaretoken"]');
        if (csrfInput) {
            cookieValue = csrfInput.value;
        }
    }
    
    // Log pour debug
    if (!cookieValue) {
        console.warn('CSRF token not found! Available cookies:', document.cookie);
    }
    
    return cookieValue || '';
}

function scrollToBottom(force = false) {
    const area = document.getElementById('messages-area');
    if (!area) return;
    
    // Si force est true, scroll toujours
    // Sinon, scroll seulement si l'utilisateur est déjà en bas (à 100px près)
    const isNearBottom = area.scrollHeight - area.scrollTop - area.clientHeight < 100;
    state.isNearBottom = isNearBottom;
    
    if (force || isNearBottom) {
        // Utiliser requestAnimationFrame pour un scroll smooth
        requestAnimationFrame(() => {
            area.scrollTop = area.scrollHeight;
            state.isNearBottom = true;
        });
    }
}

function markConversationAsRead(conversationId) {
    // Marquer tous les messages non lus comme lus
    const messages = state.messages[conversationId] || [];
    messages.forEach(msg => {
        if (msg.sender_id !== state.currentUserId && !msg.read) {
            markMessageAsRead(msg.id);
        }
    });
}

function markMessageAsRead(messageId) {
    fetch(`/api/connect/messages/${messageId}/read/`, {
        method: 'POST',
        credentials: 'same-origin',
        headers: {
            'X-CSRFToken': getCSRFToken()
        }
    }).catch(error => {
        console.error('Error marking message as read:', error);
    });
}

function updateConversationInList(conversationId) {
    // Recharger la conversation dans la liste
            loadConversations();
}

function updateOnlineStatus(userId, isOnline) {
    // Mettre à jour le badge online dans la liste
    const conversationItem = document.querySelector(`[data-conversation-id]`);
    if (conversationItem) {
        const badge = conversationItem.querySelector('.online-badge');
        if (badge) {
            badge.style.display = isOnline ? 'block' : 'none';
        }
    }
}

function updateMessageReactions(messageEl, reaction) {
    // À implémenter
}

function updateMediaPreview() {
    const preview = document.getElementById('media-preview');
    if (!preview) return;
    
    if (state.selectedMedia.length === 0 && state.selectedFiles.length === 0) {
        preview.style.display = 'none';
        return;
    }
    
    preview.style.display = 'block';
    let html = '';
    
    state.selectedMedia.forEach((file, index) => {
        const url = URL.createObjectURL(file);
        html += `
            <div class="media-preview-item">
                <img src="${url}" alt="Preview">
                <button onclick="removeMedia(${index})" class="media-remove">×</button>
            </div>
        `;
    });
    
    state.selectedFiles.forEach((file, index) => {
        html += `
            <div class="file-preview-item">
                <span>${escapeHtml(file.name)}</span>
                <button onclick="removeFile(${index})" class="file-remove">×</button>
            </div>
        `;
    });
    
    preview.innerHTML = html;
}

window.removeMedia = function(index) {
    state.selectedMedia.splice(index, 1);
    updateMediaPreview();
    handleInputChange();
};

window.removeFile = function(index) {
    state.selectedFiles.splice(index, 1);
    updateMediaPreview();
    handleInputChange();
};

function formatMessageText(text) {
    if (!text) return '';
    // Convertir URLs en liens
    text = text.replace(/(https?:\/\/[^\s]+)/g, '<a href="$1" target="_blank">$1</a>');
    // Convertir mentions @user
    text = text.replace(/@(\w+)/g, '<span class="mention">@$1</span>');
    // Préserver les sauts de ligne
    text = text.replace(/\n/g, '<br>');
    return text;
}

function formatTime(date) {
    return date.toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' });
}

function formatRelativeTime(dateString) {
    if (!dateString) return '';
    const date = new Date(dateString);
    const now = new Date();
    const diff = now - date;
    const minutes = Math.floor(diff / 60000);
    const hours = Math.floor(diff / 3600000);
    const days = Math.floor(diff / 86400000);
    
    if (minutes < 1) return 'À l\'instant';
    if (minutes < 60) return `Il y a ${minutes}min`;
    if (hours < 24) return `Il y a ${hours}h`;
    if (days === 1) return 'Hier';
    if (days < 7) return `Il y a ${days}j`;
    return date.toLocaleDateString('fr-FR', { day: 'numeric', month: 'short' });
}

function formatDate(date) {
    return date.toISOString().split('T')[0];
}

function formatDateLabel(date) {
    const today = new Date();
    const yesterday = new Date(today);
    yesterday.setDate(yesterday.getDate() - 1);
    
    if (formatDate(date) === formatDate(today)) {
        return 'Aujourd\'hui';
    } else if (formatDate(date) === formatDate(yesterday)) {
        return 'Hier';
    } else {
        return date.toLocaleDateString('fr-FR', { day: 'numeric', month: 'long', year: 'numeric' });
    }
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}

function formatDuration(seconds) {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
}

function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

window.openLightbox = function(imageUrl) {
    // À implémenter - lightbox fullscreen
    console.log('Open lightbox:', imageUrl);
    // Créer overlay lightbox
    const lightbox = document.createElement('div');
    lightbox.className = 'lightbox-overlay';
    lightbox.innerHTML = `
        <button class="lightbox-close" onclick="this.parentElement.remove()">×</button>
        <img src="${escapeHtml(imageUrl)}" alt="Image" class="lightbox-image">
    `;
    document.body.appendChild(lightbox);
    lightbox.addEventListener('click', function(e) {
        if (e.target === lightbox) {
            lightbox.remove();
        }
    });
};

window.playAudio = function(audioUrl) {
    // À implémenter - player audio
    console.log('Play audio:', audioUrl);
    const audio = new Audio(audioUrl);
    audio.play().catch(e => console.error('Error playing audio:', e));
};

// ============================================
// DÉTAILS PANEL
// ============================================

window.toggleDetailsPanel = function() {
    const panel = document.getElementById('details-panel');
    if (panel) {
        panel.classList.toggle('visible');
        // Mettre à jour le checkbox favoris si le panel est ouvert
        if (panel.classList.contains('visible') && state.activeConversationId) {
            updateFavoriteCheckbox();
        }
    }
};

window.toggleFavorite = function() {
    if (!state.activeConversationId) {
        console.error('No active conversation');
        return;
    }
    
    const checkbox = document.getElementById('favorite-toggle');
    if (!checkbox) return;
    
    fetch(`/api/connect/conversations/${state.activeConversationId}/important/`, {
        method: 'POST',
        credentials: 'same-origin',
        headers: {
            'X-CSRFToken': getCSRFToken()
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            checkbox.checked = data.favorited;
            loadConversations(); // Recharger pour mettre à jour l'icône favoris
        } else {
            alert('Erreur: ' + (data.error || 'Erreur inconnue'));
            checkbox.checked = !checkbox.checked; // Revert
        }
    })
    .catch(error => {
        console.error('Error toggling favorite:', error);
        checkbox.checked = !checkbox.checked; // Revert
        alert('Erreur lors de la mise à jour des favoris');
    });
};

function updateFavoriteCheckbox() {
    if (!state.activeConversationId) return;
    
    const conversation = state.conversations.find(c => c.id === state.activeConversationId);
    const checkbox = document.getElementById('favorite-toggle');
    
    if (checkbox && conversation) {
        checkbox.checked = conversation.favorited || false;
    }
}

window.switchDetailsTab = function(tabName) {
    document.querySelectorAll('.details-tab').forEach(tab => {
        tab.classList.toggle('active', tab.dataset.tab === tabName);
    });
    document.querySelectorAll('.details-tab-content').forEach(content => {
        content.classList.toggle('active', content.id === `tab-${tabName}`);
    });
};

// ============================================
// FONCTIONS UTILITAIRES SUPPLÉMENTAIRES
// ============================================

window.clearSearch = function() {
    const searchInput = document.getElementById('search-conversations');
    if (searchInput) {
        searchInput.value = '';
        document.getElementById('search-clear').style.display = 'none';
        state.searchQuery = '';
        loadConversations();
    }
};

window.showConversationsList = function() {
    const conversationsPanel = document.getElementById('conversations-panel');
    const chatPanel = document.getElementById('chat-panel');
    if (conversationsPanel) conversationsPanel.style.display = 'flex';
    if (chatPanel) chatPanel.style.display = 'none';
};

window.handleImageUpload = function(event) {
    const files = Array.from(event.target.files);
    files.forEach(file => {
        if (file.type.startsWith('image/')) {
            state.selectedMedia.push(file);
        }
    });
    updateMediaPreview();
    handleInputChange();
};

window.handleFileUpload = function(event) {
    const files = Array.from(event.target.files);
    files.forEach(file => {
        state.selectedFiles.push(file);
    });
    updateMediaPreview();
    handleInputChange();
};

window.openEmojiPicker = function() {
    // Fermer le GIF picker si ouvert
    closeGifPicker();
    
    // Vérifier si le picker existe déjà
    let picker = document.getElementById('emoji-picker');
    if (picker) {
        picker.style.display = picker.style.display === 'none' ? 'block' : 'none';
        return;
    }
    
    // Créer le picker
    picker = document.createElement('div');
    picker.id = 'emoji-picker';
    picker.className = 'emoji-picker-container';
    
    // Catégories d'emojis populaires
    const emojiCategories = {
        'Récents': ['😀', '😂', '❤️', '👍', '😊', '😍', '🙏', '🎉'],
        'Smileys': ['😀', '😃', '😄', '😁', '😆', '😅', '😂', '🤣', '😊', '😇', '🙂', '🙃', '😉', '😌', '😍', '🥰', '😘', '😗', '😙', '😚', '😋', '😛', '😝', '😜', '🤪', '🤨', '🧐', '🤓', '😎', '🤩', '🥳', '😏', '😒', '😞', '😔', '😟', '😕', '🙁', '☹️', '😣', '😖', '😫', '😩', '🥺', '😢', '😭', '😤', '😠', '😡', '🤬', '🤯', '😳', '🥵', '🥶', '😱', '😨', '😰', '😥', '😓'],
        'Cœurs': ['❤️', '🧡', '💛', '💚', '💙', '💜', '🖤', '🤍', '🤎', '💔', '❤️‍🔥', '❤️‍🩹', '💕', '💞', '💓', '💗', '💖', '💘', '💝', '💟'],
        'Gestes': ['👍', '👎', '👊', '✊', '🤛', '🤜', '🤞', '✌️', '🤟', '🤘', '👌', '🤌', '🤏', '👈', '👉', '👆', '🖕', '👇', '☝️', '👋', '🤚', '🖐', '✋', '🖖', '👏', '🙌', '🤲', '🤝', '🙏', '✍️', '💪', '🦾', '🦿', '🦵', '🦶'],
        'Activités': ['🎉', '🎊', '🎈', '🎁', '🏆', '🥇', '🥈', '🥉', '⚽', '🏀', '🏈', '⚾', '🎾', '🏐', '🏉', '🎱', '🏓', '🏸', '🥅', '🏒', '🏑', '🏏', '⛳', '🏹', '🎣', '🥊', '🥋', '🎽', '🛹', '🛷', '⛸', '🥌', '🎿', '⛷', '🏂', '🏋️', '🤼', '🤸', '🤺', '⛹️', '🤾', '🏌️', '🏇', '🧘', '🏄', '🏊', '🤽', '🚣', '🧗', '🚵', '🚴', '🏃', '🚶', '🧍', '🧎', '🏃', '💃', '🕺', '🕴', '👯', '🧘', '🧗', '🤹', '🤼', '🤸', '🤺', '⛹️', '🤾', '🏌️', '🏇', '🧘', '🏄', '🏊', '🤽', '🚣', '🧗', '🚵', '🚴', '🏃', '🚶', '🧍', '🧎'],
        'Objets': ['📱', '💻', '⌚', '📷', '📹', '📺', '🔊', '🎵', '🎶', '🎤', '🎧', '📻', '🎷', '🎺', '🎸', '🎹', '🥁', '🎪', '🎭', '🎨', '🎬', '🎤', '🎧', '🎼', '🎹', '🥁', '🎷', '🎺', '🎸', '🪕', '🎻', '🎲', '♟️', '🎯', '🎳', '🎮', '🎰', '🧩']
    };
    
    let html = '<div class="emoji-picker-header"><span>Emojis</span><button class="emoji-picker-close" onclick="closeEmojiPicker()">×</button></div>';
    html += '<div class="emoji-picker-tabs">';
    
    let tabIndex = 0;
    for (const category in emojiCategories) {
        html += `<button class="emoji-tab ${tabIndex === 0 ? 'active' : ''}" data-category="${category}">${category}</button>`;
        tabIndex++;
    }
    html += '</div>';
    
    html += '<div class="emoji-picker-content">';
    for (const category in emojiCategories) {
        html += `<div class="emoji-category ${category === 'Récents' ? 'active' : ''}" data-category="${category}">`;
        emojiCategories[category].forEach(emoji => {
            html += `<span class="emoji-item" data-emoji="${emoji}">${emoji}</span>`;
        });
        html += '</div>';
    }
    html += '</div>';
    
    picker.innerHTML = html;
    
    // Positionner le picker
    const inputArea = document.querySelector('.message-input-area');
    if (inputArea) {
        inputArea.style.position = 'relative';
        inputArea.appendChild(picker);
    } else {
        document.body.appendChild(picker);
    }
    
    // Event listeners
    picker.querySelectorAll('.emoji-item').forEach(item => {
        item.addEventListener('click', function() {
            const emoji = this.dataset.emoji;
            insertEmoji(emoji);
            closeEmojiPicker();
        });
    });
    
    picker.querySelectorAll('.emoji-tab').forEach(tab => {
        tab.addEventListener('click', function() {
            const category = this.dataset.category;
            picker.querySelectorAll('.emoji-tab').forEach(t => t.classList.remove('active'));
            picker.querySelectorAll('.emoji-category').forEach(c => c.classList.remove('active'));
            this.classList.add('active');
            picker.querySelector(`.emoji-category[data-category="${category}"]`).classList.add('active');
        });
    });
};

window.closeEmojiPicker = function() {
    const picker = document.getElementById('emoji-picker');
    if (picker) {
        picker.style.display = 'none';
    }
};

function insertEmoji(emoji) {
    const input = document.getElementById('message-input');
    if (input) {
        const cursorPos = input.selectionStart || input.value.length;
        const textBefore = input.value.substring(0, cursorPos);
        const textAfter = input.value.substring(cursorPos);
        input.value = textBefore + emoji + textAfter;
        input.selectionStart = input.selectionEnd = cursorPos + emoji.length;
        input.focus();
        handleInputChange();
    }
}

window.openGifPicker = function() {
    // Fermer l'emoji picker si ouvert
    closeEmojiPicker();
    
    // Vérifier si le picker existe déjà
    let picker = document.getElementById('gif-picker');
    if (picker) {
        picker.style.display = picker.style.display === 'none' ? 'block' : 'none';
        return;
    }
    
    // Créer le picker
    picker = document.createElement('div');
    picker.id = 'gif-picker';
    picker.className = 'gif-picker-container';
    
    let html = '<div class="gif-picker-header"><span>GIFs</span><button class="gif-picker-close" onclick="closeGifPicker()">×</button></div>';
    html += '<div class="gif-picker-search"><input type="text" id="gif-search-input" placeholder="Rechercher un GIF..."></div>';
    html += '<div class="gif-picker-content" id="gif-picker-content"><div class="gif-loading">Chargement des GIFs...</div></div>';
    
    picker.innerHTML = html;
    
    // Positionner le picker
    const inputArea = document.querySelector('.message-input-area');
    if (inputArea) {
        inputArea.style.position = 'relative';
        inputArea.appendChild(picker);
    } else {
        document.body.appendChild(picker);
    }
    
    // Charger les GIFs tendances (utilisant Giphy API - vous devrez ajouter votre clé API)
    loadTrendingGifs();
    
    // Event listener pour la recherche
    const searchInput = picker.querySelector('#gif-search-input');
    let searchTimeout;
    searchInput.addEventListener('input', function(e) {
        e.stopPropagation();
        clearTimeout(searchTimeout);
        const query = this.value.trim();
        if (query.length >= 2) {
            searchTimeout = setTimeout(() => searchGifs(query), 500);
        } else if (query.length === 0) {
            loadTrendingGifs();
        }
    });
    
    // Fermer en cliquant ailleurs
    setTimeout(() => {
        document.addEventListener('click', function closeOnOutsideClick(e) {
            if (!picker.contains(e.target) && !e.target.closest('.toolbar-btn[onclick*="openGifPicker"]')) {
                closeGifPicker();
                document.removeEventListener('click', closeOnOutsideClick);
            }
        });
    }, 0);
};

window.closeGifPicker = function() {
    const picker = document.getElementById('gif-picker');
    if (picker) {
        picker.style.display = 'none';
    }
};

function loadTrendingGifs() {
    const content = document.getElementById('gif-picker-content');
    if (!content) return;
    
    content.innerHTML = '<div class="gif-loading">Chargement des GIFs tendances...</div>';
    
    // Utiliser Giphy API
    fetch('https://api.giphy.com/v1/gifs/trending?api_key=hvkPdVo9s1snnAqEPEEVRlziJT3BiIHq&limit=20')
        .then(response => response.json())
        .then(data => {
            if (data.data) {
                renderGifs(data.data);
            } else {
                // Fallback: utiliser des GIFs de démonstration
                renderDemoGifs();
            }
        })
        .catch(() => {
            // En cas d'erreur, utiliser des GIFs de démonstration
            renderDemoGifs();
        });
}

function searchGifs(query) {
    const content = document.getElementById('gif-picker-content');
    if (!content) return;
    
    content.innerHTML = '<div class="gif-loading">Recherche...</div>';
    
    // Utiliser Giphy API
    fetch(`https://api.giphy.com/v1/gifs/search?api_key=hvkPdVo9s1snnAqEPEEVRlziJT3BiIHq&q=${encodeURIComponent(query)}&limit=20`)
        .then(response => response.json())
        .then(data => {
            if (data.data && data.data.length > 0) {
                renderGifs(data.data);
            } else {
                content.innerHTML = '<div class="gif-empty">Aucun GIF trouvé</div>';
            }
        })
        .catch(() => {
            content.innerHTML = '<div class="gif-empty">Erreur de recherche</div>';
        });
}

function renderGifs(gifs) {
    const content = document.getElementById('gif-picker-content');
    if (!content) return;
    
    let html = '<div class="gif-grid">';
    gifs.forEach(gif => {
        const url = gif.images?.fixed_height?.url || gif.images?.downsized?.url || '';
        if (url) {
            html += `<div class="gif-item" data-url="${url}"><img src="${url}" alt="GIF" loading="lazy"></div>`;
        }
    });
    html += '</div>';
    
    content.innerHTML = html;
    
    // Event listeners
    content.querySelectorAll('.gif-item').forEach(item => {
        item.addEventListener('click', function() {
            const url = this.dataset.url;
            insertGif(url);
            closeGifPicker();
        });
    });
}

function renderDemoGifs() {
    // GIFs de démonstration (remplacez par de vrais GIFs ou obtenez une clé API Giphy)
    const demoGifs = [
        'https://media.giphy.com/media/3o7aCTPPb4gEb5L0x2/giphy.gif',
        'https://media.giphy.com/media/l0MYC0LajbaPoEADu/giphy.gif',
        'https://media.giphy.com/media/3o7abldet0l7eE62g0/giphy.gif',
        'https://media.giphy.com/media/l0HlNQ03J5JxX6lva/giphy.gif',
        'https://media.giphy.com/media/3o7aD2saQ8l3KY3i9i/giphy.gif'
    ];
    
    const content = document.getElementById('gif-picker-content');
    if (!content) return;
    
    let html = '<div class="gif-grid">';
    demoGifs.forEach(url => {
        html += `<div class="gif-item" data-url="${url}"><img src="${url}" alt="GIF" loading="lazy"></div>`;
    });
    html += '</div>';
    
    content.innerHTML = html;
    
    // Event listeners
    content.querySelectorAll('.gif-item').forEach(item => {
        item.addEventListener('click', function() {
            const url = this.dataset.url;
            insertGif(url);
            closeGifPicker();
        });
    });
}

function insertGif(url) {
    // Télécharger le GIF et l'ajouter comme image
    closeGifPicker();
    
    // Afficher un indicateur de chargement
    const inputArea = document.querySelector('.message-input-area');
    if (inputArea) {
        const loadingIndicator = document.createElement('div');
        loadingIndicator.className = 'gif-loading-indicator';
        loadingIndicator.innerHTML = '<div class="spinner"></div><span>Téléchargement du GIF...</span>';
        loadingIndicator.style.cssText = 'position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); background: white; padding: 16px; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.15); z-index: 1001; display: flex; align-items: center; gap: 12px;';
        inputArea.appendChild(loadingIndicator);
    }
    
    fetch(url)
        .then(response => {
            if (!response.ok) {
                throw new Error('Erreur lors du téléchargement du GIF');
            }
            return response.blob();
        })
        .then(blob => {
            // Créer un fichier à partir du blob
            const file = new File([blob], `gif-${Date.now()}.gif`, { type: 'image/gif' });
            
            // Ajouter à la liste des médias sélectionnés
            state.selectedMedia.push(file);
            
            // Mettre à jour l'aperçu
            updateMediaPreview();
            
            // Mettre à jour le bouton d'envoi
            handleInputChange();
            
            // Retirer l'indicateur de chargement
            const loadingIndicator = inputArea?.querySelector('.gif-loading-indicator');
            if (loadingIndicator) {
                loadingIndicator.remove();
            }
        })
        .catch(error => {
            console.error('Erreur lors du téléchargement du GIF:', error);
            alert('Erreur lors du téléchargement du GIF. Veuillez réessayer.');
            
            // Retirer l'indicateur de chargement
            const loadingIndicator = inputArea?.querySelector('.gif-loading-indicator');
            if (loadingIndicator) {
                loadingIndicator.remove();
            }
        });
}

window.startVoiceCall = function() {
    // À implémenter - appel vocal
    console.log('Start voice call');
    alert('Appel vocal à implémenter');
};

window.startVideoCall = function() {
    // À implémenter - appel vidéo
    console.log('Start video call');
    alert('Appel vidéo à implémenter');
};

// ============================================
// PARAMÈTRES MESSAGES
// ============================================

window.toggleMessagesSettings = function() {
    const dropdown = document.getElementById('messages-settings-dropdown');
    if (dropdown) {
        const isVisible = dropdown.style.display === 'block';
        dropdown.style.display = isVisible ? 'none' : 'block';
        
        // Fermer si on clique ailleurs
        if (!isVisible) {
        setTimeout(() => {
                document.addEventListener('click', function closeOnOutsideClick(e) {
                    if (!dropdown.contains(e.target) && !document.getElementById('btn-messages-settings').contains(e.target)) {
                        dropdown.style.display = 'none';
                        document.removeEventListener('click', closeOnOutsideClick);
                    }
                });
            }, 0);
        }
    }
};

window.markAllConversationsRead = function() {
    if (!confirm('Marquer toutes les conversations comme lues ?')) {
        return;
    }
    
    fetch('/api/connect/conversations/mark-all-read/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken()
        },
        credentials: 'same-origin'
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Recharger les conversations
        loadConversations();
            // Fermer le dropdown
            document.getElementById('messages-settings-dropdown').style.display = 'none';
        } else {
            alert('Erreur: ' + (data.error || 'Impossible de marquer toutes les conversations comme lues'));
        }
    })
    .catch(error => {
        console.error('Erreur:', error);
        alert('Erreur lors de la requête');
    });
};

window.archiveAllConversations = function() {
    if (!confirm('Archiver toutes les conversations ?')) {
        return;
    }
    
    fetch('/api/connect/conversations/archive-all/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken()
        },
        credentials: 'same-origin'
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Recharger les conversations
            loadConversations();
            // Fermer le dropdown
            document.getElementById('messages-settings-dropdown').style.display = 'none';
        } else {
            alert('Erreur: ' + (data.error || 'Impossible d\'archiver toutes les conversations'));
        }
    })
    .catch(error => {
        console.error('Erreur:', error);
        alert('Erreur lors de la requête');
    });
};

window.openMessagesPreferences = function() {
    alert('Préférences de messages - À implémenter');
    document.getElementById('messages-settings-dropdown').style.display = 'none';
};

window.openNotificationSettings = function() {
    alert('Paramètres de notifications - À implémenter');
    document.getElementById('messages-settings-dropdown').style.display = 'none';
};

console.log('✓ messages-complete.js loaded successfully');



