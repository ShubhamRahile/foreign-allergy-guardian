from django.db import models
from django.conf import settings

class ScanHistory(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='scan_history')
    barcode = models.CharField(max_length=50, blank=True, null=True)
    product_name = models.CharField(max_length=255, default='Unknown Product')
    ingredients = models.TextField(blank=True, null=True)
    detected_allergens = models.JSONField(default=list, help_text="List of matched allergens.")
    result = models.CharField(max_length=20, choices=[('safe', 'Safe'), ('danger', 'Danger')], default='safe')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = "Scan Histories"

    def __str__(self):
        return f"{self.product_name} ({self.barcode}) - {self.result.upper()} by {self.user.username}"
