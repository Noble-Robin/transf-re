from django import forms

class AddCategoryForm(forms.Form):
    name = forms.CharField(label="Nom de la catégorie", max_length=255, widget=forms.TextInput(attrs={
        'class': 'modern-input',
        'placeholder': 'Nom de la catégorie...'
    }))
    image = forms.ImageField(label="Logo (optionnel)", required=False, widget=forms.ClearableFileInput(attrs={
        'class': 'modern-input',
    }))
