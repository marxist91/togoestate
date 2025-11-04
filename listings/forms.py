from django import forms
from .models import Listing, ListingPhoto


class ListingPhotoForm(forms.ModelForm):
    class Meta:
        model = ListingPhoto
        fields = ['image', 'is_cover']
        widgets = {
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'is_cover': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class ListingForm(forms.ModelForm):
    class Meta:
        model = Listing
        fields = [
            'title', 'category', 'listing_type', 'price', 'currency',
            'bedrooms', 'bathrooms', 'surface', 'city', 'address', 'description'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'listing_type': forms.Select(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'currency': forms.TextInput(attrs={'class': 'form-control'}),
            'bedrooms': forms.NumberInput(attrs={'class': 'form-control'}),
            'bathrooms': forms.NumberInput(attrs={'class': 'form-control'}),
            'surface': forms.NumberInput(attrs={'class': 'form-control'}),
            'city': forms.Select(attrs={'class': 'form-control'}),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }
