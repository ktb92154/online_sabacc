from gettext import gettext as _

from django.shortcuts import redirect

import django.contrib.auth as auth
from django.contrib.auth.decorators import login_required

from game import models

from .viewhelpers import json_output, make_url


API_VERSION = 0.1


@json_output
def logout(request):
    # TODO: The API should have no concept of login/logout.
    # Use tokens instead
    if not request.user.is_authenticated():
        return _("Not logged in")
    auth.logout(request)
    return _("Successfully logged out")


def start_game(request):
    # TODO: convert this into a context manager
    game = models.Game.load()
    try:
        game.add_player_from_user(request.user)
        game.add_dummy_computer_player()
        game.start()  # This not only starts, but also finishes the game
    finally:
        game.unload()
    return redirect(index)


@login_required
@json_output
def index(request):
    """API version and navigation"""
    return {
        "api_version": API_VERSION,
        "navigation": {
            _("Log out"): make_url(request, logout),
            _("Start game"): make_url(request, start_game),
        },
    }
