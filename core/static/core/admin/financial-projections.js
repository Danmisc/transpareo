/**
 * FINANCIAL PROJECTIONS - JavaScript pour gestion tabs, calculs, graphiques
 */

// ============================================
// VARIABLES GLOBALES
// ============================================

let charts = {};

// ============================================
// INITIALISATION
// ============================================

function initFinancialProjections() {
    // Initialiser les tabs
    initTabs();
    
    // Initialiser les calculs automatiques
    initAutoCalculations();
    
    // Initialiser les graphiques
    initCharts();
    
    // Initialiser les formulaires
    initForms();
}

// ============================================
// TABS
// ============================================

function switchTab(tabName) {
    // Masquer tous les panels
    document.querySelectorAll('.tab-panel').forEach(panel => {
        panel.classList.remove('active');
    });
    
    // Retirer active de tous les boutons
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    
    // Afficher le panel sélectionné
    const panel = document.getElementById(`tab-${tabName}`);
    if (panel) {
        panel.classList.add('active');
    }
    
    // Activer le bouton
    const btn = document.querySelector(`[data-tab="${tabName}"]`);
    if (btn) {
        btn.classList.add('active');
    }
    
    // Reinitialiser les graphiques si nécessaire
    if (tabName === 'income-statement') {
        initIncomeStatementCharts();
    } else if (tabName === 'cash-flow') {
        initCashFlowChart();
    } else if (tabName === 'scenarios') {
        initScenariosCharts();
    }
}

function initTabs() {
    // Le premier tab est actif par défaut
    switchTab('income-statement');
}

// ============================================
// CALCULS AUTOMATIQUES
// ============================================

function initAutoCalculations() {
    // Écouter les changements dans les inputs financiers
    document.querySelectorAll('.financial-input').forEach(input => {
        input.addEventListener('blur', function() {
            handleFinancialInputChange(this);
        });
        
        input.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                this.blur();
            }
        });
    });
}

function handleFinancialInputChange(input) {
    const field = input.dataset.field;
    const period = input.dataset.period;
    const month = input.dataset.month;
    const year = input.dataset.year;
    
    // Sauvegarder selon le contexte
    if (month) {
        saveCashFlow(parseInt(month), parseFloat(input.value) || 0, field);
    } else if (year && field.startsWith('assets_') || field.startsWith('liabilities_')) {
        saveBalanceSheet(parseInt(year), parseFloat(input.value) || 0, field);
    } else if (period || field.startsWith('revenue_') || field.startsWith('variable_cost_') || field.startsWith('fixed_cost_')) {
        saveProjection(field, period, parseFloat(input.value) || 0);
    }
    
    // Recalculer les valeurs dépendantes
    recalculateFinancialValues();
}

function recalculateFinancialValues() {
    // Recalculer les totaux du compte de résultat
    recalculateIncomeStatement();
    
    // Recalculer les flux de trésorerie
    recalculateCashFlow();
    
    // Recalculer les bilans
    recalculateBalanceSheets();
}

function recalculateIncomeStatement() {
    // Logique de calcul du compte de résultat
    // TODO: Implémenter les calculs complets
}

