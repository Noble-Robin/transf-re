"""
Vue d'administration pour tester la connexion LDAP
"""
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages
from .services.user_service import UserService
import json

try:
    from .services.ldap_manager import LDAPManager
except ImportError:
    LDAPManager = None

@login_required
def ldap_test_view(request):
    """
    Vue pour tester la connexion LDAP
    """
    if request.method == 'POST':
        test_type = request.POST.get('test_type')
        
        if test_type == 'connection':
            return test_ldap_connection()
        elif test_type == 'auth':
            username = request.POST.get('username')
            password = request.POST.get('password')
            return test_user_authentication(username, password)
        elif test_type == 'users':
            return test_get_users()
        elif test_type == 'service':
            return test_user_service()
    
    return render(request, 'caplogy_app/ldap_test.html')

def test_ldap_connection():
    """Test de connexion LDAP"""
    try:
        if LDAPManager is None:
            return JsonResponse({
                'success': False,
                'message': 'LDAPManager non disponible'
            })
            
        ldap_manager = LDAPManager()
        result = ldap_manager.test_connection()
        
        if result['success']:
            return JsonResponse({
                'success': True,
                'message': 'Connexion LDAP réussie',
                'server_info': result['server_info']
            })
        else:
            return JsonResponse({
                'success': False,
                'message': f"Erreur de connexion: {result['error']}"
            })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f"Erreur: {str(e)}"
        })

def test_user_authentication(username, password):
    """Test d'authentification utilisateur"""
    try:
        if LDAPManager is None:
            return JsonResponse({
                'success': False,
                'message': 'LDAPManager non disponible'
            })
            
        ldap_manager = LDAPManager()
        result = ldap_manager.authenticate_user(username, password)
        
        if result['success']:
            return JsonResponse({
                'success': True,
                'message': 'Authentification réussie',
                'user_info': result['user_info']
            })
        else:
            return JsonResponse({
                'success': False,
                'message': f"Échec de l'authentification: {result['error']}"
            })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f"Erreur: {str(e)}"
        })

def test_get_users():
    """Test de récupération des utilisateurs"""
    try:
        user_service = UserService()
        profs = user_service.get_ldap_profs()
        
        return JsonResponse({
            'success': True,
            'message': f'{len(profs)} professeurs trouvés',
            'users': profs[:10]  # Limiter à 10 pour l'affichage
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f"Erreur: {str(e)}"
        })

def test_user_service():
    """Test du service utilisateur complet"""
    try:
        user_service = UserService()
        profs = user_service.get_ldap_profs()
        
        return JsonResponse({
            'success': True,
            'message': f'Service utilisateur OK - {len(profs)} professeurs',
            'count': len(profs),
            'sample': profs[:5]  # Échantillon de 5 utilisateurs
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f"Erreur: {str(e)}"
        })
