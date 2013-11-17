from django.views.generic import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

import re
import random

from django.http import HttpResponse
from cruncher.models import *

from cruncher.jobs.txtconfig import *
from cruncher.jobs.txtl import *
from cruncher.jobs.names import all_names, num_names
from cruncher.queuer.bridge import *

def get_random_name(user):
	while(True):
		n = random_name()
		if not user_has_name(user, n):
			return n
	return False


def random_int(max_value):
	return random.randrange(0, max_value)

def random_name():
	i = random_int(num_names)
	return all_names[i]

class TwilioView(View):
	def post(self, request, **kwargs):
		user = UserProfile.GetFromPhone((request.POST["From"])[2:])

		# User is not registered
		if(user == False):
			return HttpResponse(respond_with_message("You aren't a CrowdCrunch member. Sign up at http://crowdcrunch.com!"))

		message = ''.join(re.split('\W+', request.POST["Body"].lower()))

		# User wants to go online
		if message == "crunchtime":
			if(user.status == 3 or user.status == 1):
				return HttpResponse(respond_with_message("Finish one thing before you start another."))
			else:
				user.MarkAvailable()
				return HttpResponse(respond_with_message("You've been marked as available! Expect to receive a job soon."))

		# Is the user responding to a work request?
		if user_has_last_work_request(user):
			if message == "help":
				# Respond with specific help
				return HttpResponse(respond_with_message("Reply 'offline' to go offline, 'accept' to accept job, or 'decline' to decline job."))

			if message == "decline":
				# Decline the job
				clear_job_request_for_user(user)
				return HttpResponse(dont_respond())

			if message == "accept":
				# Accept the job
				j = get_last_work_request(user)

				clear_job_request_for_user(user)
				n = get_random_name(user)
				set_job_for_user(user, n.lower(), j, JOB_WORKER)
				user.StartWorking()

				j = Job.objects.get(id = j)
				j.status = 1
				j.save()

				return HttpResponse(respond_with_message("This job's name is " + n + " please start future messages to it with the name. Text '" + n + ", I'm finished' when you are done."))

			if message == "offline":
				# offline sending the user texts
				clear_job_request_for_user(user)
				user.MarkUnavailable()
				return HttpResponse(respond_with_message("You are now marked as offline. Send 'crunchtime' to us again to start receiving jobs."))

			return HttpResponse(respond_with_message("I didn't understand. Please reply with 'accept', 'decline' or 'offline'."))

		# Handle help
		if message == "help":
			return HttpResponse(respond_with_message("Text a request and we will forward it to your personal assistant."))

		body = request.POST["Body"]
		name = re.split("\W+", body.lower())[0]

		if user_has_name(user, name):
			# They are replying to a job... Let's log that.
			j = get_job_info(user, name)
			print j

			message = body[len(name):]

			if "decline" in message.lower():
				user.StopWorking()

				j[0].status = 0
				j[0].save()
				QueueJob(j[0])

				return HttpResponse(respond_with_message("We have ended your involvement with that job. Expect another job coming soon."))


			if "i'm finished" in message.lower():
				user.StopWorking()
				j[0].status = 2
				j[0].save()
				return HttpResponse(respond_with_message("Good work. We will send you another job as it becomes available."))

			Communication.Log(j[0], message, j[1])

			other = j[0].owner
			person_name = "Owner"
			# if this is from the owner
			if j[1] == 2 and j[0].worker:
				person_name = "Worker"
				other = j[0].worker

			other_profile = UserProfile.Get(other)

			QueueTextToUser(other_profile.phone_number, "From " + person_name + " : " + message)

			return HttpResponse(dont_respond())
		else:
			# The are creating a new job. Let's tell them.

			j = Job.Create(body, 0.0, user.user_id)

			if (j):
				QueueJob(j)
				n = get_random_name(user)
				set_job_for_user(user, n.lower(), j.id, JOB_OWNER)
				return HttpResponse(respond_with_message("We have created your job. It is being sent to " + n + " as we speak. Please start messages regarding this job with " + n + "."))

			return HttpResponse(respond_with_message("It looks like you don't have enough credits to make that request. Please login online and buy some more."))

	@method_decorator(csrf_exempt)
	def dispatch(self, *args, **kwargs):
		return super(TwilioView, self).dispatch(*args, **kwargs)