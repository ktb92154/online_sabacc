"""
Tests for the game module
"""
import random
import unittest

import mox

import sabacc.back.Agents as agents
import sabacc.back.Game as game

# TODO: Move this to a common location
class MockableTestCase(unittest.TestCase):
    
    def __init__(self, *args, **kwargs):
        super(MockableTestCase, self).__init__(*args, **kwargs)
        self.mocker = mox.Mox()
        self.addCleanup(self.mocker.UnsetStubs)
        
        
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
        

class GameTests(MockableTestCase):
    
    def setUp(self):
        self.messages = []
        game.interface = DummyInterface(self)
        self.addCleanup(game.reset)
        def unset_game_things():
            game.interface = None
            game.game_in_progress = False
        self.addCleanup(unset_game_things)
        self.mocker.StubOutWithMock(random, "shuffle", lambda thing: thing)
        
    def _put_players_in_game(self, players):
        for player in players:
            game.names.append(player.name)
            game.loaded.append((player, [], True))
            game.players_in_game += 1

    def test_only_one_player_has_credits(self):
        """SF Bug:1884682
        If none of the players can afford the initial ante except for one,
        that player is declared the winner and gets the 'winnings'.
        Unfortunately in this case the 'winnings' consist of only half of what
        the player paid to get into the game in the first place, as he doesn't
        win whatever was in the Sabacc pot."""
        rich = self.mocker.CreateMock(agents.HumanAgent, {
            "name": "Richard", "credits": 1000, "quit_next_turn": False})
        poor = self.mocker.CreateMock(agents.HumanAgent, {
            "name": "Pablo", "credits": 0, "quit_next_turn": False})
        self._put_players_in_game([rich, poor])
        game.start_game(10)
        self.assertEqual(rich.credits, 1000)
        self.assertEqual(poor.credits, 0)
        self.assertEqual(self.messages, [
            "Pablo could not afford the buy into the game",
            "The game was won by Richard.",
            "Pablo re-entered the game"])
        self.assertEqual((game.hand_pot, game.sabacc_pot), (0, 0))
        
    def test_no_winners(self):
        """If there are no winners, winnings will not stay in the hand pot"""
        winner = self.mocker.CreateMock(agents.HumanAgent, {
            "name": "William Winner", "credits": 20, "quit_next_turn": False})
        loser = self.mocker.CreateMock(agents.HumanAgent, {
            "name": "Larry Loser", "credits": 20, "quit_next_turn": True})
        winner.bet = lambda *a: 0
        loser.bet = lambda *a: -1
        self._put_players_in_game([winner, loser])
        game.start_game(10)
        self.assertEqual(self.messages, [
            "%s left the game" % loser.name,
            "The game was won by %s." % winner.name])
        self.assertEqual(game.hand_pot, 0)
        self.assertEqual(game.sabacc_pot, 20)
        
    def test_maximum_bet_too_high(self):
        """Try to bet more than another player has"""
        rich = self.mocker.CreateMock(agents.HumanAgent, {
            "name": "Richard", "credits": 1000, "quit_next_turn": False})
        poor = self.mocker.CreateMock(agents.HumanAgent, {
            "name": "Pablo", "credits": 20, "quit_next_turn": False})
        self._put_players_in_game([rich, poor])
        with self.assertRaises(self.failureException) as context:
            game.start_game(10)
        self.assertEqual(context.exception.message,
                         "You cannot bet more than another player has!")


if __name__ == "__main__":
    unittest.main()