/**
 * MARKET STUDY RESULTS - JavaScript pour graphiques Chart.js
 */

// ============================================
// INITIALISATION CHARTS
// ============================================

function initCharts() {
    // Attendre que les données soient disponibles
    if (typeof questionsStats === 'undefined' || !questionsStats || questionsStats.length === 0) {
        setTimeout(initCharts, 100);
        return;
    }
    
    questionsStats.forEach(stat => {
        const question = stat.question;
        const canvas = document.getElementById(`chart-${question.id}`);
        if (!canvas) return;
        
        const ctx = canvas.getContext('2d');
        
        if (question.question_type === 'single_choice' && stat.options_count) {
            initPieChart(ctx, stat.options_count, stat.total_answers || 0);
        } else if (question.question_type === 'multiple_choice' && stat.options_count) {
            initBarChart(ctx, stat.options_count, stat.total_answers || 0);
        } else if (question.question_type === 'scale' && stat.distribution) {
            initScaleChart(ctx, stat.distribution, question.scale_min, question.scale_max);
        } else if (question.question_type === 'nps' && stat.detractors !== undefined) {
            initNPSChart(ctx, stat.detractors || 0, stat.passives || 0, stat.promoters || 0);
        }
    });
}

// ============================================
// PIE CHART (Choix unique)
// ============================================

function initPieChart(ctx, optionsCount, total) {
    const labels = Object.keys(optionsCount);
    const data = Object.values(optionsCount);
    const colors = generateColors(labels.length);
    
    new Chart(ctx, {
        type: 'pie',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: colors,
                borderWidth: 2,
                borderColor: '#fff'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'right',
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
                            const label = context.label || '';
                            const value = context.parsed || 0;
                            const percentage = total > 0 ? ((value / total) * 100).toFixed(1) : 0;
                            return `${label}: ${value} (${percentage}%)`;
                        }
                    }
                }
            }
        }
    });
}

// ============================================
// BAR CHART (Choix multiple)
// ============================================

function initBarChart(ctx, optionsCount, total) {
    const labels = Object.keys(optionsCount);
    const data = Object.values(optionsCount);
    const colors = generateColors(labels.length);
    
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Nombre de réponses',
                data: data,
                backgroundColor: colors.map(c => c + '80'), // 50% opacity
                borderColor: colors,
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
                            const percentage = total > 0 ? ((value / total) * 100).toFixed(1) : 0;
                            return `${value} réponses (${percentage}%)`;
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        stepSize: 1
                    }
                }
            }
        }
    });
}

// ============================================
// SCALE CHART (Distribution)
// ============================================

function initScaleChart(ctx, distribution, min, max) {
    const labels = [];
    const data = [];
    
    for (let i = min; i <= max; i++) {
        labels.push(i.toString());
        data.push(distribution[i] || 0);
    }
    
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Nombre de réponses',
                data: data,
                backgroundColor: 'rgba(211, 88, 11, 0.6)',
                borderColor: '#D3580B',
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        stepSize: 1
                    }
                }
            }
        }
    });
}

// ============================================
// NPS CHART
// ============================================

function initNPSChart(ctx, detractors, passives, promoters) {
    const total = detractors + passives + promoters;
    const labels = ['Détracteurs', 'Passifs', 'Promoteurs'];
    const data = [detractors, passives, promoters];
    const colors = ['#EF4444', '#F59E0B', '#10B981'];
    
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Nombre de réponses',
                data: data,
                backgroundColor: colors.map(c => c + '80'),
                borderColor: colors,
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
                            const percentage = total > 0 ? ((value / total) * 100).toFixed(1) : 0;
                            return `${value} (${percentage}%)`;
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        stepSize: 1
                    }
                }
            }
        }
    });
}

// ============================================
// FILTER TEXT ANSWERS
// ============================================

function filterTextAnswers(input, questionId) {
    const searchTerm = input.value.toLowerCase();
    const answersList = document.getElementById(`text-answers-${questionId}`);
    if (!answersList) return;
    
    const answerItems = answersList.querySelectorAll('.text-answer-item');
    answerItems.forEach(item => {
        const content = item.querySelector('.text-answer-content').textContent.toLowerCase();
        if (content.includes(searchTerm)) {
            item.style.display = 'block';
        } else {
            item.style.display = 'none';
        }
    });
}

// ============================================
// UTILITIES
// ============================================

function generateColors(count) {
    const colors = [
        '#D3580B', '#3B82F6', '#10B981', '#F59E0B', '#8B5CF6',
        '#EF4444', '#06B6D4', '#84CC16', '#F97316', '#EC4899'
    ];
    
    const result = [];
    for (let i = 0; i < count; i++) {
        result.push(colors[i % colors.length]);
    }
    return result;
}

