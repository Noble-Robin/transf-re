from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
import json
import os
import time

from django.contrib.auth import login as dj_login, logout as dj_logout
from django.contrib.auth.decorators import login_required, user_passes_test
from .services.user_service import UserService
from .services.moodle_api import MoodleAPI
from .services.nextcloud_api import NextcloudAPI

us = UserService()

def login_view(request):
    if request.method == 'POST':
        uname = request.POST.get('username', '').strip()
        pwd   = request.POST.get('password', '').strip()
        user_info = us.authenticate(uname, pwd)
        if not user_info:
            messages.error(request, "Identifiants invalides")
            return render(request, 'caplogy_app/login.html')
        # Récupération de l'utilisateur Django existant
        from django.contrib.auth.models import User
        try:
            django_user = User.objects.get(username=uname)
        except User.DoesNotExist:
            messages.error(request, "Utilisateur introuvable côté Django")
            return render(request, 'caplogy_app/login.html')
        # Connexion au milieu de session Django
        dj_login(request, django_user, backend='django.contrib.auth.backends.ModelBackend')
        return redirect('home')
    return render(request, 'caplogy_app/login.html')

# @login_required
def home_view(request):
    # Si l'utilisateur n'a aucun accès, afficher une page d'accueil vide/minimale
    if hasattr(request.user, 'userprofile') and request.user.userprofile.role == 'none':
        return render(request, 'caplogy_app/home_none.html')
    api = MoodleAPI(
        url=os.getenv('MOODLE_URL'),
        token=os.getenv('MOODLE_TOKEN')
    )
    return render(request, 'caplogy_app/home.html')

# @login_required
def category_view(request):
    try:
        api = MoodleAPI(
            url=os.getenv('MOODLE_URL'),
            token=os.getenv('MOODLE_TOKEN')
        )
        categories = api.get_all_categories()
        
        # Créer un dictionnaire pour faire le mapping parent-enfant plus facilement
        categories_dict = {cat['id']: cat for cat in categories}
        
        # Fonction récursive pour compter les cours dans une catégorie et ses sous-catégories
        def count_total_courses(category_id, visited=None):
            if visited is None:
                visited = set()
            
            # Éviter les cycles infinis
            if category_id in visited:
                return 0
            visited.add(category_id)
            
            category = categories_dict.get(category_id)
            if not category:
                return 0
            
            # Commencer par les cours de cette catégorie
            total_courses = category.get('coursecount', 0)
            
            # Ajouter les cours de toutes les sous-catégories
            for cat in categories:
                if cat.get('parent') == category_id:
                    total_courses += count_total_courses(cat['id'], visited.copy())
            
            return total_courses
        
        # Enrichir les données de l'API avec nos champs personnalisés
        for category in categories:
            # Calculer le total des cours (catégorie + sous-catégories)
            total_courses = count_total_courses(category['id'])
            
            # Mettre à jour le coursecount avec le total récursif
            category['coursecount'] = total_courses
            
            # Ajouter le champ has_courses basé sur le total (au lieu de coursecount direct)
            category['has_courses'] = total_courses > 0
            
            # Vérifier s'il y a vraiment des sous-catégories
            has_subcategories = any(cat.get('parent') == category['id'] for cat in categories)
            category['has_subcategories'] = has_subcategories
        
        # Filtrer pour ne retourner que les catégories de niveau racine
        root_categories = [cat for cat in categories if cat.get('parent', 0) == 0]
        
        # Appliquer le filtre de cours si spécifié
        course_filter = request.GET.get('filter_courses')
        if course_filter == 'with_courses':
            root_categories = [cat for cat in root_categories if cat.get('has_courses', False)]
        elif course_filter == 'without_courses':
            root_categories = [cat for cat in root_categories if not cat.get('has_courses', False)]
        # Si course_filter est 'all' ou None, on garde toutes les catégories
                
    except Exception as e:
        # En cas d'erreur de connexion, utiliser des données de test
        categories = [
            {
                'id': 1,
                'name': 'Mathématiques',
                'description': 'Cours de mathématiques pour tous niveaux',
                'coursecount': 5,
                'has_courses': True,
                'has_subcategories': True
            },
            {
                'id': 2,
                'name': 'Sciences',
                'description': 'Cours de physique, chimie et biologie',
                'coursecount': 8,
                'has_courses': True,
                'has_subcategories': True
            },
            {
                'id': 3,
                'name': 'Informatique',
                'description': 'Programmation et technologies de l\'information',
                'coursecount': 12,
                'has_courses': True,
                'has_subcategories': True
            },
            {
                'id': 4,
                'name': 'Langues',
                'description': 'Cours de langues étrangères',
                'coursecount': 6,
                'has_courses': True,
                'has_subcategories': True
            },
            {
                'id': 5,
                'name': 'Arts',
                'description': 'Catégorie en préparation',
                'coursecount': 0,
                'has_courses': False,
                'has_subcategories': False
            }
        ]
        messages.warning(request, "Connexion à Moodle indisponible. Affichage des données de test.")
        root_categories = [cat for cat in categories if cat.get('parent', 0) == 0]
    return render(request, 'caplogy_app/category.html', {'categories': root_categories})

