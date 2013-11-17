from django.views.generic import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from django.http import HttpResponse
from texting.texting import *
from cruncher.models import *

class TwilioView(View):
	def post(self, request, **kwargs):
		user = UserProfile.GetFromPhone(request.POST["From"])
		print request.POST
		if(user == False):
			return HttpResponse(respond_with_message("You aren't a CrowdCrunch member. Sign up at http://crowdcrunch.com!"))
		return HttpResponse(dont_respond())

	@method_decorator(csrf_exempt)
	def dispatch(self, *args, **kwargs):
		return super(TwilioView, self).dispatch(*args, **kwargs)