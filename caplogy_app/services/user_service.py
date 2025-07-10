import os, json, hashlib
from django.conf import settings
from ..models import UserProfile
from django.contrib.auth.models import User

# AD/LDAP
from ldap3 import Server, Connection, ALL, NTLM

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
        Authentifie via AD/LDAP, synchronise l’utilisateur Django/UserProfile
        """
        try:
            print(f"Tentative de connexion LDAP vers {settings.AD_SERVER}")
            server = Server(settings.AD_SERVER, get_info=ALL)
            user_dn = f"{settings.AD_DOMAIN}\\{username}"
            print(f"DN utilisateur: {user_dn}")
            
            conn = Connection(
                server,
                user=user_dn,
                password=password,
                authentication=NTLM,
                auto_bind=False
            )
            
            print("Tentative de bind...")
            if not conn.bind():
                print(f"Erreur de liaison LDAP: {conn.result}")
                return None
            
            print("Connexion LDAP réussie!")
            
        except Exception as e:
            print(f"Erreur de connexion LDAP: {e}")
            print(f"Type d'erreur: {type(e)}")
            return None

        # Recherche des groupes AD pour déterminer le rôle
        conn.search(
            settings.AD_SEARCH_BASE,
            f"(sAMAccountName={username})",
            attributes=['memberOf']
        )
        entry = conn.entries[0] if conn.entries else None
        groupes = entry.memberOf.values if entry and hasattr(entry.memberOf, 'values') else []
        role = 'admin' if any('Domain Admins' in g for g in groupes) else 'user'

        # Synchronisation avec Django
        user, _ = User.objects.get_or_create(username=username)
        UserProfile.objects.get_or_create(user=user, defaults={'role': role})

        return {'username': username, 'role': role}

    def get_users(self):
        return [{'username': u['username'], 'role': u['role']} for u in self.users]

    def add_user(self, username, password, role='user'):
        if any(u['username'] == username for u in self.users):
            return False
        entry = {'username': username, 'password': self._hash_password(password), 'role': role}
        self.users.append(entry)
        self._save()
        return True