function recalculateCashFlow() {
    const rows = document.querySelectorAll('#cash-flow-table tbody tr[data-month]');
    
    rows.forEach((row, index) => {
        const month = parseInt(row.dataset.month);
        
        // Calculer les totaux
        const inflowsSales = parseFloat(row.querySelector('[data-field="inflows_sales"]').value) || 0;
        const inflowsFunding = parseFloat(row.querySelector('[data-field="inflows_funding"]').value) || 0;
        const inflowsLoans = parseFloat(row.querySelector('[data-field="inflows_loans"]').value) || 0;
        const totalInflows = inflowsSales + inflowsFunding + inflowsLoans;
        
        const outflowsPurchases = parseFloat(row.querySelector('[data-field="outflows_purchases_charges"]').value) || 0;
        const outflowsInvestments = parseFloat(row.querySelector('[data-field="outflows_investments"]').value) || 0;
        const outflowsRepayments = parseFloat(row.querySelector('[data-field="outflows_loan_repayments"]').value) || 0;
        const totalOutflows = outflowsPurchases + outflowsInvestments + outflowsRepayments;
        
        const variation = totalInflows - totalOutflows;
        
        // Solde initial (premier mois = 0 ou valeur saisie, autres = solde final précédent)
        let openingBalance = 0;
        if (month === 1) {
            openingBalance = parseFloat(row.querySelector('[data-field="opening_balance"]')?.textContent.replace(' €', '').replace(',', '') || 0);
        } else {
            const prevRow = rows[month - 2];
            if (prevRow) {
                openingBalance = parseFloat(prevRow.querySelector('[data-field="closing_balance"]')?.textContent.replace(' €', '').replace(',', '') || 0);
            }
        }
        
        const closingBalance = openingBalance + variation;
        
        // Mettre à jour les cellules calculées
        updateCell(row, 'total_inflows', totalInflows);
        updateCell(row, 'total_outflows', totalOutflows);
        updateCell(row, 'variation', variation);
        updateCell(row, 'opening_balance', openingBalance);
        updateCell(row, 'closing_balance', closingBalance);
        
        // Mettre à jour le solde initial du mois suivant
        if (month < 12) {
            const nextRow = rows[month];
            if (nextRow) {
                updateCell(nextRow, 'opening_balance', closingBalance);
                // Recalculer le mois suivant
                recalculateCashFlowRow(nextRow);
            }
        }
    });
    
    // Réinitialiser le graphique
    initCashFlowChart();
}

function recalculateCashFlowRow(row) {
    const month = parseInt(row.dataset.month);
    
    const inflowsSales = parseFloat(row.querySelector('[data-field="inflows_sales"]').value) || 0;
    const inflowsFunding = parseFloat(row.querySelector('[data-field="inflows_funding"]').value) || 0;
    const inflowsLoans = parseFloat(row.querySelector('[data-field="inflows_loans"]').value) || 0;
    const totalInflows = inflowsSales + inflowsFunding + inflowsLoans;
    
    const outflowsPurchases = parseFloat(row.querySelector('[data-field="outflows_purchases_charges"]').value) || 0;
    const outflowsInvestments = parseFloat(row.querySelector('[data-field="outflows_investments"]').value) || 0;
    const outflowsRepayments = parseFloat(row.querySelector('[data-field="outflows_loan_repayments"]').value) || 0;
    const totalOutflows = outflowsPurchases + outflowsInvestments + outflowsRepayments;
    
    const variation = totalInflows - totalOutflows;
    const openingBalance = parseFloat(row.querySelector('[data-field="opening_balance"]')?.textContent.replace(' €', '').replace(',', '') || 0);
    const closingBalance = openingBalance + variation;
    
    updateCell(row, 'total_inflows', totalInflows);
    updateCell(row, 'total_outflows', totalOutflows);
    updateCell(row, 'variation', variation);
    updateCell(row, 'closing_balance', closingBalance);
}

function updateCell(row, field, value) {
    const cell = row.querySelector(`[data-field="${field}"]`);
    if (cell) {
        cell.textContent = value.toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g, ',') + ' €';
        
        // Ajouter classe negative si valeur négative
        if (value < 0) {
            cell.classList.add('negative');
        } else {
            cell.classList.remove('negative');
        }
    }
}

