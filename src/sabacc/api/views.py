import django.contrib.auth as auth
from django.contrib.auth.decorators import login_required

from .viewhelpers import json_output, make_url


API_VERSION = 0.1


@json_output
def logout(request):
    if not request.user.is_authenticated():
        return "Not logged in"
    auth.logout(request)
    return "Successfully logged out"


@login_required
@json_output
def index(request):
    """API version and navigation"""
    return {
        "api_version": API_VERSION,
        "navigation": {
            "logout": make_url(request, logout),
        },
    }