# @login_required
def subcategory_view(request, category_id):
    try:
        api = MoodleAPI(
            url=os.getenv('MOODLE_URL'),
            token=os.getenv('MOODLE_TOKEN')
        )
        
        # Récupérer toutes les catégories pour avoir une vue complète de la hiérarchie
        all_categories = api.get_all_categories()
        categories_dict = {cat['id']: cat for cat in all_categories}
        
        # Fonction récursive pour compter les cours dans une catégorie et ses sous-catégories
        def count_total_courses(category_id, visited=None):
            if visited is None:
                visited = set()
            
            # Éviter les cycles infinis
            if category_id in visited:
                return 0
            visited.add(category_id)
            
            category = categories_dict.get(category_id)
            if not category:
                return 0
            
            # Commencer par les cours de cette catégorie
            total_courses = category.get('coursecount', 0)
            
            # Ajouter les cours de toutes les sous-catégories
            for cat in all_categories:
                if cat.get('parent') == category_id:
                    total_courses += count_total_courses(cat['id'], visited.copy())
            
            return total_courses
        
        # Récupérer les sous-catégories directes
        subcategories = api.get_subcategories(category_id)
        
        # Enrichir chaque sous-catégorie avec le comptage récursif
        for subcategory in subcategories:
            # Calculer le total des cours (sous-catégorie + ses sous-sous-catégories)
            total_courses = count_total_courses(subcategory['id'])
            
            # Mettre à jour le coursecount avec le total récursif
            subcategory['coursecount'] = total_courses
            
            # Ajouter le champ has_courses basé sur le total
            subcategory['has_courses'] = total_courses > 0
            
            # Vérifier s'il y a vraiment des sous-sous-catégories
            has_subcategories = any(cat.get('parent') == subcategory['id'] for cat in all_categories)
            subcategory['has_subcategories'] = has_subcategories
        
        # Récupérer le nom de la catégorie parent et construire le chemin
        parent_name = "Catégorie"
        breadcrumb_path = []
        
        # Fonction pour trouver une catégorie par ID dans toutes les catégories
        def find_category_by_id(cat_id):
            return categories_dict.get(cat_id)
        
        # Trouver la catégorie parent
        parent_category = find_category_by_id(int(category_id))
        if parent_category:
            parent_name = parent_category.get('name', 'Catégorie')
            
            # Construire le chemin de navigation (breadcrumb) en remontant la hiérarchie
            def build_breadcrumb(cat_id, path=[]):
                category = find_category_by_id(cat_id)
                if category:
                    path.insert(0, {'name': category.get('name', 'Catégorie'), 'id': cat_id})
                    parent_id = category.get('parent')
                    if parent_id and parent_id != 0:
                        build_breadcrumb(parent_id, path)
                return path
            
            breadcrumb_path = build_breadcrumb(int(category_id))
                
    except Exception as e:
        # En cas d'erreur de connexion à l'API Moodle
        subcategories = []
        parent_name = "Catégorie"
        breadcrumb_path = []
        messages.error(request, f"Erreur de connexion à Moodle: {str(e)}")
    
    return render(request, 'caplogy_app/subcategory.html', {
        'subcategories': subcategories,
        'parent_name': parent_name,
        'parent_id': category_id,
        'breadcrumb_path': breadcrumb_path
    })

