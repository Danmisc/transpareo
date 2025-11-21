# Guide d'utilisation du Design System Transpareo

## Vue d'ensemble

Le Design System Transpareo fournit des composants réutilisables, des transitions fluides, et une accessibilité complète pour toute l'application.

## Principes de design

1. **Layout adaptatif** : Desktop/tablette/mobile + compact/large
2. **Bords arrondis doux** : Utilisation de `--radius-lg`, `--radius-xl`
3. **Couleur orange Transpareo** : `--color-accent` (orange-400)
4. **Mode sombre** : Support via `[data-theme="dark"]`
5. **Typographie lisible** : Interlignes larges (`--line-height-normal`, `--line-height-relaxed`)
6. **Transitions contextuelles** : Fade/slide automatiques
7. **Accessibilité** : Contraste, navigation clavier, ARIA

## Utilisation

### 1. Inclusion dans les templates

Le design system est déjà inclus dans `base.html`. Pour l'utiliser dans d'autres templates :

```django
{% extends "core/base.html" %}
{% load static %}
```

### 2. Composants réutilisables

#### Carte utilisateur

```django
{% include "core/components/user_card.html" with user=user %}
```

#### Breadcrumb

```django
{% include "core/components/breadcrumb.html" with breadcrumb_items=breadcrumb_items %}
```

Dans la vue :
```python
context = {
    'breadcrumb_items': [
        {'title': 'Connect', 'url': '/connect/'},
        {'title': 'Profil', 'url': '/profile/'},
        {'title': 'Paramètres', 'url': None},  # Dernier élément (pas de lien)
    ]
}
```

#### Tags

```django
{% include "core/components/tags.html" with tags=tags %}
```

Dans la vue :
```python
context = {
    'tags': [
        {'label': 'Toulouse', 'icon': '📍', 'url': '/search/?city=toulouse'},
        {'label': '2 pièces', 'accent': True},
    ]
}
```

#### Modale

```django
{% include "core/components/modal.html" with modal_id="myModal" title="Titre" content="<p>Contenu</p>" %}
```

### 3. Classes CSS disponibles

#### Cartes

- `.card` - Carte générique
- `.card-compact` - Carte compacte
- `.card-large` - Carte large
- `.user-card` - Carte utilisateur
- `.post-card` - Carte post
- `.logement-card` - Carte logement

#### Boutons

- `.btn` - Bouton de base
- `.btn-primary` - Bouton principal (orange)
- `.btn-secondary` - Bouton secondaire
- `.btn-ghost` - Bouton fantôme
- `.btn-sm` - Petit bouton
- `.btn-lg` - Grand bouton

#### Tags

- `.tag` - Tag générique
- `.tag-accent` - Tag avec accent orange

### 4. JavaScript - Fonctions globales

#### Feedback visuel

```javascript
// Afficher un toast
showToast('Message de succès', 'success', 3000);
showToast('Erreur', 'error', 3000);
showToast('Information', 'info', 3000);

// Afficher un loader sur un bouton
showLoader(document.getElementById('myButton'));

// Cacher le loader
hideLoader(document.getElementById('myButton'));

// Afficher un check
showCheck(document.getElementById('myButton'));

// Animation shake (erreur)
shake(document.getElementById('myInput'));
```

#### Modales

```javascript
// Ouvrir une modale
openModal('myModalId');

// Fermer la modale actuelle
closeModal();
```

#### Breadcrumb

Le breadcrumb est géré automatiquement. Il sauvegarde l'historique dans `sessionStorage`.

### 5. Quick Actions contextuelles

Ajoutez `data-quick-actions` sur n'importe quel élément :

```html
<div data-quick-actions='[
    {"icon": "💬", "label": "Envoyer un message", "url": "/messages/"},
    {"icon": "➕", "label": "Ajouter", "action": "addToFavorites"}
]'>
    Contenu avec quick actions
</div>
```

### 6. Context Menu

Créez un template de menu contextuel :

```django
{% include "core/components/context_menu.html" with menu_id="userMenu" menu_items=menu_items %}
```

Ajoutez `data-context-menu="userMenu"` sur l'élément :

```html
<div data-context-menu="userMenu">
    Clic droit ici
</div>
```

### 7. Variables CSS disponibles

#### Couleurs

- `--color-accent` - Orange Transpareo principal
- `--color-accent-hover` - Orange au survol
- `--color-accent-light` - Orange clair
- `--color-bg-primary` - Fond principal
- `--color-text-primary` - Texte principal
- `--color-border` - Couleur des bordures

#### Espacement

- `--space-1` à `--space-24` - Échelle d'espacement

#### Bordures arrondies

- `--radius-sm` à `--radius-full` - Rayons de bordure

#### Transitions

- `--transition-fast` - 150ms
- `--transition-base` - 250ms
- `--transition-slow` - 350ms

### 8. Mode sombre

Activez le mode sombre en ajoutant `data-theme="dark"` sur `<html>` :

```javascript
document.documentElement.setAttribute('data-theme', 'dark');
```

### 9. Accessibilité

- **Skip link** : Ajouté automatiquement (Aller au contenu principal)
- **Focus visible** : Tous les éléments focusables ont un outline orange
- **ARIA labels** : Ajoutés automatiquement aux boutons sans texte
- **Navigation clavier** : Support complet (Tab, Escape, flèches)
- **Screen reader** : Classe `.sr-only` disponible

### 10. Responsive

Le design system est entièrement responsive :

- **Mobile** : `< 640px`
- **Tablette** : `640px - 1024px`
- **Desktop** : `> 1024px`

Utilisez les classes `.container-compact`, `.container-normal`, `.container-large` pour contrôler la largeur.

### 11. Exemple complet

```django
{% extends "core/base.html" %}
{% load static %}

{% block title %}Ma Page{% endblock %}

{% block content %}
<main id="main-content">
    {% include "core/components/breadcrumb.html" with breadcrumb_items=breadcrumb_items %}
    
    <div class="container container-normal">
        <div class="card">
            <h1>Titre</h1>
            <p>Contenu</p>
            
            {% include "core/components/user_card.html" with user=user %}
            
            {% include "core/components/tags.html" with tags=tags %}
            
            <button class="btn btn-primary" onclick="showToast('Succès!', 'success')">
                Cliquer
            </button>
        </div>
    </div>
</main>
{% endblock %}
```

## Bonnes pratiques

1. **Toujours utiliser les composants réutilisables** plutôt que de créer des styles custom
2. **Respecter les variables CSS** pour la cohérence
3. **Tester l'accessibilité** avec un lecteur d'écran
4. **Utiliser les transitions** pour les changements de vue
5. **Ajouter des ARIA labels** si nécessaire
6. **Tester sur mobile** pour le responsive

