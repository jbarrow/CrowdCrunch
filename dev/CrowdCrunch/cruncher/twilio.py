from django.views.generic import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

import re

from django.http import HttpResponse
from texting.texting import *
from cruncher.models import *

user_map = dict()

names = [name.strip() for line in open('names.txt')]

class TwilioView(View):
	def post(self, request, **kwargs):
		user = UserProfile.GetFromPhone((request.POST["From"])[2:])

		if(user == False):
			return HttpResponse(respond_with_message("You aren't a CrowdCrunch member. Sign up at http://crowdcrunch.com!"))

		message = ''.join(re.split('\W+', request.POST["Body"].lower()))

		print message

		if message == "crunchtime":
			if(user.status == 0):
				return HttpResponse(respond_with_message("Finish one thing before you start another."))
			else:
				return HttpResponse(respond_with_message("You've been marked as available! Expect to hear back soon."))

		# Handle help
		if message == "help":
			return HttpResponse(respond_with_message("Go to http://crowdcrunch.com/help for help!"))

		if message == "decline":
			# Decline the job

		if message == "stop":
			# Stop sending the user texts

		# The real fucking magic
		if user.id in user_map[user.id]:

		else:
			# The user has never created a job before. That means that this
			# is not a help request so they must be creating a job
			user_map[user.id] = dict()
			return HttpResponse(respond_with_message("Your job has been added. What is your budget in USD?"))

		return HttpResponse(dont_respond())

	@method_decorator(csrf_exempt)
	def dispatch(self, *args, **kwargs):
		return super(TwilioView, self).dispatch(*args, **kwargs)

def get_new_name_for_user(user_id):