function recalculateBalanceSheets() {
    document.querySelectorAll('.balance-sheet-table').forEach(table => {
        const year = parseInt(table.dataset.year);
        
        // Calculer total actif
        const fixedAssets = parseFloat(table.querySelector('[data-field="assets_fixed_assets"]').value) || 0;
        const receivables = parseFloat(table.querySelector('[data-field="assets_receivables"]').value) || 0;
        const cash = parseFloat(table.querySelector('[data-field="assets_cash"]').value) || 0;
        const totalAssets = fixedAssets + receivables + cash;
        
        // Calculer total passif
        const shareCapital = parseFloat(table.querySelector('[data-field="liabilities_share_capital"]').value) || 0;
        const reserves = parseFloat(table.querySelector('[data-field="liabilities_reserves"]')?.value || table.querySelector('[data-field="liabilities_reserves"]')?.textContent.replace(' €', '').replace(',', '') || 0);
        const financialDebt = parseFloat(table.querySelector('[data-field="liabilities_financial_debt"]').value) || 0;
        const tradePayables = parseFloat(table.querySelector('[data-field="liabilities_trade_payables"]')?.value || table.querySelector('[data-field="liabilities_trade_payables"]')?.textContent.replace(' €', '').replace(',', '') || 0);
        const totalLiabilities = shareCapital + reserves + financialDebt + tradePayables;
        
        // Mettre à jour les cellules
        updateBalanceSheetCell(table, 'total_assets', totalAssets);
        updateBalanceSheetCell(table, 'total_liabilities', totalLiabilities);
        
        // Vérifier l'équilibre
        const balanceCheck = Math.abs(totalAssets - totalLiabilities) < 0.01;
        const checkDiv = table.closest('.balance-sheet-card').querySelector('.balance-check');
        if (checkDiv) {
            checkDiv.className = 'balance-check ' + (balanceCheck ? 'success' : 'error');
            checkDiv.innerHTML = balanceCheck 
                ? '<span>✓ Équilibre vérifié (Actif = Passif)</span>'
                : '<span>✗ Erreur: Actif ≠ Passif</span>';
        }
    });
}

function updateBalanceSheetCell(table, field, value) {
    const cell = table.querySelector(`[data-field="${field}"]`);
    if (cell && !cell.querySelector('input')) {
        cell.textContent = value.toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g, ',') + ' €';
    }
}

// ============================================
// SAUVEGARDE AJAX
// ============================================

function saveProjection(field, period, value) {
    // Sauvegarder la projection (logique simplifiée)
    // TODO: Implémenter la sauvegarde complète
}

function saveCashFlow(month, value, field) {
    const formData = new FormData();
    formData.append('month', month);
    formData.append('year', 1);
    formData.append(field, value);
    
    fetch(saveCashFlowUrl, {
        method: 'POST',
        body: formData,
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': csrfToken,
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Mettre à jour les valeurs calculées
            if (data.data) {
                const row = document.querySelector(`#cash-flow-table tbody tr[data-month="${month}"]`);
                if (row && data.data) {
                    if (data.data.total_inflows !== undefined) updateCell(row, 'total_inflows', data.data.total_inflows);
                    if (data.data.total_outflows !== undefined) updateCell(row, 'total_outflows', data.data.total_outflows);
                    if (data.data.variation !== undefined) updateCell(row, 'variation', data.data.variation);
                    if (data.data.opening_balance !== undefined) updateCell(row, 'opening_balance', data.data.opening_balance);
                    if (data.data.closing_balance !== undefined) updateCell(row, 'closing_balance', data.data.closing_balance);
                }
            }
            
            // Recalculer tous les mois suivants
            recalculateCashFlow();
        }
    })
    .catch(error => {
        console.error('Erreur:', error);
    });
}

function saveBalanceSheet(year, value, field) {
    const formData = new FormData();
    formData.append('year', year);
    formData.append(field, value);
    
    fetch(saveBalanceSheetUrl, {
        method: 'POST',
        body: formData,
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': csrfToken,
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Recalculer le bilan
            recalculateBalanceSheets();
        }
    })
    .catch(error => {
        console.error('Erreur:', error);
    });
}

// ============================================
// GRAPHIQUES
// ============================================

function initCharts() {
    initIncomeStatementCharts();
    initCashFlowChart();
    initScenariosCharts();
}

function initIncomeStatementCharts() {
    // Graphique CA vs Charges
    const ctxRevenue = document.getElementById('chart-revenue-costs');
    if (ctxRevenue && !charts.revenueCosts) {
        charts.revenueCosts = new Chart(ctxRevenue, {
            type: 'bar',
            data: {
                labels: ['Année 1', 'Année 2', 'Année 3'],
                datasets: [
                    {
                        label: 'Revenus',
                        data: [0, 0, 0],
                        backgroundColor: 'rgba(16, 185, 129, 0.8)',
                    },
                    {
                        label: 'Charges',
                        data: [0, 0, 0],
                        backgroundColor: 'rgba(239, 68, 68, 0.8)',
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                    }
                }
            }
        });
    }
    
    // Graphique Résultat Net
    const ctxResult = document.getElementById('chart-net-result');
    if (ctxResult && !charts.netResult) {
        charts.netResult = new Chart(ctxResult, {
            type: 'line',
            data: {
                labels: ['Année 1', 'Année 2', 'Année 3'],
                datasets: [{
                    label: 'Résultat Net',
                    data: [0, 0, 0],
                    borderColor: '#D3580B',
                    backgroundColor: 'rgba(211, 88, 11, 0.1)',
                    tension: 0.4,
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                    }
                },
                scales: {
                    y: {
                        beginAtZero: false,
                    }
                }
            }
        });
    }
}

