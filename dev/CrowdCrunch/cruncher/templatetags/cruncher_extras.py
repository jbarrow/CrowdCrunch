from django import template
from cruncher.models import *

register = template.Library()

@register.simple_tag
def active(request, match):
	return "class='active'" if (request.path == match) else ""

@register.filter
def has_work(user):
	return UserProfile.Get(user).HasWork()
	
@register.filter
def has_work(user):
	return UserProfile.Get(user).HasWork()

