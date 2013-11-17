## Redis Interface for Twilio
from CrowdCrunch.settings import REDIS_URL
from worker import conn

from cruncher.models import *

## NAME CONTROL

def get_redis_key(user_id, name):
	return "cc:" + str(user_id) + ":" + name

def user_has_name(user, name):
	return (conn.get(get_redis_key(user.id, name)) != None)

def remove_name_for_user(user, name):
	conn.delete(get_redis_key(user.id, name))



JOB_OWNER  = 1
JOB_WORKER = 2
def get_job_info(user, name):
	c = conn.get(get_redis_key(user.id, name))
	if(c == None):
		return False

	c = c.split(":")

	j = JOB_OWNER
	if(c[1]==2):
		j = JOB_WORKER

	return (Job.objects.get(id=c[0]), j)


def set_job_for_user(user, name, job_id, work_status):
	if(work_status == JOB_WORKER):
		conn.set(get_has_work_key(user), "yes")
	conn.set(get_redis_key(user.id, name), str(job_id) + ":" + str(work_status))

## HAS WORK

def get_has_work_key(user):
	return "cc:" + str(user.id) + ":__working"

def user_has_work(user):
	return (conn.get(get_has_work_key(user.id)) != None)

def user_finished_work(user):
	conn.delete(get_has_work_key(user))

## JOB REQUEST

def get_last_work_request_key(user_id):
	return "cc:" + str(user_id) + ":__last_work_request"

def user_has_last_work_request(user):
	return (conn.get(get_last_work_request_key(user.id)) != None)

def get_last_work_request(user):
	return conn.get(get_last_work_request_key(user.id))

def set_job_request_for_user(user, job_id):
	conn.set(get_last_work_request_key(user.id), job_id)

def clear_job_request_for_user(user):
	conn.delete(get_last_work_request_key(user.id))