from django.conf.urls import url
from . import views

#A-Z, a-z, 0-9, .#/-?
URI = r'\S+$'

urlpatterns = [
    url(r'^$', views.show_blank_home, name='show_blank_home'),

    # ex:
    url(r'^(?P<srcuri>'+ URI + r')$', views.do_redirect,
        name='do_redirect'),
]
