# Creates links for the OOI materials: MP4, Script, Captions
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

# Exported from Google Docs
# https://docs.google.com/spreadsheets/d/1AD5xSEPCcWDO4EGp3A55sIDBZbR0kJz2WM6KdlxXG2s/

fobj = file('ooi-redirects.csv', 'rt')
for idx, line in enumerate(fobj.readlines()):

    if idx < 2:
        continue

    line = line.strip().split(',')

    redir_base = line[6]
    if len(redir_base.strip()) == 0:
        continue

    video_src = redir_base + '.mp4'
    gDoc_src = redir_base + '-script'
    caption_src = redir_base + '-captions'

    video_dst = line[9]
    gDoc_dst = line[5].strip('/edit')
    caption_dst = video_dst.replace('.mp4', '.srt')

    status_code = 307

    # Testing the URLs
    #try:
        #req = urllib2.Request('http://yint.org/' + video_src)
        #response = urllib2.urlopen(req)
        #the_page = response.read()

        #print('***: ' + the_page[0:100])
        #print('-----------------')
    #except Exception as e:
        #print('Error:' + str(e))
        #print('-----------------')


    #------
    redir, created = Redirect.objects.get_or_create(source=video_src.strip(),
                                            destination=video_dst.strip(),
                                            status_code=status_code,
                                            is_logged=True,
                                            is_active=True)
    redir.extra_info = 'OOI-4C3'
    redir.save()

    #------
    redir, created = Redirect.objects.get_or_create(source=gDoc_src.strip(),
                                            destination=gDoc_dst.strip(),
                                            status_code=status_code,
                                            is_logged=True,
                                            is_active=True)
    redir.extra_info = 'OOI-4C3'
    redir.save()

    #------
    redir, created = Redirect.objects.get_or_create(source=caption_src.strip(),
                                            destination=caption_dst.strip(),
                                            status_code=status_code,
                                            is_logged=True,
                                            is_active=True)
    redir.extra_info = 'OOI-4C3'
    redir.save()





fobj.close()
