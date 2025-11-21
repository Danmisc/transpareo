/**
 * DASHBOARD - JavaScript pour les graphiques et interactions
 */

let userGrowthChart = null;
let candidaturesDonutChart = null;
let revenueChart = null;

function initDashboardCharts() {
    initUserGrowthChart();
    initCandidaturesDonutChart();
    initRevenueChart();
}

/**
 * Graphique 1 - Croissance Utilisateurs (Line chart)
 */
function initUserGrowthChart() {
    const ctx = document.getElementById('userGrowthChart');
    if (!ctx || !userGrowthData) return;

    const data = JSON.parse(userGrowthData);

    userGrowthChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.map(item => item.month),
            datasets: [
                {
                    label: 'Locataires',
                    data: data.map(item => item.locataires),
                    borderColor: '#3B82F6',
                    backgroundColor: 'rgba(59, 130, 246, 0.1)',
                    tension: 0.4,
                    fill: true
                },
                {
                    label: 'Propriétaires',
                    data: data.map(item => item.proprietaires),
                    borderColor: '#10B981',
                    backgroundColor: 'rgba(16, 185, 129, 0.1)',
                    tension: 0.4,
                    fill: true
                },
                {
                    label: 'Total',
                    data: data.map(item => item.total),
                    borderColor: '#D3580B',
                    backgroundColor: 'rgba(211, 88, 11, 0.1)',
                    tension: 0.4,
                    fill: true,
                    borderWidth: 2
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true,
                    position: 'top',
                    labels: {
                        usePointStyle: true,
                        padding: 15
                    }
                },
                tooltip: {
                    mode: 'index',
                    intersect: false,
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    padding: 12,
                    titleFont: {
                        size: 14,
                        weight: 'bold'
                    },
                    bodyFont: {
                        size: 13
                    }
                }
            },
            scales: {
                x: {
                    grid: {
                        display: false
                    },
                    ticks: {
                        font: {
                            size: 12
                        }
                    }
                },
                y: {
                    beginAtZero: true,
                    grid: {
                        color: 'rgba(0, 0, 0, 0.05)'
                    },
                    ticks: {
                        font: {
                            size: 12
                        },
                        callback: function(value) {
                            return value.toLocaleString();
                        }
                    }
                }
            },
            interaction: {
                mode: 'nearest',
                axis: 'x',
                intersect: false
            },
            animation: {
                duration: 1000,
                easing: 'easeInOutQuart'
            }
        }
    });
}

/**
 * Graphique 2 - Candidatures par Statut (Donut chart)
 */
function initCandidaturesDonutChart() {
    const ctx = document.getElementById('candidaturesDonutChart');
    if (!ctx || !candidaturesStats || totalCandidatures === 0) return;

    const stats = candidaturesStats;
    const colors = {
        'en_attente': '#F59E0B',
        'acceptees': '#10B981',
        'refusees': '#EF4444',
        'en_cours': '#3B82F6'
    };

    candidaturesDonutChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: [
                'En attente',
                'Acceptées',
                'Refusées',
                'En cours'
            ],
            datasets: [{
                data: [
                    stats.en_attente || 0,
                    stats.acceptees || 0,
                    stats.refusees || 0,
                    stats.en_cours || 0
                ],
                backgroundColor: [
                    colors.en_attente,
                    colors.acceptees,
                    colors.refusees,
                    colors.en_cours
                ],
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'right',
                    labels: {
                        usePointStyle: true,
                        padding: 15,
                        font: {
                            size: 13
                        }
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    padding: 12,
                    callbacks: {
                        label: function(context) {
                            const label = context.label || '';
                            const value = context.parsed || 0;
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const percentage = total > 0 ? ((value / total) * 100).toFixed(1) : 0;
                            return `${label}: ${value} (${percentage}%)`;
                        }
                    }
                },
                datalabels: {
                    display: true,
                    color: '#111827',
                    font: {
                        size: 12,
                        weight: 'bold'
                    },
                    formatter: function(value, context) {
                        const total = context.dataset.data.reduce((a, b) => a + b, 0);
                        if (total === 0) return '';
                        const percentage = ((value / total) * 100).toFixed(0);
                        return percentage > 5 ? percentage + '%' : '';
                    }
                }
            },
            cutout: '70%',
            animation: {
                animateRotate: true,
                duration: 1000
            }
        },
        plugins: [ChartDataLabels]
    });
}

