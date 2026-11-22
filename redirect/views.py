import ipaddress
import logging
from pathlib import Path

from django.conf import settings
from django.db.models import F
from django.http import Http404
from django.shortcuts import HttpResponse, HttpResponseRedirect
from django.utils import timezone
from django.views.decorators.cache import never_cache

from . import models

logger = logging.getLogger(__name__)
logger.debug("Starting views.py file")


# If a user downloads the same file more than 5 times in this interval, then
# they will be blocked
THROTTLE_SECONDS = 15 * 60


def get_IP_address(request) -> str | None:
    """
    Returns the visitor's IP address given the Django ``request``, or None.

    Caddy sets X-Real-IP to the client address (resolved from Cloudflare's
    header). X-Forwarded-For can hold a chain "client, proxy1, ..."; only its
    first entry is the client. REMOTE_ADDR is the proxy itself, so it is the
    last resort. A value that is not an IP address is dropped, because the
    database column only accepts addresses.
    """
    meta = request.META
    candidates = (
        meta.get("HTTP_X_REAL_IP", ""),
        meta.get("HTTP_X_FORWARDED_FOR", "").split(",")[0],
        meta.get("REMOTE_ADDR", ""),
    )
    for value in candidates:
        try:
            return str(ipaddress.ip_address(value.strip()))
        except ValueError:
            continue
    return None


def is_static_file(srcuri: str) -> bool:
    """True if ``srcuri`` names an existing file inside STATIC_ROOT."""
    root = Path(settings.STATIC_ROOT).resolve()
    target = (root / srcuri).resolve()
    return target.is_relative_to(root) and target.is_file()


class ForceStatic(Exception):
    pass


def track_statistics(request, redirect):
    """Track statistics related to each link request"""

    if redirect.is_logged is False:
        return

    totalizer, _ = models.TotalStats.objects.get_or_create(redir=redirect)
    # Add one inside the database, so two simultaneous visits both count.
    models.TotalStats.objects.filter(pk=totalizer.pk).update(
        accesses=F("accesses") + 1, last_access=timezone.now()
    )
    models.Statistic.objects.create(
        redir=redirect,
        referrer=request.META.get("HTTP_REFERER", "")[0:249],
        user_agent=request.META.get("HTTP_USER_AGENT", "")[0:249],
        ip_address=get_IP_address(request),
    )


def show_blank_home(request):
    return HttpResponse(
        'tiny; a personalized <a href="https://en.'
        'wikipedia.org/wiki/URL_shortening">link shortener</a> '
        "service; any issues? contact kgdunn @ gmail.com"
    )


# Cloudflare caches responses for paths ending in .pdf, .mp4 and the like.
# A cached redirect never reaches the app, so the visit would go uncounted.
@never_cache
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
        delta = timezone.now() - prior_downloads[4].accessed

        # total_seconds(), not .seconds: the latter drops whole days, so five
        # downloads spread over several days could look like a burst.
        if delta.total_seconds() < THROTTLE_SECONDS:
            logger.warning(f"BLOCKED [{ip_address}]: {srcuri}")
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
        logger.info(f"FORCED MEDIA: {srcuri}")
        return HttpResponseRedirect(
            settings.STATIC_URL + redirect.destination, status=redirect.status_code
        )

    except models.Redirect.DoesNotExist:
        # A deactivated link gives a 404, as the model's help text promises.
        if models.Redirect.objects.filter(source=srcuri).exists():
            raise Http404()

        # Only a path naming a real file under STATIC_ROOT becomes a link.
        # Anything else (mostly bots probing for wp-config.php, .env and the
        # like) writes nothing and is sent on to /static/, which gives a 404.
        if is_static_file(srcuri):
            redirect, created = models.Redirect.objects.get_or_create(
                source=srcuri,
                defaults={"destination": srcuri, "extra_info": "Auto"},
            )
            track_statistics(request, redirect)
            if created:
                logger.info(f"AUTO created redirect: {redirect}")
        else:
            logger.warning(f"FAIL: {srcuri}")

        return HttpResponseRedirect(settings.STATIC_URL + srcuri)
