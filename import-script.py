import os
import django
import urllib2


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
import yint.settings
os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "yint.settings"
)
django.setup()

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
    destination = rest.strip().split('[')

    status_code = 302
    if len(destination) > 1:
        if destination[1].find('R=') >= 0:
            status_code = 307
    destination = destination[0].strip()

    print(destination)

    # Testing the URLs
    try:
        req = urllib2.Request('http://yint.org/' + source)
        response = urllib2.urlopen(req)
        the_page = response.read()

        print('***: ' + the_page[0:100])
        print('-----------------')
    except Exception as e:
        print('Error:' + str(e))
        print('-----------------')


    # This was how I originally converted the .htaccess file into the Django DB
    # --------
    #redir, created = Redirect.objects.get_or_create(source=source.strip(),
                                            #destination=destination.strip(),
                                            #status_code=status_code,
                                            #is_logged=True,
                                            #is_active=True)
    #redir.save()




fobj.close()