from django.views.generic import TemplateView
from django.contrib.auth.models import User
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth import authenticate, login
from cruncher.models import *

class LandingView(TemplateView):
	template_name="home.html"

	# @ensure_csrf_cookie
	def get(self, request, **kwargs):
		if request.user.is_authenticated():
			return redirect("/dashboard")
		else:
			return super(LandingView, self).get(request, **kwargs)

	def get_context_data(self, **kwargs):
		context = super(LandingView, self).get_context_data(**kwargs)
		context['error'] = ("error" in self.request.GET)
		context['disabled'] = ("disabled" in self.request.GET)
		context['fill_error'] = ("no-fill" in self.request.GET)
		return context

	# @csrf_protect
	def post(self, request, **kwargs):
		if request.POST['login'] == "1":
			username = request.POST['username']
			password = request.POST['password']
			user = authenticate(username=username, password=password)
			if user is not None:
				if user.is_active:
					login(request, user)
					return redirect("/dashboard")
				else:
					return redirect("/?disabled")
			else:
				return redirect("/?error")
		else:
			email = request.POST['email']
			phone = u''.join(c for c in request.POST['phone'] if '0' <= c <= '9')
			phone_verify = u''.join(c for c in request.POST['phone_verify'] if '0' <= c <= '9')
			password = request.POST['password']
			if(email == u'' or phone == u'' or phone_verify == u'' or phone != phone_verify or password == u''):
				return redirect("/?no-fill")
			user = User.objects.create_user(email, email, password)
			user.save()

			profile = UserProfile()
			profile.phone_number = phone
			profile.status = 2
			profile.credits = 5
			profile.current_job_id = 0
			profile.user_id = user
			profile.save()

			user = authenticate(username=email, password=password)
			login(request, user)
			
			return redirect("/dashboard?new")

class UserCreationView(TemplateView):
	pass