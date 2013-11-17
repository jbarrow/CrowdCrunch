from rq import Queue
from worker import conn

from cruncher.jobs.txtl import send_text, send_verify_token

import time

from cruncher.models import *

q = Queue(connection=conn)

def SendVerifyToUser(phone):
	q.enqueue(send_verify_token, phone)

def QueueTextToUser(phone, message):
	q.enqueue(send_text, phone, message)

def WorkerJobRunner(job):
	user = None
	while user == None:
		try:
			user = UserProfile.objects.filter(status=1)[0]
		except:
			time.sleep(1)
			continue

	QueueTextToUser(user.phone, "You have been assigned the job (reply with accept, decline, or stop): " + job.description)


def QueueJob(job):
	q.enqueue(WorkerJobRunner, job)