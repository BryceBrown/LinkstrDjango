# Create your views here.
from FrontEnd.models import *
from FrontEnd.serializers import *
from django.shortcuts import get_object_or_404, render, render_to_response 
from django.views.decorators.http import require_POST, require_GET
from django.contrib.auth import authenticate, login, logout
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.contrib.auth.models import User
from django.template import RequestContext
from django.utils.http import urlencode
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
from FrontEnd.forms import *
from FrontEnd import utility
from FrontEnd import constants
import logging
import random
import thread
import stripe

#MESSAGE TYPES
INFO_MESSAGE_TYPE = 0
ERROR_MESSAGE_TYPE = 1
SUCCESS_MESSAGE_TYPE = 2

def postResponse(path, message='', messageType=1, section=''):
    if message == '':
        return HttpResponseRedirect(path + section)
    messageString = urlencode({
        'message' : message,
        'mtype': messageType,
    })
    return HttpResponseRedirect(path + '?' + messageString + section)

@require_POST
def postSignup(request):
    if request.user.is_authenticated():
        return HttpResponse('', status=401)
    redir = '/Dashboard'
    if 'redir' in request.POST:
        redir = request.POST['redir']
    form = SignupFormRecaptcha(request.POST)
    if not form.is_valid():
        nv_dict = {'signup_captcha': form, 'redir': redir}
        if 'companyid' in request.POST:
            nv_dict['company'] = request.POST['companyid']
        return render_to_response('beta_signup.html', nv_dict, context_instance=RequestContext(request))
    #first create user
    if 'companyid' in request.POST:
        print "CompanyId: " + request.POST['companyid']
        company = get_object_or_404(Company, pk=request.POST['companyid'])
        pendingRequests = PendingUserRegistration.objects.filter(Email=request.POST['Email']).filter(Company=company)
        if pendingRequests.count() == 0:
            return HttpResponseRedirect('/Signup/')
        if company.getMaxUsers() <= company.Users.count():
            print "Company Users: " + str(company.getMaxUsers())
            return HttpResponseRedirect('/Signup/?error=TooManyUsers')
        newUser = form.createUser()
        extUser = newUser.ExtUser
        extUser.Company = company
        pendingRequests.delete()
    elif 'Company' in request.POST:
        #TODO for Beta everyone has a pro package level
        newUser = form.createUser()
        extUser = newUser.ExtUser
        company = Company(Name=request.POST['Company'], PackageLevel=3,Owner=newUser,StripeBillingToken='zzz')
        company.save()
        domain = SupportedDomain(Domain=utility.getSafeDomainNameForCompany(company.Name), Company=company)
        domain.save()
        extUser.Company = company
    else:
        return HttpResponseRedirect('/Signup/')

    extUser.ActivationCode = utility.string_generator(25)
    extUser.AccountActivated = True
    extUser.save()
    #utility.sendSignupEmail(newUser.email, extUser.ActivationCode)
    usr = authenticate(username=newUser.username, password=request.POST['Password'])
    login(request, usr)

    return HttpResponseRedirect(redir)

@require_POST
def postLogin(request):
    try:
        redir = request.META['HTTP_REFERER']
        if 'redir' in request.POST:
            redir = request.POST['redir']
        else:
            redir = '/Dashboard'
        username = request.POST['Username']
        password = request.POST['Password']
    except(KeyError):
        raise Http404
    user = authenticate(username=username,password=password)
    if user is not None:
        if not user.ExtUser.AccountActivated:
            return HttpResponseRedirect('/PleaseAuthenticate')
        login(request, user)
        return HttpResponseRedirect(redir)
    else:
        return HttpResponseRedirect('/Login/')

@require_POST
def postBasicSignup(request):
    if not request.user.is_authenticated():
        return HttpResponse('', status=401)
    if 'stripeToken' not in request.POST or 'stripeEmail' not in request.POST:
        return HttpResponse('', status=400)
    try:
        print request.POST
        company = request.user.ExtUser.Company
        if company is None:
            return HttpResponse('', status=400)
        stripe.api_key = constants.STIPE_API_SECRET_KEY
        newCustomer = stripe.Customer.create(
            card=request.POST['stripeToken'],
            plan='Basic',
            email=request.POST['stripeEmail']
        )
        print newCustomer
        if newCustomer != None:
            company.StripeBillingToken = newCustomer.id
            company.PackageLevel = 2
            company.save()
            return HttpResponseRedirect('/Plans/SignupComplete')
    except Exception, e:
        logging.debug(str(e))
        raise e

