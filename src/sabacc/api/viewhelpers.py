from django.core.urlresolvers import reverse
import django.http
import django.utils.simplejson as json

import functools


def make_url(request, reversible):
    return request.build_absolute_uri(reverse(reversible))


def json_output(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        output = func(*args, **kwargs)
        return django.http.HttpResponse(json.dumps(output),
                                        content_type="application/json")
    return wrapper
