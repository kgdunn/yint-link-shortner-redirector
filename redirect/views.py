from django.shortcuts import render, HttpResponse, HttpResponseRedirect, Http404
import logging
from . import models

logger = logging.getLogger(__name__)
logger.debug('A new call to the views.py file')


from django.conf import settings

class ForceStatic(Exception):
    pass

def track_statistics(request, redirect):
    """Track statistics related to each link request"""
    pass

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
    srcuri = srcuri.replace('$','').replace('(', '').replace(')', '')
    try:
        redirect = models.Redirect.objects.get(source=srcuri.strip())
        logger.debug('{0}'.format(srcuri))
        track_statistics(request, redirect)
        if redirect.destination.startswith('http'):
            return HttpResponseRedirect(redirect.destination, status=301)
        else:
            raise ForceStatic()

    except ForceStatic:
        logger.warn('FORCED MEDIA: {0}'.format(srcuri))
        return HttpResponseRedirect(settings.STATIC_URL + redirect.destination)

    except models.Redirect.DoesNotExist:
        logger.warn('FAIL: {0}'.format(srcuri))
        raise Http404('Not found.')