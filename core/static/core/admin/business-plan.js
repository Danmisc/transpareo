/**
 * BUSINESS PLAN - JavaScript pour édition riche, auto-save, tableaux éditables
 */

// ============================================
// VARIABLES GLOBALES
// ============================================

let saveTimeouts = {};
let richSaveTimeouts = {};
let listSaveTimeouts = {};
let tableSaveTimeouts = {};

// ============================================
// INITIALISATION
// ============================================

function initBusinessPlan() {
    // Fermer les dropdowns au click extérieur
    document.addEventListener('click', function(e) {
        if (!e.target.closest('.actions-dropdown')) {
            const dropdowns = document.querySelectorAll('.actions-dropdown');
            dropdowns.forEach(dropdown => dropdown.classList.remove('active'));
        }
    });

    // Fermer l'indicateur de sauvegarde après 3 secondes
    const saveIndicator = document.getElementById('save-indicator');
    if (saveIndicator) {
        setTimeout(() => {
            saveIndicator.style.display = 'none';
        }, 3000);
    }

    // Initialiser les éditeurs riches
    initRichEditors();
}

// ============================================
// ÉDITEURS RICHES
// ============================================

function initRichEditors() {
    const richEditors = document.querySelectorAll('.rich-editor');
    richEditors.forEach(editor => {
        editor.addEventListener('paste', function(e) {
            e.preventDefault();
            const text = e.clipboardData.getData('text/plain');
            document.execCommand('insertText', false, text);
        });
    });
}

function formatText(command) {
    document.execCommand(command, false, null);
}

function saveRichField(editor) {
    const fieldName = editor.dataset.field;
    const content = editor.innerHTML;

    // Créer FormData
    const formData = new FormData();
    formData.append('field', fieldName);
    formData.append('value', content);
    formData.append('csrfmiddlewaretoken', csrfToken);

    // Envoyer la requête
    fetch(saveUrl, {
        method: 'POST',
        body: formData,
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showSaveIndicator(data.message, data.updated_at);
        } else {
            console.error('Erreur de sauvegarde:', data.error);
        }
    })
    .catch(error => {
        console.error('Erreur réseau:', error);
    });

    // Nettoyer le timeout
    if (richSaveTimeouts[fieldName]) {
        clearTimeout(richSaveTimeouts[fieldName]);
        delete richSaveTimeouts[fieldName];
    }
}

function debounceSaveRich(editor) {
    const fieldName = editor.dataset.field;

    // Annuler le timeout précédent
    if (richSaveTimeouts[fieldName]) {
        clearTimeout(richSaveTimeouts[fieldName]);
    }

    // Créer un nouveau timeout (3 secondes)
    richSaveTimeouts[fieldName] = setTimeout(() => {
        saveRichField(editor);
    }, 3000);
}

// ============================================
// CHAMPS SIMPLES (INPUT, TEXTAREA, SELECT)
// ============================================

function saveField(field) {
    const fieldName = field.dataset.field;
    let fieldValue = field.value;

    // Traiter les valeurs selon le type
    if (field.type === 'number') {
        fieldValue = fieldValue ? parseFloat(fieldValue) : null;
    } else if (field.type === 'date') {
        fieldValue = fieldValue || null;
    }

    // Créer FormData
    const formData = new FormData();
    formData.append('field', fieldName);
    formData.append('value', fieldValue || '');
    formData.append('csrfmiddlewaretoken', csrfToken);

    // Envoyer la requête
    fetch(saveUrl, {
        method: 'POST',
        body: formData,
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showSaveIndicator(data.message, data.updated_at);
        } else {
            console.error('Erreur de sauvegarde:', data.error);
        }
    })
    .catch(error => {
        console.error('Erreur réseau:', error);
    });

    // Nettoyer le timeout
    if (saveTimeouts[fieldName]) {
        clearTimeout(saveTimeouts[fieldName]);
        delete saveTimeouts[fieldName];
    }
}

function debounceSave(field) {
    const fieldName = field.dataset.field;

    // Annuler le timeout précédent
    if (saveTimeouts[fieldName]) {
        clearTimeout(saveTimeouts[fieldName]);
    }

    // Créer un nouveau timeout (3 secondes)
    saveTimeouts[fieldName] = setTimeout(() => {
        saveField(field);
    }, 3000);
}

// ============================================
// LISTES ÉDITABLES
// ============================================

function addListItem(fieldName) {
    const listContainer = document.getElementById(fieldName);
    if (!listContainer) return;

    const listItem = document.createElement('div');
    listItem.className = 'list-item';
    listItem.innerHTML = `
        <input type="text" class="list-input" placeholder="Nouvel item..." onblur="saveListField('${fieldName}')" oninput="debounceSaveList('${fieldName}')">
        <button type="button" class="list-remove" onclick="removeListItem(this, '${fieldName}')">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <line x1="18" y1="6" x2="6" y2="18"></line>
                <line x1="6" y1="6" x2="18" y2="18"></line>
            </svg>
        </button>
    `;

    // Insérer avant le bouton "Ajouter"
    const addButton = listContainer.querySelector('.btn-add-item');
    listContainer.insertBefore(listItem, addButton);

    // Focus sur le nouvel input
    const newInput = listItem.querySelector('.list-input');
    newInput.focus();
}

