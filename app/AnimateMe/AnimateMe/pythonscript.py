import os

def say_hello():
	return "This is a test"

def test(message):
	directory = os.getcwd()
	return message + ":" + directory