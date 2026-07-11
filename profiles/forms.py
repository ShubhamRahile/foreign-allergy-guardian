from django import forms
from .models import MedicalProfile
from accounts.models import User

class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))
    phone = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ['email', 'phone']

class MedicalProfileForm(forms.ModelForm):
    class Meta:
        model = MedicalProfile
        fields = ['emergency_contact', 'allergies', 'dietary_restrictions', 'uploaded_file']
        widgets = {
            'emergency_contact': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 3, 
                'placeholder': 'Name: Jane Doe\nRelationship: Spouse\nPhone: +1 555-0100'
            }),
            'allergies': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'e.g. peanuts, dairy, wheat, sesame'
            }),
            'dietary_restrictions': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 3, 
                'placeholder': 'e.g. Vegan, Gluten-Free, Halal, Kosher'
            }),
            'uploaded_file': forms.FileInput(attrs={'class': 'form-control'}),
        }
