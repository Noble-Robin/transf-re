#!/usr/bin/env python3
"""
Script de test pour la connexion LDAPS
"""
import os
import sys
import django
from pathlib import Path

# Ajouter le répertoire du projet au Python path
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

# Configurer Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'caplogy_project.settings')
django.setup()

from caplogy_app.services.ldap_manager import LDAPManager
from caplogy_app.services.user_service import UserService

def test_ldap_connection():
    """Test de base de la connexion LDAP"""
    print("=== Test de connexion LDAP ===")
    
    ldap_manager = LDAPManager()
    result = ldap_manager.test_connection()
    
    if result['success']:
        print("✅ Connexion au serveur LDAP réussie")
        print(f"Informations serveur: {result['server_info']}")
    else:
        print("❌ Échec de la connexion au serveur LDAP")
        print(f"Erreur: {result['error']}")
    
    return result['success']

def test_user_authentication():
    """Test d'authentification utilisateur"""
    print("\n=== Test d'authentification utilisateur ===")
    
    # Demander les credentials à l'utilisateur
    username = input("Nom d'utilisateur: ")
    password = input("Mot de passe: ")
    
    ldap_manager = LDAPManager()
    result = ldap_manager.authenticate_user(username, password)
    
    if result['success']:
        print("✅ Authentification réussie")
        print(f"Informations utilisateur: {result['user_info']}")
    else:
        print("❌ Échec de l'authentification")
        print(f"Erreur: {result['error']}")
    
    return result['success']

def test_get_users():
    """Test de récupération des utilisateurs"""
    print("\n=== Test de récupération des utilisateurs ===")
    
    service_username = os.getenv('NEXTCLOUD_USER')
    service_password = os.getenv('NEXTCLOUD_PASSWORD')
    
    if not service_username or not service_password:
        print("❌ Credentials de service non configurés")
        print("Configurez NEXTCLOUD_USER et NEXTCLOUD_PASSWORD dans le fichier .env")
        return False
    
    ldap_manager = LDAPManager()
    users = ldap_manager.get_all_users(service_username, service_password)
    
    if users:
        print(f"✅ {len(users)} utilisateurs récupérés")
        for user in users[:5]:  # Afficher les 5 premiers
            print(f"  - {user['username']}: {user['name']} ({user['mail']})")
        if len(users) > 5:
            print(f"  ... et {len(users) - 5} autres")
    else:
        print("❌ Aucun utilisateur trouvé")
    
    return len(users) > 0

def test_user_service():
    """Test du service utilisateur"""
    print("\n=== Test du service utilisateur ===")
    
    user_service = UserService()
    profs = user_service.get_ldap_profs()
    
    if profs:
        print(f"✅ {len(profs)} professeurs récupérés via UserService")
        for prof in profs[:3]:  # Afficher les 3 premiers
            print(f"  - {prof['username']}: {prof['name']} ({prof['mail']})")
    else:
        print("❌ Aucun professeur trouvé via UserService")
    
    return len(profs) > 0

def main():
    """Fonction principale"""
    print("🔍 Test de configuration LDAPS pour Caplogy")
    print("=" * 50)
    
    # Test 1: Connexion de base
    connection_ok = test_ldap_connection()
    
    if not connection_ok:
        print("\n❌ Connexion LDAP échouée - Arrêt des tests")
        return
    
    # Test 2: Authentification utilisateur
    auth_ok = test_user_authentication()
    
    # Test 3: Récupération des utilisateurs
    users_ok = test_get_users()
    
    # Test 4: Service utilisateur
    service_ok = test_user_service()
    
    # Résumé
    print("\n" + "=" * 50)
    print("📊 Résumé des tests:")
    print(f"  Connexion LDAP: {'✅' if connection_ok else '❌'}")
    print(f"  Authentification: {'✅' if auth_ok else '❌'}")
    print(f"  Récupération utilisateurs: {'✅' if users_ok else '❌'}")
    print(f"  Service utilisateur: {'✅' if service_ok else '❌'}")
    
    if all([connection_ok, auth_ok, users_ok, service_ok]):
        print("\n🎉 Tous les tests sont passés avec succès!")
    else:
        print("\n⚠️  Certains tests ont échoué - Vérifiez la configuration")

if __name__ == "__main__":
    main()
