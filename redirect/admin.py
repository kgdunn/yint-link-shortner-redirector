from django.contrib import admin

from .models import Redirect

class RedirectAdmin(admin.ModelAdmin):
    list_display = ('source', 'destination', 'extra_info', 'is_logged',
                    'is_active', )

    list_display_links = list_display

admin.site.register(Redirect, RedirectAdmin)