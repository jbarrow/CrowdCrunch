from django.views.generic import TemplateView, View
from django.shortcuts import redirect

from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect

from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import check_password

from cruncher.models import *
from django.db.models import Q

from django.http import HttpResponse

from django.views.generic.detail import DetailView

from cruncher.queuer.bridge import QueueJob

class LoggedInView(TemplateView):
	def get_context_data(self, **kwargs):
		context = super(LoggedInView, self).get_context_data(**kwargs)

		if self.request.user.is_authenticated():
			context['logged_in'] = True

		return context

class LoggedInDetailView(DetailView):
	def get_context_data(self, **kwargs):
		context = super(LoggedInDetailView, self).get_context_data(**kwargs)

		if self.request.user.is_authenticated():
			context['logged_in'] = True

		return context

class RateJob(View):
	def get(self, request, **kwargs):
		j = Job.objects.get(id=kwargs['pk'])
		if(request.user == j.owner):
			rate = int(kwargs['r'])
			j.rating = rate
			j.save()
			return redirect("/jobs/" + str(j.id))
		else:
			return HttpResponse(status=403)

class CompleteJobStatus(View):
	status=2

	def get(self, request, **kwargs):
		pk = kwargs['pk']
		j = Job.objects.get(id=pk)
		j.status = self.status
		j.save()
		j.Complete()
		return redirect("/jobs/" + str(j.id))

class ViewJob(LoggedInDetailView):
	template_name="cruncher/job_detail.html"

	def get_queryset(self):
		return Job.objects.filter(Q(owner=self.request.user) | Q(worker=self.request.user))

class CurrentJobView(ViewJob):
	def get_object(self, queryset=None):
		return UserProfile.Get(self.request.user).GetCurrentJob()


class VerifyPhoneView(View):
	@method_decorator(csrf_protect)
	def post(self, request, **kwargs):
		p = UserProfile.Get(request.user)
		code = request.POST['code']
		if(p):
			phone = p.phone_number
			phone = phone.split(":")
			if(len(phone) == 2 and phone[1] == code):
				p.phone_verified = True
				p.phone_number = phone[0]
				p.save()
				return redirect("/dashboard?verified")
		return redirect("/dashboard?verify-error")

class CreateJobView(View):
	@method_decorator(csrf_protect)
	def post(self, request, **kwargs):
		description = request.POST['description']
		budget = request.POST['budget'] if request.POST["budget"] != "" else 0.0
		print budget
		result = Job.Create(description, budget, request.user)
		if(result):
			QueueJob(result)
			return redirect("/dashboard?created")
		else:
			return redirect("/dashboard?create-error")

class CreditAccountView(View):
	def get(self, request, **kwargs):
		if request.user.is_staff:
			p = UserProfile.Get(request.user)

			if(p):
				p.AddCredits(5)
				return redirect("/dashboard")
		else:
			return HttpResponse(status=403)

class DashboardView(LoggedInView):
	template_name="dashboard.html" 

	def get_context_data(self, **kwargs):
		context = super(DashboardView, self).get_context_data(**kwargs)
		user = self.request.user
		profile = UserProfile.objects.get(user_id=user)
		context['total_jobs'] = Job.objects.filter(owner=user).order_by("-created")
		context['working_count'] = Job.objects.filter(Q(status=0) | Q(status=1), owner=user).count()
		context['working_job'] = profile.current_job if profile.current_job_id != 0 else  False
		context['credits'] = profile.credits
		context['stars'] = profile.StarValue()
		context['new'] = ("new" in self.request.GET)
		context['created'] = ("created" in self.request.GET)
		context['create_error'] = ("create-error" in self.request.GET)
		context['unverified'] = not profile.phone_verified
		context['just_verified'] = ("verified" in self.request.GET)
		context['verification_error'] = ("verify-error" in self.request.GET)
		return context

class ProfileView(LoggedInView):
	template_name="profile.html"

	def get_context_data(self, **kwargs):
		context = super(ProfileView, self).get_context_data(**kwargs)
		context['password_error'] = ("password-error" in self.request.GET)
		context['success'] = ("success" in self.request.GET)
		return context

	@method_decorator(csrf_protect)
	def post(self, request, **kwargs):
		user = request.user
		if(check_password(request.POST['password'], user.password)):
			user.email = request.POST['username']
			user.username = request.POST['username']
			if(request.POST['new_password'] != ""):
				user.set_password(request.POST['new_password'])
			user.save()
			return redirect("/profile?success")
		else:
			return redirect("/profile?password-error")

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

	@method_decorator(csrf_protect)
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
			first_name = request.POST['first_name']
			last_name = request.POST['last_name']
			if(
				email == u'' or 
				phone == u'' or 
				phone_verify == u'' or 
				first_name == u'' or 
				last_name == u'' or 
				phone != phone_verify or 
				password == u''
				):
				return redirect("/?no-fill")
			user = User.objects.create_user(email, email, password)
			user.first_name = first_name
			user.last_name = last_name
			user.save()

			# send verify token
			verify_token = send_verify_token(phone)

			profile = UserProfile()
			profile.phone_number = (phone + ":" + verify_token)
			profile.status = 2
			profile.credits = 5
			profile.user_id = user
			profile.save()

			user = authenticate(username=email, password=password)
			login(request, user)

			return redirect("/dashboard?new")
