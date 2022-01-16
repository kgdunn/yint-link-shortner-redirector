from django.urls import re_path

from . import views

# A-Z, a-z, 0-9, .#/-?
URI = r"\S+$"
app_name = "redirect"
urlpatterns = [
    re_path(r"^$", views.show_blank_home, name="show_blank_home"),
    re_path(r"^(?P<srcuri>" + URI + r")$", views.do_redirect, name="do_redirect"),
]
