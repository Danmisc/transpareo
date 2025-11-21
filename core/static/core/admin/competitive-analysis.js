/**
 * COMPETITIVE ANALYSIS - JavaScript pour gestion tableau, graphiques, modales
 */

// ============================================
// VARIABLES GLOBALES
// ============================================

let radarChart = null;
let usersBarChart = null;

// ============================================
// INITIALISATION
// ============================================

function initCompetitiveAnalysis() {
    // Initialiser les graphiques
    initCharts();
    
    // Gestion formulaire SWOT
    initSwotForm();
}

// ============================================
// GRAPHIQUES
// ============================================

function initCharts() {
    if (typeof competitorsData === 'undefined' || !competitorsData || competitorsData.length === 0) {
        return;
    }
    
    // Radar Chart
    initRadarChart();
    
    // Bar Chart - Utilisateurs
    initUsersBarChart();
}

function initRadarChart() {
    const ctx = document.getElementById('radar-chart');
    if (!ctx) return;
    
    // Données Transpareo (à adapter selon vos vraies données)
    const transpareoData = {
        label: 'Transpareo',
        data: [8, 7, 9, 8, 7, 6], // Fonctionnalités, Prix, UX, Marketing, Innovation, Notoriété
        backgroundColor: 'rgba(211, 88, 11, 0.2)',
        borderColor: '#D3580B',
        borderWidth: 2,
        pointBackgroundColor: '#D3580B',
        pointBorderColor: '#fff',
        pointHoverBackgroundColor: '#fff',
        pointHoverBorderColor: '#D3580B'
    };
    
    // Données concurrents (top 3)
    const competitors = competitorsData.slice(0, 3);
    const datasets = [transpareoData];
    
    competitors.forEach((competitor, index) => {
        const colors = [
            { bg: 'rgba(59, 130, 246, 0.2)', border: '#3B82F6' },
            { bg: 'rgba(16, 185, 129, 0.2)', border: '#10B981' },
            { bg: 'rgba(139, 92, 246, 0.2)', border: '#8B5CF6' }
        ];
        
        datasets.push({
            label: competitor.name,
            data: [
                calculateFeaturesScore(competitor),
                calculatePricingScore(competitor),
                competitor.design_score || 0,
                calculateMarketingScore(competitor),
                competitor.speed_score || 0,
                calculateNotorietyScore(competitor)
            ],
            backgroundColor: colors[index].bg,
            borderColor: colors[index].border,
            borderWidth: 2,
            pointBackgroundColor: colors[index].border,
            pointBorderColor: '#fff',
            pointHoverBackgroundColor: '#fff',
            pointHoverBorderColor: colors[index].border
        });
    });
    
    radarChart = new Chart(ctx, {
        type: 'radar',
        data: {
            labels: ['Fonctionnalités', 'Prix', 'UX', 'Marketing', 'Innovation', 'Notoriété'],
            datasets: datasets
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                r: {
                    beginAtZero: true,
                    max: 10,
                    ticks: {
                        stepSize: 2
                    }
                }
            },
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        padding: 15,
                        font: {
                            size: 13
                        }
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return context.dataset.label + ': ' + context.parsed.r + '/10';
                        }
                    }
                }
            }
        }
    });
}

function initUsersBarChart() {
    const ctx = document.getElementById('users-bar-chart');
    if (!ctx) return;
    
    const labels = ['Transpareo'];
    const data = [0]; // Valeur Transpareo (à adapter)
    
    competitorsData.forEach(competitor => {
        labels.push(competitor.name);
        data.push(competitor.estimated_users || 0);
    });
    
    usersBarChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Nombre d\'utilisateurs estimé',
                data: data,
                backgroundColor: [
                    'rgba(211, 88, 11, 0.8)',
                    ...competitorsData.map((_, i) => {
                        const colors = ['rgba(59, 130, 246, 0.8)', 'rgba(16, 185, 129, 0.8)', 'rgba(139, 92, 246, 0.8)'];
                        return colors[i % colors.length];
                    })
                ],
                borderColor: [
                    '#D3580B',
                    ...competitorsData.map((_, i) => {
                        const colors = ['#3B82F6', '#10B981', '#8B5CF6'];
                        return colors[i % colors.length];
                    })
                ],
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const value = context.parsed.y || 0;
                            if (value >= 1000000) {
                                return (value / 1000000).toFixed(1) + 'M utilisateurs';
                            } else if (value >= 1000) {
                                return (value / 1000).toFixed(0) + 'K utilisateurs';
                            }
                            return value + ' utilisateurs';
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: function(value) {
                            if (value >= 1000000) {
                                return (value / 1000000).toFixed(1) + 'M';
                            } else if (value >= 1000) {
                                return (value / 1000).toFixed(0) + 'K';
                            }
                            return value;
                        }
                    }
                }
            }
        }
    });
}

