from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .forms import SchoolImageForm
from .models import SchoolImage
from django.views.decorators.http import require_http_methods
from .services.moodle_api import MoodleAPI
import os
from django import forms

@require_http_methods(["GET", "POST"])
def school_image_upload(request, category_id=None):
    category_name = None
    if category_id:
        # Récupérer le nom de la catégorie principale depuis Moodle
        api = MoodleAPI(
            url=os.getenv('MOODLE_URL'),
            token=os.getenv('MOODLE_TOKEN')
        )
        try:
            all_cats = api.get_all_categories()
            cat = next((c for c in all_cats if c['id'] == int(category_id)), None)
            if cat:
                category_name = cat.get('name')
        except Exception:
            category_name = None
        instance = SchoolImage.objects.filter(category_id=category_id).first()
    else:
        instance = None
    if request.method == 'POST':
        form = SchoolImageForm(request.POST, request.FILES, instance=instance)
        if form.is_valid():
            form.save()
            messages.success(request, "Logo enregistré avec succès !")
            return redirect('categories')  # Redirige vers la liste des catégories
    else:
        form = SchoolImageForm(instance=instance)
        if category_id:
            form.fields['category_id'].initial = category_id
            form.fields['category_id'].widget = forms.HiddenInput()
    return render(request, 'caplogy_app/school_image_form.html', {'form': form, 'category_id': category_id, 'category_name': category_name})
