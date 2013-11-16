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
	current_job = models.ForeignKey(Job) 
	user_id = models.ForeignKey(User)
	phone_number = models.CharField(max_length=255)