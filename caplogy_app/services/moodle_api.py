import requests
import urllib3

# Désactiver les avertissements SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class MoodleAPI:
    def get_course_teachers(self, course_id):
        """
        Récupère la liste des enseignants (roleid=3) inscrits à un cours Moodle.
        Nécessite que le service web core_enrol_get_enrolled_users soit activé côté Moodle.
        Retourne une liste de dicts utilisateurs (id, username, firstname, lastname, email...)
        """
        try:
            params = {'courseid': course_id}
            users = self._request('core_enrol_get_enrolled_users', params)
            if not isinstance(users, list):
                return []
            teachers = []
            for user in users:
                # Vérifier les rôles attribués à l'utilisateur dans ce cours
                roles = user.get('roles', [])
                for role in roles:
                    if role.get('roleid') == 3:  # 3 = enseignant
                        teachers.append(user)
                        break
            return teachers
        except Exception as e:
            print(f"Erreur lors de la récupération des enseignants du cours {course_id}: {e}")
            return []
    def __init__(self, url: str, token: str, fmt: str = 'json'):
        self.base = url
        self.token = token
        self.fmt = fmt

    def _request(self, function: str, params: dict):
        payload = {
            'wstoken': self.token,
            'moodlewsrestformat': self.fmt,
            'wsfunction': function,
            **params
        }
        
        # Validation des paramètres pour éviter les erreurs de paramètre invalide
        if function == 'core_course_get_contents':
            courseid = params.get('courseid')
            if not courseid or not str(courseid).isdigit():
                raise ValueError(f"courseid invalide pour {function}: {courseid}")
        
        try:
            r = requests.post(self.base, data=payload, verify=False)
            r.raise_for_status()
            response_data = r.json()
            
            # Vérifier si la réponse contient une erreur Moodle
            if isinstance(response_data, dict):
                if 'exception' in response_data or 'errorcode' in response_data:
                    error_code = response_data.get('errorcode', 'Erreur inconnue')
                    error_message = response_data.get('message', 'Pas de message d\'erreur')
                    
                    # Pour certaines erreurs spécifiques, lever une exception personnalisée
                    if 'invalidparameter' in error_code.lower() or 'parameter' in error_message.lower():
                        raise ValueError(f"Paramètre invalide pour {function}: {error_message}")
                    
                    # Retourner l'erreur telle quelle pour que les appelants puissent la gérer
                    return response_data
            
            return response_data
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"Erreur réseau: {e}")
        except ValueError as e:
            raise e
        except Exception as e:
            raise Exception(f"Erreur API: {e}")

    def get_categories(self, parent_id: int = 0):
        try:
            params = {
                'criteria[0][key]': 'parent',
                'criteria[0][value]': str(parent_id),
                'addsubcategories': 0
            }
            result = self._request('core_course_get_categories', params)
            
            if not isinstance(result, list):
                raise Exception("Format de réponse inattendu de l'API Moodle")
                
            return result
        except Exception as e:
            raise Exception(f"Impossible de récupérer les catégories: {str(e)}")
    
    def get_all_categories(self):
        try:
            result = self._request('core_course_get_categories', {})
            
            if not isinstance(result, list):
                raise Exception("Format de réponse inattendu de l'API Moodle")
                
            return result
        except Exception as e:
            raise Exception(f"Impossible de récupérer les catégories: {str(e)}")
    
    def get_subcategories(self, parent_id: int):
        """Récupère les sous-catégories d'une catégorie parent"""
        try:
            if parent_id is None:
                raise ValueError("Le paramètre parent_id est obligatoire")
                
            params = {
                'criteria[0][key]': 'parent',
                'criteria[0][value]': str(parent_id),
                'addsubcategories': 0
            }
            result = self._request('core_course_get_categories', params)
            
            if not isinstance(result, list):
                raise Exception("Format de réponse inattendu de l'API Moodle")
                
            return result
        except Exception as e:
            raise Exception(f"Impossible de récupérer les sous-catégories: {str(e)}")

    def create_category(self, name: str, parent_id: int):
        try:
            if not name:
                raise ValueError("Le paramètre name est obligatoire")
            if parent_id is None:
                raise ValueError("Le paramètre parent_id est obligatoire")
                
            params = {
                'categories[0][name]': name,
                'categories[0][parent]': parent_id,
                'wstoken': self.token,
                'wsfunction': 'core_course_create_categories',
                'moodlewsrestformat': self.fmt
            }
            
            response = requests.post(self.base, data=params, verify=False)
            response.raise_for_status()
            data = response.json()
            
            if isinstance(data, list) and data and 'id' in data[0]:
                return data[0]['id']
            else:
                raise Exception("Impossible de créer la catégorie, réponse API invalide")
                
        except requests.exceptions.RequestException as e:
            raise Exception(f"Erreur de requête lors de la création de la catégorie: {str(e)}")
        except Exception as e:
            raise Exception(f"Impossible de créer la catégorie: {str(e)}")

    def delete_category(self, category_id: int):
        """Supprime une catégorie Moodle."""
        try:
            if not category_id:
                raise ValueError("Le paramètre category_id est obligatoire")
                
            params = {
                'wstoken': self.token,
                'wsfunction': 'core_course_delete_categories',
                'moodlewsrestformat': 'json',
                'categories[0][id]': category_id,
                'categories[0][recursive]': 1
            }
            response = requests.post(self.base, params=params, verify=False)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            raise Exception(f"Impossible de supprimer la catégorie: {str(e)}")

    def get_courses(self):
        try:
            result = self._request('core_course_get_courses', {})
            
            # Vérifier si la réponse est une erreur d'accès
            if isinstance(result, dict) and 'exception' in result:
                raise Exception(f"Accès refusé à l'API Moodle: {result.get('message', 'Accès non autorisé')}")
            
            # Vérifier si c'est bien une liste
            if not isinstance(result, list):
                raise Exception("Format de réponse inattendu")
                
            return result
        except Exception as e:
            raise e

    def get_courses_by_category(self, category_id):
        """Récupère tous les cours d'une catégorie spécifique"""
        try:
            # Essayer d'abord avec core_course_get_courses_by_field
            params = {
                'field': 'category',
                'value': str(category_id)
            }
            result = self._request('core_course_get_courses_by_field', params)
            
            if isinstance(result, dict) and 'courses' in result:
                return result['courses']
            elif isinstance(result, dict) and 'exception' in result:
                # Fallback vers get_courses et filtrage
                return self._get_courses_by_category_fallback(category_id)
            else:
                return []
            
        except Exception as e:
            return []
    
    def _get_courses_by_category_fallback(self, category_id):
        """Méthode de fallback pour récupérer les cours d'une catégorie"""
        try:
            result = self._request('core_course_get_courses', {})
            
            # Vérifier si la réponse est une erreur d'accès
            if isinstance(result, dict) and 'exception' in result:
                raise Exception(f"Accès refusé à l'API Moodle: {result.get('message', 'Accès non autorisé')}")
            
            # Vérifier si c'est bien une liste
            if not isinstance(result, list):
                raise Exception("Format de réponse inattendu de l'API Moodle")
            
            # Filtrer les cours par categoryid
            category_courses = []
            for course in result:
                if isinstance(course, dict) and course.get('categoryid') == category_id:
                    category_courses.append(course)
            
            return category_courses
                
        except Exception as e:
            raise Exception(f"Impossible de récupérer les cours de la catégorie {category_id}: {str(e)}")

    def get_course(self, course_id):
        """Récupère un cours spécifique par son ID."""
        try:
            params = {
                'options[ids][0]': course_id,
            }
            data = self._request('core_course_get_courses_by_field', params)
            
            if isinstance(data, dict) and data.get('courses'):
                return data['courses'][0]
            else:
                raise Exception(f"Cours avec l'ID {course_id} non trouvé")
                
        except Exception as e:
            raise Exception(f"Impossible de récupérer le cours {course_id}: {str(e)}")

    def update_course(self, course_id, name, category_id):
        """Met à jour un cours existant."""
        try:
            if not name or not course_id or not category_id:
                raise ValueError("Les paramètres course_id, name et category_id sont obligatoires")
                
            params = {
                'courses[0][id]': course_id,
                'courses[0][fullname]': name,
                'courses[0][shortname]': name[:20].replace(' ', '_'),
                'courses[0][categoryid]': category_id,
            }
            return self._request('core_course_update_courses', params)
        except Exception as e:
            raise Exception(f"Impossible de mettre à jour le cours: {str(e)}")

    def create_course(self, name, category_id):
        try:
            if not name or not category_id:
                raise ValueError("Les paramètres name et category_id sont obligatoires")
                
            params = {
                'courses[0][fullname]': name,
                'courses[0][shortname]': name[:20].replace(' ', '_'),
                'courses[0][categoryid]': category_id,
            }
            data = self._request('core_course_create_courses', params)
            
            if isinstance(data, list) and data and data[0].get('id'):
                return data[0]['id']
            else:
                raise Exception("Impossible de créer le cours, réponse API invalide")
                
        except Exception as e:
            raise Exception(f"Impossible de créer le cours: {str(e)}")

    def delete_course(self, course_id):
        """Supprime un cours Moodle."""
        try:
            if not course_id:
                raise ValueError("Le paramètre course_id est obligatoire")
                
            params = {
                'courseids[0]': course_id,
            }
            return self._request('core_course_delete_courses', params)
        except Exception as e:
            raise Exception(f"Impossible de supprimer le cours: {str(e)}")

    def create_sections(self, course_id, section_names):
        params = {'courseid': course_id}
        for i, name in enumerate(section_names):
            params[f'sections[{i}][name]'] = name
        data = self._request('local_wsmanagesections_create_sections', params)
        
        # Gérer les différents types de réponses
        if isinstance(data, list):
            return [item.get('sectionnum') if isinstance(item, dict) else None for item in data]
        elif isinstance(data, dict):
            # Si c'est un dict unique, le traiter comme un seul élément
            return [data.get('sectionnum')] if 'sectionnum' in data else []
        else:
            # Si c'est une chaîne ou autre, retourner une liste vide
            return []

    def get_course_sections(self, course_id, force_refresh=False):
        """Récupère les sections d'un cours avec leurs contenus de manière robuste."""
        
        # Essayer plusieurs méthodes en ordre de priorité
        methods = [
            lambda: self.get_sections_direct(course_id),
            lambda: self._get_sections_via_get_contents(course_id, force_refresh),
            lambda: self._get_course_sections_alternative(course_id)
        ]
        
        for method_func in methods:
            try:
                result = method_func()
                
                if isinstance(result, list) and len(result) > 0:
                    # Vérifier que les sections sont valides
                    valid_sections = []
                    for item in result:
                        if isinstance(item, dict) and 'section' in item:
                            valid_sections.append(item)
                    
                    if valid_sections:
                        return valid_sections
                    
            except Exception:
                continue
        
        # Si toutes les méthodes échouent, retourner au minimum la section générale
        return [{
            'id': 0,
            'section': 0,
            'name': 'Généralités',
            'visible': 1,
            'modules': []
        }]
    
    def _get_sections_via_get_contents(self, course_id, force_refresh=False):
        """Récupère les sections via l'API core_course_get_contents avec gestion d'erreurs améliorée."""
        params = {
            'courseid': course_id,
        }
        
        # Forcer le rafraîchissement en ajoutant un timestamp pour éviter le cache
        if force_refresh:
            import time
            params['_cache_bust'] = int(time.time() * 1000)
        
        result = self._request('core_course_get_contents', params)
        
        # Vérifier si c'est une erreur d'API
        if isinstance(result, dict):
            if 'exception' in result or 'errorcode' in result:
                error_msg = result.get('message', 'Erreur inconnue')
                raise Exception(f"Erreur API Moodle: {error_msg}")
            else:
                raise Exception("Format de réponse inattendu")
        
        # Vérifier que le résultat est une liste valide
        if not isinstance(result, list):
            raise Exception(f"Format de réponse inattendu: {type(result)}")
        
        return result
    
    def _get_course_sections_alternative(self, course_id):
        """Méthode alternative pour récupérer les sections d'un cours en utilisant l'API core_course_get_courses."""
        try:
            # Utiliser core_course_get_courses pour avoir les informations du cours
            params = {
                'options[ids][0]': course_id,
            }
            courses_data = self._request('core_course_get_courses_by_field', {'field': 'id', 'value': course_id})
            
            if courses_data and 'courses' in courses_data and courses_data['courses']:
                course = courses_data['courses'][0]
                
                # Si le cours a des informations sur les sections, les utiliser
                if 'courseformatoptions' in course:
                    # Analyser les options de format pour déterminer le nombre de sections
                    format_options = course['courseformatoptions']
                    numsections = 0
                    for option in format_options:
                        if option.get('name') == 'numsections':
                            numsections = int(option.get('value', 0))
                            break
                    
                    # Construire une liste de sections basée sur le nombre de sections
                    sections = []
                    
                    # Section générale (toujours présente)
                    sections.append({
                        'id': 0,
                        'section': 0,
                        'name': 'Généralités',
                        'visible': 1,
                        'modules': []
                    })
                    
                    # Sections supplémentaires
                    for i in range(1, numsections + 1):
                        sections.append({
                            'id': i,
                            'section': i,
                            'name': f'Section {i}',
                            'visible': 1,
                            'modules': []
                        })
                    
                    return sections
            
            # Au minimum, retourner la section générale
            return [{
                'id': 0,
                'section': 0,
                'name': 'Généralités',
                'visible': 1,
                'modules': []
            }]
                
        except Exception as e:
            # Au minimum, retourner la section générale
            return [{
                'id': 0,
                'section': 0,
                'name': 'Généralités',
                'visible': 1,
                'modules': []
            }]

    def get_course_with_sections(self, course_id):
        """Récupère un cours avec toutes ses sections et contenus."""
        try:
            # Récupérer les informations de base du cours
            courses = self.get_courses()
            course = next((c for c in courses if c.get('id') == course_id), None)
            
            if course:
                try:
                    # Essayer de récupérer les sections du cours
                    sections = self.get_course_sections(course_id)
                    course['sections'] = sections
                except Exception as e:
                    # Si on ne peut pas récupérer les sections, continuer sans elles
                    course['sections'] = []
                
            return course
        except Exception as e:
            return None

    def add_url(self, course_id, sectionnum, name, url, description=''):
        """Ajoute une URL comme ressource dans un cours Moodle en utilisant notre plugin personnalisé"""
        params = {
            'courseid': course_id,
            'sectionnum': sectionnum,
            'name': name,
            'url': url,
            'description': description,
        }
        return self._request('local_ajouturl_add_url', params)

    def get_category_details(self, category_id: int):
        """Récupère les détails d'une catégorie spécifique par son ID."""
        try:
            if not category_id:
                raise ValueError("Le paramètre category_id est obligatoire")
                
            params = {
                'criteria[0][key]': 'id',
                'criteria[0][value]': str(category_id)
            }
            categories = self._request('core_course_get_categories', params)
            
            if not isinstance(categories, list):
                raise Exception("Format de réponse inattendu de l'API Moodle")
                
            if not categories:
                raise Exception(f"Catégorie avec l'ID {category_id} non trouvée")
                
            return categories[0]
        except Exception as e:
            raise Exception(f"Impossible de récupérer la catégorie: {str(e)}")

    def delete_sections(self, course_id, section_nums, verify_deletion=True):
        """
        Supprime des sections spécifiques d'un cours en utilisant le plugin wsmanagesections.
        Avec vérification optionnelle de la suppression effective.
        """
        if not section_nums:
            return {'success': True, 'message': 'Aucune section à supprimer'}
        
        # Filtrer les sections à ne pas supprimer (section 0)
        valid_sections = [num for num in section_nums if isinstance(num, int) and num > 0]
        if not valid_sections:
            return {'success': True, 'message': 'Aucune section valide à supprimer'}
        
        try:
            # Préparer les paramètres pour l'API
            params = {
                'courseid': course_id,
            }
            for i, section_num in enumerate(valid_sections):
                params[f'sectionnums[{i}]'] = section_num
            
            # Appeler l'API de suppression
            result = self._request('local_wsmanagesections_delete_sections', params)
            
            # Vérifier si c'est une erreur
            if isinstance(result, dict) and ('exception' in result or 'errorcode' in result):
                error_msg = result.get('message', 'Erreur de suppression inconnue')
                return {'success': False, 'error': error_msg}
            
            # Vérification optionnelle que les sections ont bien été supprimées
            if verify_deletion:
                import time
                time.sleep(1)  # Attendre un peu pour que la suppression soit effective
                
                remaining_sections = self.get_course_sections(course_id, force_refresh=True)
                remaining_nums = {s.get('section', 0) for s in remaining_sections if isinstance(s, dict)}
                
                still_present = [num for num in valid_sections if num in remaining_nums]
                if still_present:
                    return {
                        'success': False, 
                        'error': f'Sections non supprimées: {still_present}',
                        'partial_success': len(still_present) < len(valid_sections)
                    }
            
            return {'success': True, 'deleted_sections': valid_sections}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def update_sections(self, course_id, section_names):
        """
        Met à jour les sections d'un cours existant en utilisant le plugin wsmanagesections.
        Compare les sections existantes avec les nouvelles et ne modifie que ce qui a changé.
        Note: La section 0 (section générale) est toujours conservée.
        """
        try:
            # Nettoyage préventif des doublons existants
            self.cleanup_duplicate_sections(course_id)
            
            # Nettoyer et filtrer les noms de sections
            cleaned_sections = []
            for name in section_names:
                name = name.strip()
                if name and name.lower() not in ['généralités', 'generalites', 'general']:
                    cleaned_sections.append(name)
            
            # Récupérer les sections existantes
            existing_sections = self.get_course_sections(course_id)
            
            # Extraire SEULEMENT les noms des sections > 0 (excluant la section générale)
            existing_section_names = []
            existing_section_nums = []
            
            for section in existing_sections:
                # Vérifier que section est bien un dictionnaire
                if not isinstance(section, dict):
                    continue
                    
                section_num = section.get('section', 0)
                if section_num > 0:  # Ignorer la section 0 (générale)
                    existing_section_names.append(section.get('name', ''))
                    existing_section_nums.append(section_num)
            
            # Si les listes sont identiques, rien à faire
            if existing_section_names == cleaned_sections:
                return existing_section_nums
            
            # Supprimer d'abord les anciennes sections, puis créer les nouvelles
            # Cela évite les conflits de numérotation avec la section générale
            
            # 1. Supprimer toutes les sections existantes (sauf la section 0)
            if existing_section_nums:
                try:
                    delete_result = self.delete_sections(course_id, existing_section_nums)
                    
                    # Vérification : attendre un peu et vérifier que les sections sont vraiment supprimées
                    import time
                    time.sleep(1)
                    
                    # Vérifier si les sections ont vraiment été supprimées
                    sections_after_delete = self.get_course_sections(course_id, force_refresh=True)
                    remaining_sections = [s for s in sections_after_delete if isinstance(s, dict) and s.get('section', 0) > 0]
                    if remaining_sections:
                        # Essayer de forcer la suppression
                        remaining_nums = [s.get('section') for s in remaining_sections if isinstance(s, dict)]
                        force_delete_result = self.delete_sections(course_id, remaining_nums)
                        time.sleep(1)
                    
                except Exception as e:
                    # Si la suppression échoue, on ne peut pas continuer proprement
                    raise e
            
            # 2. Créer les nouvelles sections
            created_sections = []
            if cleaned_sections:
                try:
                    created_sections = self.create_sections(course_id, cleaned_sections)
                    
                    # Attendre un peu pour laisser le temps à Moodle de traiter
                    import time
                    time.sleep(2)
                    
                except Exception as e:
                    raise e
            
            return created_sections
                
        except Exception as e:
            # En cas d'erreur, essayer quand même de créer les nouvelles sections (après filtrage)
            if section_names:
                cleaned = [name.strip() for name in section_names if name.strip() and name.strip().lower() not in ['généralités', 'generalites', 'general']]
                return self.create_sections(course_id, cleaned)
            else:
                return []
    
    def cleanup_duplicate_sections(self, course_id):
        """
        Nettoie les sections dupliquées dans un cours.
        Supprime les sections > 0 qui ont le même nom que la section générale.
        """
        try:
            sections = self.get_course_sections(course_id)
            
            # Trouver la section générale (section 0)
            general_section = None
            for section in sections:
                if isinstance(section, dict) and section.get('section', -1) == 0:
                    general_section = section
                    break
            
            if not general_section:
                return False
            
            general_name = general_section.get('name', '').strip().lower()
            
            # Trouver les sections dupliquées (sections > 0 avec le même nom)
            duplicates_to_remove = []
            for section in sections:
                if not isinstance(section, dict):
                    continue
                    
                section_num = section.get('section', -1)
                section_name = section.get('name', '').strip().lower()
                
                if section_num > 0 and section_name == general_name:
                    duplicates_to_remove.append(section_num)
            
            # Supprimer les doublons
            if duplicates_to_remove:
                delete_result = self.delete_sections(course_id, duplicates_to_remove)
                return True
            else:
                return False
                
        except Exception:
            return False

    def get_sections_direct(self, course_id):
        """Récupère les sections directement via l'API Moodle en utilisant une requête plus directe."""
        try:
            # Essayer plusieurs approches pour obtenir les sections
            methods_to_try = [
                ('core_course_get_contents', {'courseid': course_id}),
                ('local_wsmanagesections_get_sections', {'courseid': course_id}),
                ('core_course_get_course', {'courseid': course_id}),
            ]
            
            for method_name, method_params in methods_to_try:
                try:
                    result = self._request(method_name, method_params)
                    
                    # Gérer les différents types de réponse
                    if isinstance(result, list):
                        # Vérifier que les éléments sont des sections valides
                        valid_sections = []
                        for item in result:
                            if isinstance(item, dict) and ('section' in item or 'id' in item):
                                # Normaliser la structure de section
                                normalized_section = {
                                    'id': item.get('id', item.get('section', 0)),
                                    'section': item.get('section', item.get('id', 0)),
                                    'name': item.get('name', f"Section {item.get('section', item.get('id', 0))}"),
                                    'visible': item.get('visible', 1),
                                    'modules': item.get('modules', [])
                                }
                                valid_sections.append(normalized_section)
                        
                        if valid_sections:
                            return valid_sections
                    
                    elif isinstance(result, dict):
                        # Vérifier si c'est une erreur
                        if 'exception' in result or 'errorcode' in result:
                            continue
                        
                        # Chercher les sections dans le dictionnaire
                        if 'sections' in result:
                            return result['sections']
                        elif method_name == 'core_course_get_course':
                            # Construire les sections à partir des infos du cours
                            return self._build_sections_from_course_data(result, course_id)
                        
                except Exception:
                    continue
            
            # Retourner au minimum la section générale
            return [{
                'id': 0,
                'section': 0,
                'name': 'Généralités',
                'visible': 1,
                'modules': []
            }]
            
        except Exception:
            return [{
                'id': 0,
                'section': 0,
                'name': 'Généralités',
                'visible': 1,
                'modules': []
            }]
    
    def _build_sections_from_course_data(self, course_data, course_id):
        """Construit une liste de sections à partir des données du cours."""
        try:
            sections = []
            
            # Section générale (toujours présente)
            sections.append({
                'id': 0,
                'section': 0,
                'name': 'Généralités',
                'visible': 1,
                'modules': []
            })
            
            # Essayer de détecter le nombre de sections
            numsections = 0
            if 'courseformatoptions' in course_data:
                for option in course_data['courseformatoptions']:
                    if option.get('name') == 'numsections':
                        numsections = int(option.get('value', 0))
                        break
            
            # Ajouter les sections supplémentaires
            for i in range(1, numsections + 1):
                sections.append({
                    'id': i,
                    'section': i,
                    'name': f'Section {i}',
                    'visible': 1,
                    'modules': []
                })
            
            return sections
            
        except Exception:
            return [{
                'id': 0,
                'section': 0,
                'name': 'Généralités',
                'visible': 1,
                'modules': []
            }]
    

    def assign_teachers_to_course(self, course_id, usernames):
        """
        Affecte un ou plusieurs profs (usernames LDAP) au cours comme enseignants (roleid=3 par défaut sur Moodle)
        Utilise enrol_manual_enrol_users (plus fiable pour l'enrôlement dans un cours).
        """
        if not usernames:
            return None
        # Récupérer les userids Moodle à partir des usernames
        userids = []
        for username in usernames:
            params = {'field': 'username', 'values[0]': username}
            result = self._request('core_user_get_users_by_field', params)
            if isinstance(result, list) and result:
                userids.append(result[0]['id'])
        if not userids:
            return None
        # Enrôler les users comme enseignants dans le cours (roleid=3)
        enrolments = []
        for userid in userids:
            enrolments.append({
                'roleid': 3,  # 3 = enseignant
                'userid': userid,
                'courseid': course_id
            })
        params = {}
        for i, enrol in enumerate(enrolments):
            params[f'enrolments[{i}][roleid]'] = enrol['roleid']
            params[f'enrolments[{i}][userid]'] = enrol['userid']
            params[f'enrolments[{i}][courseid]'] = enrol['courseid']
        result = self._request('enrol_manual_enrol_users', params)
        print(f"[DEBUG][enrol_manual_enrol_users] course_id={course_id} usernames={usernames} userids={userids} params={params}\nRésultat API: {result}")
        return result