@require_POST
def postProSignup(request):
    if not request.user.is_authenticated():
        return HttpResponse('', status=401)
    if 'stripeToken' not in request.POST or 'stripeEmail' not in request.POST:
        return HttpResponse('', status=400)
    try:
        print request.POST
        company = request.user.ExtUser.Company
        if company is None:
            return HttpResponse('', status=400)
        stripe.api_key = constants.LIVE_STRIPE_API_KEY
        newCustomer = stripe.Customer.create(
            card=request.POST['stripeToken'],
            plan='Pro',
            email=request.POST['stripeEmail']
        )
        print newCustomer
        if newCustomer != None:
            company.StripeBillingToken = newCustomer.id
            company.PackageLevel = 3
            company.save()
            return HttpResponseRedirect('/Dashboard')
    except Exception, e:
        logging.debug(str(e))
        raise e

@require_POST
def postEnterpriseSignup(request):
    if not request.user.is_authenticated():
        return HttpResponse('', status=401)
    if 'stripeToken' not in request.POST or 'stripeEmail' not in request.POST:
        return HttpResponse('', status=400)
    try:
        print request.POST
        company = request.user.ExtUser.Company
        if company is None:
            return HttpResponse('', status=400)
        stripe.api_key = constants.LIVE_STRIPE_API_KEY
        newCustomer = stripe.Customer.create(
            card=request.POST['stripeToken'],
            plan='Enterprise',
            email=request.POST['stripeEmail']
        )
        print newCustomer
        if newCustomer != None:
            company.StripeBillingToken = newCustomer.id
            company.PackageLevel = 4
            company.save()
            return HttpResponseRedirect('/Plans/SignupComplete')
    except Exception, e:
        logging.debug(str(e))
        raise e
    
@require_POST
def postCreateCompany(request):
    if not request.user.is_authenticated():
        return HttpResponse('', status=401)
    if request.user.ExtUser.Company is not None:
        return HttpResponse('', status=400)
    if Company.objects.filter(Owner=request.user).count() > 0 or Company.objects.filter(Name=request.POST['Name']).count() > 0:
        return HttpResponse('', status=400)
    company = Company.objects.create(Name=request.POST['Name'], Owner=request.User)
    company.save()
    extUser = request.user.ExtUser
    extUser.Company = company
    extUser.save()
    return HttpResponse('{ "message": "created" }', status=200)

@require_POST
def addEditDomain(request):
    if not request.user.is_authenticated():
        return HttpResponse('', status=401)
    if not request.user.ExtUser.IsAdmin:
        return HttpResponse('', status=401)
    try:
        domain = request.POST['Domain']
        domainId = request.POST['DomainId']
        interstitialId = request.POST['DomainInterstitital']
        if str(domainId) == "-1":
            if 'goli.us' in domain:
                return postResponse('/Settings/', 'You cannot add a new goli.us domain.', ERROR_MESSAGE_TYPE, '#Domains')
            #Previous Domain 
            prevDomains = SupportedDomain.objects.filter(Domain=domain)
            if prevDomains.count() == 0:
                newDomain = SupportedDomain(Domain=domain,Company=request.user.ExtUser.Company)
                if str(interstitialId) != "-1":
                    inter = Intersticial.objects.get(pk=interstitialId)
                    if inter.Company == request.user.ExtUser.Company:
                        newDomain.Intersticial = inter
                newDomain.save()
                return postResponse('/Settings/', 'Domain added!', SUCCESS_MESSAGE_TYPE, '#Domains')
        else:
            domainToEdit = SupportedDomain.objects.get(pk=domainId)
            if domainToEdit.Company == request.user.ExtUser.Company:
                inter = None
                if str(interstitialId) != "-1":
                    inter = Intersticial.objects.get(pk=interstitialId)
                if inter is not None and inter.Company != request.user.ExtUser.Company:
                    return postResponse('/Settings/', "You don't own this interstitial", ERROR_MESSAGE_TYPE, '#Domains')
                domainToEdit.Intersticial = inter
                domainToEdit.save()
                return postResponse('/Settings/', 'Domain edited!', SUCCESS_MESSAGE_TYPE, '#Domains')
            else:
                return postResponse('/Settings/', "You don't own this domain", ERROR_MESSAGE_TYPE, '#Domains')

        return HttpResponseRedirect('/Settings/?#Domains')
    except Exception, e:
        logging.debug(str(e))
    return HttpResponseRedirect('/Settings/?#Domains', status=403)

