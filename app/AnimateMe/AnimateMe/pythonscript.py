"""
Module for basic Python functions.
"""

import os


def say_hello():
    """
    Return a test message.
    """
    return "This is a test"


def test(message):
    """
    Append current directory to message.
    """
    directory = os.getcwd()
    return message + ":" + directory