from django.db import models

class Redirect(models.Model):
    source = models.CharField(max_length=500)
    destination = models.CharField(max_length=500)
    is_logged = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True, help_text=('If False, then '
                                    'the redirect will give a 404 instead.'))
