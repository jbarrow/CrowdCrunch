from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Job(models.Model):
	STATUS_CHOICES = (
		(0, "Queued"),
		(1, "Working"),
		(2, "Accepted"),
		(3, "Rejected"),
		(4, "Error"),
	)
	description = models.TextField()
	status = models.IntegerField(choices = STATUS_CHOICES)
	rating = models.IntegerField(default=0)
	cost = models.DecimalField(max_digits=5, decimal_places=2, default=0)
	created = models.DateTimeField(auto_now_add=True, null=True)
	owner = models.ForeignKey(User, related_name="owned_jobs")
	worker = models.ForeignKey(User, related_name="worked_jobs")

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
		j.worker_id = 0

		try:
			j.save()
		except:
			p.AddCredits(1)
			return False
		# Start Working Here..
		return True

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

	@classmethod
	def Log(job, text, sender):
		c = Communication()
		c.job = job
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
		(3, "Error"),
	)
	status = models.IntegerField(choices = STATUS_CHOICES)
	credits = models.IntegerField()
	current_job = models.ForeignKey(Job, null=True, blank=True) 
	user_id = models.ForeignKey(User)
	phone_number = models.CharField(max_length=255)
	phone_verified = models.BooleanField(default=False)

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

	def MarkAvailable(self):
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
		return 0.0