document.addEventListener('DOMContentLoaded', () => {
    console.log('🚀 DEBUG: create_course.js chargé et DOMContentLoaded déclenché');
    
    // Gestion des catégories en cascade
    const categorySelects = [
        document.getElementById('cat-level-0'),
        document.getElementById('cat-level-1'),
        document.getElementById('cat-level-2')
    ];

    // Charger les catégories principales
    loadCategories(0, categorySelects[0]);

    // Gestionnaires d'événements pour les sélecteurs de catégories
    categorySelects.forEach((select, index) => {
        select.addEventListener('change', (e) => {
            handleCategoryChange(index, e.target.value);
        });
    });

    function loadCategories(parentId, selectElement) {
        const url = parentId === 0 
            ? '/api/categories/' 
            : `/api/categories/?parent=${parentId}`;
            
        fetch(url)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                selectElement.innerHTML = '<option value="">Sélectionnez...</option>';
                const categories = data.categories || data;
                categories.forEach(category => {
                    const option = new Option(category.name, category.id);
                    selectElement.add(option);
                });
            })
            .catch(error => {
                selectElement.innerHTML = '<option value="">Erreur de chargement</option>';
            });
    }

    function handleCategoryChange(level, categoryId) {
        // Masquer et vider les niveaux suivants
        for (let i = level + 1; i < categorySelects.length; i++) {
            categorySelects[i].classList.add('hidden');
            categorySelects[i].innerHTML = '<option value="">Sélectionnez...</option>';
        }

        // Si une catégorie est sélectionnée, charger les sous-catégories
        if (categoryId && categorySelects[level + 1]) {
            const url = `/api/categories/?parent=${categoryId}`;
            fetch(url)
                .then(response => {
                    if (!response.ok) {
                        throw new Error(`HTTP error! status: ${response.status}`);
                    }
                    return response.json();
                })
                .then(data => {
                    const categories = data.categories || data;
                    if (categories.length > 0) {
                        const nextSelect = categorySelects[level + 1];
                        nextSelect.classList.remove('hidden');
                        nextSelect.innerHTML = '<option value="">Sélectionnez...</option>';
                        categories.forEach(category => {
                            const option = new Option(category.name, category.id);
                            nextSelect.add(option);
                        });
                    }
                })
                .catch(error => {
                    // Erreur silencieuse
                });
        }
    }

    // Gestion des sections
    const sectionsList = document.getElementById('sections-list');
    const addSectionBtn = document.getElementById('add-section');
    let sectionCounter = 0;

    addSectionBtn.addEventListener('click', addNewSection);

    function addNewSection() {
        sectionCounter++;
        const sectionItem = createSectionElement(sectionCounter);
        sectionsList.appendChild(sectionItem);
        
        // Animation d'apparition
        setTimeout(() => {
            sectionItem.style.opacity = '1';
            sectionItem.style.transform = 'translateY(0)';
        }, 10);

        // Focus sur le champ titre
        const titleInput = sectionItem.querySelector('.section-title-input');
        titleInput.focus();
    }

    function createSectionElement(sectionNumber) {
        const sectionDiv = document.createElement('div');
        sectionDiv.className = 'section-item';
        sectionDiv.style.opacity = '0';
        sectionDiv.style.transform = 'translateY(-20px)';
        sectionDiv.style.transition = 'all 0.3s ease';
        
        sectionDiv.innerHTML = `
            <div class="section-header-item">
                <div class="section-number">${sectionNumber}</div>
                <input type="text" 
                       name="section_${sectionNumber}" 
                       placeholder="Titre de la section ${sectionNumber}" 
                       required 
                       class="section-title-input">
                <button type="button" class="delete-section-btn" onclick="deleteSection(this)">
                    ✕
                </button>
            </div>
            <div class="section-actions">
                <button type="button" class="resource-btn" onclick="addResource(this, ${sectionNumber})">
                    Ajouter une ressource
                </button>
                <input type="hidden" name="file_${sectionNumber}" id="file_${sectionNumber}">
                <span class="selected-file" id="selected-file-${sectionNumber}"></span>
            </div>
        `;
        
        return sectionDiv;
    }

    // Fonction globale pour supprimer une section
    window.deleteSection = function(deleteBtn) {
        const sectionItem = deleteBtn.closest('.section-item');
        
        // Animation de disparition
        sectionItem.style.opacity = '0';
        sectionItem.style.transform = 'translateY(-20px)';
        
        setTimeout(() => {
            sectionItem.remove();
            updateSectionNumbers();
        }, 300);
    };

    // Fonction globale pour ajouter une ressource
    window.addResource = function(btn, sectionId) {
        console.log('🔍 DEBUG: addResource appelée avec sectionId:', sectionId);
        console.log('🔍 DEBUG: btn:', btn);
        console.log('🔍 DEBUG: modal element:', modal);
        
        currentSectionId = sectionId;
        currentResourceBtn = btn;
        openFileModal('/');
    };
    
    console.log('🚀 DEBUG: Fonction addResource définie sur window:', typeof window.addResource);

    function updateSectionNumbers() {
        const sections = sectionsList.querySelectorAll('.section-item');
        sections.forEach((section, index) => {
            const number = index + 1;
            const numberElement = section.querySelector('.section-number');
            const titleInput = section.querySelector('.section-title-input');
            const hiddenInput = section.querySelector('input[type="hidden"]');
            const selectedFile = section.querySelector('.selected-file');
            
            numberElement.textContent = number;
            titleInput.name = `section_${number}`;
            titleInput.placeholder = `Titre de la section ${number}`;
            hiddenInput.name = `file_${number}`;
            hiddenInput.id = `file_${number}`;
            selectedFile.id = `selected-file-${number}`;
        });
        sectionCounter = sections.length;
    }

    // Gestion de la modal de fichiers
    const modal = document.getElementById('nc-modal');
    const modalClose = document.getElementById('nc-close');
    const fileList = document.getElementById('nc-list');
    const currentPathDiv = document.getElementById('nc-current-path');
    let currentSectionId = null;
    let currentResourceBtn = null;

    modalClose.addEventListener('click', closeFileModal);
    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            closeFileModal();
        }
    });

    function openFileModal(path) {
        console.log('🔍 DEBUG: openFileModal appelée avec path:', path);
        console.log('🔍 DEBUG: modal element avant add class:', modal);
        
        modal.classList.add('active');
        console.log('🔍 DEBUG: modal.classList après add active:', modal.classList.toString());
        
        loadFiles(path);
    }

    function closeFileModal() {
        modal.classList.remove('active');
        currentSectionId = null;
        currentResourceBtn = null;
    }

    function loadFiles(path) {
        console.log('DEBUG: loadFiles appelée avec path:', path);
        
        // Afficher un bouton de chargement stylisé
        fileList.innerHTML = '<li class="loading-item no-hover" style="text-align: center; padding: 1.5rem; cursor: default !important; pointer-events: none;"><div style="color: #e5e7eb; padding: 0.75rem 1.5rem; border-radius: 0.5rem; display: inline-block; font-weight: 500;">🔄 Chargement en cours...</div></li>';
        
        // Modifier le style du bouton de chargement pour le mode clair
        const isDarkMode = document.documentElement.classList.contains('dark') || 
                          window.matchMedia('(prefers-color-scheme: dark)').matches;
        
        // Couleurs adaptatives
        const colors = isDarkMode ? {
            loadingBg: '#1f2937',
            loadingText: '#e5e7eb',
            textPrimary: '#e5e7eb',
            textSecondary: '#9ca3af',
            hoverBg: '#374151',
            hoverBgFile: '#065f46',
            hoverTextFile: '#10b981',
            errorText: '#f87171'
        } : {
            loadingBg: '#3b82f6',
            loadingText: '#ffffff',
            textPrimary: '#374151',
            textSecondary: '#6b7280',
            hoverBg: '#f3f4f6',
            hoverBgFile: '#ecfdf5',
            hoverTextFile: '#059669',
            errorText: '#ef4444'
        };

        // Créer un timeout personnalisé pour le fetch (60 secondes)
        const controller = new AbortController();
        const timeoutId = setTimeout(() => {
            controller.abort();
        }, 60000); // 60 secondes

        // Faire l'appel AJAX pour récupérer les fichiers Nextcloud
        fetch(`/nc_dir/?path=${encodeURIComponent(path)}`, {
            signal: controller.signal,
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => {
            clearTimeout(timeoutId);
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            return response.json();
        })
        .then(data => {
            processFileData(data, path, colors, isDarkMode);
        })
        .catch(error => {
            clearTimeout(timeoutId);
            console.error('Erreur lors du chargement des fichiers:', error);
            
            let errorMessage = '❌ Erreur de chargement';
            if (error.name === 'AbortError') {
                errorMessage = '⏰ Timeout: Nextcloud met trop de temps à répondre (>30s)';
            } else if (error.message.includes('HTTP')) {
                errorMessage = `❌ Erreur serveur: ${error.message}`;
            } else if (error.message.includes('Failed to fetch')) {
                errorMessage = '🌐 Erreur de connexion réseau';
            }
            
            fileList.innerHTML = `<li style="text-align: center; padding: 2rem; color: ${colors.errorText}; background-color: ${isDarkMode ? '#7f1d1d' : '#fef2f2'}; border-radius: 0.5rem; margin: 1rem;">${errorMessage}<br><small style="opacity: 0.8;">Réessayez en rafraîchissant la page ou contactez l'administrateur</small></li>`;
        });
    }

    // Fonction pour mettre à jour le message de chargement avec progression
    function updateLoadingMessage(message, progress = null) {
        const loadingElement = fileList.querySelector('.loading-item');
        if (loadingElement) {
            let progressBar = '';
            if (progress !== null) {
                progressBar = `<div style="width: 100%; background-color: #374151; border-radius: 4px; overflow: hidden; margin-top: 0.5rem;">
                    <div style="width: ${progress}%; height: 6px; background: linear-gradient(90deg, #3b82f6, #10b981); transition: width 0.3s ease;"></div>
                </div>`;
            }
            
            loadingElement.innerHTML = `<div style="background: #1f2937; color: #e5e7eb; padding: 0.75rem 1.5rem; border-radius: 0.5rem; display: inline-block; font-weight: 500;">
                🔄 ${message}${progressBar}
            </div>`;
        }
    }

    function processFileData(data, path, colors, isDarkMode) {
        // Maintenant afficher le chemin une fois les données chargées
        if (currentPathDiv) {
            // Appliquer directement les styles dark mode au conteneur
            if (isDarkMode) {
                currentPathDiv.style.color = '#e5e7eb';
                currentPathDiv.style.backgroundColor = '#374151';
                currentPathDiv.style.borderColor = '#4b5563';
            } else {
                // Appliquer directement les styles pour le mode clair
                currentPathDiv.style.color = '#374151';
                currentPathDiv.style.backgroundColor = '#ffffff';
                currentPathDiv.style.borderColor = '#e5e7eb';
            }
            
            // Construire la navigation par chemin
            currentPathDiv.innerHTML = ''; // Vider le contenu
            
            // Ajouter l'icône et la racine
            const rootSpan = document.createElement('span');
            rootSpan.innerHTML = '📁 ';
            rootSpan.style.color = colors.textPrimary;
            currentPathDiv.appendChild(rootSpan);
            
            // Racine cliquable
            const rootLink = document.createElement('span');
            rootLink.textContent = 'Biblio_Cours_Caplogy';
            rootLink.style.cursor = 'pointer';
            rootLink.style.color = colors.textPrimary + ' !important';
            rootLink.style.fontWeight = '600';
            rootLink.onclick = () => loadFiles('/');
            
            // Ajouter un effet hover programmatique
            rootLink.addEventListener('mouseenter', () => {
                rootLink.style.backgroundColor = isDarkMode ? '#4b5563' : '#e5e7eb';
                rootLink.style.padding = '0.125rem 0.25rem';
                rootLink.style.borderRadius = '0.25rem';
            });
            rootLink.addEventListener('mouseleave', () => {
                rootLink.style.backgroundColor = '';
                rootLink.style.padding = '';
                rootLink.style.borderRadius = '';
            });
            
            currentPathDiv.appendChild(rootLink);
            
            // Ajouter les sous-dossiers si on n'est pas à la racine
            let cleanPath = path.replace(/^\/+|\/+$/g, '');
            if (cleanPath && cleanPath !== '') {
                const pathParts = cleanPath.split('/').filter(part => part !== '');
                let currentNavPath = '';
                
                pathParts.forEach((part, index) => {
                    // Ajouter le séparateur
                    const separator = document.createElement('span');
                    separator.textContent = ' / ';
                    separator.style.color = colors.textSecondary;
                    currentPathDiv.appendChild(separator);
                    
                    // Construire le chemin pour ce niveau
                    currentNavPath += '/' + part;
                    
                    // Créer le lien cliquable
                    const partLink = document.createElement('span');
                    partLink.textContent = part;
                    partLink.style.cursor = 'pointer';
                    partLink.style.color = colors.textPrimary;
                    partLink.style.fontWeight = '500';
                    
                    // Si c'est le dernier élément (dossier courant), le rendre non cliquable
                    if (index === pathParts.length - 1) {
                        partLink.style.cursor = 'default';
                        partLink.style.fontWeight = '600';
                    } else {
                        // Ajouter un effet hover programmatique
                        partLink.addEventListener('mouseenter', () => {
                            partLink.style.backgroundColor = isDarkMode ? '#4b5563' : '#e5e7eb';
                            partLink.style.padding = '0.125rem 0.25rem';
                            partLink.style.borderRadius = '0.25rem';
                        });
                        partLink.addEventListener('mouseleave', () => {
                            partLink.style.backgroundColor = '';
                            partLink.style.padding = '';
                            partLink.style.borderRadius = '';
                        });
                        
                        // Capturer la valeur dans une closure
                        const navPath = currentNavPath + '/';
                        partLink.onclick = () => loadFiles(navPath);
                    }
                    
                    currentPathDiv.appendChild(partLink);
                });
            }
            
            // Réafficher le chemin
            currentPathDiv.style.display = 'block';
            console.log('DEBUG: navigation par chemin mise à jour');
        }
        fileList.innerHTML = '';
        
        // Ajouter le dossier parent si on n'est pas à la racine
        if (path !== '/') {
            const parentPath = path.replace(/\/[^\/]*\/$/, '/');
            const parentItem = document.createElement('li');
            parentItem.innerHTML = '📁 ⬆️ .. (Dossier parent)';
            parentItem.dataset.type = 'folder';
            parentItem.dataset.path = parentPath;
            parentItem.style.fontWeight = 'bold';
            parentItem.style.color = isDarkMode ? '#60a5fa' : '#3b82f6';
            parentItem.style.cursor = 'pointer';
            parentItem.style.padding = '0.5rem';
            parentItem.style.borderRadius = '0.375rem';
            parentItem.style.transition = 'background-color 0.2s';
            parentItem.style.borderBottom = `1px solid ${isDarkMode ? '#4b5563' : '#e5e7eb'}`;
            parentItem.style.marginBottom = '0.5rem';
            
            // Effet hover pour le dossier parent
            parentItem.addEventListener('mouseenter', () => {
                parentItem.style.backgroundColor = isDarkMode ? '#1e3a8a' : '#eff6ff';
            });
            parentItem.addEventListener('mouseleave', () => {
                parentItem.style.backgroundColor = '';
            });
            
            fileList.appendChild(parentItem);
        }

        // Ajouter les dossiers
        if (data.folders) {
            data.folders.forEach(folderName => {
                // Filtrer le dossier racine Biblio_Cours_Caplogy quand on est à la racine
                if ((path === '/' || path === '') && folderName === 'Biblio_Cours_Caplogy') {
                    // Ne pas afficher ce dossier comme bouton cliquable
                    return;
                }
                
                // Éviter d'afficher le dossier courant comme un sous-dossier
                const currentFolderName = path.split('/').filter(p => p).pop();
                if (folderName === currentFolderName) {
                    return;
                }
                
                const listItem = document.createElement('li');
                listItem.innerHTML = `📁 ${folderName}`;
                listItem.dataset.type = 'folder';
                listItem.dataset.path = path + folderName + '/';
                listItem.style.fontWeight = '500';
                listItem.style.cursor = 'pointer';
                listItem.style.padding = '0.5rem';
                listItem.style.borderRadius = '0.375rem';
                listItem.style.transition = 'background-color 0.2s';
                listItem.style.color = colors.textPrimary;
                
                // Effet hover
                listItem.addEventListener('mouseenter', () => {
                    listItem.style.backgroundColor = colors.hoverBg;
                });
                listItem.addEventListener('mouseleave', () => {
                    listItem.style.backgroundColor = '';
                });
                
                fileList.appendChild(listItem);
            });
        }

        // Ajouter les fichiers
        if (data.files) {
            data.files.forEach(fileName => {
                const listItem = document.createElement('li');
                const fileIcon = getFileIcon(fileName);
                listItem.innerHTML = `${fileIcon} ${fileName}`;
                listItem.dataset.type = 'file';
                listItem.dataset.path = path + fileName;
                listItem.style.cursor = 'pointer';
                listItem.style.padding = '0.5rem';
                listItem.style.borderRadius = '0.375rem';
                listItem.style.transition = 'background-color 0.2s';
                listItem.style.color = colors.textPrimary;
                
                // Effet hover pour les fichiers
                listItem.addEventListener('mouseenter', () => {
                    listItem.style.backgroundColor = colors.hoverBgFile;
                    listItem.style.color = colors.hoverTextFile;
                });
                listItem.addEventListener('mouseleave', () => {
                    listItem.style.backgroundColor = '';
                    listItem.style.color = colors.textPrimary;
                });
                
                fileList.appendChild(listItem);
            });
        }

        if (fileList.children.length === 0) {
            fileList.innerHTML = `<li style="text-align: center; padding: 2rem; color: ${colors.textSecondary};">📂 Dossier vide</li>`;
        }
    }

    function getFileIcon(fileName) {
        const extension = fileName.split('.').pop().toLowerCase();
        const iconMap = {
            'pdf': '📄',
            'doc': '📝',
            'docx': '📝',
            'xls': '📊',
            'xlsx': '📊',
            'ppt': '📽️',
            'pptx': '📽️',
            'jpg': '🖼️',
            'jpeg': '🖼️',
            'png': '🖼️',
            'gif': '🖼️',
            'mp4': '🎥',
            'mp3': '🎵',
            'zip': '🗜️',
            'rar': '🗜️',
            'txt': '📄'
        };
        return iconMap[extension] || '🔗';
    }

    // Gestionnaire de clic pour la liste des fichiers
    fileList.addEventListener('click', (e) => {
        const listItem = e.target.closest('li');
        if (!listItem || !listItem.dataset.type) return;

        const { type, path } = listItem.dataset;

        if (type === 'folder') {
            loadFiles(path);
        } else if (type === 'file') {
            selectFile(path);
        }
    });

    function selectFile(filePath) {
        if (currentSectionId && currentResourceBtn) {
            const fileName = filePath.split('/').pop();
            const hiddenInput = document.getElementById(`file_${currentSectionId}`);
            const selectedFileSpan = document.getElementById(`selected-file-${currentSectionId}`);
            
            hiddenInput.value = filePath;
            selectedFileSpan.textContent = `${fileName}`;
            selectedFileSpan.style.color = '#10b981';
            selectedFileSpan.style.fontWeight = '500';
            
            currentResourceBtn.textContent = `✅ ${fileName}`;
            currentResourceBtn.style.background = 'linear-gradient(135deg, #10b981 0%, #059669 100%)';
        }
        closeFileModal();
    }

    // Gestion de la soumission du formulaire
    document.getElementById('course-form').addEventListener('submit', (e) => {
        e.preventDefault();
        
        // Validation basique
        const title = document.getElementById('title').value.trim();
        if (!title) {
            alert('⚠️ Veuillez saisir un titre pour le cours');
            return;
        }

        const sections = sectionsList.querySelectorAll('.section-item');
        if (sections.length === 0) {
            const confirmCreate = confirm('❓ Aucune section n\'a été créée. Voulez-vous créer le cours sans section ?');
            if (!confirmCreate) return;
        }

        // Validation des sections
        let hasEmptySection = false;
        sections.forEach(section => {
            const titleInput = section.querySelector('.section-title-input');
            if (!titleInput.value.trim()) {
                hasEmptySection = true;
            }
        });

        if (hasEmptySection) {
            alert('⚠️ Toutes les sections doivent avoir un titre');
            return;
        }

        // Animation du bouton de soumission
        const submitBtn = e.target.querySelector('button[type="submit"]');
        const originalText = submitBtn.innerHTML;
        const loadingText = window.isEdit ? '⏳ Modification en cours...' : '⏳ Création en cours...';
        submitBtn.innerHTML = loadingText;
        submitBtn.disabled = true;

        // Soumission du formulaire
        setTimeout(() => {
            e.target.submit();
        }, 500);
    });

    // Initialisation pour le mode édition
    function initEditMode() {
        if (window.isEdit) {
            const courseDataElement = document.getElementById('course-data');
            if (courseDataElement) {
                const courseData = {
                    id: parseInt(courseDataElement.dataset.id),
                    categoryid: parseInt(courseDataElement.dataset.categoryid),
                    fullname: courseDataElement.dataset.fullname,
                    shortname: courseDataElement.dataset.shortname
                };
                
                // Validation des données
                if (!courseData.categoryid || courseData.categoryid === 0) {
                    return;
                }
                
                // Stocker les données globalement pour un accès facile
                window.courseData = courseData;
                
                // Charger les sections existantes
                loadExistingSections();
                
                // Optimisation : utiliser les données pré-construites si disponibles
                const hierarchyElement = document.getElementById('category-hierarchy-data');
                if (hierarchyElement) {
                    // Présélection immédiate avec les données pré-construites
                    setTimeout(() => {
                        preselectCategory(courseData.categoryid);
                    }, 50);
                } else {
                    // Fallback vers l'ancienne méthode
                    setTimeout(() => {
                        preselectCategory(courseData.categoryid);
                    }, 100);
                }
            }
        }
    }

    function loadExistingSections() {
        const sectionsDataElement = document.getElementById('course-sections-data');
        if (sectionsDataElement) {
            const sectionElements = sectionsDataElement.querySelectorAll('.section-data');
            
            sectionElements.forEach((sectionElement, index) => {
                const sectionData = {
                    id: sectionElement.dataset.id,
                    name: sectionElement.dataset.name,
                    summary: sectionElement.dataset.summary
                };
                
                // Filtrer les sections "Généralités" - elles ne doivent pas apparaître dans l'interface d'édition
                const sectionName = sectionData.name ? sectionData.name.trim().toLowerCase() : '';
                if (sectionName === 'généralités' || sectionName === 'generalites' || sectionName === 'general') {
                    return; // Ignorer cette section
                }
                
                // Récupérer les modules de cette section
                const moduleElements = sectionElement.querySelectorAll('.module-data');
                const modules = Array.from(moduleElements).map(moduleEl => ({
                    id: moduleEl.dataset.id,
                    name: moduleEl.dataset.name,
                    modname: moduleEl.dataset.modname,
                    url: moduleEl.dataset.url,
                    description: moduleEl.dataset.description
                }));
                
                // Créer la section dans l'interface SEULEMENT si ce n'est pas la section générale
                if (sectionData.name && sectionData.name.trim()) {
                    sectionCounter++;
                    const sectionItem = createSectionElementWithData(sectionCounter, sectionData, modules);
                    sectionsList.appendChild(sectionItem);
                    
                    // Animation d'apparition
                    setTimeout(() => {
                        sectionItem.style.opacity = '1';
                        sectionItem.style.transform = 'translateY(0)';
                    }, 10);
                }
            });
        }
    }

    function createSectionElementWithData(sectionNumber, sectionData, modules = []) {
        const sectionDiv = document.createElement('div');
        sectionDiv.className = 'section-item';
        sectionDiv.style.opacity = '0';
        sectionDiv.style.transform = 'translateY(-20px)';
        sectionDiv.style.transition = 'all 0.3s ease';
        
        // Créer la liste des ressources existantes
        let resourcesHtml = '';
        modules.forEach(module => {
            if (module.name && module.name.trim()) {
                resourcesHtml += `
                    <div class="existing-resource">
                        ${module.url ? `<a href="${module.url}" target="_blank" class="resource-link">🔗</a>` : ''}
                        <span class="resource-name">${module.name}</span>
                        <span class="resource-type">(${module.modname || 'Ressource'})</span>
                    </div>
                `;
            }
        });
        
        sectionDiv.innerHTML = `
            <div class="section-header-item">
                <div class="section-number">${sectionNumber}</div>
                <input type="text" 
                       name="section_${sectionNumber}" 
                       value="${sectionData.name || ''}"
                       placeholder="Titre de la section ${sectionNumber}" 
                       required 
                       class="section-title-input">
                <button type="button" class="delete-section-btn" onclick="deleteSection(this)">
                    ✕
                </button>
            </div>
            ${resourcesHtml ? `<div class="existing-resources">${resourcesHtml}</div>` : ''}
            <div class="section-actions">
                <button type="button" class="resource-btn" onclick="addResource(this, ${sectionNumber})">
                    Ajouter une ressource
                </button>
                <input type="hidden" name="file_${sectionNumber}" id="file_${sectionNumber}">
                <span class="selected-file" id="selected-file-${sectionNumber}"></span>
            </div>
        `;
        
        return sectionDiv;
    }

    function preselectCategory(categoryId) {
        if (!categoryId) return Promise.resolve();
        
        // Utiliser directement les données de présélection du backend
        const preselectionData = getPreselectionData();
        if (preselectionData && preselectionData.target_category_id == categoryId) {
            return preselectFromOptimizedData(preselectionData);
        } else {
            return Promise.resolve();
        }
    }

    function getPreselectionData() {
        const preselectionElement = document.getElementById('preselection-data');
        if (preselectionElement) {
            try {
                return JSON.parse(preselectionElement.textContent);
            } catch (e) {
                return null;
            }
        }
        return null;
    }

    function preselectFromOptimizedData(data) {
        
        try {
            const { path, years, formations } = data;
            
            if (!path || path.length === 0) {
                return Promise.resolve();
            }
            
            // Attendre que les catégories principales soient chargées avant de présélectionner
            return new Promise((resolve) => {
                const waitForSchools = () => {
                    const schoolSelect = categorySelects[0];
                    
                    // Vérifier si les écoles sont déjà chargées
                    if (schoolSelect.options.length > 1) {
                        doPreselection();
                        resolve();
                    } else {
                        // Attendre un peu et réessayer
                        setTimeout(waitForSchools, 50);
                    }
                };
                
                const doPreselection = () => {
                    // École (niveau 0)
                    if (path.length >= 1) {
                        const school = path[0];
                        categorySelects[0].value = school.id;
                        categorySelects[0].classList.remove('hidden');
                        
                        // Année (niveau 1)
                        if (path.length >= 2 && years && years.length > 0) {
                            const year = path[1];
                            
                            const yearSelect = categorySelects[1];
                            yearSelect.innerHTML = '<option value="">Sélectionnez...</option>';
                            years.forEach(y => {
                                const option = new Option(y.name, y.id);
                                yearSelect.add(option);
                            });
                            yearSelect.classList.remove('hidden');
                            yearSelect.value = year.id;
                            
                            // Formation (niveau 2)
                            if (path.length >= 3 && formations && formations.length > 0) {
                                const formation = path[2];
                                
                                const formationSelect = categorySelects[2];
                                formationSelect.innerHTML = '<option value="">Sélectionnez...</option>';
                                formations.forEach(f => {
                                    const option = new Option(f.name, f.id);
                                    formationSelect.add(option);
                                });
                                formationSelect.classList.remove('hidden');
                                formationSelect.value = formation.id;
                            }
                        }
                    }
                };
                
                waitForSchools();
            });
            
        } catch (error) {
            return Promise.reject(error);
        }
    }

    // Initialiser le mode édition si nécessaire
    initEditMode();
});