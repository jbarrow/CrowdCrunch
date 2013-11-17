from django.views.generic import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

import re
import random

from django.http import HttpResponse
from cruncher.models import *

from cruncher.payment.payment import make_transaction

from cruncher.jobs.txtconfig import *
from cruncher.jobs.txtl import *
from cruncher.jobs.names import all_names, num_names
from cruncher.queuer.bridge import *

p = re.compile(".*?(\d) stars?")
b = re.compile(".*?budget (\d+) credits?")

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
			if message == "learn":
				# Respond with specific help
				return HttpResponse(respond_with_message("Reply 'offline' to go offline, 'accept' to accept job, or 'decline' to decline job."))

			if message == "decline":
				# Decline the job
				j = get_last_work_request(user)
				clear_job_request_for_user(user)
				QueueJob(Job.objects.get(id=j))
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
				j.worker = user.user_id
				j.save()

				return HttpResponse(respond_with_message("This job's name is " + n + " please start future messages to it with the name. Text '" + n + ", I'm finished' when you are done."))

			if message == "offline":
				# offline sending the user texts
				clear_job_request_for_user(user)
				user.MarkUnavailable()
				return HttpResponse(respond_with_message("You are now marked as offline. Send 'crunchtime' to us again to start receiving jobs."))

			return HttpResponse(respond_with_message("I didn't understand. Please reply with 'accept', 'decline' or 'offline'."))

		# Handle help
		if message == "learn":
			return HttpResponse(respond_with_message("Text a request and we will forward it to your personal assistant."))

		body = request.POST["Body"]
		name = re.split("\W+", body.lower())[0]

		if user_has_name(user, name):
			# They are replying to a job... Let's log that.
			j = get_job_info(user, name)

			message = body[len(name):]

			if "pay" in message.lower():
				data = re.split("\W+", message.lower())
				address = data[data.index("pay") + 1]
				amount = data[data.index("pay") + 2]
				if float(amount) <= (2/460) * j[0].cost:
					make_transaction(address, amount)
					return HttpResponse(respond_with_message("The payment has been successfully made."))
				else:
					return HttpResponse(respond_with_message("That amount is not budgeted for this job. Why don't you contact the owner?"))

			if "decline" in message.lower() and j[1] == 2:
				user.StopWorking()

				j[0].status = 0
				j[0].worker = None
				j[0].save()
				QueueJob(j[0])

				return HttpResponse(respond_with_message("We have ended your involvement with that job. Expect another job coming soon."))

			# Frank accept 5 stars
			if "accept" in message.lower() and j[1] == 1 and j[0].status == 2:
				j[0].status = 3

				m = p.match(message.lower())
				rating = 0
				if m != None:
					rating = int(m.group(1))
				j[0].rating = rating

				j[0].save()
				j[0].Complete()

				QueueTextToUser(UserProfile.Get(j[0].worker).phone_number, "The task you were working on was accepted.")
				return HttpResponse(respond_with_message("You have accepted the work, the worker will be credited."))

			if "reject" in message.lower() and j[1] == 1 and j[0].status == 2:
				j[0].status = 4
				j[0].save()
				j[0].Complete()

				QueueTextToUser(UserProfile.Get(j[0].worker).phone_number, "The task you were working on was rejected.")
				return HttpResponse(respond_with_message("I'm sorry to here that you have rejected the work. Should we try again?"))

			if "i'm finished" in message.lower() and j[1] == 2:
				user.StopWorking()
				j[0].status = 2
				j[0].save()

				other_profile = UserProfile.Get(j[0].owner)
				name = get_name_for_user_job(other_profile, j[0])

				QueueTextToUser(UserProfile.Get(j[0].owner).phone_number, "Your task, " + name + ", has been completed.")
				return HttpResponse(respond_with_message("Good work. We will send you another job as it becomes available."))

			Communication.Log(j[0], message, j[1])

			other = j[0].owner
			# if this is from the owner
			if j[1] == 1:
				other = j[0].worker

			other_profile = UserProfile.Get(other)

			person_name = get_name_for_user_job(other_profile, j[0])

			QueueTextToUser(other_profile.phone_number, "From " + person_name + " : " + message)

			return HttpResponse(dont_respond())
		else:
			# The are creating a new job. Let's tell them.

			the_budget = 0
			m = b.match(body.lower())
			if m != None:
				the_budget = int(m.group(1))

			j = Job.Create(body, the_budget, user.user_id)

			if (j):
				QueueJob(j)
				n = get_random_name(user)
				set_job_for_user(user, n.lower(), j.id, JOB_OWNER)
				return HttpResponse(respond_with_message("We have created your job. It is being sent to " + n + " as we speak. Please start messages regarding this job with " + n + "."))

			return HttpResponse(respond_with_message("It looks like you don't have enough credits to make that request. Please login online and buy some more."))

	@method_decorator(csrf_exempt)
	def dispatch(self, *args, **kwargs):
		return super(TwilioView, self).dispatch(*args, **kwargs)