# @login_required
def category_courses_view(request, category_id):
    """Vue pour afficher les cours d'une catégorie spécifique et de ses sous-catégories"""
    try:
        api = MoodleAPI(
            url=os.getenv('MOODLE_URL'),
            token=os.getenv('MOODLE_TOKEN')
        )
        
        # Récupérer toutes les catégories pour identifier les sous-catégories
        all_categories = api.get_all_categories()
        categories_dict = {cat['id']: cat for cat in all_categories}
        
        # Fonction récursive pour collecter tous les IDs de catégories (catégorie + sous-catégories)
        def get_all_category_ids(category_id, visited=None):
            if visited is None:
                visited = set()
            
            # Éviter les cycles infinis
            if category_id in visited:
                return []
            visited.add(category_id)
            
            category_ids = [category_id]
            
            # Ajouter toutes les sous-catégories
            for cat in all_categories:
                if cat.get('parent') == category_id:
                    category_ids.extend(get_all_category_ids(cat['id'], visited.copy()))
            
            return category_ids
        
        # Obtenir tous les IDs de catégories (principale + sous-catégories)
        target_category_ids = get_all_category_ids(int(category_id))
        
        # Récupérer les cours de toutes ces catégories
        all_courses = []
        for cat_id in target_category_ids:
            try:
                category_courses = api.get_courses_by_category(cat_id)
                if category_courses:
                    # Ajouter l'information de la catégorie source à chaque cours
                    for course in category_courses:
                        course['source_category_id'] = cat_id
                        if cat_id in categories_dict:
                            course['source_category_name'] = categories_dict[cat_id].get('name', f'Catégorie {cat_id}')
                        else:
                            course['source_category_name'] = f'Catégorie {cat_id}'
                    all_courses.extend(category_courses)
            except Exception as course_error:
                print(f"Erreur lors de la récupération des cours de la catégorie {cat_id}: {course_error}")
                continue
        
        courses = all_courses
        
        # Récupérer les informations de la catégorie et construire le breadcrumb
        breadcrumb_path = []
        try:
            all_categories = api.get_all_categories()
            
            # Fonction pour trouver une catégorie par ID dans toutes les catégories
            def find_category_by_id(cat_id):
                for cat in all_categories:
                    if cat.get('id') == cat_id:
                        return cat
                return None
            
            # Trouver la catégorie actuelle
            current_category = find_category_by_id(int(category_id))
            if current_category:
                category_name = current_category.get('name', 'Catégorie')
                
                # Construire le chemin de navigation (breadcrumb) en remontant la hiérarchie
                def build_breadcrumb(cat_id, path=[]):
                    category = find_category_by_id(cat_id)
                    if category:
                        path.insert(0, {'name': category.get('name', 'Catégorie'), 'id': cat_id})
                        parent_id = category.get('parent')
                        if parent_id and parent_id != 0:
                            build_breadcrumb(parent_id, path)
                    return path
                
                breadcrumb_path = build_breadcrumb(int(category_id))
            else:
                category_name = f'Catégorie {category_id}'
                
        except Exception as cat_error:
            print(f"Erreur lors de la récupération du nom de catégorie: {cat_error}")
            # Utiliser des noms de catégories par défaut basés sur l'ID
            category_names = {
                1: 'Mathématiques',
                2: 'Sciences', 
                3: 'Informatique',
                4: 'Langues',
                5: 'Arts'
            }
            category_name = category_names.get(int(category_id), f'Catégorie {category_id}')
            breadcrumb_path = [{'name': category_name, 'id': int(category_id)}]
        
        if not courses:
            messages.warning(request, "Aucun cours trouvé dans cette catégorie.")
            
    except Exception as e:
        print(f"Erreur dans category_courses_view: {e}")
        messages.error(request, f"Erreur de connexion à Moodle: {str(e)}")
        courses = []
    
    return render(request, 'caplogy_app/category_courses.html', {
        'courses': courses,
        'category_name': category_name,
        'category_id': category_id,
        'breadcrumb_path': breadcrumb_path
    })

def is_admin(user):
    if hasattr(user, 'userprofile'):
        return user.userprofile.role == 'admin'
    return False

# @login_required
@user_passes_test(is_admin)
def admin_view(request):
    from django.contrib.auth.models import User
    user_service = UserService()
    ldap_profs = user_service.get_ldap_profs()
    users = []
    # Inclure tous les utilisateurs Django
    for user in User.objects.all():
        profile = getattr(user, 'userprofile', None)
        role = profile.role if profile else 'none'
        users.append({
            'id': user.id,
            'username': user.username,
            'role': role,
            'is_ldap_prof': any(user.username == prof['username'] for prof in ldap_profs)
        })
    # Inclure les profs LDAP qui n'ont pas encore de compte Django
    for prof in ldap_profs:
        if not any(u['username'] == prof['username'] for u in users):
            users.append({
                'id': None,
                'username': prof['username'],
                'role': 'none',
                'is_ldap_prof': True,
                'name': prof['name'],
                'mail': prof['mail']
            })
    # Gestion du changement de rôle
    if request.method == 'POST' and 'change_role' in request.POST:
        user_id = request.POST.get('user_id')
        new_role = request.POST.get('new_role')
        username = request.POST.get('username')
        try:
            if user_id:
                user = User.objects.get(id=user_id)
            else:
                # Créer le compte Django si inexistant
                user, _ = User.objects.get_or_create(username=username)
            profile = getattr(user, 'userprofile', None)
            if not profile:
                from .models import UserProfile
                profile = UserProfile.objects.create(user=user, role=new_role)
            else:
                if new_role in ['admin', 'user', 'none']:
                    profile.role = new_role
                    profile.save()
            messages.success(request, f"Rôle de {username} mis à jour en '{new_role}'")
        except Exception as e:
            messages.error(request, f"Erreur lors du changement de rôle: {str(e)}")
        return redirect('admin_page')
    return render(request, 'caplogy_app/admin.html', {'users': users, 'ldap_profs': ldap_profs})