// ============================================
// CALCUL SCORES
// ============================================

function calculateFeaturesScore(competitor) {
    let score = 0;
    let count = 0;
    
    // Compter les fonctionnalités (simplifié)
    if (competitor.feature_search === 'yes') score += 2;
    else if (competitor.feature_search === 'partial') score += 1;
    count += 2;
    
    // Ajouter d'autres critères selon vos besoins
    return Math.min(10, (score / count) * 10);
}

function calculatePricingScore(competitor) {
    // Score basé sur le modèle tarifaire (à adapter)
    // Plus le prix est compétitif, plus le score est élevé
    return 7; // Valeur par défaut
}

function calculateMarketingScore(competitor) {
    const socialScore = competitor.social_media_score || 0;
    const seoScore = competitor.seo_score || 0;
    return (socialScore + seoScore) / 2;
}

function calculateNotorietyScore(competitor) {
    // Score basé sur le nombre d'utilisateurs (à adapter)
    const users = competitor.estimated_users || 0;
    if (users >= 1000000) return 10;
    if (users >= 100000) return 8;
    if (users >= 10000) return 6;
    if (users >= 1000) return 4;
    return 2;
}

// ============================================
// MODALES
// ============================================

function openAddCompetitorModal() {
    const modal = document.getElementById('add-competitor-modal');
    if (modal) {
        modal.style.display = 'flex';
        // Réinitialiser le formulaire
        document.getElementById('add-competitor-form').reset();
    }
}

function openEditCompetitorModal(competitorId) {
    // Charger les données du concurrent et ouvrir la modale d'édition
    loadCompetitorData(competitorId);
}

function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.style.display = 'none';
        // Réinitialiser les formulaires
        if (modalId === 'add-competitor-modal') {
            document.getElementById('add-competitor-form').reset();
        } else if (modalId === 'edit-competitor-modal') {
            document.getElementById('edit-competitor-form').reset();
            const logoPreview = document.getElementById('edit_logo_preview');
            if (logoPreview) logoPreview.innerHTML = '';
        }
    }
}

function loadCompetitorData(competitorId) {
    // Charger les données via AJAX
    const getCompetitorUrl = editCompetitorUrl.replace('/edit/', '/data/');
    
    fetch(getCompetitorUrl + competitorId + '/', {
        method: 'GET',
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            fillEditForm(data.competitor);
            const modal = document.getElementById('edit-competitor-modal');
            if (modal) {
                modal.style.display = 'flex';
            }
        } else {
            alert('Erreur: ' + (data.error || 'Impossible de charger les données'));
        }
    })
    .catch(error => {
        console.error('Erreur:', error);
        alert('Erreur lors du chargement des données');
    });
}

