from rq import Queue
from worker import conn

from cruncher.jobs.txtl import send_text, send_verify_token

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
			tmp = UserProfile.objects.filter(status=1)
			if job.budget > 0.0:
				for v in tmp:
					if v.BudgetEligible():
						user = v
						break
				raise Exception("Couldn't find a good user.")
			else:
				user=tmp[0]
		except Exception as inst:
			time.sleep(1)

	set_job_request_for_user(user, job.id)
	QueueTextToUser(user.phone_number, "You have been assigned the job (reply with accept, decline, or stop): " + job.description)

def QueueJob(job):
	q.enqueue(WorkerJobRunner, job)