# Create your views here.
from FrontEnd.models import *
from django.shortcuts import get_object_or_404, render, render_to_response 
from django.views.decorators.http import require_POST, require_GET
from django.contrib.auth import authenticate, login, logout
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.db.models import Sum
from django.contrib.auth.models import User
from django.template import RequestContext
from FrontEnd.forms import *
from django.contrib.admin.views.decorators import staff_member_required

def index(request):
	return render_to_response('index.html', {}, context_instance=RequestContext(request))

def about(request):
	return render_to_response('about.html', {}, context_instance=RequestContext(request))

def signup(request):
	return render_to_response('signup.html', {'signup_captcha': SignupFormRecaptcha()}, context_instance=RequestContext(request))

def pricing(request):
	redir = "/Plans/Pro/Purchase"
	return render_to_response('pricing.html', {'redir' : redir}, context_instance=RequestContext(request))

def loginView(request):
	return render_to_response('login.html', {}, context_instance=RequestContext(request))

def tour(request):
	return render_to_response('tour.html', {}, context_instance=RequestContext(request))

def pleaseAuthenticate(request):
	return render_to_response('please_authenticate.html', {}, context_instance=RequestContext(request))

def mySettingsView(request):
	if not request.user.is_authenticated():
		return HttpResponseRedirect('/Login')
	getData = request.GET.copy()
	return render_to_response('settings.html', getData, context_instance=RequestContext(request))

def activateAccount(request):
	try:
		activation_code = request.GET['auth']
		extUser = ExtendedUser.objects.get(ActivationCode=activation_code)
		extUser.AccountActivated = True
		extUser.save()
		return HttpResponseRedirect('/Login')
	except Exception, e:
		logger.error("Error Activating account: " + str(e))
		raise Http404

def logoutPage(request):
	logout(request)
	return HttpResponseRedirect('/')

#Plans
def basicPlan(request):
	return render_to_response('plans_basic.html', {}, context_instance=RequestContext(request))

def proPlan(request):
	redir = "/Plans/Pro/Purchase"
	if not request.user.is_authenticated():
		return HttpResponseRedirect('/Signup?redir=' + redir)
	return render_to_response('plans_pro.html', {}, context_instance=RequestContext(request))

def enterprisePlan(request):
	return render_to_response('plans_enterprise.html', {}, context_instance=RequestContext(request))

def comparePlan(request):
	return render_to_response('plans_compare.html', {}, context_instance=RequestContext(request))

def testFullSignup(request):
	return render_to_response('signup_old.html', {'signup_captcha': SignupFormRecaptcha()}, context_instance=RequestContext(request))

def planFreeTrialBetaClick(request):
	return HttpResponseRedirect('/Signup')
	#return render_to_response('plans_purchase.html', {'plan_name': 'Basic Plan', 'cost': 2000, 'post_action': '/Post/BasicSignup/', 'cost_display': '$20/month'}, context_instance=RequestContext(request))

def plansPurchaseBasic(request):
	#if not request.user.is_authenticated():
	#	return HttpResponseRedirect('/Login?redir=/Plans/Basic/Purchase')
	return render_to_response('plans_purchase.html', {'plan_name': 'Basic Plan', 'cost': 2000, 'post_action': '/Post/BasicSignup/', 'cost_display': '$20/month'}, context_instance=RequestContext(request))

def plansPurchasePro(request):
	if not request.user.is_authenticated():
		return HttpResponseRedirect('/Login?redir=/Plans/Pro/Purchase')
	if request.user.ExtUser.Company.StripeBillingToken != 'zzz':
		return HttpResponseRedirect('/Dashboard')
	return render_to_response('plans_pro_purchase.html', {'plan_name': 'Pro Plan', 'cost': 2000, 'post_action': '/Post/ProSignup/', 'cost_display': '$20/month'}, context_instance=RequestContext(request))

def plansPurchaseEnterprise(request):
	#if not request.user.is_authenticated():
	#	return HttpResponseRedirect('/Login?redir=/Plans/Enterprise/Purchase')
	return render_to_response('plans_purchase.html', {'plan_name': 'Enterprise Plan', 'cost': 10000, 'post_action': '/Post/EnterpriseSignup/', 'cost_display': '$100/month'}, context_instance=RequestContext(request))

def redir404(request):
	return render_to_response('404.html', {}, context_instance=RequestContext(request))

def documentation(request):
	return render_to_response('documentation.html', {}, context_instance=RequestContext(request))

def betaWelcome(request):
	return render_to_response('welcome_to_beta.html', {}, context_instance=RequestContext(request))

@staff_member_required
def adminStatusPage(request):
	if not request.user.is_authenticated():
		raise Http404
	variables = {}
	variables['num_users'] = User.objects.all().count()
	variables['pending_registrations'] = PendingUserRegistration.objects.all().count()
	variables['num_links'] = RedirectLink.objects.all().count()
	variables['num_numclicks'] = LinkClickTotal.objects.all().aggregate(Sum('TotalClicked'))['TotalClicked__sum']
	variables['num_companies'] = Company.objects.all().count()
	variables['num_paying_companies'] = Company.objects.exclude(StripeBillingToken='zzz').exclude(StripeBillingToken='').count()
	return render_to_response('admin_overview.html', variables,  context_instance=RequestContext(request))

def betaSignup(request):
	company = None
	if 'company' in request.GET:
		company = get_object_or_404(Company, pk=request.GET['company'])
	redir = '/Dashboard'
	if 'redir' in request.POST or 'redir' in request.GET:
		if 'redir' in request.POST:
			redir = request.POST['redir']
		if 'redir' in request.GET:
			redir = request.GET['redir']
		if request.user.is_authenticated():
			return HttpResponseRedirect(redir)
	return render_to_response('beta_signup.html', 
		{'company': company, 'signup_captcha': SignupFormRecaptcha(), 'redir': redir}, 
		context_instance=RequestContext(request))

def dashboardView(request):
	if not request.user.is_authenticated():
		return HttpResponseRedirect('/Login?redir=/Dashboard')
	if request.user.ExtUser.Company.StripeBillingToken == 'expired':
		return HttpResponseRedirect('/Pricing?expired=true')
	return render_to_response('dashboardv3.html', {
		'current_domain_angular' : "{{currentDomain == null ? 'Loading...' : currentDomain.Domain}}",
		'link_text': "{{ linkText }}",
		'company': request.user.ExtUser.Company,
		}, context_instance=RequestContext(request))

def testAdd(request):
	return render_to_response('testtemplate.html', {}, context_instance=RequestContext(request))

def kupadayPrivacyPolicy(request):
	return render_to_response('kupaday_privacy.html', {}, context_instance=RequestContext(request))

def cancelAccount(request):
	return render_to_response('cancel_account.html', {}, context_instance=RequestContext(request))

def cancellationComplete(request):
	return render_to_response('cancellation_complete.html', {}, context_instance=RequestContext(request))