@require_POST
def deleteDomain(request):
    if not request.user.is_authenticated():
        return HttpResponse('', status=401)
    if not request.user.ExtUser.IsAdmin:
        return HttpResponse('', status=401)
    try:
        domain = request.POST['Domain']
        prevDomain = SupportedDomain.objects.get(Domain=domain)
        #make sure the domain is owned and it is not the last one
        if prevDomain.Company == request.user.ExtUser.Company and SupportedDomain.objects.filter(Company=prevDomain.Company).count() > 1:
            prevDomain.delete()
            return postResponse('/Settings/', 'Domain ' + domain + ' was deleted', SUCCESS_MESSAGE_TYPE, '#Domains')
        else:
            return postResponse('/Settings/', 'Error deleting domain', ERROR_MESSAGE_TYPE, '#Domains')
    except Exception, e:
        logging.debug(str(e))
    return HttpResponseRedirect('/Settings/')

@require_POST
def addEditInterstitial(request):
    if not request.user.is_authenticated():
        return HttpResponse('', status=401)
    if not request.user.ExtUser.IsAdmin:
        return HttpResponse('', status=401)
    try:
        interId = request.POST['InterstitialId']
        name = request.POST['InterstitialName']
        url = request.POST['InterstitialUrl']
        displaychance = request.POST['DisplayChance']
        active = ('InterstitialActive' in request.POST)
        print interId
        if interId != '-1':
            stitial = Intersticial.objects.get(pk=interId)
            if stitial.Company == request.user.ExtUser.Company:
                stitial.Name = name
                stitial.Url = url
                stitial.Active = active
                stitial.DisplayChance = displaychance
                stitial.save()
                return postResponse('/Settings/', name + ' updated', SUCCESS_MESSAGE_TYPE, '#Intersticials')
            else:
                return postResponse('/Settings/', name + ' does not belong to your company', ERROR_MESSAGE_TYPE, '#Intersticials')
        else:
            stitial = Intersticial(Name=name, Url=url, DisplayChance=displaychance, Active=active, Company=request.user.ExtUser.Company)
            stitial.save()
            return postResponse('/Settings/', name  + ' created', SUCCESS_MESSAGE_TYPE, '#Intersticials')
    except Exception, e:
        logging.debug(str(e))
    return HttpResponseRedirect('/Settings/?#Intersticials')

@require_POST
def deleteInterstitial(request):
    if not request.user.is_authenticated():
        return HttpResponse('', status=401)
    if not request.user.ExtUser.IsAdmin:
        return HttpResponse('', status=401)
    try:
        inter = Intersticial.objects.get(pk=request.POST['InterstitialId'])
        if inter.Company == request.user.ExtUser.Company:
            inter.delete()
            return postResponse('/Settings/', 'Interstitial Deleted', SUCCESS_MESSAGE_TYPE, '#Interstitials')
    except Exception, e:
        logging.debug(str(e))
    return HttpResponseRedirect('/Settings/?#Intersticials')


@require_POST
def addUserInvite(request):
    if not request.user.is_authenticated():
        return HttpResponse('', status=401)
    if not request.user.ExtUser.IsAdmin:
        return HttpResponse('', status=401)
    try:
        email = request.POST['Email']
        if User.objects.filter(email=email).count() != 0:
            return postResponse('/Settings/', 'A User with this email already exists', ERROR_MESSAGE_TYPE, '#Users')
        if PendingUserRegistration.objects.filter(Email=email).count() != 0:
            return postResponse('/Settings/', 'A Pending registration for this email already exists', ERROR_MESSAGE_TYPE, '#Users')
        if PendingUserRegistration.objects.filter(Company=request.user.ExtUser.Company).count() >= 10:
            return postResponse('/Settings/', 'You may only have a maximum of 10 pending invites', ERROR_MESSAGE_TYPE, '#Users')
        reg = PendingUserRegistration(Email=email, Company=request.user.ExtUser.Company)
        reg.save()
        #TODO send signup email with request id
        thread.start_new_thread(utility.sendEmail, (email, 
            constants.PENDING_USER_SIGNUP.replace("{0}",reg.Company.Name).replace("{1}",str(reg.Company.id)), 
            "Linkstr invite from " + reg.Company.Name))
        return HttpResponseRedirect('/Settings/?#Users')
    except Exception, e:
        logging.debug(str(e))
    return HttpResponseRedirect('/Settings/?#Users', status=403)

