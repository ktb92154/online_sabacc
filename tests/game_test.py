"""
Tests for the game module
"""
import unittest

import sabacc.back.Game as game


class GameTests(unittest.TestCase):

    def test_end_to_end(self):
        game.start_game()


if __name__ == "__main__":
    unittest.main()