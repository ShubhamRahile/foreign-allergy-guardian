from django.db import models
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

class MedicalProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='medical_profile')
    emergency_contact = models.TextField(blank=True, null=True, help_text="Name, relationship, and phone of emergency contact.")
    allergies = models.TextField(blank=True, null=True, help_text="Comma-separated list of allergens (e.g. peanuts, dairy, gluten).")
    dietary_restrictions = models.TextField(blank=True, null=True, help_text="Any additional dietary preferences or restrictions.")
    uploaded_file = models.FileField(upload_to='allergy_files/', blank=True, null=True, help_text="A text (.txt) file containing a list of allergens, one per line.")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Medical Profile for {self.user.username}"

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        MedicalProfile.objects.create(user=instance)

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'medical_profile'):
        instance.medical_profile.save()
