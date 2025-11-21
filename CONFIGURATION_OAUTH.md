# Configuration OAuth Google

Pour que le bouton "Continuer avec Google" fonctionne, vous devez configurer vos clés API Google OAuth.

## Étapes de configuration

### 1. Créer un projet Google Cloud

1. Allez sur [Google Cloud Console](https://console.cloud.google.com/)
2. Créez un nouveau projet ou sélectionnez un projet existant
3. Activez l'API **Google Identity** (anciennement Google+ API)

### 2. Créer des identifiants OAuth 2.0

1. Allez dans **"APIs & Services" > "Credentials"**
2. Cliquez sur **"Create Credentials" > "OAuth client ID"**
3. Si c'est la première fois, configurez l'**OAuth consent screen** :
   - Type d'utilisateur : **External** (ou Internal si vous avez un compte Google Workspace)
   - Remplissez les informations de base (nom de l'application, email de support)
   - Ajoutez l'email de support et le domaine (si applicable)
   - Ajoutez les scopes : `email` et `profile`
   - Ajoutez des utilisateurs de test (pour le mode test)
   - Soumettez pour révision (si nécessaire)

### 3. Créer l'ID client OAuth

1. Dans **"Create OAuth client ID"** :
   - **Application type** : `Web application`
   - **Name** : `Transpareo` (ou le nom de votre choix)
   - **Authorized JavaScript origins** :
     - `http://127.0.0.1:8000` (pour le développement local)
     - `http://localhost:8000` (si vous utilisez localhost)
   - **Authorized redirect URIs** :
     - `http://127.0.0.1:8000/accounts/google/login/callback/`
     - `http://localhost:8000/accounts/google/login/callback/`

2. Cliquez sur **"Create"**
3. Copiez le **Client ID** et le **Client Secret**

### 4. Configurer les variables d'environnement

Créez un fichier `.env` à la racine du dossier `backend/` avec le contenu suivant :

```env
GOOGLE_CLIENT_ID=votre-client-id-ici.apps.googleusercontent.com
GOOGLE_SECRET=votre-client-secret-ici
```

**Important** : Ne commitez JAMAIS le fichier `.env` dans Git ! Il doit être dans `.gitignore`.

### 5. Installer python-dotenv

Si ce n'est pas déjà fait, installez le package :

```bash
pip install python-dotenv
```

Ou utilisez le script :

```bash
python check_and_install.py
```

### 6. Redémarrer le serveur Django

Après avoir configuré le `.env`, redémarrez le serveur :

```bash
python manage.py runserver
```

## Vérification

1. Allez sur la page de connexion
2. Cliquez sur "Continuer avec Google"
3. Vous devriez être redirigé vers la page de connexion Google (pas une page violette)

## Dépannage

### Erreur : "Missing required parameter: client_id"

Cela signifie que les variables d'environnement ne sont pas chargées. Vérifiez :

1. Que le fichier `.env` existe dans `backend/`
2. Que les noms des variables sont corrects : `GOOGLE_CLIENT_ID` et `GOOGLE_SECRET`
3. Que `python-dotenv` est installé
4. Que le serveur a été redémarré après la création du `.env`

### Erreur : "redirect_uri_mismatch"

Vérifiez que l'URI de redirection dans Google Cloud Console correspond exactement à :
- `http://127.0.0.1:8000/accounts/google/login/callback/`

L'URI est sensible à la casse et doit correspondre exactement, y compris le slash final.


