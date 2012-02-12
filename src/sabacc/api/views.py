import django.http
import django.utils.simplejson as json


def index(request):
    return django.http.HttpResponse(json.dumps({}))
