from twilio.rest import TwilioRestClient
from twilio import twiml

from string import digits
from random import choice

#from CrowdCrunch import settings
#from cruncher.models import *

account = "AC61b168a14cd3c4c2d480006903327506"
token = "3dc14327f5d7a9e883702bdbbe2648aa"
client = TwilioRestClient(account, token)

def generate_token():
	return ''.join(choice(digits) for i in xrange(4))

def send_verify_token(number):
	"""
	It generates a token, sends it to the number, and returns
	the token to be stored in the databse
	"""
	token = generate_token()
	client.messages.create(to=number, from_="+17039978527", body="Your token is: " + token)
	return token

def dont_respond():
	return str(twiml.Response())

def respond_with_message(message):
	r = twiml.Response()
	r.message(message)
	return str(r)