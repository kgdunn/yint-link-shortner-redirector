from django.contrib import admin

from .models import Redirect, TotalStats


class RedirectAdmin(admin.ModelAdmin):
    list_display = ('source', 'destination', 'extra_info', 'is_logged',
                    'is_active', 'status_code')

    list_display_links = list_display

class TotalizerAdmin(admin.ModelAdmin):
    list_display = ('redir', 'accesses', 'last_access',)
    list_display_links = list_display

admin.site.register(Redirect, RedirectAdmin)
admin.site.register(TotalStats, TotalizerAdmin)