/**
 * Graphique 3 - Revenus Mensuels (Bar chart empilé)
 */
function initRevenueChart() {
    const ctx = document.getElementById('revenueChart');
    if (!ctx || !revenueMonthlyData) return;

    const data = JSON.parse(revenueMonthlyData);

    revenueChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: data.map(item => item.month),
            datasets: [
                {
                    label: 'Abonnements',
                    data: data.map(item => item.abonnements || 0),
                    backgroundColor: '#3B82F6',
                    borderColor: '#3B82F6',
                    borderWidth: 0
                },
                {
                    label: 'Commissions',
                    data: data.map(item => item.commissions || 0),
                    backgroundColor: '#10B981',
                    borderColor: '#10B981',
                    borderWidth: 0
                },
                {
                    label: 'Services',
                    data: data.map(item => item.services || 0),
                    backgroundColor: '#D3580B',
                    borderColor: '#D3580B',
                    borderWidth: 0
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true,
                    position: 'top',
                    labels: {
                        usePointStyle: true,
                        padding: 15
                    }
                },
                tooltip: {
                    mode: 'index',
                    intersect: false,
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    padding: 12,
                    callbacks: {
                        label: function(context) {
                            const label = context.dataset.label || '';
                            const value = context.parsed.y || 0;
                            return `${label}: ${value.toLocaleString('fr-FR')} €`;
                        },
                        footer: function(tooltipItems) {
                            const total = tooltipItems.reduce((sum, item) => sum + (item.parsed.y || 0), 0);
                            return `Total: ${total.toLocaleString('fr-FR')} €`;
                        }
                    }
                }
            },
            scales: {
                x: {
                    stacked: true,
                    grid: {
                        display: false
                    },
                    ticks: {
                        font: {
                            size: 12
                        }
                    }
                },
                y: {
                    stacked: true,
                    beginAtZero: true,
                    grid: {
                        color: 'rgba(0, 0, 0, 0.05)'
                    },
                    ticks: {
                        font: {
                            size: 12
                        },
                        callback: function(value) {
                            return value.toLocaleString('fr-FR') + ' €';
                        }
                    }
                }
            },
            animation: {
                duration: 1000,
                easing: 'easeInOutQuart'
            }
        }
    });

    // Ajouter ligne de moyenne
    const avgValue = data.reduce((sum, item) => {
        return sum + (item.abonnements || 0) + (item.commissions || 0) + (item.services || 0);
    }, 0) / data.length;

    revenueChart.data.datasets.push({
        label: 'Moyenne',
        data: new Array(data.length).fill(avgValue),
        type: 'line',
        borderColor: '#6B7280',
        borderWidth: 2,
        borderDash: [5, 5],
        fill: false,
        pointRadius: 0,
        pointHoverRadius: 0
    });

    revenueChart.update();
}

/**
 * Export chart
 */
function exportChart(chartId, format) {
    const chart = {
        'userGrowthChart': userGrowthChart,
        'revenueChart': revenueChart
    }[chartId];

    if (!chart) return;

    if (format === 'png') {
        const url = chart.toBase64Image();
        const link = document.createElement('a');
        link.download = `${chartId}_${new Date().toISOString().split('T')[0]}.png`;
        link.href = url;
        link.click();
    } else if (format === 'csv') {
        // Export CSV
        const labels = chart.data.labels;
        const datasets = chart.data.datasets;
        
        let csv = 'Date,' + datasets.map(d => d.label).join(',') + '\n';
        
        labels.forEach((label, index) => {
            csv += label + ',';
            csv += datasets.map(d => d.data[index] || 0).join(',') + '\n';
        });
        
        const blob = new Blob([csv], { type: 'text/csv' });
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.download = `${chartId}_${new Date().toISOString().split('T')[0]}.csv`;
        link.href = url;
        link.click();
        window.URL.revokeObjectURL(url);
    }
}

// Auto-refresh des filtres
document.addEventListener('DOMContentLoaded', function() {
    const filtersForm = document.getElementById('dashboard-filters');
    if (filtersForm) {
        const selects = filtersForm.querySelectorAll('.filter-select');
        selects.forEach(select => {
            select.addEventListener('change', function() {
                filtersForm.submit();
            });
        });
    }
});

