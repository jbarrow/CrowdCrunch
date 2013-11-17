from django.db import models
from django.contrib.auth.models import User
from django.db.models import Q

# Create your models here.

class Job(models.Model):
	STATUS_CHOICES = (
		(0, "Queued"),
		(1, "Working"),
		(2, "Completed"),
		(3, "Accepted"),
		(4, "Rejected"),
		(5, "Error"),
	)
	description = models.TextField()
	status = models.IntegerField(choices = STATUS_CHOICES)
	rating = models.IntegerField(default=0)
	cost = models.DecimalField(max_digits=5, decimal_places=2, default=0)
	created = models.DateTimeField(auto_now_add=True, null=True)
	owner = models.ForeignKey(User, related_name="owned_jobs", null=True, blank=True)
	worker = models.ForeignKey(User, related_name="worked_jobs", null=True, blank=True)

	def __unicode__(self):
		return "(%s) %s wants %s" % (self.get_status_display(), self.owner, self.description)

	def Complete(self):
		if self.status == 3:
			self.worker.AddCredits(1)
		elif self.status == 2:
			self.worker.RemoveCredits(1)

	@classmethod
	def Create(cls, description, budget, user):

		p = UserProfile.Get(user)

		if(p):
			ok = p.RemoveCredits(1)
			if(not ok):
				return False
		else:
			return False

		j = Job()
		j.description = description
		j.status = 0
		j.cost = budget
		j.owner = user

		try:
			j.save()
		except:
			p.AddCredits(1)
			return False

		return j

	@classmethod
	def CreateWithPhone(cls, description, budget, phone):
		u = False
		try:
			u = UserProfile.objects.get(phone_number=string)
		except:
			return False
		return cls.Create(description, budget, u)

class Communication(models.Model):
	SENDER_CHOICES = (
		(0, "Server"),
		(1, "Owner"),
		(2, "Worker"),
	)
	job = models.ForeignKey(Job)
	sender = models.IntegerField(choices=SENDER_CHOICES)
	text = models.TextField()
	timestamp = models.DateTimeField(auto_now_add=True, null=True)

	def __unicode__(self):
		return "%s on %s" % (self.get_sender_display(), self.job)

	class Meta:
		ordering = ['-timestamp']

	@classmethod
	def Log(cls, job, text, sender):
		cls.LogId(job.id, text, sender)

	@classmethod
	def LogId(cls, job_id, text, sender):
		c = Communication()
		c.job_id = job_id
		c.sender = sender
		c.text = text
		c.save()

class Payment(models.Model):
	number = models.CharField(max_length=255)
	job = models.ForeignKey(Job)
	balance = models.DecimalField(max_digits=5, decimal_places=2, default=0)

class File(models.Model):
	path = models.URLField()
	job = models.ForeignKey(Job)

class UserProfile(models.Model):
	STATUS_CHOICES = (
		(0, "Unavailable"),
		(1, "Available"),
		(2, "Unknown"),
		(3, "Working"),
		(4, "Error"),
	)
	status = models.IntegerField(choices = STATUS_CHOICES)
	credits = models.IntegerField()
	current_job = models.ForeignKey(Job, null=True, blank=True) 
	user_id = models.ForeignKey(User)
	phone_number = models.CharField(max_length=255)
	phone_verified = models.BooleanField(default=False)

	def __unicode__(self):
		return "%s (%s): %s credits" % (self.user_id, self.get_status_display(), str(self.credits))

	@classmethod
	def Get(cls, user):
		o = False
		try:
			o = UserProfile.objects.get(user_id=user)
		except:
			return False
		return o

	@classmethod
	def GetFromPhone(cls, phone):
		o = False
		try:
			o = UserProfile.objects.get(phone_number=phone)
		except:
			return False
		return o

	def GetCurrentJob(self):
		return Job.objects.get(worker=self.user_id, status=1)

	def HasWork(self):
		try:
			Job.objects.get(worker=self.user_id, status=1)
		except:
			return False
		return True

	def MarkAvailable(self):
		self.status = 1
		self.save()

	def MarkUnavailable(self):
		self.status = 0
		self.save()

	def StartWorking(self):
		self.status = 3
		self.save()

	def StopWorking(self):
		self.status = 1
		self.save()

	def AddCredits(self, credit_amount):
		self.credits += credit_amount
		self.save()

	def RemoveCredits(self, credit_amount):
		if(self.credits < credit_amount):
			return False
		self.credits -= credit_amount
		self.save()
		return True

	def StarValue(self):
		j = self.worked_jobs.filter(Q(status=3) | Q(status=4))
		total = 0.0
		for x in j:
			total += x.rating
		return total/len(j) if len(j) > 0 else 0.0

	def BudgetEligible(self):
		return (self.worked_jobs.filter(rating__gte=3).count() >= 5)