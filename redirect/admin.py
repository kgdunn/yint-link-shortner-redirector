from django.contrib import admin

from .models import Redirect, TotalStats, Statistic


class RedirectAdmin(admin.ModelAdmin):
    list_display = ('source', 'destination', 'extra_info', 'is_logged',
                    'is_active', 'status_code')
    list_display_links = list_display
    list_per_page = 400

class TotalizerAdmin(admin.ModelAdmin):
    list_display = ('redir', 'accesses', 'last_access',)
    list_display_links = list_display
    list_per_page = 400

class StatsAdmin(admin.ModelAdmin):
    list_display = ('redir', 'referrer', 'ip_address', 'accessed',)
    list_display_links = list_display
    list_per_page = 500

admin.site.register(Redirect, RedirectAdmin)
admin.site.register(TotalStats, TotalizerAdmin)
admin.site.register(Statistic, StatsAdmin)
