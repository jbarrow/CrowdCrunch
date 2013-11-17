from django.views.generic import View

from django.http import HttpResponse
from texting.texting import *

class TwilioView(View):
	def post(self, request, **kwargs):
		# pass
		# send_verify_token("6787630677")
		return HttpResponse("Hello, world.")