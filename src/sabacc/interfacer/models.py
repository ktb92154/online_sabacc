import os

from django.conf import settings
from django.db import models

from django.contrib.auth.models import User

from . import xmlloader

class UserInterface(models.Model):

    user = models.OneToOneField(User, related_name="game_interface")

    @property
    def name(self):
        return "%s %s" % (self.user.first_name, self.user.last_name)


class ComputerInterface(object):

    def __init__(self, doc):
        self._agent = doc.find("agent")

    @property
    def name(self):
        return self._agent.get("name")


def create_user_interface(instance, created, **kwargs):
    if created:
        UserInterface.objects.create(user=instance)

models.signals.post_save.connect(create_user_interface, sender=User)


class GameInterface(object):

    """Static game interface class"""

    def write(self, msg):
        print msg # TODO: something a little more elegant

    def show_all_cards(self, cards):
        print "should be showing all cards here"


def make_from_file(filename):
    doc = xmlloader.load_file(os.path.join(settings.PROJECT_ROOT, filename))
    return ComputerInterface(doc)


class InterfaceWrapper(object):

    """This class exists to wrap the new interfaces in something the old Game
    interface can understand"""
    # TODO: get rid of the need for this class

    credits = 100 # TODO: Fix this arbitrary amount
    quit_next_turn = False # TODO: what's this all about?

    def __init__(self, interface):
        self._interface = interface

    def __getattr__(self, attr):
        return getattr(self._interface, attr)

    def examine_cards(self, cards):
        print "Should be examining cards"

    def bet(self, hand, this_player_must_match):
        print "Should be making a bet"
        return -1 # fold

    def game_over(self, won, cards):
        print "Should be logging the fact that we just lost"