function removeListItem(button, fieldName) {
    const listContainer = document.getElementById(fieldName);
    if (!listContainer) return;

    const listItems = listContainer.querySelectorAll('.list-item');
    
    // Ne pas supprimer s'il n'y a qu'un seul item
    if (listItems.length <= 1) {
        // Vider l'input au lieu de supprimer
        const input = button.closest('.list-item').querySelector('.list-input');
        if (input) {
            input.value = '';
            saveListField(fieldName);
        }
        return;
    }

    button.closest('.list-item').remove();
    saveListField(fieldName);
}

function saveListField(fieldName) {
    const listContainer = document.getElementById(fieldName);
    if (!listContainer) return;

    const inputs = listContainer.querySelectorAll('.list-input');
    const values = Array.from(inputs)
        .map(input => input.value.trim())
        .filter(value => value !== '');

    // Créer FormData
    const formData = new FormData();
    formData.append('field', fieldName);
    formData.append('value', JSON.stringify(values));
    formData.append('csrfmiddlewaretoken', csrfToken);

    // Envoyer la requête
    fetch(saveUrl, {
        method: 'POST',
        body: formData,
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showSaveIndicator(data.message, data.updated_at);
        } else {
            console.error('Erreur de sauvegarde:', data.error);
        }
    })
    .catch(error => {
        console.error('Erreur réseau:', error);
    });

    // Nettoyer le timeout
    if (listSaveTimeouts[fieldName]) {
        clearTimeout(listSaveTimeouts[fieldName]);
        delete listSaveTimeouts[fieldName];
    }
}

function debounceSaveList(fieldName) {
    // Annuler le timeout précédent
    if (listSaveTimeouts[fieldName]) {
        clearTimeout(listSaveTimeouts[fieldName]);
    }

    // Créer un nouveau timeout (3 secondes)
    listSaveTimeouts[fieldName] = setTimeout(() => {
        saveListField(fieldName);
    }, 3000);
}

// ============================================
// TABLEAUX ÉDITABLES
// ============================================

function addTableRow(fieldName, defaultValues = {}) {
    const tbody = document.getElementById(fieldName + '-tbody');
    if (!tbody) return;

    // Déterminer le nombre de colonnes selon le type de tableau
    let rowHtml = '';
    if (fieldName === 'equipe_fondatrice') {
        rowHtml = `
            <tr class="table-row-editable">
                <td><input type="text" class="table-input" value="${defaultValues.nom || ''}" placeholder="Nom..." onblur="saveTableField('${fieldName}')"></td>
                <td><input type="text" class="table-input" value="${defaultValues.role || ''}" placeholder="Rôle..." onblur="saveTableField('${fieldName}')"></td>
                <td><textarea class="table-textarea" rows="2" placeholder="Bio..." onblur="saveTableField('${fieldName}')">${defaultValues.bio || ''}</textarea></td>
                <td><button type="button" class="btn-remove-row" onclick="removeTableRow(this, '${fieldName}')">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <line x1="18" y1="6" x2="6" y2="18"></line>
                        <line x1="6" y1="6" x2="18" y2="18"></line>
                    </svg>
                </button></td>
            </tr>
        `;
    } else {
        // Structure par défaut pour autres tableaux
        rowHtml = `
            <tr class="table-row-editable">
                <td><input type="text" class="table-input" onblur="saveTableField('${fieldName}')"></td>
                <td><input type="text" class="table-input" onblur="saveTableField('${fieldName}')"></td>
                <td><button type="button" class="btn-remove-row" onclick="removeTableRow(this, '${fieldName}')">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <line x1="18" y1="6" x2="6" y2="18"></line>
                        <line x1="6" y1="6" x2="18" y2="18"></line>
                    </svg>
                </button></td>
            </tr>
        `;
    }

    tbody.insertAdjacentHTML('beforeend', rowHtml);

    // Focus sur le premier input de la nouvelle ligne
    const newRow = tbody.lastElementChild;
    const firstInput = newRow.querySelector('input, textarea');
    if (firstInput) {
        firstInput.focus();
    }
}

function removeTableRow(button, fieldName) {
    const tbody = document.getElementById(fieldName + '-tbody');
    if (!tbody) return;

    const rows = tbody.querySelectorAll('tr');
    
    // Ne pas supprimer s'il n'y a qu'une seule ligne
    if (rows.length <= 1) {
        // Vider les inputs au lieu de supprimer
        const inputs = button.closest('tr').querySelectorAll('input, textarea');
        inputs.forEach(input => {
            input.value = '';
        });
        saveTableField(fieldName);
        return;
    }

    button.closest('tr').remove();
    saveTableField(fieldName);
}