@require_POST
def deleteUserInvite(request):
    if not request.user.is_authenticated():
        return HttpResponse('', status=401)
    if not request.user.ExtUser.IsAdmin:
        return HttpResponse('', status=401)
    try:
        userId = request.POST['userinviteid']
        invite = PendingUserRegistration.objects.get(pk=userId)
        if request.user.ExtUser.Company != invite.Company:
            return postResponse('/Settings/','Invite is not owned by your company', ERROR_MESSAGE_TYPE, '#Users')
        invite.delete()
        return postResponse('/Settings/', 'Invitation deleted', SUCCESS_MESSAGE_TYPE, '#Users')
    except Exception, e:
        logging.debug(str(e))
    return HttpResponse('/Settings/?#Users', status=403)

#Deletes user account that was created 
@require_POST
def revokeUserAccount(request):
    if not request.user.is_authenticated():
        return HttpResponse('', status=401)
    if not request.user.ExtUser.IsAdmin:
        return HttpResponse('', status=401)
    try:
        userId = request.POST['userid']
        usr = User.objects.get(pk=userId).ExtUser
        if usr.Company != request.user.ExtUser.Company:
            return postResponse('/Settings/', 'User is not owned by this company', ERROR_MESSAGE_TYPE, '#Users')
        if usr.Company.Owner == usr.User:
            return postResponse('/Settings/', 'Cannot delete owner of Company', ERROR_MESSAGE_TYPE, '#Users')
        name = usr.User.username
        usr.User.delete()
        return postResponse('/Settings/', 'User ' + name + ' deleted', SUCCESS_MESSAGE_TYPE, '#Users')
    except Exception, e:
        logging.debug(str(e))
    return postResponse('/Settings/')

@require_POST
def editUserAccount(request):
    if not request.user.is_authenticated():
        return HttpResponse('', status=401)
    if not request.user.ExtUser.IsAdmin:
        return HttpResponse('', status=401)
    try:
        userId = request.POST['userid']
        admin = ('UserIsAdmin' in request.POST)
        usr = ExtendedUser.objects.get(pk=userId)
        if usr.Company.Owner == usr.User:
            return postResponse('/Settings/', 'Cannot disable admin for owner', ERROR_MESSAGE_TYPE, '#Users')
        if not usr.Company == request.user.ExtUser.Company:
            return postResponse('/Settings/', 'User is not under your company', ERROR_MESSAGE_TYPE, '#Users')
        usr.IsAdmin = admin
        usr.save()
        return postResponse('/Settings/', 'User ' + usr.User.username + ' updated', SUCCESS_MESSAGE_TYPE, '#Users')
    except Exception, e:
        logging.debug(str(e))
    return postResponse('/Settings/')

@require_POST
def cancelAccount(request):
    if not request.user.is_authenticated():
        return HttpResponse('', status=401)
    company = request.user.ExtUser.Company
    if company.Owner != request.user:
        return HttpResponse('', status=401)
    if company.StripeBillingToken == 'zzz':
        return HttpResponse('', status=401)
    stripe.api_key = STIPE_API_SECRET_KEY
    #Get the customer and cancel all of the subscriptions
    customer = stripe.Customer.retreive(company.StripeBillingToken)
    subs = customer.subscriptions.all()
    logging.debug("Customer Cancelling subscriptions")
    logging.debug(str(subs))
    for obj in subs:
        obj.delete()
    cancellation = AccountCancellation()
    cancellation.CompanyCancelledFor = company
    cancellation.ReasonForCancelling = request.POST['reason']
    cancellation.CancellationExplanation = request.POST['explanation']
    cancellation.save()
    company.StripeBillingToken = 'zzz'
    company.save()
    return HttpResponseRedirect('/CancellationComplete')


