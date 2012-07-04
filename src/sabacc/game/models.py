#from django.db import models
from django.utils.importlib import import_module

import interfacer.models as interfacer


class UnloadedGame(object):

    def __getattr__(self, attr):
        raise RuntimeError("Game is no longer loaded")


class GameWrapper(object):

    """This class exists to wrap the old Game interface in something a
       little more friendly"""
    # TODO: get rid of the need for this class

    def __init__(self, game):
        self._game = game
        self._game.interface = interfacer.GameInterface()

    def __getattr__(self, attr):
        return getattr(self._game, attr)

    def _add_player(self, interface):
        self._game.names.append(interface.name)
        self._game.loaded.append((interfacer.InterfaceWrapper(interface), [],
                                 True))
        self._game.players_in_game += 1

    def add_player_from_user(self, user):
        return self._add_player(user.game_interface)

    def add_dummy_computer_player(self):
        return self._add_player(
            interfacer.make_from_file("agents/Example.xml"))

    def start(self):
        return self._game.start_game()

    def unload(self):
        self._game = UnloadedGame()
        return Game.unload()


class Game(object):

    # TODO: make this a real model

    _game_loaded = False

    @classmethod
    def load(cls):
        # FIXME remove this restriction
        assert not cls._game_loaded, "Only one game may be loaded at a time"
        mod = import_module("old_sabacc.back.Game")
        cls._game_loaded = True
        return GameWrapper(mod)

    @classmethod
    def unload(cls):
        # TODO: we also need to unload the game module from memory but there's
        # no easy way to mandate that.
        cls._game_loaded = False
