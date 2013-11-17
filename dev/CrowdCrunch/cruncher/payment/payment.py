from django.views.generic import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

import requests
import json

from django.http import HttpResponse

from cruncher.models import *
from django.contrib.auth.models import User

def make_transaction(wallet_address, amount):
	payload = {'transaction': {'to': wallet_address, 'amount': amount}}
	headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
	r = requests.post('https://coinbase.com/api/v1/transactions/send_money?api_key=a3f2f28e1c8072efd73cb761895d4ce7ab0a47672256ed497875aa6674c3bf51', data=json.dumps(payload), headers=headers)
	return json.loads(r.text)[u'status']


class CoinBaseView(View):
	def post(self, request, **kwargs):
		if json.loads(request.body)[u'order'][u'status'] == "completed":
			# Find the user and grant them tokens
			user = UserProfile.Get(User.Get(id=json.loads(request.body)[u'order'][u'custom']))
			user.AddCredits(5)
		return HttpResponse()

	@method_decorator(csrf_exempt)
	def dispatch(self, *args, **kwargs):
		return super(CoinBaseView, self).dispatch(*args, **kwargs)