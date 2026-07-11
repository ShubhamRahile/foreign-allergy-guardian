from django.contrib import admin
from .models import MedicalProfile

class MedicalProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'allergies', 'emergency_contact', 'created_at')
    search_fields = ('user__username', 'allergies', 'emergency_contact')

admin.site.register(MedicalProfile, MedicalProfileAdmin)
