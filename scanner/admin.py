from django.contrib import admin
from .models import ScanHistory

class ScanHistoryAdmin(admin.ModelAdmin):
    list_display = ('user', 'product_name', 'barcode', 'result', 'created_at')
    list_filter = ('result', 'created_at')
    search_fields = ('product_name', 'barcode', 'user__username')

admin.site.register(ScanHistory, ScanHistoryAdmin)
