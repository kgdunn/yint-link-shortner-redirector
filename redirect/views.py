from django.shortcuts import render, HttpResponse, HttpResponseRedirect

# Create your views here.
def show_blank_home(request):
    return HttpResponse('tiny; a personalized <a href="https://en.'
                        'wikipedia.org/wiki/URL_shortening">link shortener</a> '
                        'service')

def do_redirect(request, srcuri):
    return HttpResponseRedirect('http://google.com')