function fillEditForm(competitor) {
    // Remplir le formulaire d'édition avec les données du concurrent
    document.getElementById('edit_competitor_id').value = competitor.id;
    document.getElementById('edit_name').value = competitor.name || '';
    document.getElementById('edit_website').value = competitor.website || '';
    document.getElementById('edit_year_founded').value = competitor.year_founded || '';
    document.getElementById('edit_funding_raised').value = competitor.funding_raised || '';
    document.getElementById('edit_estimated_users').value = competitor.estimated_users || '';
    
    document.getElementById('edit_feature_search').value = competitor.feature_search || 'no';
    document.getElementById('edit_feature_verified_reviews').checked = competitor.feature_verified_reviews || false;
    document.getElementById('edit_feature_social_network').checked = competitor.feature_social_network || false;
    document.getElementById('edit_feature_lease_management').checked = competitor.feature_lease_management || false;
    document.getElementById('edit_feature_interactive_map').checked = competitor.feature_interactive_map || false;
    document.getElementById('edit_feature_mobile_app').checked = competitor.feature_mobile_app || false;
    
    document.getElementById('edit_pricing_model').value = competitor.pricing_model || 'free';
    document.getElementById('edit_average_price').value = competitor.average_price || '';
    document.getElementById('edit_commission_rate').value = competitor.commission_rate || '';
    
    document.getElementById('edit_design_score').value = competitor.design_score || '';
    document.getElementById('edit_mobile_friendly').checked = competitor.mobile_friendly || false;
    document.getElementById('edit_speed_score').value = competitor.speed_score || '';
    
    document.getElementById('edit_social_media_score').value = competitor.social_media_score || '';
    document.getElementById('edit_seo_score').value = competitor.seo_score || '';
    document.getElementById('edit_advertising_type').value = competitor.advertising_type || '';
    
    document.getElementById('edit_strengths').value = competitor.strengths || '';
    document.getElementById('edit_weaknesses').value = competitor.weaknesses || '';
    document.getElementById('edit_notes').value = competitor.notes || '';
    
    // Logo preview
    const logoPreview = document.getElementById('edit_logo_preview');
    if (logoPreview) {
        if (competitor.logo) {
            logoPreview.innerHTML = `<img src="${competitor.logo}" alt="Logo" style="max-width: 100px; max-height: 100px; border-radius: 8px; margin-top: 8px;">`;
        } else {
            logoPreview.innerHTML = '';
        }
    }
    
    // Mettre à jour l'URL du formulaire
    const form = document.getElementById('edit-competitor-form');
    if (form) {
        form.action = editCompetitorUrl + competitor.id + '/';
    }
}

// ============================================
// GESTION CONCURRENTS
// ============================================

function deleteCompetitor(competitorId) {
    if (!confirm('Êtes-vous sûr de vouloir supprimer ce concurrent ?')) {
        return;
    }
    
    fetch(deleteCompetitorUrl + competitorId + '/', {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrfToken,
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            location.reload();
        } else {
            alert('Erreur: ' + (data.error || 'Impossible de supprimer le concurrent'));
        }
    })
    .catch(error => {
        console.error('Erreur:', error);
        alert('Erreur lors de la suppression');
    });
}

// ============================================
// GESTION FORMULAIRE SWOT
// ============================================

function initSwotForm() {
    const form = document.getElementById('swot-form');
    if (!form) return;
    
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const formData = new FormData(form);
        
        fetch(saveSwotUrl, {
            method: 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Afficher un message de succès
                const successMsg = document.createElement('div');
                successMsg.className = 'alert alert-success';
                successMsg.textContent = data.message || 'Analyse SWOT sauvegardée avec succès';
                successMsg.style.cssText = 'position: fixed; top: 20px; right: 20px; padding: 12px 20px; background: #10B981; color: white; border-radius: 8px; z-index: 9999;';
                document.body.appendChild(successMsg);
                
                setTimeout(() => {
                    successMsg.remove();
                }, 3000);
            } else {
                alert('Erreur: ' + (data.error || 'Impossible de sauvegarder l\'analyse SWOT'));
            }
        })
        .catch(error => {
            console.error('Erreur:', error);
            alert('Erreur lors de la sauvegarde');
        });
    });
}

// ============================================
// GESTION FORMULAIRE CONCURRENT
// ============================================

document.addEventListener('DOMContentLoaded', function() {
    // Formulaire ajout
    const addForm = document.getElementById('add-competitor-form');
    if (addForm) {
        addForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const formData = new FormData(this);
            
            fetch(addCompetitorUrl, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    location.reload();
                } else {
                    alert('Erreur: ' + (data.error || 'Impossible d\'ajouter le concurrent'));
                }
            })
            .catch(error => {
                console.error('Erreur:', error);
                alert('Erreur lors de l\'ajout');
            });
        });
    }
    
    // Formulaire édition
    const editForm = document.getElementById('edit-competitor-form');
    if (editForm) {
        editForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const formData = new FormData(this);
            const competitorId = document.getElementById('edit_competitor_id').value;
            
            if (!competitorId) {
                alert('Erreur: ID concurrent manquant');
                return;
            }
            
            fetch(editCompetitorUrl + competitorId + '/', {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    location.reload();
                } else {
                    alert('Erreur: ' + (data.error || 'Impossible de modifier le concurrent'));
                }
            })
            .catch(error => {
                console.error('Erreur:', error);
                alert('Erreur lors de la modification');
            });
        });
    }
});

// Fermer la modale en cliquant en dehors
window.addEventListener('click', function(e) {
    const modals = document.querySelectorAll('.modal');
    modals.forEach(modal => {
        if (e.target === modal) {
            modal.style.display = 'none';
        }
    });
});

