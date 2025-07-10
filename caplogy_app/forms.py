from django import forms
from .models import SchoolImage

class SchoolImageForm(forms.ModelForm):
    class Meta:
        model = SchoolImage
        fields = ['category_id', 'image']
        widgets = {
            'category_id': forms.NumberInput(attrs={'class': 'modern-input', 'placeholder': 'ID de la catégorie principale (école)'}),
            'image': forms.ClearableFileInput(attrs={'class': 'modern-input'}),
        }
