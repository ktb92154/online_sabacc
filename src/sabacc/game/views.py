from django.core.urlresolvers import reverse
import django.http

import api.views


def index(request):
    return django.http.HttpResponse(
        "Nothing to see here yet. Please check out the "
        "<a href=\"%s\">API</a>." % reverse(api.views.index))
