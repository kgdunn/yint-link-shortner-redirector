from django.shortcuts import render, HttpResponse, HttpResponseRedirect, Http404
from ipware.ip import get_real_ip
import os
import logging
from . import models

logger = logging.getLogger(__name__)
logger.debug('Starting views.py file')

from django.conf import settings

class ForceStatic(Exception):
    pass

def track_statistics(request, redirect):
    """Track statistics related to each link request"""

    if redirect.is_logged == False:
        return

    totalizer = models.TotalStats.objects.get_or_create(redir=redirect)
    totalizer[0].accesses += 1
    totalizer[0].save()

    stat = models.Statistic(redir=redirect,
                    referrer=request.META.get('HTTP_REFERER', '')[0:249],
                    user_agent=request.META.get('HTTP_USER_AGENT', '')[0:249],
                    ip_address=get_real_ip(request))
    stat.save()

def show_blank_home(request):
    return HttpResponse('tiny; a personalized <a href="https://en.'
                        'wikipedia.org/wiki/URL_shortening">link shortener</a> '
                        'service')

def do_redirect(request, srcuri):
    """ Handle the redirect.

    Does the ``srcuri`` exist as an object in our database?
       YES:
           Does it begin with "http"?
               YES: then track it (stats), and do the redirect.
               NO:  append the STATIC_URL in front, and return it back

       NO: it might be static media on the server. Serve it.
           Obviously if it is not static media, then the server will 404.
    """
    srcuri = srcuri.replace('$','').replace('(', '').replace(')', '').strip()
    try:
        redirect = models.Redirect.objects.get(source=srcuri,
                                               is_active=True)
        logger.debug('REQ [{0}]: {1}'.format(get_real_ip(request),
                                             srcuri))
        track_statistics(request, redirect)
        if redirect.destination.startswith('http'):
            return HttpResponseRedirect(redirect.destination,
                                        status=redirect.status_code)
        else:
            raise ForceStatic()

    except ForceStatic:
        logger.warn('FORCED MEDIA: {0}'.format(srcuri))
        return HttpResponseRedirect(settings.STATIC_URL + redirect.destination,
                                    status=redirect.status_code)

    except models.Redirect.DoesNotExist:
        redirect, created = models.Redirect.objects.get_or_create(source=srcuri,
                                                        destination=srcuri,
                                                        extra_info='Auto(FAIL)',
                                                        is_active=True,
                                                        is_logged=True)
        track_statistics(request, redirect)

        if os.path.exists(settings.STATIC_ROOT + srcuri) and created:
            logger.info('AUTO created redirect: {0}'.format(str(redirect)))
        else:
            logger.warn('FAIL: {0}'.format(srcuri))
            redirect.delete()

        return HttpResponseRedirect(settings.STATIC_URL + srcuri)
