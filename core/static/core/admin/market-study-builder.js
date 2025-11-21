/**
 * MARKET STUDY BUILDER - JavaScript pour drag & drop, gestion questions
 */

// ============================================
// VARIABLES GLOBALES
// ============================================

let draggedElement = null;
let draggedOverElement = null;

// ============================================
// INITIALISATION
// ============================================

function initBuilder() {
    // Drag & Drop pour les types de questions
    initQuestionTypeDragDrop();
    
    // Drag & Drop pour réordonner les questions
    initQuestionsReorder();
}

// ============================================
// DRAG & DROP TYPES DE QUESTIONS
// ============================================

function initQuestionTypeDragDrop() {
    const questionTypes = document.querySelectorAll('.question-type-item');
    const builder = document.getElementById('questions-builder');
    
    questionTypes.forEach(typeItem => {
        typeItem.addEventListener('dragstart', function(e) {
            e.dataTransfer.effectAllowed = 'copy';
            e.dataTransfer.setData('questionType', this.dataset.type);
            draggedElement = this;
        });
    });
    
    builder.addEventListener('dragover', function(e) {
        e.preventDefault();
        e.dataTransfer.dropEffect = 'copy';
    });
    
    builder.addEventListener('drop', function(e) {
        e.preventDefault();
        
        const questionType = e.dataTransfer.getData('questionType');
        if (questionType) {
            addNewQuestion(questionType);
        }
        
        draggedElement = null;
    });
}

// ============================================
// DRAG & DROP RÉORDONNER QUESTIONS
// ============================================

function initQuestionsReorder() {
    const questions = document.querySelectorAll('.question-item');
    
    questions.forEach(question => {
        question.addEventListener('dragstart', function(e) {
            this.classList.add('dragging');
            draggedElement = this;
            e.dataTransfer.effectAllowed = 'move';
        });
        
        question.addEventListener('dragend', function(e) {
            this.classList.remove('dragging');
            document.querySelectorAll('.question-item').forEach(item => {
                item.classList.remove('drag-over');
            });
            draggedElement = null;
        });
        
        question.addEventListener('dragover', function(e) {
            e.preventDefault();
            e.dataTransfer.dropEffect = 'move';
            
            if (this !== draggedElement) {
                this.classList.add('drag-over');
            }
        });
        
        question.addEventListener('dragleave', function(e) {
            this.classList.remove('drag-over');
        });
        
        question.addEventListener('drop', function(e) {
            e.preventDefault();
            this.classList.remove('drag-over');
            
            if (draggedElement && this !== draggedElement) {
                const builder = document.getElementById('questions-builder');
                const allQuestions = Array.from(builder.querySelectorAll('.question-item'));
                const draggedIndex = allQuestions.indexOf(draggedElement);
                const targetIndex = allQuestions.indexOf(this);
                
                if (draggedIndex < targetIndex) {
                    builder.insertBefore(draggedElement, this.nextSibling);
                } else {
                    builder.insertBefore(draggedElement, this);
                }
                
                // Sauvegarder le nouvel ordre
                saveQuestionsOrder();
            }
        });
    });
}

// ============================================
// AJOUTER QUESTION
// ============================================

function addNewQuestion(questionType) {
    const label = prompt('Libellé de la question:');
    if (!label) return;
    
    const formData = new FormData();
    formData.append('question_type', questionType);
    formData.append('label', label);
    formData.append('description', '');
    formData.append('required', 'true');
    formData.append('order', document.querySelectorAll('.question-item').length);
    formData.append('options', JSON.stringify([]));
    formData.append('csrfmiddlewaretoken', csrfToken);
    
    fetch(saveQuestionUrl, {
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
            alert('Erreur: ' + (data.error || 'Impossible d\'ajouter la question'));
        }
    })
    .catch(error => {
        console.error('Erreur:', error);
        alert('Erreur lors de l\'ajout de la question');
    });
}

// ============================================
// SAUVEGARDER QUESTION
// ============================================

function saveQuestion(questionId) {
    const questionItem = document.querySelector(`[data-question-id="${questionId}"]`);
    if (!questionItem) return;
    
    const label = questionItem.querySelector('.question-label').value;
    const description = questionItem.querySelector('.question-description').value;
    const required = questionItem.querySelector('.question-required').checked;
    
    let scaleMin = null;
    let scaleMax = null;
    if (questionItem.querySelector('.question-scale-min')) {
        scaleMin = parseInt(questionItem.querySelector('.question-scale-min').value);
        scaleMax = parseInt(questionItem.querySelector('.question-scale-max').value);
    }
    
    const formData = new FormData();
    formData.append('question_id', questionId);
    formData.append('label', label);
    formData.append('description', description);
    formData.append('required', required);
    formData.append('scale_min', scaleMin || '');
    formData.append('scale_max', scaleMax || '');
    formData.append('order', Array.from(document.querySelectorAll('.question-item')).indexOf(questionItem));
    formData.append('options', JSON.stringify(getQuestionOptions(questionId)));
    formData.append('csrfmiddlewaretoken', csrfToken);
    
    fetch(saveQuestionUrl, {
        method: 'POST',
        body: formData,
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            console.log('Question sauvegardée');
        } else {
            alert('Erreur: ' + (data.error || 'Impossible de sauvegarder la question'));
        }
    })
    .catch(error => {
        console.error('Erreur:', error);
    });
}

