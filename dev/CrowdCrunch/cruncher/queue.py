from rq import Queue
from worker import conn

from cruncher.jobs.txtl import send_text, send_verify_token

from cruncher.models import *

q = Queue(connection=conn)

def SendVerifyToUser(phone):
	q.enque(send_verify_token, phone)

def QueueTextToUser(phone, message):
	q.enque(send_text, phone, message)

def QueueJob(job):
	user = UserProfile.objects.filter(status=1)[0]
	QueueTextToUser(user.phone, "You have been assigned the job (reply with accept, decline, or stop): " + job.description)