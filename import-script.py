import os
import django
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
import yint.settings
os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "yint.settings"
)
django.setup()



#settings.configure(
    #DATABASES = {
    #'default': {
        #'ENGINE': 'django.db.backends.sqlite3',
        #'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
        #}
    #},
    #TIME_ZONE='America/Montreal',
#)


from redirect.models import Redirect


fobj = file('existing-redirects.txt', 'rt')
for line in fobj.readlines():

    line = line.strip()
    if line.strip().startswith('#') or line.strip()=='':
        continue

    if line.startswith('RewriteRule'):
        line = line[line.find('^')+1:]
    else:
        assert(False)


    source, rest = line.split('$')
    source = source.strip('/').strip('^')
    destination = rest.strip()
    #rest = rest.split('[')
    print(rest)

    redir = Redirect.objects.get_or_create(source=source,
                                            destination=destination,
                                            status_code=302,
                                            is_logged=True,
                                            is_active=True)

    redir.save()



fobj.close()