// ============================================
// GESTION OPTIONS
// ============================================

function getQuestionOptions(questionId) {
    const optionsList = document.querySelector(`.options-list[data-question-id="${questionId}"]`);
    if (!optionsList) return [];
    
    const optionInputs = optionsList.querySelectorAll('.option-input');
    const options = [];
    optionInputs.forEach(input => {
        if (input.value.trim()) {
            options.push(input.value.trim());
        }
    });
    return options;
}

function addOption(questionId) {
    const optionsList = document.querySelector(`.options-list[data-question-id="${questionId}"]`);
    if (!optionsList) return;
    
    const optionItem = document.createElement('div');
    optionItem.className = 'option-item';
    optionItem.innerHTML = `
        <input type="text" class="option-input" placeholder="Nouvelle option..." onblur="saveQuestionOptions(${questionId})">
        <button type="button" class="btn-remove-option" onclick="removeOption(this, ${questionId})">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <line x1="18" y1="6" x2="6" y2="18"></line>
                <line x1="6" y1="6" x2="18" y2="18"></line>
            </svg>
        </button>
    `;
    
    optionsList.appendChild(optionItem);
    
    const newInput = optionItem.querySelector('.option-input');
    newInput.focus();
}

function removeOption(button, questionId) {
    const optionItem = button.closest('.option-item');
    const optionsList = optionItem.closest('.options-list');
    
    if (optionsList.querySelectorAll('.option-item').length <= 1) {
        // Ne pas supprimer s'il n'y a qu'une option, juste vider l'input
        const input = optionItem.querySelector('.option-input');
        input.value = '';
        input.focus();
    } else {
        optionItem.remove();
    }
    
    saveQuestionOptions(questionId);
}

function saveQuestionOptions(questionId) {
    // Récupérer le type de question pour savoir si on doit sauvegarder les options
    const questionItem = document.querySelector(`[data-question-id="${questionId}"]`);
    const questionType = questionItem ? questionItem.dataset.questionType : null;
    
    if (questionType && (questionType === 'single_choice' || questionType === 'multiple_choice')) {
        saveQuestion(questionId);
    }
}

// ============================================
// SUPPRIMER QUESTION
// ============================================

function deleteQuestion(questionId) {
    if (!confirm('Êtes-vous sûr de vouloir supprimer cette question ?')) {
        return;
    }
    
    fetch(deleteQuestionUrl + questionId + '/', {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrfToken,
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            const questionItem = document.querySelector(`[data-question-id="${questionId}"]`);
            if (questionItem) {
                questionItem.remove();
                
                // Sauvegarder le nouvel ordre
                saveQuestionsOrder();
            }
        } else {
            alert('Erreur: ' + (data.error || 'Impossible de supprimer la question'));
        }
    })
    .catch(error => {
        console.error('Erreur:', error);
        alert('Erreur lors de la suppression');
    });
}

// ============================================
// SAUVEGARDER ORDRE DES QUESTIONS
// ============================================

function saveQuestionsOrder() {
    const questions = document.querySelectorAll('.question-item');
    const orders = [];
    
    questions.forEach((question, index) => {
        const questionId = question.dataset.questionId;
        if (questionId) {
            orders.push({
                id: parseInt(questionId),
                order: index
            });
        }
    });
    
    fetch(reorderQuestionsUrl, {
        method: 'POST',
        body: JSON.stringify({ orders: orders }),
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken,
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            console.log('Ordre sauvegardé');
        }
    })
    .catch(error => {
        console.error('Erreur:', error);
    });
}

// ============================================
// APERÇU
// ============================================

function previewForm() {
    const previewPanel = document.getElementById('builder-preview');
    const previewContent = document.getElementById('preview-content');
    
    // Générer l'aperçu depuis les questions
    const questions = document.querySelectorAll('.question-item');
    let previewHTML = '<div class="preview-form">';
    
    questions.forEach((question, index) => {
        const questionId = question.dataset.questionId;
        const label = question.querySelector('.question-label').value;
        const description = question.querySelector('.question-description').value;
        const required = question.querySelector('.question-required').checked;
        
        previewHTML += `
            <div class="preview-question">
                <label class="preview-label">
                    ${label} ${required ? '<span class="required">*</span>' : ''}
                </label>
                ${description ? `<p class="preview-description">${description}</p>` : ''}
                <div class="preview-field">
                    ${generatePreviewField(question)}
                </div>
            </div>
        `;
    });
    
    previewHTML += '</div>';
    previewContent.innerHTML = previewHTML;
    
    previewPanel.style.display = 'block';
}

function generatePreviewField(question) {
    // Générer le champ selon le type de question
    // Simplifié pour l'exemple
    return '<input type="text" class="preview-input" placeholder="Réponse..." disabled>';
}

function closePreview() {
    const previewPanel = document.getElementById('builder-preview');
    previewPanel.style.display = 'none';
}

// ============================================
// ACTIVER ÉTUDE
// ============================================

function activateStudy() {
    if (!confirm('Activer cette étude ? Elle sera accessible publiquement.')) {
        return;
    }
    
    // TODO: Implémenter l'activation via une vue Django
    alert('Fonctionnalité d\'activation à implémenter');
}

