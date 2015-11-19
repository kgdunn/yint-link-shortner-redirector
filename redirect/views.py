from django.shortcuts import render, HttpResponse, HttpResponseRedirect, Http404
import logging
from . import models

logger = logging.getLogger(__name__)
logger.debug('A new call to the views.py file')

def show_blank_home(request):
    return HttpResponse('tiny; a personalized <a href="https://en.'
                        'wikipedia.org/wiki/URL_shortening">link shortener</a> '
                        'service')

def do_redirect(request, srcuri):
    #if srcuri.lower() == 'favicon.ico':
    #    return Http404('')

    srcuri = srcuri.replace('$','').replace('(', '').replace(')', '')
    try:
        source = models.Redirect.objects.get(source=srcuri.strip())
        logger.debug('{0}'.format(srcuri))
        return HttpResponseRedirect(source.destination, status=301)

    except models.Redirect.DoesNotExist:
        logger.warn('NOT FOUND: {0}'.format(srcuri))
        return show_blank_home(request)