function saveTableField(fieldName) {
    const tbody = document.getElementById(fieldName + '-tbody');
    if (!tbody) return;

    const rows = tbody.querySelectorAll('tr');
    const data = [];

    rows.forEach(row => {
        const inputs = row.querySelectorAll('input, textarea');
        const rowData = {};

        if (fieldName === 'equipe_fondatrice') {
            rowData.nom = inputs[0] ? inputs[0].value.trim() : '';
            rowData.role = inputs[1] ? inputs[1].value.trim() : '';
            rowData.bio = inputs[2] ? inputs[2].value.trim() : '';
        } else {
            // Structure par défaut
            inputs.forEach((input, index) => {
                rowData[`col${index}`] = input.value.trim();
            });
        }

        // Ne pas ajouter si tous les champs sont vides
        if (Object.values(rowData).some(val => val !== '')) {
            data.push(rowData);
        }
    });

    // Créer FormData
    const formData = new FormData();
    formData.append('field', fieldName);
    formData.append('value', JSON.stringify(data));
    formData.append('csrfmiddlewaretoken', csrfToken);

    // Envoyer la requête
    fetch(saveUrl, {
        method: 'POST',
        body: formData,
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showSaveIndicator(data.message, data.updated_at);
        } else {
            console.error('Erreur de sauvegarde:', data.error);
        }
    })
    .catch(error => {
        console.error('Erreur réseau:', error);
    });

    // Nettoyer le timeout
    if (tableSaveTimeouts[fieldName]) {
        clearTimeout(tableSaveTimeouts[fieldName]);
        delete tableSaveTimeouts[fieldName];
    }
}

// ============================================
// INDICATEUR DE SAUVEGARDE
// ============================================

function showSaveIndicator(message, updatedAt) {
    const indicator = document.getElementById('save-indicator');
    const messageEl = document.getElementById('save-message');
    
    if (indicator && messageEl) {
        messageEl.textContent = message + (updatedAt ? ' - ' + updatedAt : '');
        indicator.style.display = 'flex';
        
        // Masquer après 3 secondes
        setTimeout(() => {
            indicator.style.display = 'none';
        }, 3000);
    }
}

// ============================================
// DROPDOWN VERSIONS
// ============================================

function toggleVersionsDropdown() {
    const dropdown = document.querySelector('.actions-dropdown');
    if (dropdown) {
        dropdown.classList.toggle('active');
    }
}

// ============================================
// RESTAURER VERSION
// ============================================

function restoreVersion(versionId) {
    if (!confirm('Êtes-vous sûr de vouloir restaurer cette version ? Les modifications actuelles seront perdues.')) {
        return;
    }

    fetch(`/connect-admin/business-plan/restore-version/${versionId}/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrfToken,
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert(data.message);
            // Recharger la page
            location.reload();
        } else {
            alert('Erreur: ' + (data.error || 'Impossible de restaurer la version'));
        }
    })
    .catch(error => {
        console.error('Erreur:', error);
        alert('Erreur lors de la restauration');
    });

    // Fermer le dropdown
    toggleVersionsDropdown();
}

// ============================================
// UPLOAD DOCUMENT
// ============================================

document.addEventListener('DOMContentLoaded', function() {
    const uploadForm = document.getElementById('upload-document-form');
    if (uploadForm) {
        uploadForm.addEventListener('submit', function(e) {
            e.preventDefault();

            const formData = new FormData(this);

            fetch('/connect-admin/business-plan/upload-document/', {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert(data.message);
                    // Recharger la page pour afficher le nouveau document
                    location.reload();
                } else {
                    alert('Erreur: ' + (data.error || 'Impossible d\'uploader le document'));
                }
            })
            .catch(error => {
                console.error('Erreur:', error);
                alert('Erreur lors de l\'upload');
            });
        });
    }
});

// ============================================
// DELETE DOCUMENT
// ============================================

function deleteDocument(docId) {
    if (!confirm('Êtes-vous sûr de vouloir supprimer ce document ?')) {
        return;
    }

    // TODO: Implémenter la vue de suppression
    fetch(`/connect-admin/business-plan/delete-document/${docId}/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrfToken,
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert(data.message);
            location.reload();
        } else {
            alert('Erreur: ' + (data.error || 'Impossible de supprimer le document'));
        }
    })
    .catch(error => {
        console.error('Erreur:', error);
        alert('Erreur lors de la suppression');
    });
}

// ============================================
// CHECKBOXES
// ============================================

function saveCheckboxes(fieldName) {
    const checkboxes = document.querySelectorAll(`input[name="${fieldName}"]:checked`);
    const values = Array.from(checkboxes).map(cb => cb.value);

    // Créer FormData
    const formData = new FormData();
    formData.append('field', fieldName);
    formData.append('value', JSON.stringify(values));
    formData.append('csrfmiddlewaretoken', csrfToken);

    // Envoyer la requête
    fetch(saveUrl, {
        method: 'POST',
        body: formData,
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showSaveIndicator(data.message, data.updated_at);
        } else {
            console.error('Erreur de sauvegarde:', data.error);
        }
    })
    .catch(error => {
        console.error('Erreur réseau:', error);
    });
}

