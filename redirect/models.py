from django.db import models

class Redirect(models.Model):
    """ The redirector definition. """
    source = models.CharField(max_length=500)
    destination = models.CharField(max_length=500)
    extra_info = models.CharField(blank=True, max_length=200)
    is_logged = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True, help_text=('If False, then '
                                    'the redirect will give a 404 instead.'))

    def save(self, *args, **kwargs):
        self.source  = self.source.strip()
        self.destination  = self.destination.strip()
        super(Redirect, self).save(*args, **kwargs)

    def __str__(self):
        return '{0}\t:\t{1}'.format(self.source, self.destination)


class TotalStats(models.Model):
    """ Tracking stats for a redirector """
    redir = models.ForeignKey('redirect.Redirect')
    accesses = models.BigIntegerField(default=0)
    last_access = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Total Stats'

