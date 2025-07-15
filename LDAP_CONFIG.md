# Configuration LDAPS pour Caplogy

## 📋 Prérequis

1. **Python packages** installés :
   ```bash
   pip install -r requirements.txt
   ```

2. **Accès réseau** au serveur Active Directory sur le port 636 (LDAPS)

3. **Certificat SSL** configuré ou validation SSL désactivée pour les tests

## 🔧 Configuration

### 1. Fichier `.env`

Créez un fichier `.env` à la racine du projet avec les variables suivantes :

```env
# Configuration Django
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,intranet.caplogy.com

# Configuration LDAP/Active Directory
AD_SERVER=ldaps://10.3.0.107
AD_DOMAIN=CAPLOGY
AD_SEARCH_BASE=DC=CAPLOGY,DC=LOCAL

# Configuration Moodle
MOODLE_URL=https://your-moodle-url.com
MOODLE_TOKEN=your-moodle-token-here

# Configuration Nextcloud (utilisé comme compte de service LDAP)
NEXTCLOUD_WEBDAV_URL=https://your-nextcloud-url.com
NEXTCLOUD_SHARE_URL=https://your-nextcloud-url.com
NEXTCLOUD_USER=your-service-account-username
NEXTCLOUD_PASSWORD=your-service-account-password
```

### 2. Paramètres LDAP avancés

Les paramètres suivants sont configurés dans `settings.py` :

- **AD_SERVER** : URL du serveur LDAP avec SSL (ldaps://)
- **AD_DOMAIN** : Domaine NetBIOS (CAPLOGY)
- **AD_SEARCH_BASE** : Base DN pour les recherches
- **LDAP_USER_SEARCH_BASE** : OU spécifique pour les utilisateurs/professeurs
- **LDAP_USE_SSL** : Utilisation du SSL (True par défaut)
- **LDAP_SSL_VERIFY** : Vérification des certificats SSL (False pour les tests)

## 🧪 Tests

### 1. Script de test en ligne de commande

```bash
python test_ldap.py
```

Ce script teste :
- La connexion au serveur LDAP
- L'authentification d'un utilisateur
- La récupération des utilisateurs
- Le service utilisateur complet

### 2. Interface web de test

Accédez à : `http://localhost:8000/admin/ldap-test/`

Cette interface permet de tester tous les aspects de la configuration LDAP via une interface web.

## 🔍 Diagnostic des erreurs

### Erreur de connexion SSL

```
[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed
```

**Solution** : Définir `LDAP_SSL_VERIFY=False` dans `settings.py` pour les tests

### Erreur de bind

```
[ERROR] Échec de l'authentification LDAP
```

**Solutions** :
1. Vérifier le format du nom d'utilisateur (`DOMAIN\username`)
2. Vérifier le mot de passe
3. Vérifier que l'utilisateur existe dans l'AD
4. Vérifier les permissions du compte

### Erreur de recherche

```
[ERROR] Erreur lors de la récupération des utilisateurs
```

**Solutions** :
1. Vérifier le `LDAP_USER_SEARCH_BASE`
2. Vérifier les permissions du compte de service
3. Vérifier le filtre de recherche

## 🚀 Utilisation

### 1. Authentification des utilisateurs

Le système utilise automatiquement LDAP pour l'authentification. Les utilisateurs se connectent avec leur nom d'utilisateur et mot de passe Active Directory.

### 2. Récupération des professeurs

La liste des professeurs est récupérée depuis l'OU "Utilisateurs Caplogy" et utilisée pour l'affectation aux cours Moodle.

### 3. Synchronisation utilisateurs

Les utilisateurs sont automatiquement synchronisés avec Django lors de leur première connexion.

## 📁 Structure des fichiers

```
caplogy_app/
├── services/
│   ├── ldap_manager.py      # Gestionnaire LDAP principal
│   ├── user_service.py      # Service utilisateur (modifié)
│   └── moodle_api.py        # API Moodle (modifiée)
├── templates/caplogy_app/
│   └── ldap_test.html       # Interface de test LDAP
├── views_ldap_test.py       # Vues pour les tests LDAP
└── urls.py                  # Routes (modifiées)
```

## 🛠️ Dépannage

### Logs détaillés

Les logs détaillés sont affichés dans la console Django. Pour plus de détails, consultez les messages prefixés par `[DEBUG]`, `[SUCCESS]`, `[ERROR]`.

### Test étape par étape

1. **Test de connexion** : `python test_ldap.py`
2. **Test web** : `/admin/ldap-test/`
3. **Test d'authentification** : Essayer de se connecter avec un compte AD
4. **Test de récupération** : Créer un cours et vérifier la liste des professeurs

### Problèmes courants

1. **Port 636 bloqué** : Vérifier le pare-feu
2. **Certificat SSL invalide** : Désactiver la vérification SSL temporairement
3. **Permissions insuffisantes** : Utiliser un compte de service avec les bonnes permissions
4. **OU incorrect** : Vérifier le `LDAP_USER_SEARCH_BASE`

## 📞 Support

En cas de problème, vérifiez :
1. Les logs Django
2. Les tests LDAP
3. La configuration réseau
4. Les permissions Active Directory