function initCashFlowChart() {
    const ctx = document.getElementById('chart-cash-flow');
    if (!ctx) return;
    
    // Détruire le graphique existant
    if (charts.cashFlow) {
        charts.cashFlow.destroy();
    }
    
    // Récupérer les données
    const labels = [];
    const balances = [];
    const inflows = [];
    const outflows = [];
    
    document.querySelectorAll('#cash-flow-table tbody tr[data-month]').forEach(row => {
        const month = parseInt(row.dataset.month);
        labels.push(`Mois ${month}`);
        
        const closingBalance = parseFloat(row.querySelector('[data-field="closing_balance"]')?.textContent.replace(' €', '').replace(',', '') || 0);
        const totalInflows = parseFloat(row.querySelector('[data-field="total_inflows"]')?.textContent.replace(' €', '').replace(',', '') || 0);
        const totalOutflows = parseFloat(row.querySelector('[data-field="total_outflows"]')?.textContent.replace(' €', '').replace(',', '') || 0);
        
        balances.push(closingBalance);
        inflows.push(totalInflows);
        outflows.push(totalOutflows);
    });
    
    charts.cashFlow = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Trésorerie',
                    data: balances,
                    borderColor: '#D3580B',
                    backgroundColor: 'rgba(211, 88, 11, 0.1)',
                    fill: true,
                    tension: 0.4,
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return context.dataset.label + ': ' + context.parsed.y.toFixed(2) + ' €';
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: false,
                }
            }
        }
    });
}

function initScenariosCharts() {
    // Graphiques des scénarios
    // TODO: Implémenter les graphiques comparatifs
}

// ============================================
// FORMULAIRES
// ============================================

function initForms() {
    // Formulaire KPIs
    const kpisForm = document.getElementById('kpis-form');
    if (kpisForm) {
        kpisForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const formData = new FormData(this);
            
            fetch(saveKpisUrl, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showSuccessMessage(data.message || 'KPIs sauvegardés avec succès');
                } else {
                    alert('Erreur: ' + (data.error || 'Impossible de sauvegarder'));
                }
            })
            .catch(error => {
                console.error('Erreur:', error);
                alert('Erreur lors de la sauvegarde');
            });
        });
    }
    
    // Formulaires scénarios
    document.querySelectorAll('.scenario-form').forEach(form => {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const formData = new FormData(this);
            formData.append('scenario_id', this.dataset.scenarioId);
            
            fetch(saveScenarioUrl, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showSuccessMessage(data.message || 'Scénario sauvegardé avec succès');
                } else {
                    alert('Erreur: ' + (data.error || 'Impossible de sauvegarder'));
                }
            })
            .catch(error => {
                console.error('Erreur:', error);
                alert('Erreur lors de la sauvegarde');
            });
        });
    });
}

// ============================================
// UTILITAIRES
// ============================================

function showSuccessMessage(message) {
    const msg = document.createElement('div');
    msg.className = 'alert alert-success';
    msg.textContent = message;
    msg.style.cssText = 'position: fixed; top: 20px; right: 20px; padding: 12px 20px; background: #10B981; color: white; border-radius: 8px; z-index: 9999;';
    document.body.appendChild(msg);
    
    setTimeout(() => {
        msg.remove();
    }, 3000);
}

function exportToExcel() {
    // TODO: Implémenter l'export Excel
    alert('Export Excel à implémenter');
}

function exportToPDF() {
    // TODO: Implémenter l'export PDF
    alert('Export PDF à implémenter');
}

