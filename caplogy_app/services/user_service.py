import os, json, hashlib
from django.conf import settings
from ..models import UserProfile
from django.contrib.auth.models import User

# AD/LDAP - Méthode simplifiée comme dans testLDAP.py
from ldap3 import Server, Connection, NTLM

class UserService:
    def __init__(self, file_path=None):
        self.file_path = file_path or os.path.join(settings.BASE_DIR, 'users.json')
        if not os.path.exists(self.file_path):
            self._create_default_admin()
        else:
            self._load()

    def _load(self):
        with open(self.file_path, 'r') as f:
            data = json.load(f)
        self.users = data.get('users', [])

    def _save(self):
        with open(self.file_path, 'w') as f:
            json.dump({'users': self.users}, f, indent=4)

    def _hash_password(self, password):
        return hashlib.sha256(password.encode('utf-8')).hexdigest()

    def _create_default_admin(self):
        self.users = []
        default = {'username': 'admin', 'password': self._hash_password('admin'), 'role': 'admin'}
        self.users.append(default)
        self._save()

    def authenticate(self, username, password):
        """
        Authentifie via AD/LDAP, synchronise l'utilisateur Django/UserProfile
        Utilise la méthode simplifiée qui fonctionne (comme testLDAP.py)
        """
        try:
            print(f"[DEBUG] Tentative d'authentification LDAP pour: {username}")
            
            # Configuration simple comme dans testLDAP.py
            server = Server(settings.AD_SERVER, get_info=None, use_ssl=True)
            user_dn = f"{settings.AD_DOMAIN}\\{username}"
            
            print(f"[DEBUG] Serveur: {settings.AD_SERVER}")
            print(f"[DEBUG] DN utilisateur: {user_dn}")
            
            # Connexion simple comme dans testLDAP.py
            conn = Connection(server, user=user_dn, password=password, authentication=NTLM)
            
            if conn.bind():
                print(f"[SUCCESS] Authentification LDAP réussie pour {username}")
                
                # Rechercher les informations utilisateur
                search_filter = f"(sAMAccountName={username})"
                conn.search(
                    settings.AD_SEARCH_BASE,
                    search_filter,
                    attributes=['cn', 'mail', 'memberOf', 'displayName']
                )
                
                # Traiter les résultats
                user_info = {'sAMAccountName': username}
                groups = []
                
                if conn.entries:
                    entry = conn.entries[0]
                    user_info['cn'] = str(entry.cn) if entry.cn else ''
                    user_info['mail'] = str(entry.mail) if hasattr(entry, 'mail') and entry.mail else ''
                    user_info['displayName'] = str(entry.displayName) if hasattr(entry, 'displayName') and entry.displayName else ''
                    
                    if hasattr(entry, 'memberOf') and entry.memberOf:
                        groups = [str(group) for group in entry.memberOf]
                
                # Déterminer le rôle
                role = 'admin' if any('Domain Admins' in g for g in groups) else 'user'
                
                print(f"[DEBUG] Groupes trouvés: {groups}")
                print(f"[DEBUG] Rôle attribué: {role}")
                
                conn.unbind()
                
                # Synchronisation avec Django
                user, created = User.objects.get_or_create(
                    username=username,
                    defaults={
                        'email': user_info.get('mail', ''),
                        'first_name': user_info.get('displayName', '').split(' ')[0] if user_info.get('displayName') else '',
                        'last_name': ' '.join(user_info.get('displayName', '').split(' ')[1:]) if user_info.get('displayName') else '',
                    }
                )
                
                # Mettre à jour les informations si l'utilisateur existe déjà
                if not created:
                    user.email = user_info.get('mail', user.email)
                    if user_info.get('displayName'):
                        name_parts = user_info.get('displayName', '').split(' ')
                        user.first_name = name_parts[0] if name_parts else ''
                        user.last_name = ' '.join(name_parts[1:]) if len(name_parts) > 1 else ''
                    user.save()
                
                UserProfile.objects.update_or_create(
                    user=user,
                    defaults={'role': role}
                )
                
                print(f"[DEBUG] Utilisateur Django synchronisé: {username}, rôle: {role}")
                return {'username': username, 'role': role}
                
            else:
                print(f"[ERROR] Échec de l'authentification LDAP pour {username}")
                print(f"LDAP result: {conn.result}")
                print(f"LDAP last error: {conn.last_error}")
                return None
                
        except Exception as e:
            print(f"[ERROR] Erreur lors de l'authentification: {e}")
            import traceback
            traceback.print_exc()
            return None

    def get_users(self):
        return [{'username': u['username'], 'role': u['role']} for u in self.users]

    def add_user(self, username, password, role='user'):
        if any(u['username'] == username for u in self.users):
            return False
        entry = {'username': username, 'password': self._hash_password(password), 'role': role}
        self.users.append(entry)
        self._save()
        return True

    def get_ldap_profs(self):
        """
        Récupère tous les utilisateurs de l'OU Utilisateurs Caplogy (profs) depuis LDAP
        Utilise la méthode simplifiée qui fonctionne (comme testLDAP.py)
        """
        try:
            print(f"[DEBUG] Récupération des professeurs via LDAP")
            
            # Configuration simple comme dans testLDAP.py
            server = Server(settings.AD_SERVER, get_info=None, use_ssl=True)
            
            # Utiliser les credentials Nextcloud comme compte de service
            service_username = os.getenv('NEXTCLOUD_USER')
            service_password = os.getenv('NEXTCLOUD_PASSWORD')
            
            if not service_username or not service_password:
                print("[ERROR] Credentials Nextcloud manquants dans .env")
                return []
                
            user_dn = f"{settings.AD_DOMAIN}\\{service_username}"
            
            print(f"[DEBUG] Connexion service avec: {user_dn}")
            
            # Connexion simple comme dans testLDAP.py
            conn = Connection(server, user=user_dn, password=service_password, authentication=NTLM)
            
            if conn.bind():
                print(f"[SUCCESS] Connexion LDAP service réussie")
                
                # Rechercher tous les utilisateurs dans l'OU Utilisateurs Caplogy
                search_filter = "(objectClass=user)"
                conn.search(
                    settings.AD_SEARCH_BASE,
                    search_filter,
                    attributes=['sAMAccountName', 'cn', 'mail', 'displayName']
                )
                
                users = []
                for entry in conn.entries:
                    if hasattr(entry, 'sAMAccountName') and entry.sAMAccountName:
                        user_info = {
                            'username': str(entry.sAMAccountName),
                            'cn': str(entry.cn) if entry.cn else '',
                            'email': str(entry.mail) if hasattr(entry, 'mail') and entry.mail else '',
                            'displayName': str(entry.displayName) if hasattr(entry, 'displayName') and entry.displayName else ''
                        }
                        users.append(user_info)
                
                conn.unbind()
                print(f"[DEBUG] {len(users)} professeurs trouvés dans LDAP")
                return users
                
            else:
                print(f"[ERROR] Échec de la connexion LDAP service")
                print(f"LDAP result: {conn.result}")
                return []
                
        except Exception as e:
            print(f"[ERROR] Erreur LDAP lors de la récupération des profs: {e}")
            import traceback
            traceback.print_exc()
            return []