def add_category_view(request):
    if request.method == 'POST':
        try:
            # Lecture des données JSON
            data = json.loads(request.body)

            name = data.get('name')
            if not name:
                return JsonResponse({'success': False, 'error': 'Le paramètre name est manquant'})

            parent_id = data.get('parent_id', 0)

            api = MoodleAPI(
                url=os.getenv('MOODLE_URL'),
                token=os.getenv('MOODLE_TOKEN')
            )
            new_id = api.create_category(name, parent_id)
            if new_id:
                return JsonResponse({'success': True, 'id': new_id})
            else:
                return JsonResponse({'success': False, 'error': 'Failed to create category'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

def delete_category_view(request):
    if request.method == 'POST':
        # Essayer de récupérer l'ID depuis POST ou JSON
        category_id = request.POST.get('category_id')
        if not category_id:
            try:
                data = json.loads(request.body)
                category_id = data.get('category_id')
            except Exception:
                category_id = None
        try:
            if not category_id:
                return JsonResponse({'success': False, 'error': 'Le paramètre category_id est obligatoire'})
            api = MoodleAPI(
                url=os.getenv('MOODLE_URL'),
                token=os.getenv('MOODLE_TOKEN')
            )
            api.delete_category(category_id)
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Méthode non autorisée'})

# @login_required
def promote_to_admin(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_id = data.get('id')
            
            from django.contrib.auth.models import User
            user = User.objects.get(id=user_id)
            user.is_staff = True
            user.is_superuser = True
            user.save()
            
            return JsonResponse({'success': True})
        except User.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Utilisateur introuvable'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Méthode non autorisée'})

def courses(request):
    try:
        api = MoodleAPI(
                url=os.getenv('MOODLE_URL'),
                token=os.getenv('MOODLE_TOKEN')
            )
        
        selected_school = request.GET.get('school') or None

        raw = api.get_courses()
        raw = [c for c in raw if c.get('id') != 1]

        all_cats = api.get_all_categories()
        cat_map = {c['id']: c for c in all_cats}
        
        def find_root(cat_id):
            if not cat_id or cat_id not in cat_map:
                return cat_id
            parent = cat_map.get(cat_id, {}).get('parent')
            return cat_id if not parent or parent == 0 else find_root(parent)

        enriched = []
        for c in raw:
            try:
                cat_id = c.get('categoryid')
                if not cat_id:
                    continue
                    
                rid = find_root(cat_id)
                c['root_id'] = rid
                c['schoolname'] = cat_map.get(rid, {}).get('name', '—')
                enriched.append(c)
            except Exception as e:
                print(f"Erreur lors du traitement du cours {c.get('id', 'inconnu')}: {e}")
                continue

        if selected_school:
            enriched = [c for c in enriched if str(c.get('root_id', '')) == selected_school]

        schools = [c for c in all_cats if c.get('parent') == 0]

        return render(request, 'caplogy_app/courses.html', {
            'courses': enriched,
            'schools': schools,
            'selected_school': str(selected_school or ''),
        })
    except Exception as e:
        print(f"Erreur dans courses: {e}")
        messages.error(request, f"Erreur lors de la récupération des cours: {str(e)}")
        return render(request, 'caplogy_app/courses.html', {
            'courses': [],
            'schools': [],
            'selected_school': '',
        })

def courses_api(request):
    try:
        api = MoodleAPI(
                url=os.getenv('MOODLE_URL'),
                token=os.getenv('MOODLE_TOKEN')
            )
        
        school    = request.GET.get('school')
        year      = request.GET.get('year')
        formation = request.GET.get('formation')
        raw = [c for c in api.get_courses() if c.get('id') != 1]
        all_cats = api.get_all_categories()
        cat_map = {c['id']: c for c in all_cats}

        def find_root(cid):
            if cid not in cat_map:
                return cid  # Retourner l'ID original si non trouvé
            parent = cat_map[cid].get('parent', 0)
            return cid if parent == 0 else find_root(parent)

        def find_year(cid, root):
            if cid not in cat_map:
                return cid  # Retourner l'ID original si non trouvé
            parent = cat_map[cid].get('parent', 0)
            return cid if parent == root else find_year(parent, root)

        def find_formation(cid, year_id):
            if cid not in cat_map:
                return cid  # Retourner l'ID original si non trouvé
            parent = cat_map[cid].get('parent', 0)
            return cid if parent == year_id else find_formation(parent, year_id)

        data = []
        for c in raw:
            try:
                cid          = c.get('categoryid')
                if not cid:
                    continue  # Ignorer les cours sans catégorie
                    
                root_id      = find_root(cid)
                year_id      = find_year(cid, root_id)
                formation_id = find_formation(cid, year_id)
                
                if school and str(root_id) != school:
                    continue
                if year and str(year_id) != year:
                    continue
                if formation and str(formation_id) != formation:
                    continue
                    
                data.append({
                    'id':            c['id'],
                    'fullname':      c['fullname'],
                    'schoolname':    cat_map.get(root_id, {}).get('name', 'Catégorie inconnue'),
                    'yearname':      cat_map.get(year_id, {}).get('name', 'Année inconnue'),
                    'formationname': cat_map.get(formation_id, {}).get('name', 'Formation inconnue'),
                })
            except Exception as e:
                # Ignorer les cours qui causent des erreurs
                print(f"Erreur lors du traitement du cours {c.get('id', 'inconnu')}: {e}")
                continue
                
        return JsonResponse({'courses': data})
    except Exception as e:
        print(f"Erreur dans courses_api: {e}")
        return JsonResponse({'error': f'Erreur lors de la récupération des cours: {str(e)}'}, status=500)

def create_course(request, course_id=None):
    """Vue pour créer ou éditer un cours"""
    api = MoodleAPI(
            url=os.getenv('MOODLE_URL'),
            token=os.getenv('MOODLE_TOKEN')
        )
    
    # Déterminer si on est en mode édition
    is_edit = course_id is not None
    course_data = None
    
    if is_edit:
        try:
            # Récupérer les données complètes du cours pour l'édition
            course_data = api.get_course_with_sections(course_id)
            if not course_data:
                messages.error(request, "Cours introuvable")
                return redirect('courses')
        except Exception as e:
            messages.error(request, f"Erreur lors de la récupération du cours: {str(e)}")
            return redirect('courses')
    
    if request.method == 'POST':
        title = request.POST['title']
        cat_id = (request.POST.get('subsubcategory') or 
                  request.POST.get('subcategory') or 
                  request.POST.get('category'))
        selected_profs = request.POST.getlist('profs')
        
        if not cat_id:
            messages.error(request, "Veuillez sélectionner une catégorie")
            top_cats = api.get_categories(0)
            context = {
                'categories': top_cats,
                'is_edit': is_edit,
                'course': course_data
            }
            return render(request, 'caplogy_app/create_course.html', context)
        
        try:
            if is_edit:
                # Mettre à jour le cours existant
                api.update_course(course_id, title, cat_id)
                # Affecter les profs sélectionnés au cours
                if selected_profs:
                    api.assign_teachers_to_course(course_id, selected_profs)
                
                # Récupérer et traiter les sections pour l'édition
                sections = [v for k,v in request.POST.items() if k.startswith('section_')]
                
                # Récupérer les fichiers/URLs associés aux sections
                files_data = {}
                for key, value in request.POST.items():
                    if key.startswith('file_') and value.strip():
                        section_num = key.replace('file_', '')
                        files_data[section_num] = value.strip()
                
                # Debug logging
                print(f"DEBUG - POST data: {dict(request.POST)}")
                print(f"DEBUG - Sections found: {sections}")
                print(f"DEBUG - Files data: {files_data}")
                
                if sections:
                    # Utiliser la méthode update_sections pour les opérations sur les sections
                    section_nums = api.update_sections(course_id, sections)
                    print(f"DEBUG - Section nums created: {section_nums}")
                    
                    # Ajouter les URLs aux sections créées
                    if files_data and section_nums:
                        print(f"DEBUG - Processing URLs for sections")
                        for i, section_num in enumerate(section_nums):
                            file_key = str(i + 1)  # Les clés de fichiers sont basées sur l'ordre dans l'interface
                            print(f"DEBUG - Looking for file_key: {file_key} in files_data: {files_data}")
                            if file_key in files_data:
                                file_path = files_data[file_key]
                                section_title = sections[i] if i < len(sections) else f"Section {i+1}"
                                print(f"DEBUG - Processing file: {file_path} for section {section_num} (title: {section_title})")
                                # Déterminer si c'est un fichier Nextcloud ou une URL externe
                                if file_path.startswith('http'):
                                    # C'est une URL externe
                                    try:
                                        print(f"DEBUG - Adding URL: {file_path}")
                                        result = api.add_url(course_id, section_num, f"Lien - {section_title}", file_path, f"Ressource pour {section_title}")
                                        print(f"DEBUG - URL add result: {result}")
                                    except Exception as url_error:
                                        print(f"Erreur lors de l'ajout de l'URL {file_path}: {url_error}")
                                else:
                                    # C'est un fichier Nextcloud - générer l'URL de partage
                                    try:
                                        print(f"DEBUG - Processing Nextcloud file: {file_path}")
                                        # Générer l'URL de partage Nextcloud
                                        nextcloud_api = NextcloudAPI(
                                            base_url=os.getenv('NEXTCLOUD_WEBDAV_URL'),
                                            share_url=os.getenv('NEXTCLOUD_SHARE_URL'),
                                            user=os.getenv('NEXTCLOUD_USER'),
                                            password=os.getenv('NEXTCLOUD_PASSWORD')
                                        )
                                        share_url = nextcloud_api.get_share_url(file_path)
                                        if share_url:
                                            print(f"DEBUG - Adding Nextcloud URL: {share_url}")
                                            result = api.add_url(course_id, section_num, f"Fichier - {section_title}", share_url, f"Fichier Nextcloud pour {section_title}")
                                            print(f"DEBUG - Nextcloud URL add result: {result}")
                                    except Exception as nc_error:
                                        print(f"Erreur lors de la création du lien Nextcloud pour {file_path}: {nc_error}")
                
                messages.success(request, f"Cours '{title}' modifié avec succès")
            else:
                # Créer un nouveau cours
                course_id = api.create_course(title, cat_id)
                if course_id:
                    # Affecter les profs sélectionnés au cours
                    if selected_profs:
                        api.assign_teachers_to_course(course_id, selected_profs)
                    
                    sections = [v for k,v in request.POST.items() if k.startswith('section_')]
                    
                    # Récupérer les fichiers/URLs associés aux sections
                    files_data = {}
                    for key, value in request.POST.items():
                        if key.startswith('file_') and value.strip():
                            section_num = key.replace('file_', '')
                            files_data[section_num] = value.strip()
                    
                    # Debug logging
                    print(f"DEBUG - POST data: {dict(request.POST)}")
                    print(f"DEBUG - Sections found: {sections}")
                    print(f"DEBUG - Files data: {files_data}")
                    
                    # Créer les sections
                    section_nums = api.create_sections(course_id, sections)
                    print(f"DEBUG - Section nums created: {section_nums}")
                    
                    # Ajouter les URLs aux sections créées
                    if files_data and section_nums:
                        print(f"DEBUG - Processing URLs for sections")
                        # Itérer sur les sections dans l'ordre de création (interface utilisateur)
                        for i, section_num in enumerate(section_nums):
                            # Les clés de fichiers correspondent à l'ordre dans l'interface (1-based)
                            file_key = str(i + 1)
                            print(f"DEBUG - Section {i+1} (Moodle section {section_num}): looking for file_key: {file_key} in files_data: {files_data}")
                            if file_key in files_data:
                                file_path = files_data[file_key]
                                section_title = sections[i] if i < len(sections) else f"Section {i+1}"
                                print(f"DEBUG - Processing file: {file_path} for section {section_num} (title: {section_title})")
                                # Déterminer si c'est un fichier Nextcloud ou une URL externe
                                if file_path.startswith('http'):
                                    # C'est une URL externe
                                    try:
                                        print(f"DEBUG - Adding URL: {file_path}")
                                        result = api.add_url(course_id, section_num, f"Lien - {section_title}", file_path, f"Ressource pour {section_title}")
                                        print(f"DEBUG - URL add result: {result}")
                                    except Exception as url_error:
                                        print(f"Erreur lors de l'ajout de l'URL {file_path}: {url_error}")
                                else:
                                    # C'est un fichier Nextcloud - générer l'URL de partage
                                    try:
                                        print(f"DEBUG - Processing Nextcloud file: {file_path}")
                                        # Générer l'URL de partage Nextcloud
                                        nextcloud_api = NextcloudAPI(
                                            base_url=os.getenv('NEXTCLOUD_WEBDAV_URL'),
                                            share_url=os.getenv('NEXTCLOUD_SHARE_URL'),
                                            user=os.getenv('NEXTCLOUD_USER'),
                                            password=os.getenv('NEXTCLOUD_PASSWORD')
                                        )
                                        share_url = nextcloud_api.get_share_url(file_path)
                                        if share_url:
                                            print(f"DEBUG - Adding Nextcloud URL: {share_url}")
                                            result = api.add_url(course_id, section_num, f"Fichier - {section_title}", share_url, f"Fichier Nextcloud pour {section_title}")
                                            print(f"DEBUG - Nextcloud URL add result: {result}")
                                    except Exception as nc_error:
                                        print(f"Erreur lors de la création du lien Nextcloud pour {file_path}: {nc_error}")
                    
                    messages.success(request, f"Cours '{title}' créé avec succès")
                else:
                    messages.error(request, "Erreur lors de la création du cours")
                    
        except Exception as e:
            action = "modification" if is_edit else "création"
            messages.error(request, f"Erreur lors de la {action} du cours: {str(e)}")
            
        return redirect('courses')

    # Préparer le contexte pour le template
    top_cats = api.get_categories(0)
    user_service = UserService()
    profs = user_service.get_ldap_profs()
    # Pour le mode édition, construire le chemin de présélection rapide
    preselection_data = None
    
    if is_edit and course_data and course_data.get('categoryid'):
        category_id = course_data['categoryid']
        print(f"Mode édition: construction du chemin pour categoryid={category_id}")
        
        try:
            start_time = time.time()
            
            # Utiliser get_all_categories() pour récupérer toutes les catégories rapidement
            all_cats = api.get_all_categories()
            cat_map = {c['id']: c for c in all_cats}
            
            print(f"Récupéré {len(all_cats)} catégories en {time.time() - start_time:.3f}s")
            
            if category_id in cat_map:
                # Fonction pour remonter la hiérarchie : formation → année → école
                def build_category_path(target_id):
                    path = []
                    current_id = target_id
                    
                    while current_id and current_id in cat_map:
                        category = cat_map[current_id]
                        path.append({
                            'id': current_id,
                            'name': category.get('name', ''),
                            'parent': category.get('parent', 0)
                        })
                        
                        parent_id = category.get('parent', 0)
                        if parent_id == 0:
                            break
                        current_id = parent_id
                    
                    # Inverser pour avoir école → année → formation
                    return list(reversed(path))
                
                category_path = build_category_path(category_id)
                print(f"Chemin trouvé: {[f'{cat['name']} (ID: {cat['id']})' for cat in category_path]}")
                
                # Construire les données de présélection
                preselection_data = {
                    'target_category_id': category_id,
                    'path': category_path
                }
                
                # Ajouter les catégories nécessaires pour peupler les selects
                if len(category_path) >= 1:
                    # École sélectionnée - récupérer toutes les années
                    school_id = category_path[0]['id']
                    years = [c for c in all_cats if c.get('parent', 0) == school_id]
                    preselection_data['years'] = years
                    
                    if len(category_path) >= 2:
                        # Année sélectionnée - récupérer toutes les formations
                        year_id = category_path[1]['id']
                        formations = [c for c in all_cats if c.get('parent', 0) == year_id]
                        preselection_data['formations'] = formations
                
                end_time = time.time()
                print(f"Données de présélection construites en {end_time - start_time:.3f}s")
                print(f"École: {category_path[0]['name'] if category_path else 'N/A'}")
                print(f"Année: {category_path[1]['name'] if len(category_path) > 1 else 'N/A'}")
                print(f"Formation: {category_path[2]['name'] if len(category_path) > 2 else 'N/A'}")
                
        except Exception as e:
            print(f"Erreur lors de la construction du chemin: {e}")
            import traceback
            traceback.print_exc()
            preselection_data = None
    
    context = {
        'categories': top_cats,
        'is_edit': is_edit,
        'course': course_data,
        'preselection_data': json.dumps(preselection_data) if preselection_data else None,
        'profs': profs
    }
    return render(request, 'caplogy_app/create_course.html', context)

# @login_required
def delete_course(request, course_id):
    """Vue pour supprimer un cours"""
    if request.method != 'GET':
        messages.error(request, "Méthode non autorisée")
        return redirect('courses')
    
    api = MoodleAPI(
        url=os.getenv('MOODLE_URL'),
        token=os.getenv('MOODLE_TOKEN')
    )
    
    try:
        # Obtenir d'abord les informations du cours pour afficher un message plus informatif
        courses = api.get_courses()
        course_to_delete = next((c for c in courses if c.get('id') == course_id), None)
        
        if not course_to_delete:
            messages.error(request, "Cours introuvable")
            return redirect('courses')
        
        # Supprimer le cours via l'API Moodle
        api.delete_course(course_id)
        messages.success(request, f"Cours '{course_to_delete.get('fullname', 'Sans nom')}' supprimé avec succès")
        
    except Exception as e:
        messages.error(request, f"Erreur lors de la suppression du cours: {str(e)}")
    
    return redirect('courses')


def list_nc_dir(request):
    try:
        path = request.GET.get('path', '/')
        print(f"[DEBUG] list_nc_dir appelé avec path: {path}")
        
        # Vérification des variables d'environnement
        nc_webdav = os.getenv('NEXTCLOUD_WEBDAV_URL')
        nc_share = os.getenv('NEXTCLOUD_SHARE_URL')
        nc_user = os.getenv('NEXTCLOUD_USER')
        nc_password = os.getenv('NEXTCLOUD_PASSWORD')
        
        print(f"[DEBUG] Variables d'environnement:")
        print(f"  NEXTCLOUD_WEBDAV_URL: {nc_webdav}")
        print(f"  NEXTCLOUD_SHARE_URL: {nc_share}")
        print(f"  NEXTCLOUD_USER: {nc_user}")
        print(f"  NEXTCLOUD_PASSWORD: {'***' if nc_password else None}")
        
        if not all([nc_webdav, nc_share, nc_user, nc_password]):
            missing = []
            if not nc_webdav: missing.append('NEXTCLOUD_WEBDAV_URL')
            if not nc_share: missing.append('NEXTCLOUD_SHARE_URL')
            if not nc_user: missing.append('NEXTCLOUD_USER')
            if not nc_password: missing.append('NEXTCLOUD_PASSWORD')
            
            error_msg = f'Configuration Nextcloud manquante. Variables manquantes: {", ".join(missing)}'
            print(f"[ERROR] {error_msg}")
            return JsonResponse({'error': error_msg}, status=500)
        
        # Créer une instance de NextcloudAPI
        print(f"[DEBUG] Création de l'instance NextcloudAPI...")
        nc_api = NextcloudAPI(
            base_url=nc_webdav,
            share_url=nc_share,
            user=nc_user,
            password=nc_password
        )
        
        print(f"[DEBUG] Appel de nc_api.list_nc_dir('{path}')...")
        folders, files = nc_api.list_nc_dir(path)
        print(f"[DEBUG] Résultat: {len(folders)} dossiers, {len(files)} fichiers")
        
        return JsonResponse({'folders': folders, 'files': files})
    except Exception as e:
        error_msg = f'Erreur lors de la lecture du répertoire: {str(e)}'
        print(f"[ERROR] {error_msg}")
        import traceback
        print(f"[ERROR] Traceback: {traceback.format_exc()}")
        return JsonResponse({'error': error_msg}, status=500)

def categories_api(request):
    try:
        # Vérification des variables d'environnement
        moodle_url = os.getenv('MOODLE_URL')
        moodle_token = os.getenv('MOODLE_TOKEN')
        
        if not moodle_url or not moodle_token:
            return JsonResponse({'error': 'Configuration Moodle manquante. Veuillez configurer les variables d\'environnement MOODLE_URL et MOODLE_TOKEN.'}, status=500)
        
        api = MoodleAPI(url=moodle_url, token=moodle_token)
        
        parent_id = request.GET.get('parent')
        if parent_id:
            try:
                parent_id = int(parent_id)
                categories = api.get_categories(parent_id)
            except (ValueError, TypeError):
                return JsonResponse({'error': 'Invalid parent ID'}, status=400)
        else:
            categories = api.get_categories(0)
        
        formatted_categories = []
        for cat in categories:
            formatted_categories.append({
                'id': cat['id'],
                'name': cat['name'],
                'parent': cat.get('parent', 0)
            })
        
        return JsonResponse({'categories': formatted_categories})
    except Exception as e:
        return JsonResponse({'error': f'Erreur lors de la récupération des catégories: {str(e)}'}, status=500)

def build_category_hierarchy_for_course(api, target_category_id):
    """
    Construit rapidement la hiérarchie des catégories et le chemin de sélection
    en utilisant get_all_categories() comme les autres vues (courses_api, etc.)
    """
    try:
        start_time = time.time()
        print(f"[FAST] Building hierarchy for category {target_category_id} using get_all_categories()")
        
        # 1. Récupérer TOUTES les catégories d'un coup (comme courses_api)
        all_cats = api.get_all_categories()
        cat_map = {c['id']: c for c in all_cats}
        
        end_time = time.time()
        print(f"[FAST] Retrieved {len(all_cats)} categories in {end_time - start_time:.3f} seconds")
        
        if target_category_id not in cat_map:
            print(f"[FAST] Category {target_category_id} not found in category map")
            return None, None
        
        # 2. Trouver le chemin vers la catégorie cible (même logique que courses_api)
        def find_path_to_root(cat_id):
            """Trouve le chemin de la catégorie vers la racine"""
            path = []
            current_id = cat_id
            
            while current_id and current_id in cat_map:
                path.append(current_id)
                parent_id = cat_map[current_id].get('parent', 0)
                if parent_id == 0:
                    break
                current_id = parent_id
            
            return list(reversed(path))  # Inverser pour avoir racine->feuille
        
        selection_path = find_path_to_root(target_category_id)
        print(f"[FAST] Found selection path: {selection_path}")
        
        # 3. Organiser les catégories par niveaux pour l'interface
        hierarchy = {
            'main': [c for c in all_cats if c.get('parent', 0) == 0],  # Écoles
            'sub': {},
            'subsub': {}
        }
        
        # Pré-charger les sous-catégories pour le chemin de sélection
        if len(selection_path) >= 1:
            # Charger les années pour l'école sélectionnée
            school_id = selection_path[0]
            hierarchy['sub'][school_id] = [c for c in all_cats if c.get('parent', 0) == school_id]
            
            if len(selection_path) >= 2:
                # Charger les formations pour l'année sélectionnée
                year_id = selection_path[1]
                hierarchy['subsub'][year_id] = [c for c in all_cats if c.get('parent', 0) == year_id]
        
        total_time = time.time() - start_time
        print(f"[FAST] Total hierarchy building time: {total_time:.3f} seconds")
        
        return hierarchy, selection_path
        
    except Exception as e:
        print(f"[FAST] Error in build_category_hierarchy_for_course: {e}")
        import traceback
        traceback.print_exc()
        return None, None