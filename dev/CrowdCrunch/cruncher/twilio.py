from django.views.generic import View

from django.http import HttpResponse
from texting.texting import *

class TwilioView(View):
	def get(self, request, **kwargs):
		return HttpResponse("Hello, world.")