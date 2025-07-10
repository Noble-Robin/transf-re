document.addEventListener('DOMContentLoaded', () => {
    const schoolFilter = document.getElementById('schoolFilter')
    const schoolSearchInput = document.getElementById('schoolSearchInput')
    const schoolSelectContainer = document.getElementById('schoolSelectContainer')
    const schoolDropdown = document.getElementById('schoolDropdown')
    const yearFilter = document.getElementById('yearFilter')
    const formationFilter = document.getElementById('formationFilter')
    const searchFilter = document.getElementById('searchFilter')
    const resetBtn = document.getElementById('resetFilters')
    const tableBody = document.querySelector('#coursesTable tbody')

    const yearGroup = document.getElementById('yearGroup')
    const formationGroup = document.getElementById('formationGroup')

    // Fonction pour gérer le composant de recherche d'école
    function initSchoolSearchable() {
        const dropdownItems = schoolDropdown.querySelectorAll('.dropdown-item')
        
        // Vérifier s'il y a une sélection initiale
        const selectedItem = schoolDropdown.querySelector('[data-selected="true"]')
        if (selectedItem) {
            schoolSearchInput.value = selectedItem.textContent.trim()
            schoolFilter.value = selectedItem.dataset.value
            selectedItem.classList.add('selected')
        } else {
            // Par défaut, sélectionner "Toutes les écoles"
            const defaultItem = schoolDropdown.querySelector('[data-value=""]')
            if (defaultItem) {
                schoolSearchInput.value = defaultItem.textContent.trim()
                schoolFilter.value = ''
                defaultItem.classList.add('selected')
            }
        }

        // Afficher/masquer la liste déroulante
        schoolSearchInput.addEventListener('focus', () => {
            // Montrer toutes les options quand on clique
            dropdownItems.forEach(item => item.classList.remove('hidden'))
            schoolSelectContainer.classList.add('open')
        })

        schoolSearchInput.addEventListener('click', () => {
            // Sélectionner tout le texte pour faciliter la recherche
            schoolSearchInput.select()
        })

        schoolSearchInput.addEventListener('blur', (e) => {
            // Délai pour permettre le clic sur un élément
            setTimeout(() => {
                if (!schoolSelectContainer.contains(document.activeElement)) {
                    schoolSelectContainer.classList.remove('open')
                    // Restaurer toutes les options quand on ferme
                    dropdownItems.forEach(item => item.classList.remove('hidden'))
                }
            }, 150)
        })

        // Fonction de filtrage
        schoolSearchInput.addEventListener('input', () => {
            const searchTerm = schoolSearchInput.value.toLowerCase()
            
            // Si l'input est vide, montrer toutes les options
            if (searchTerm === '') {
                dropdownItems.forEach(item => item.classList.remove('hidden'))
                schoolSelectContainer.classList.add('open')
                return
            }
            
            dropdownItems.forEach(item => {
                const text = item.textContent.toLowerCase()
                if (text.includes(searchTerm)) {
                    item.classList.remove('hidden')
                } else {
                    item.classList.add('hidden')
                }
            })
            
            schoolSelectContainer.classList.add('open')
        })

        // Gestion des clics sur les éléments
        dropdownItems.forEach(item => {
            item.addEventListener('mousedown', (e) => {
                e.preventDefault() // Empêche la perte de focus
                
                // Retirer la sélection précédente
                dropdownItems.forEach(i => i.classList.remove('selected'))
                
                // Ajouter la sélection à l'élément cliqué
                item.classList.add('selected')
                
                // Mettre à jour les valeurs
                schoolSearchInput.value = item.textContent.trim()
                schoolFilter.value = item.dataset.value
                
                // Restaurer toutes les options
                dropdownItems.forEach(i => i.classList.remove('hidden'))
                
                // Fermer la liste déroulante
                schoolSelectContainer.classList.remove('open')
                
                // Déclencher l'événement change
                schoolFilter.dispatchEvent(new Event('change'))
            })
        })

        // Navigation au clavier
        schoolSearchInput.addEventListener('keydown', (e) => {
            const visibleItems = Array.from(dropdownItems).filter(item => !item.classList.contains('hidden'))
            const selectedIndex = visibleItems.findIndex(item => item.classList.contains('selected'))

            switch (e.key) {
                case 'ArrowDown':
                    e.preventDefault()
                    const nextIndex = selectedIndex < visibleItems.length - 1 ? selectedIndex + 1 : 0
                    selectItem(visibleItems[nextIndex])
                    break
                case 'ArrowUp':
                    e.preventDefault()
                    const prevIndex = selectedIndex > 0 ? selectedIndex - 1 : visibleItems.length - 1
                    selectItem(visibleItems[prevIndex])
                    break
                case 'Enter':
                    e.preventDefault()
                    if (selectedIndex >= 0) {
                        visibleItems[selectedIndex].click()
                    }
                    break
                case 'Escape':
                    schoolSelectContainer.classList.remove('open')
                    schoolSearchInput.blur()
                    break
            }
        })

        function selectItem(item) {
            dropdownItems.forEach(i => i.classList.remove('selected'))
            if (item) {
                item.classList.add('selected')
                item.scrollIntoView({ block: 'nearest' })
            }
        }
    }

    // Initialiser le composant de recherche
    initSchoolSearchable()

    function toggleGroups() {
        if (schoolFilter.value) {
            yearGroup.classList.remove('hidden')
        } else {
            yearGroup.classList.add('hidden')
            yearFilter.innerHTML = '<option value="">Toutes les années</option>'
            formationGroup.classList.add('hidden')
            formationFilter.innerHTML = '<option value="">Toutes les formations</option>'
        }

        if (yearFilter.value) {
            formationGroup.classList.remove('hidden')
        } else {
            formationGroup.classList.add('hidden')
            formationFilter.innerHTML = '<option value="">Toutes les formations</option>'
        }
    }

    function loadSubcategories(parent, target, placeholder) {
        target.innerHTML = `<option value="">${placeholder}</option>`
        if (!parent.value) return
        fetch(`/api/categories/?parent=${parent.value}`)
            .then(r => r.json())
            .then(json => {
                json.categories.forEach(cat => {
                    const o = document.createElement('option')
                    o.value = cat.id
                    o.textContent = cat.name
                    target.appendChild(o)
                })
            })
    }

    function updateTable() {
        const p = new URLSearchParams()
        if (schoolFilter.value) p.set('school', schoolFilter.value)
        if (yearFilter.value) p.set('year', yearFilter.value)
        if (formationFilter.value) p.set('formation', formationFilter.value)
        if (searchFilter.value) p.set('search', searchFilter.value)
        fetch(`/api/courses/?${p.toString()}`)
            .then(r => r.json())
            .then(json => {
                tableBody.innerHTML = ''
                json.courses.forEach(c => {
                    const tr = document.createElement('tr')
                    tr.innerHTML = `
            <td>${c.fullname}</td>
            <td>${c.schoolname}</td>
            <td>${c.yearname || ''}</td>
            <td>${c.formationname || ''}</td>
            <td>
                <a href="/courses/edit/${c.id}/" class="btn btn-edit" title="Modifier le cours">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
                        <path d="m18.5 2.5 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
                    </svg>
                    <span>Modifier</span>
                </a>
                <a href="/courses/delete/${c.id}/" class="btn btn-delete" title="Supprimer le cours" onclick="return confirm('Êtes-vous sûr de vouloir supprimer ce cours ?')">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <polyline points="3,6 5,6 21,6"></polyline>
                        <path d="m19,6v14a2,2 0 0,1 -2,2H7a2,2 0 0,1 -2,-2V6m3,0V4a2,2 0 0,1 2,-2h4a2,2 0 0,1 2,2v2"></path>
                        <line x1="10" y1="11" x2="10" y2="17"></line>
                        <line x1="14" y1="11" x2="14" y2="17"></line>
                    </svg>
                    <span>Supprimer</span>
                </a>
            </td>`
                    tableBody.appendChild(tr)
                })
            })
    }

    schoolFilter.addEventListener('change', () => {
        toggleGroups()
        loadSubcategories(schoolFilter, yearFilter, 'Toutes les années')
        updateTable()
    })

    yearFilter.addEventListener('change', () => {
        toggleGroups()
        loadSubcategories(yearFilter, formationFilter, 'Toutes les formations')
        updateTable()
    })

    formationFilter.addEventListener('change', updateTable)
    searchFilter.addEventListener('input', updateTable)
    resetBtn.addEventListener('click', () => {
        schoolFilter.value = ''
        schoolSearchInput.value = 'Toutes les écoles'
        searchFilter.value = ''
        
        // Retirer toutes les sélections
        const dropdownItems = schoolDropdown.querySelectorAll('.dropdown-item')
        dropdownItems.forEach(item => {
            item.classList.remove('selected')
            item.classList.remove('hidden')
        })
        
        // Sélectionner "Toutes les écoles"
        const defaultItem = schoolDropdown.querySelector('[data-value=""]')
        if (defaultItem) {
            defaultItem.classList.add('selected')
        }
        
        toggleGroups()
        updateTable()
    })

    toggleGroups()
    updateTable()
})
