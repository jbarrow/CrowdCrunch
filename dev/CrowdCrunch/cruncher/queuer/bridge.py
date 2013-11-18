from rq import Queue
from worker import conn

from cruncher.jobs.txtl import send_text, send_verify_token

from django.db.models import Q

import time

from cruncher.models import UserProfile
from cruncher.jobs.txtconfig import *

q = Queue(connection=conn)

def SendVerifyToUser(phone):
	q.enqueue(send_verify_token, phone)

def QueueTextToUser(phone, message):
	q.enqueue(send_text, phone, message)

def WorkerJobRunner(job):
	user = None
	while user == None:
		try:
			# Algorithm in Finding User
			# print "Welcome"

			tmp = UserProfile.objects.filter(~Q(user_id_id=job.owner.id), status=1)

			if job.cost > 0.0:
				# print job.budget
				# print "Hello"
				for v in tmp:
					if v.BudgetEligible():
						user = v
						break
				if user == None:
					raise Exception("Couldn't find a good user.")
			else:
				# print "No budget"
				user=tmp[0]
		except Exception as inst:
			# print inst
			time.sleep(1)

	set_job_request_for_user(user, job.id)
	QueueTextToUser(user.phone_number, "You have been assigned the job (reply with accept, decline, or stop): " + job.description)

def QueueJob(job):
	q.enqueue(WorkerJobRunner, job)