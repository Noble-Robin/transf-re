from django.shortcuts import render, redirect
from django.contrib import messages
from .forms_add_category import AddCategoryForm
from .models import SchoolImage
from .services.moodle_api import MoodleAPI
import os

def add_category_page(request):
    if request.method == 'POST':
        form = AddCategoryForm(request.POST, request.FILES)
        if form.is_valid():
            name = form.cleaned_data['name']
            image = form.cleaned_data['image']
            # Création de la catégorie sur Moodle
            api = MoodleAPI(
                url=os.getenv('MOODLE_URL'),
                token=os.getenv('MOODLE_TOKEN')
            )
            try:
                category_id = api.create_category(name, parent_id=0)
            except Exception as e:
                messages.error(request, f"Erreur lors de la création de la catégorie : {e}")
                return render(request, 'caplogy_app/add_category.html', {'form': form})
            # Si une image est fournie, l'associer
            if image and category_id:
                SchoolImage.objects.create(category_id=category_id, image=image)
            elif not image:
                messages.warning(request, "Catégorie créée sans logo. Vous pouvez l'ajouter plus tard.")
            messages.success(request, "Catégorie créée avec succès !")
            return redirect('categories')
    else:
        form = AddCategoryForm()
    return render(request, 'caplogy_app/add_category.html', {'form': form})
