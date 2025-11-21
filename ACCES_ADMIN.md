# Guide d'accès au Panel Admin Transpareo Connect

## Comment accéder aux pages admin

### 1. Créer un compte administrateur

Si vous n'avez pas encore de compte administrateur, créez-en un :

```bash
cd "d:\transpareo html version\backend"
python manage.py createsuperuser
```

Suivez les instructions pour définir :
- Username
- Email
- Password

**Important** : Le compte créé aura automatiquement `is_staff=True` et `is_superuser=True`.

### 2. Donner les droits admin à un utilisateur existant

Si vous avez déjà un compte utilisateur et souhaitez lui donner les droits admin :

```bash
cd "d:\transpareo html version\backend"
python manage.py shell
```

Puis dans le shell Python :

```python
from django.contrib.auth import get_user_model
User = get_user_model()

# Remplacer 'username' par le nom d'utilisateur souhaité
user = User.objects.get(username='votre_username')
user.is_staff = True
user.is_superuser = True
user.save()

print(f"Les droits admin ont été accordés à {user.username}")
```

### 3. Accéder au panel admin

#### Méthode 1 : Via le menu utilisateur (recommandé)

1. Connectez-vous avec votre compte administrateur
2. Cliquez sur votre avatar/username en haut à droite de la navbar
3. Dans le menu déroulant, cliquez sur **"Panel Admin"** (visible uniquement pour les admins)

#### Méthode 2 : Via l'URL directe

Accédez directement à l'URL :

```
http://127.0.0.1:8000/connect-admin/dashboard/
```

### 4. Pages disponibles dans le panel admin

Une fois dans le panel admin, vous pouvez accéder à :

#### Navigation principale
- **Tableau de bord** : `/connect-admin/dashboard/`
  - Statistiques en temps réel
  - Alertes importantes
  - Graphiques de croissance

- **Utilisateurs** : `/connect-admin/users/`
  - Liste de tous les utilisateurs
  - Recherche et filtres (actifs, suspendus, bannis)
  - Actions : suspendre, bannir, supprimer, révoquer badges

- **Modération** : `/connect-admin/moderation/posts/`
  - Posts signalés
  - Commentaires signalés
  - Messages privés signalés

- **Vérifications** : `/connect-admin/verifications/identity/`
  - Demandes de vérification d'identité
  - Demandes de vérification propriétaire

- **Réclamations** : `/connect-admin/reclamations/`
  - Réclamations de logements
  - Approuver/Refuser les réclamations

- **Groupes** : `/connect-admin/groups/`
  - Liste de tous les groupes
  - Groupes signalés

- **Tickets Support** : `/connect-admin/tickets/`
  - Gérer les tickets d'assistance
  - Répondre aux utilisateurs

- **Statistiques** : `/connect-admin/statistics/`
  - Statistiques avancées
  - Export CSV des données

### 5. Sécurité

- **Protection automatique** : Toutes les pages admin sont protégées par le décorateur `@admin_required`
- **Redirection** : Si un utilisateur non-admin essaie d'accéder à une page admin, il sera redirigé vers la page d'accueil Connect
- **Permissions** : Seuls les utilisateurs avec `is_staff=True` OU `is_superuser=True` peuvent accéder

### 6. Vérifier vos droits admin

Pour vérifier si votre compte a les droits admin :

```bash
cd "d:\transpareo html version\backend"
python manage.py shell
```

```python
from django.contrib.auth import get_user_model
User = get_user_model()

user = User.objects.get(username='votre_username')
print(f"is_staff: {user.is_staff}")
print(f"is_superuser: {user.is_superuser}")
```

### 7. Dépannage

#### Problème : Le lien "Panel Admin" n'apparaît pas dans le menu
**Solution** : Vérifiez que votre compte a `is_staff=True` ou `is_superuser=True`

#### Problème : Erreur "Accès refusé" lors de l'accès à une page admin
**Solution** : Votre compte n'a pas les droits admin. Utilisez la méthode 2 ci-dessus pour les activer.

#### Problème : Redirection vers la page de connexion
**Solution** : Assurez-vous d'être connecté avec votre compte administrateur

### URLs complètes du panel admin

- Dashboard : `http://127.0.0.1:8000/connect-admin/dashboard/`
- Utilisateurs : `http://127.0.0.1:8000/connect-admin/users/`
- Modération Posts : `http://127.0.0.1:8000/connect-admin/moderation/posts/`
- Modération Commentaires : `http://127.0.0.1:8000/connect-admin/moderation/comments/`
- Modération Messages : `http://127.0.0.1:8000/connect-admin/moderation/messages/`
- Vérifications Identité : `http://127.0.0.1:8000/connect-admin/verifications/identity/`
- Vérifications Propriétaire : `http://127.0.0.1:8000/connect-admin/verifications/owner/`
- Réclamations : `http://127.0.0.1:8000/connect-admin/reclamations/`
- Groupes : `http://127.0.0.1:8000/connect-admin/groups/`
- Groupes Signalés : `http://127.0.0.1:8000/connect-admin/groups/signaled/`
- Tickets Support : `http://127.0.0.1:8000/connect-admin/tickets/`
- Statistiques : `http://127.0.0.1:8000/connect-admin/statistics/`
- Export CSV : `http://127.0.0.1:8000/connect-admin/export/csv/?type=users`

