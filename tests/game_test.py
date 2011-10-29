"""
Tests for the game module
"""
import unittest

import mock

import sabacc.back.Game as game


class DummyInterface(object):
    
    def __init__(self, test):
        self._test = test
        
    def write_error(self, msg):
        self._test.fail(msg)
        
    def write(self, msg):
        self._test.messages.append(msg)
    
    def _do_nothing(self, *args, **kwargs):
        pass
    
    show_all_cards = _do_nothing
        

class GameTests(unittest.TestCase):

    def setUp(self):
        self.messages = []
        game.interface = DummyInterface(self)
        def unset_game_interface():
            game.interface = None
        self.addCleanup(unset_game_interface)
        self.addCleanup(game.reset)

    def test_only_one_player_has_credits(self):
        """SF Bug:1884682
        If none of the players can afford the initial ante except for one,
        that player is declared the winner and gets the 'winnings'.
        Unfortunately in this case the 'winnings' consist of only half of what
        the player paid to get into the game in the first place, as he doesn't
        win whatever was in the Sabacc pot."""
        rich = mock.Mock()
        rich.name = "Richard"
        rich.credits = 1000
        rich.quit_next_turn = False
        poor = mock.Mock()
        poor.name = "Pablo"
        poor.credits = 0
        poor.quit_next_turn = False
        game.names = [rich.name, poor.name]
        game.loaded = [(rich, [], True), (poor, [], True)]
        game.players_in_game = 2
        game.start_game(10)
        self.assertEqual(rich.credits, 1000)
        self.assertEqual(poor.credits, 0)
        self.assertEqual(self.messages, [
            "Pablo could not afford the buy into the game",
            "The game was won by Richard.",
            "Pablo re-entered the game"])
        self.assertEqual((game.hand_pot, game.sabacc_pot), (0, 0))


if __name__ == "__main__":
    unittest.main()