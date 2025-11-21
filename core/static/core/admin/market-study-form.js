/**
 * MARKET STUDY FORM - JavaScript pour validation, progress bar
 */

// ============================================
// INITIALISATION
// ============================================

function initForm() {
    // Générer les options d'échelle
    generateScaleOptions();
    
    // Mettre à jour la progress bar
    updateProgressBar();
    
    // Validation en temps réel
    initValidation();
    
    // Soumission du formulaire
    initFormSubmit();
}

// ============================================
// GÉNÉRER OPTIONS ÉCHELLE
// ============================================

function generateScaleOptions() {
    const scaleGroups = document.querySelectorAll('.scale-options');
    
    scaleGroups.forEach(group => {
        const min = parseInt(group.dataset.scaleMin || 1);
        const max = parseInt(group.dataset.scaleMax || 5);
        const questionId = group.dataset.questionId;
        const required = group.closest('.question-block')?.dataset.required === 'True';
        
        let html = '';
        for (let i = min; i <= max; i++) {
            html += `
                <label class="scale-option">
                    <input type="radio" name="question_${questionId}" value="${i}" ${required ? 'required' : ''}>
                    <span>${i}</span>
                </label>
            `;
        }
        
        group.innerHTML = html;
    });
    
    // Générer les options NPS (0-10)
    const npsGroups = document.querySelectorAll('.nps-options[data-question-id]');
    
    npsGroups.forEach(group => {
        const questionId = group.dataset.questionId;
        const required = group.closest('.question-block')?.dataset.required === 'True';
        
        let html = '';
        for (let i = 0; i <= 10; i++) {
            html += `
                <label class="nps-option">
                    <input type="radio" name="question_${questionId}" value="${i}" ${required ? 'required' : ''}>
                    <span>${i}</span>
                </label>
            `;
        }
        
        group.innerHTML = html;
    });
}

// ============================================
// PROGRESS BAR
// ============================================

function updateProgressBar() {
    const questions = document.querySelectorAll('.question-block');
    const inputs = document.querySelectorAll('.form-input, .form-textarea, input[type="radio"]:checked, input[type="checkbox"]:checked, input[type="date"], input[type="file"]');
    const requiredInputs = document.querySelectorAll('[required]');
    
    let answeredCount = 0;
    requiredInputs.forEach(input => {
        if (input.type === 'radio' || input.type === 'checkbox') {
            const name = input.name;
            const checked = document.querySelector(`input[name="${name}"]:checked`);
            if (checked) answeredCount++;
        } else if (input.type === 'file') {
            if (input.files.length > 0) answeredCount++;
        } else {
            if (input.value.trim()) answeredCount++;
        }
    });
    
    const progress = questions.length > 0 ? (answeredCount / questions.length) * 100 : 0;
    const progressFill = document.getElementById('progress-fill');
    if (progressFill) {
        progressFill.style.width = progress + '%';
    }
}

// ============================================
// VALIDATION
// ============================================

function initValidation() {
    const inputs = document.querySelectorAll('input, textarea, select');
    
    inputs.forEach(input => {
        input.addEventListener('input', function() {
            updateProgressBar();
            validateField(this);
        });
        
        input.addEventListener('change', function() {
            updateProgressBar();
            validateField(this);
        });
    });
}

function validateField(field) {
    const questionBlock = field.closest('.question-block');
    if (!questionBlock) return;
    
    const isValid = field.checkValidity();
    
    if (field.required && !isValid) {
        questionBlock.classList.add('invalid');
    } else {
        questionBlock.classList.remove('invalid');
    }
}

// ============================================
// FORM SUBMIT
// ============================================

function initFormSubmit() {
    const form = document.getElementById('study-form');
    if (!form) return;
    
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        
        // Valider tous les champs requis
        const requiredInputs = form.querySelectorAll('[required]');
        let isValid = true;
        
        requiredInputs.forEach(input => {
            if (input.type === 'radio' || input.type === 'checkbox') {
                const name = input.name;
                const checked = form.querySelector(`input[name="${name}"]:checked`);
                if (!checked) {
                    isValid = false;
                    const questionBlock = input.closest('.question-block');
                    if (questionBlock) {
                        questionBlock.classList.add('invalid');
                    }
                }
            } else if (!input.value.trim()) {
                isValid = false;
                const questionBlock = input.closest('.question-block');
                if (questionBlock) {
                    questionBlock.classList.add('invalid');
                }
            }
        });
        
        if (!isValid) {
            alert('Veuillez remplir tous les champs obligatoires.');
            return;
        }
        
        // Soumettre le formulaire
        const formData = new FormData(form);
        
        fetch(form.action, {
            method: 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Afficher le message de succès
                form.style.display = 'none';
                const successMessage = document.getElementById('success-message');
                if (successMessage) {
                    successMessage.style.display = 'block';
                    const completionMessage = document.getElementById('completion-message');
                    if (completionMessage && data.message) {
                        completionMessage.textContent = data.message;
                    }
                }
            } else {
                alert('Erreur: ' + (data.error || 'Impossible de soumettre le formulaire'));
            }
        })
        .catch(error => {
            console.error('Erreur:', error);
            alert('Erreur lors de la soumission du formulaire');
        });
    });
}

