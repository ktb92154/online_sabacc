from django.utils import unittest

from . import game_test

def suite():
    loader = unittest.TestLoader()
    return loader.loadTestsFromTestCase(game_test.GameTests)
