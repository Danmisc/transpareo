/* ============================================
   TRANSPAREO DESIGN SYSTEM - JAVASCRIPT
   Transitions, micro-interactions, accessibilité
   ============================================ */

(function() {
    'use strict';

    // ========== TRANSITIONS CONTEXTUELLES ==========
    
    /**
     * Gestionnaire de transitions de page (fade/slide)
     */
    class PageTransition {
        constructor() {
            this.init();
        }

        init() {
            // Intercepter les clics sur les liens internes
            document.addEventListener('click', (e) => {
                const link = e.target.closest('a[href^="/"]');
                if (!link || link.target === '_blank' || link.hasAttribute('data-no-transition')) {
                    return;
                }

                const href = link.getAttribute('href');
                if (href && !href.startsWith('#') && !href.startsWith('javascript:')) {
                    e.preventDefault();
                    this.transitionTo(href);
                }
            });
        }

        transitionTo(url, type = 'fade') {
            const body = document.body;
            
            // Ajouter classe de sortie
            body.classList.add(`transition-${type}-exit`);
            
            setTimeout(() => {
                window.location.href = url;
            }, 250);
        }
    }

    // ========== MICRO-INTERACTIONS ==========
    
    /**
     * Gestionnaire de feedback visuel
     */
    class FeedbackManager {
        constructor() {
            this.toasts = [];
        }

        showToast(message, type = 'info', duration = 3000) {
            const toast = document.createElement('div');
            toast.className = `toast toast-${type}`;
            toast.textContent = message;
            toast.setAttribute('role', 'alert');
            toast.setAttribute('aria-live', 'polite');
            
            document.body.appendChild(toast);
            
            // Animation d'entrée
            requestAnimationFrame(() => {
                toast.classList.add('show');
            });
            
            // Suppression automatique
            setTimeout(() => {
                this.hideToast(toast);
            }, duration);
            
            this.toasts.push(toast);
            return toast;
        }

        hideToast(toast) {
            toast.classList.remove('show');
            setTimeout(() => {
                if (toast.parentNode) {
                    toast.parentNode.removeChild(toast);
                }
            }, 300);
        }

        showLoader(element) {
            if (element.dataset.loading === 'true') return;
            
            element.dataset.loading = 'true';
            const loader = document.createElement('span');
            loader.className = 'loader';
            loader.setAttribute('aria-label', 'Chargement en cours');
            element.appendChild(loader);
            element.disabled = true;
        }

        hideLoader(element) {
            element.dataset.loading = 'false';
            const loader = element.querySelector('.loader');
            if (loader) {
                loader.remove();
            }
            element.disabled = false;
        }

        showCheck(element) {
            const check = document.createElement('span');
            check.className = 'check-animation';
            check.innerHTML = '✓';
            check.setAttribute('aria-label', 'Succès');
            element.appendChild(check);
            
            setTimeout(() => {
                check.remove();
            }, 1000);
        }

        shake(element) {
            element.classList.add('shake');
            element.setAttribute('aria-invalid', 'true');
            
            setTimeout(() => {
                element.classList.remove('shake');
            }, 500);
        }
    }

    // ========== MODALES ==========
    
    /**
     * Gestionnaire de modales
     */
    class ModalManager {
        constructor() {
            this.currentModal = null;
            this.init();
        }

        init() {
            // Fermer au clic sur le backdrop
            document.addEventListener('click', (e) => {
                if (e.target.classList.contains('modal-backdrop')) {
                    this.close();
                }
            });

            // Fermer avec Escape
            document.addEventListener('keydown', (e) => {
                if (e.key === 'Escape' && this.currentModal) {
                    this.close();
                }
            });

            // Focus trap
            document.addEventListener('keydown', (e) => {
                if (e.key === 'Tab' && this.currentModal) {
                    this.trapFocus(e);
                }
            });
        }

        open(modalId) {
            const modal = document.getElementById(modalId);
            if (!modal) return;

            const backdrop = document.createElement('div');
            backdrop.className = 'modal-backdrop';
            backdrop.setAttribute('aria-hidden', 'true');
            
            modal.classList.add('modal');
            document.body.appendChild(backdrop);
            document.body.appendChild(modal);
            document.body.style.overflow = 'hidden';

            // Animation
            requestAnimationFrame(() => {
                backdrop.classList.add('show');
                modal.classList.add('show');
            });

            // Focus sur le premier élément focusable
            const firstFocusable = modal.querySelector('button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])');
            if (firstFocusable) {
                firstFocusable.focus();
            }

            this.currentModal = modal;
        }

        close() {
            if (!this.currentModal) return;

            const backdrop = document.querySelector('.modal-backdrop');
            const modal = this.currentModal;

            backdrop.classList.remove('show');
            modal.classList.remove('show');

            setTimeout(() => {
                if (backdrop.parentNode) {
                    backdrop.parentNode.removeChild(backdrop);
                }
                if (modal.parentNode) {
                    modal.parentNode.removeChild(modal);
                }
                document.body.style.overflow = '';
            }, 300);

            this.currentModal = null;
        }

        trapFocus(e) {
            const modal = this.currentModal;
            const focusableElements = modal.querySelectorAll(
                'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
            );
            const firstElement = focusableElements[0];
            const lastElement = focusableElements[focusableElements.length - 1];

            if (e.shiftKey && document.activeElement === firstElement) {
                e.preventDefault();
                lastElement.focus();
            } else if (!e.shiftKey && document.activeElement === lastElement) {
                e.preventDefault();
                firstElement.focus();
            }
        }
    }

    // ========== CONTEXT MENU ==========
    
    /**
     * Gestionnaire de menu contextuel
     */
    class ContextMenuManager {
        constructor() {
            this.menu = null;
            this.init();
        }

        init() {
            document.addEventListener('contextmenu', (e) => {
                const target = e.target.closest('[data-context-menu]');
                if (!target) {
                    this.close();
                    return;
                }

                e.preventDefault();
                this.open(e, target);
            });

            document.addEventListener('click', () => {
                this.close();
            });

            document.addEventListener('keydown', (e) => {
                if (e.key === 'Escape') {
                    this.close();
                }
            });
        }

        open(e, target) {
            this.close();

            const menuId = target.dataset.contextMenu;
            const menuTemplate = document.getElementById(menuId);
            if (!menuTemplate) return;

            this.menu = menuTemplate.cloneNode(true);
            this.menu.id = '';
            this.menu.className = 'context-menu';
            this.menu.style.display = 'block';

            document.body.appendChild(this.menu);

            const rect = target.getBoundingClientRect();
            const menuRect = this.menu.getBoundingClientRect();
            
            let top = e.clientY;
            let left = e.clientX;

            // Ajuster si le menu dépasse
            if (top + menuRect.height > window.innerHeight) {
                top = window.innerHeight - menuRect.height - 10;
            }
            if (left + menuRect.width > window.innerWidth) {
                left = window.innerWidth - menuRect.width - 10;
            }

            this.menu.style.top = `${top}px`;
            this.menu.style.left = `${left}px`;

            requestAnimationFrame(() => {
                this.menu.classList.add('show');
            });
        }

        close() {
            if (this.menu) {
                this.menu.classList.remove('show');
                setTimeout(() => {
                    if (this.menu && this.menu.parentNode) {
                        this.menu.parentNode.removeChild(this.menu);
                    }
                    this.menu = null;
                }, 200);
            }
        }
    }

    // ========== BREADCRUMB ==========
    
    /**
     * Gestionnaire de breadcrumb dynamique
     */
    class BreadcrumbManager {
        constructor() {
            this.history = [];
            this.init();
        }

        init() {
            // Sauvegarder l'historique
            if (sessionStorage.getItem('breadcrumb')) {
                this.history = JSON.parse(sessionStorage.getItem('breadcrumb'));
            }

            // Ajouter la page actuelle
            this.add({
                title: document.title,
                url: window.location.pathname
            });

            // Mettre à jour le breadcrumb
            this.update();
        }

        add(item) {
            // Éviter les doublons
            if (this.history.length > 0 && this.history[this.history.length - 1].url === item.url) {
                return;
            }

            this.history.push(item);
            
            // Limiter à 5 éléments
            if (this.history.length > 5) {
                this.history.shift();
            }

            sessionStorage.setItem('breadcrumb', JSON.stringify(this.history));
        }

        update() {
            const breadcrumbEl = document.querySelector('.breadcrumb');
            if (!breadcrumbEl) return;

            breadcrumbEl.innerHTML = '';

            this.history.forEach((item, index) => {
                const isLast = index === this.history.length - 1;
                
                const itemEl = document.createElement('div');
                itemEl.className = 'breadcrumb-item';

                if (isLast) {
                    itemEl.className += ' breadcrumb-current';
                    itemEl.textContent = item.title;
                } else {
                    const link = document.createElement('a');
                    link.href = item.url;
                    link.className = 'breadcrumb-link';
                    link.textContent = item.title;
                    itemEl.appendChild(link);
                }

                breadcrumbEl.appendChild(itemEl);

                if (!isLast) {
                    const separator = document.createElement('span');
                    separator.className = 'breadcrumb-separator';
                    separator.textContent = '›';
                    separator.setAttribute('aria-hidden', 'true');
                    breadcrumbEl.appendChild(separator);
                }
            });
        }
    }

    // ========== QUICK ACTIONS ==========
    
    /**
     * Gestionnaire de quick actions contextuelles
     */
    class QuickActionsManager {
        constructor() {
            this.actions = [];
            this.init();
        }

        init() {
            // Créer le conteneur
            const container = document.createElement('div');
            container.className = 'quick-actions';
            container.id = 'quick-actions';
            document.body.appendChild(container);

            // Détecter les éléments avec quick actions
            document.addEventListener('mouseenter', (e) => {
                const target = e.target.closest('[data-quick-actions]');
                if (target) {
                    this.show(target);
                }
            }, true);

            document.addEventListener('mouseleave', (e) => {
                const target = e.target.closest('[data-quick-actions]');
                if (target) {
                    this.hide();
                }
            }, true);
        }

        show(element) {
            const actions = JSON.parse(element.dataset.quickActions);
            const container = document.getElementById('quick-actions');
            container.innerHTML = '';

            actions.forEach(action => {
                const btn = document.createElement('button');
                btn.className = 'quick-action-btn';
                btn.innerHTML = action.icon || '⚡';
                btn.setAttribute('aria-label', action.label);
                btn.title = action.label;
                
                if (action.url) {
                    btn.onclick = () => window.location.href = action.url;
                } else if (action.action) {
                    btn.onclick = () => {
                        if (typeof window[action.action] === 'function') {
                            window[action.action](element);
                        }
                    };
                }

                container.appendChild(btn);
            });
        }

        hide() {
            const container = document.getElementById('quick-actions');
            if (container) {
                container.innerHTML = '';
            }
        }
    }

    // ========== ACCESSIBILITÉ ==========
    
    /**
     * Améliorations d'accessibilité
     */
    class AccessibilityManager {
        constructor() {
            this.init();
        }

        init() {
            // Skip link
            this.addSkipLink();

            // Navigation au clavier améliorée
            this.improveKeyboardNavigation();

            // ARIA labels automatiques
            this.addAriaLabels();
        }

        addSkipLink() {
            const skipLink = document.createElement('a');
            skipLink.href = '#main-content';
            skipLink.className = 'skip-link';
            skipLink.textContent = 'Aller au contenu principal';
            document.body.insertBefore(skipLink, document.body.firstChild);
        }

        improveKeyboardNavigation() {
            // Navigation par flèches dans les listes
            document.addEventListener('keydown', (e) => {
                if (e.key === 'ArrowDown' || e.key === 'ArrowUp') {
                    const list = e.target.closest('[role="listbox"], [role="menu"]');
                    if (list) {
                        e.preventDefault();
                        const items = Array.from(list.querySelectorAll('[role="option"], [role="menuitem"]'));
                        const currentIndex = items.indexOf(e.target);
                        const nextIndex = e.key === 'ArrowDown' 
                            ? (currentIndex + 1) % items.length
                            : (currentIndex - 1 + items.length) % items.length;
                        items[nextIndex].focus();
                    }
                }
            });
        }

        addAriaLabels() {
            // Boutons sans texte
            document.querySelectorAll('button:not([aria-label]):not(:has(span, img))').forEach(btn => {
                if (!btn.textContent.trim()) {
                    btn.setAttribute('aria-label', 'Bouton');
                }
            });

            // Images sans alt
            document.querySelectorAll('img:not([alt])').forEach(img => {
                img.setAttribute('alt', '');
                img.setAttribute('aria-hidden', 'true');
            });
        }
    }

    // ========== INITIALISATION ==========
    
    document.addEventListener('DOMContentLoaded', () => {
        window.pageTransition = new PageTransition();
        window.feedback = new FeedbackManager();
        window.modal = new ModalManager();
        window.contextMenu = new ContextMenuManager();
        window.breadcrumb = new BreadcrumbManager();
        window.quickActions = new QuickActionsManager();
        window.accessibility = new AccessibilityManager();

        // Exposer globalement pour utilisation facile
        window.showToast = (message, type, duration) => {
            window.feedback.showToast(message, type, duration);
        };

        window.showLoader = (element) => {
            window.feedback.showLoader(element);
        };

        window.hideLoader = (element) => {
            window.feedback.hideLoader(element);
        };

        window.showCheck = (element) => {
            window.feedback.showCheck(element);
        };

        window.shake = (element) => {
            window.feedback.shake(element);
        };

        window.openModal = (modalId) => {
            window.modal.open(modalId);
        };

        window.closeModal = () => {
            window.modal.close();
        };
    });

})();

