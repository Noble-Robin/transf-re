"""
Utilitaire pour la gestion des connexions LDAP/Active Directory
"""
import os
import ssl
from django.conf import settings
from ldap3 import Server, Connection, ALL, NTLM, Tls
from ldap3.core.exceptions import LDAPException


class LDAPManager:
    """
    Gestionnaire de connexions LDAP avec support SSL/TLS
    """
    
    def __init__(self):
        self.server_uri = settings.AD_SERVER
        self.domain = settings.AD_DOMAIN
        self.search_base = settings.AD_SEARCH_BASE
        self.user_search_base = settings.LDAP_USER_SEARCH_BASE
        
    def _get_server(self):
        """
        Crée et retourne un objet Server LDAP avec configuration SSL
        """
        try:
            # Configuration TLS pour LDAPS
            tls_configuration = Tls(
                validate=ssl.CERT_NONE if not settings.LDAP_SSL_VERIFY else ssl.CERT_REQUIRED,
                version=ssl.PROTOCOL_TLS,
                ciphers='ALL:@SECLEVEL=0'  # Permet les anciens ciphers si nécessaire
            )
            
            server = Server(
                self.server_uri,
                use_ssl=settings.LDAP_USE_SSL,
                tls=tls_configuration,
                get_info=ALL
            )
            
            print(f"[DEBUG] Serveur LDAP configuré: {self.server_uri}")
            return server
            
        except Exception as e:
            print(f"[ERROR] Erreur lors de la configuration du serveur LDAP: {e}")
            raise
    
    def authenticate_user(self, username, password):
        """
        Authentifie un utilisateur via LDAP
        """
        try:
            server = self._get_server()
            
            # Format du DN utilisateur pour l'authentification
            user_dn = f"{self.domain}\\{username}"
            
            print(f"[DEBUG] Tentative d'authentification pour: {user_dn}")
            
            # Tentative de connexion
            connection = Connection(
                server,
                user=user_dn,
                password=password,
                authentication=NTLM,
                auto_bind=True
            )
            
            if connection.bind():
                print(f"[SUCCESS] Authentification réussie pour {username}")
                
                # Récupérer les informations utilisateur
                user_info = self._get_user_info(connection, username)
                connection.unbind()
                
                return {
                    'success': True,
                    'username': username,
                    'user_info': user_info
                }
            else:
                print(f"[ERROR] Échec de l'authentification pour {username}")
                return {'success': False, 'error': 'Identifiants invalides'}
                
        except LDAPException as e:
            print(f"[ERROR] Erreur LDAP lors de l'authentification: {e}")
            return {'success': False, 'error': f'Erreur LDAP: {str(e)}'}
        except Exception as e:
            print(f"[ERROR] Erreur générale lors de l'authentification: {e}")
            return {'success': False, 'error': f'Erreur: {str(e)}'}
    
    def _get_user_info(self, connection, username):
        """
        Récupère les informations détaillées d'un utilisateur
        """
        try:
            search_filter = f"(sAMAccountName={username})"
            
            connection.search(
                self.user_search_base,
                search_filter,
                attributes=['cn', 'mail', 'displayName', 'memberOf', 'sAMAccountName']
            )
            
            if connection.entries:
                entry = connection.entries[0]
                
                # Extraire les groupes
                groups = []
                if hasattr(entry, 'memberOf') and entry.memberOf:
                    groups = [str(group) for group in entry.memberOf]
                
                return {
                    'cn': str(entry.cn) if entry.cn else '',
                    'mail': str(entry.mail) if hasattr(entry, 'mail') and entry.mail else '',
                    'displayName': str(entry.displayName) if hasattr(entry, 'displayName') and entry.displayName else '',
                    'groups': groups,
                    'sAMAccountName': str(entry.sAMAccountName) if entry.sAMAccountName else username
                }
            else:
                return {'sAMAccountName': username}
                
        except Exception as e:
            print(f"[ERROR] Erreur lors de la récupération des infos utilisateur: {e}")
            return {'sAMAccountName': username}
    
    def get_all_users(self, service_username=None, service_password=None):
        """
        Récupère tous les utilisateurs de l'OU spécifiée
        """
        try:
            server = self._get_server()
            
            # Utiliser un compte de service si fourni
            if service_username and service_password:
                user_dn = f"{self.domain}\\{service_username}"
                connection = Connection(
                    server,
                    user=user_dn,
                    password=service_password,
                    authentication=NTLM,
                    auto_bind=True
                )
            else:
                # Connexion anonyme (peut ne pas fonctionner selon la config AD)
                connection = Connection(server, auto_bind=True)
            
            if not connection.bind():
                print("[ERROR] Impossible de se connecter au serveur LDAP")
                return []
            
            # Rechercher tous les utilisateurs
            search_filter = "(objectClass=person)"
            
            connection.search(
                self.user_search_base,
                search_filter,
                attributes=['sAMAccountName', 'cn', 'mail', 'displayName']
            )
            
            users = []
            for entry in connection.entries:
                if entry.sAMAccountName:  # S'assurer qu'il y a un nom d'utilisateur
                    users.append({
                        'username': str(entry.sAMAccountName),
                        'name': str(entry.cn) if entry.cn else str(entry.sAMAccountName),
                        'mail': str(entry.mail) if hasattr(entry, 'mail') and entry.mail else '',
                        'displayName': str(entry.displayName) if hasattr(entry, 'displayName') and entry.displayName else ''
                    })
            
            connection.unbind()
            print(f"[DEBUG] {len(users)} utilisateurs trouvés")
            return users
            
        except Exception as e:
            print(f"[ERROR] Erreur lors de la récupération des utilisateurs: {e}")
            return []
    
    def test_connection(self):
        """
        Test la connexion au serveur LDAP
        """
        try:
            server = self._get_server()
            connection = Connection(server)
            
            if connection.bind():
                print("[SUCCESS] Connexion au serveur LDAP réussie")
                server_info = connection.server.info if connection.server else "Informations non disponibles"
                connection.unbind()
                return {
                    'success': True,
                    'server_info': str(server_info)
                }
            else:
                print("[ERROR] Impossible de se connecter au serveur LDAP")
                return {'success': False, 'error': 'Connexion échouée'}
                
        except Exception as e:
            print(f"[ERROR] Erreur lors du test de connexion: {e}")
            return {'success': False, 'error': str(e)}
