/**
 * ADMIN PANEL - JavaScript pour les interactions
 */

(function() {
    'use strict';

    // Éléments DOM
    const sidebar = document.getElementById('admin-sidebar');
    const mobileToggle = document.getElementById('mobile-menu-toggle');
    const mobileOverlay = document.getElementById('mobile-overlay');
    const adminWrapper = document.querySelector('.admin-main-wrapper');
    const topbarDropdowns = document.querySelectorAll('.topbar-dropdown');
    const globalSearch = document.getElementById('global-search');

    // ============================================
    // MOBILE MENU TOGGLE
    // ============================================

    function initMobileMenu() {
        if (!mobileToggle || !sidebar || !mobileOverlay) return;

        // Toggle sidebar
        mobileToggle.addEventListener('click', function(e) {
            e.stopPropagation();
            toggleSidebar();
        });

        // Close sidebar on overlay click
        mobileOverlay.addEventListener('click', function() {
            closeSidebar();
        });

        // Close sidebar on ESC key
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape' && sidebar.classList.contains('mobile-open')) {
                closeSidebar();
            }
        });

        // Close sidebar on window resize (desktop)
        window.addEventListener('resize', function() {
            if (window.innerWidth > 1024 && sidebar.classList.contains('mobile-open')) {
                closeSidebar();
            }
        });
    }

    function toggleSidebar() {
        if (sidebar && mobileOverlay) {
            const isOpen = sidebar.classList.contains('mobile-open');
            if (isOpen) {
                closeSidebar();
            } else {
                openSidebar();
            }
        }
    }

    function openSidebar() {
        if (sidebar && mobileOverlay) {
            sidebar.classList.add('mobile-open');
            mobileOverlay.classList.add('active');
            document.body.style.overflow = 'hidden';
        }
    }

    function closeSidebar() {
        if (sidebar && mobileOverlay) {
            sidebar.classList.remove('mobile-open');
            mobileOverlay.classList.remove('active');
            document.body.style.overflow = '';
        }
    }

    // ============================================
    // TOPBAR DROPDOWNS
    // ============================================

    function initTopbarDropdowns() {
        topbarDropdowns.forEach(function(dropdown) {
            const button = dropdown.querySelector('.topbar-btn');
            const menu = dropdown.querySelector('.dropdown-menu');

            if (!button || !menu) return;

            // Toggle dropdown on button click
            button.addEventListener('click', function(e) {
                e.stopPropagation();
                toggleDropdown(dropdown);
            });

            // Close dropdown on outside click
            document.addEventListener('click', function(e) {
                if (!dropdown.contains(e.target)) {
                    closeDropdown(dropdown);
                }
            });

            // Close dropdown on ESC key
            document.addEventListener('keydown', function(e) {
                if (e.key === 'Escape' && dropdown.classList.contains('active')) {
                    closeDropdown(dropdown);
                }
            });
        });
    }

    function toggleDropdown(dropdown) {
        const isActive = dropdown.classList.contains('active');
        
        // Close all other dropdowns
        topbarDropdowns.forEach(function(d) {
            if (d !== dropdown) {
                closeDropdown(d);
            }
        });

        // Toggle current dropdown
        if (isActive) {
            closeDropdown(dropdown);
        } else {
            openDropdown(dropdown);
        }
    }

    function openDropdown(dropdown) {
        dropdown.classList.add('active');
    }

    function closeDropdown(dropdown) {
        dropdown.classList.remove('active');
    }

    // ============================================
    // NAVIGATION ACTIVE STATE
    // ============================================

    function initNavigationActiveState() {
        // L'état actif est géré côté serveur avec les classes Django
        // Cette fonction peut être utilisée pour des interactions supplémentaires
        
        const navLinks = document.querySelectorAll('.nav-link');
        navLinks.forEach(function(link) {
            link.addEventListener('click', function() {
                // Smooth scroll vers le haut si nécessaire
                if (window.innerWidth <= 1024) {
                    closeSidebar();
                }
            });
        });
    }

    // ============================================
    // GLOBAL SEARCH
    // ============================================

    function initGlobalSearch() {
        if (!globalSearch) return;

        // Debounce function
        let searchTimeout;
        globalSearch.addEventListener('input', function(e) {
            clearTimeout(searchTimeout);
            const query = e.target.value.trim();

            searchTimeout = setTimeout(function() {
                if (query.length >= 2) {
                    performSearch(query);
                }
            }, 300);
        });

        // Search on Enter
        globalSearch.addEventListener('keydown', function(e) {
            if (e.key === 'Enter') {
                e.preventDefault();
                const query = e.target.value.trim();
                if (query.length >= 2) {
                    performSearch(query);
                }
            }
        });
    }

    function performSearch(query) {
        // TODO: Implémenter la recherche globale
        console.log('Recherche globale:', query);
        // Exemple: window.location.href = `/admin/search?q=${encodeURIComponent(query)}`;
    }

    // ============================================
    // SMOOTH TRANSITIONS
    // ============================================

    function initSmoothTransitions() {
        // Ajouter une classe pour activer les transitions après le chargement
        document.addEventListener('DOMContentLoaded', function() {
            document.body.classList.add('transitions-enabled');
        });

        // Transitions pour les liens de navigation
        const navLinks = document.querySelectorAll('.nav-link, .breadcrumb-link');
        navLinks.forEach(function(link) {
            link.addEventListener('click', function(e) {
                // Ajouter une transition de fade out si nécessaire
                const href = this.getAttribute('href');
                if (href && href !== '#' && !href.startsWith('javascript:')) {
                    // Laisser le navigateur gérer la navigation normalement
                }
            });
        });
    }

    // ============================================
    // SIDEBAR SCROLL SYNC (si nécessaire)
    // ============================================

    function initSidebarScroll() {
        if (!sidebar) return;

        // Sauvegarder la position du scroll
        let scrollPosition = sessionStorage.getItem('adminSidebarScroll');
        if (scrollPosition) {
            sidebar.scrollTop = parseInt(scrollPosition, 10);
        }

        // Sauvegarder la position lors du scroll
        sidebar.addEventListener('scroll', function() {
            sessionStorage.setItem('adminSidebarScroll', sidebar.scrollTop);
        });
    }

    // ============================================
    // NAVIGATION GROUPS (DROPDOWNS)
    // ============================================

    function initNavGroups() {
        const navGroups = document.querySelectorAll('.nav-group');
        const categoryToggles = document.querySelectorAll('.nav-category-toggle');
        
        if (!navGroups.length || !categoryToggles.length) return;

        // Restaurer l'état depuis localStorage
        const savedState = localStorage.getItem('adminNavGroupsState');
        const openGroups = savedState ? JSON.parse(savedState) : [];

        // Ouvrir automatiquement la catégorie contenant l'item actif
        const activeLink = document.querySelector('.nav-link.active');
        if (activeLink) {
            const activeGroup = activeLink.closest('.nav-group');
            if (activeGroup) {
                const category = activeGroup.querySelector('.nav-category-toggle')?.getAttribute('data-category');
                if (category && !openGroups.includes(category)) {
                    openGroups.push(category);
                }
            }
        }

        // Si aucune catégorie n'est ouverte, ouvrir la première par défaut
        if (openGroups.length === 0 && navGroups.length > 0) {
            const firstToggle = navGroups[0].querySelector('.nav-category-toggle');
            if (firstToggle) {
                const firstCategory = firstToggle.getAttribute('data-category');
                openGroups.push(firstCategory);
            }
        }

        // Appliquer l'état sauvegardé
        navGroups.forEach(function(group) {
            const toggle = group.querySelector('.nav-category-toggle');
            if (!toggle) return;
            
            const category = toggle.getAttribute('data-category');
            if (openGroups.includes(category)) {
                group.classList.add('open');
            }
        });

        // Gérer les clics sur les toggles
        categoryToggles.forEach(function(toggle) {
            toggle.addEventListener('click', function(e) {
                e.preventDefault();
                e.stopPropagation();
                
                const group = toggle.closest('.nav-group');
                if (!group) return;
                
                const category = toggle.getAttribute('data-category');
                const isOpen = group.classList.contains('open');
                
                // Toggle l'état
                if (isOpen) {
                    group.classList.remove('open');
                    // Retirer de la liste des groupes ouverts
                    const index = openGroups.indexOf(category);
                    if (index > -1) {
                        openGroups.splice(index, 1);
                    }
                } else {
                    group.classList.add('open');
                    // Ajouter à la liste des groupes ouverts
                    if (!openGroups.includes(category)) {
                        openGroups.push(category);
                    }
                }
                
                // Sauvegarder l'état
                localStorage.setItem('adminNavGroupsState', JSON.stringify(openGroups));
            });
        });
    }

    // ============================================
    // KEYBOARD NAVIGATION
    // ============================================

    function initKeyboardNavigation() {
        // Navigation au clavier dans la sidebar
        const navLinks = document.querySelectorAll('.nav-link');
        let currentIndex = -1;

        document.addEventListener('keydown', function(e) {
            // Alt + S pour focus sur la recherche
            if (e.altKey && e.key === 's') {
                e.preventDefault();
                if (globalSearch) {
                    globalSearch.focus();
                }
            }

            // Alt + M pour toggle sidebar mobile
            if (e.altKey && e.key === 'm' && window.innerWidth <= 1024) {
                e.preventDefault();
                toggleSidebar();
            }

            // Navigation avec les flèches dans la sidebar (si focus)
            if (sidebar && sidebar.contains(document.activeElement)) {
                if (e.key === 'ArrowDown' || e.key === 'ArrowUp') {
                    e.preventDefault();
                    navLinks.forEach(function(link, index) {
                        if (link === document.activeElement) {
                            currentIndex = index;
                        }
                    });

                    if (e.key === 'ArrowDown') {
                        currentIndex = (currentIndex + 1) % navLinks.length;
                    } else {
                        currentIndex = (currentIndex - 1 + navLinks.length) % navLinks.length;
                    }

                    if (navLinks[currentIndex]) {
                        navLinks[currentIndex].focus();
                    }
                }
            }
        });
    }

    // ============================================
    // INITIALIZATION
    // ============================================

    function init() {
        initMobileMenu();
        initTopbarDropdowns();
        initNavigationActiveState();
        initGlobalSearch();
        initSmoothTransitions();
        initSidebarScroll();
        initKeyboardNavigation();
        initNavGroups();

        // Log pour debug
        if (window.location.search.includes('debug=admin')) {
            console.log('Admin Panel initialized:', {
                sidebar: !!sidebar,
                mobileToggle: !!mobileToggle,
                topbarDropdowns: topbarDropdowns.length
            });
        }
    }

    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

    // Export functions for external use if needed
    window.AdminPanel = {
        toggleSidebar: toggleSidebar,
        openSidebar: openSidebar,
        closeSidebar: closeSidebar
    };

})();

