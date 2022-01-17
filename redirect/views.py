import datetime
import logging
import os

from django.conf import settings
from django.shortcuts import HttpResponse, HttpResponseRedirect
from django.utils.timezone import utc

from . import models

logger = logging.getLogger(__name__)
logger.debug("Starting views.py file")


# If a user downloads the same file more than 5 times in this interval, then
# they will be blocked
THROTTLE_SECONDS = 15 * 60


def get_IP_address(request) -> str:
    """
    Returns the visitor's IP address as a string given the Django ``request``.
    """
    # Catchs the case when the user is on a proxy
    ip = request.META.get("HTTP_X_FORWARDED_FOR", "")
    if ip == "" or ip.lower() in ("unkown",):
        ip = request.META.get("REMOTE_ADDR", "")  # User is not on a proxy
    if ip == "" or ip.lower() in ("unkown",):
        ip = request.META.get("HTTP_X_REAL_IP")
    return ip


class ForceStatic(Exception):
    pass


def track_statistics(request, redirect):
    """Track statistics related to each link request"""

    if redirect.is_logged is False:
        return

    totalizer = models.TotalStats.objects.get_or_create(redir=redirect)
    totalizer[0].accesses += 1
    totalizer[0].save()

    stat = models.Statistic(
        redir=redirect,
        referrer=request.META.get("HTTP_REFERER", "")[0:249],
        user_agent=request.META.get("HTTP_USER_AGENT", "")[0:249],
        ip_address=get_IP_address(request),
    )
    stat.save()
    return totalizer[0], stat


def show_blank_home(request):
    return HttpResponse(
        'tiny; a personalized <a href="https://en.'
        'wikipedia.org/wiki/URL_shortening">link shortener</a> '
        "service; any issues? contact kgdunn @ gmail.com"
    )


def do_redirect(request, srcuri):
    """Handle the redirect.

    Does the ``srcuri`` exist as an object in our database?
       YES:
           Does it begin with "http"?
               YES: then track it (stats), and do the redirect.
               NO:  append the STATIC_URL in front, and return it back

       NO: it might be static media on the server. Serve it.
           Obviously if it is not static media, then the server will 404.
    """
    ip_address = get_IP_address(request)
    srcuri = srcuri.replace("$", "").replace("(", "").replace(")", "").strip()
    redir_exists = True
    try:
        redirect = models.Redirect.objects.get(source=srcuri, is_active=True)
        prior_downloads = models.Statistic.objects.filter(
            ip_address=ip_address,
            redir=redirect,
            user_agent=request.META.get("HTTP_USER_AGENT", "")[0:249],
        ).order_by("-accessed")[:5]

    except models.Redirect.DoesNotExist:
        redir_exists = False

    if redir_exists and len(prior_downloads) == 5:
        delta = (
            datetime.datetime.now().replace(tzinfo=utc) - prior_downloads[4].accessed
        )

        if delta.seconds < THROTTLE_SECONDS:
            logger.warn(f"BLOCKED [{ip_address}]: {srcuri}")
            stat = models.Statistic(
                redir=redirect,
                ip_address=ip_address,
                referrer="BLOCKED ACCESS",
                user_agent=request.META.get("HTTP_USER_AGENT", "")[0:249],
            )
            stat.save()

            return HttpResponse(
                (
                    "Too many downloads in a short time. Please "
                    "download less aggressively. You may have a "
                    "virus/malware on your device that is causing "
                    "many, rapid downloads of the same file. Try "
                    "using another computer/device."
                ),
                status=503,
            )

    try:
        if redir_exists is False:
            raise models.Redirect.DoesNotExist

        logger.debug(f"REQ [{ip_address}]: {srcuri}")
        track_statistics(request, redirect)

        referer = request.META.get("HTTP_REFERER", "")
        if redirect.referer_constraint:
            if not (redirect.referer_constraint in referer):
                logger.debug(
                    f"REFERER NOT ALLOWED: [{referer}]: {redirect.referer_constraint}"
                )
                if redirect.customized_error:
                    return HttpResponse(redirect.customized_error)
                else:
                    return HttpResponse(
                        (
                            "You have accessed the link from a location that is not allowed."
                        )
                    )

        if redirect.destination.startswith("http"):
            return HttpResponseRedirect(
                redirect.destination, status=redirect.status_code
            )
        else:
            raise ForceStatic()

    except ForceStatic:
        logger.warn(f"FORCED MEDIA: {srcuri}")
        return HttpResponseRedirect(
            settings.STATIC_URL + redirect.destination, status=redirect.status_code
        )

    except models.Redirect.DoesNotExist:
        redirect, created = models.Redirect.objects.get_or_create(
            source=srcuri,
            destination=srcuri,
            extra_info="Auto(FAIL)",
            is_active=True,
            is_logged=True,
        )
        totalizer, statitem = track_statistics(request, redirect)
        if os.path.exists(str(settings.STATIC_ROOT) + srcuri) and created:
            logger.info(f"AUTO created redirect: {str(redirect)}")
        else:
            logger.warn(f"FAIL: {srcuri}")
            totalizer.delete()
            statitem.delete()
            redirect.delete()

        return HttpResponseRedirect(settings.STATIC_URL + srcuri)
