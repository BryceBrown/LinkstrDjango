#This file holds daily cron job url handlers
from FrontEnd.models import *
from django.views.decorators.http import require_POST, require_GET
from django.contrib.auth import authenticate, login, logout
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.db.models import Sum
from django.contrib.auth.models import User
from django.template import RequestContext
from FrontEnd.forms import *
from google.appengine.api import mail
from FrontEnd import constants
from FrontEnd import utility
from django.utils import timezone


def storeAdminStat(request):
    if not 'HTTP_X_APPENGINE_CRON' in request.META:
        raise Http404
    stat = LinkstrAdminStat()
    stat.Users = User.objects.all().count()
    stat.PendingRegistrations = PendingUserRegistration.objects.all().count()
    stat.Links = RedirectLink.objects.all().count()
    stat.Clicks = LinkClickTotal.objects.all().aggregate(Sum('TotalClicked'))['TotalClicked__sum']
    stat.Companies = Company.objects.all().count()
    stat.PayingCompanies = Company.objects.exclude(StripeBillingToken='zzz').exclude(StripeBillingToken='').exclude(StripeBillingToken='expired').count()
    stat.save()
    return HttpResponse('OK', status=200)

def expireAccount(request):
    if not 'HTTP_X_APPENGINE_CRON' in request.META:
        raise Http404
    #Get All companies who are zzz  (In Trial Mode)
    #Get their owners
    #if any of them are a month old, 
    trialCompanies = Company.objects.filter(StripeBillingToken='zzz')
    for company in trialCompanies:
        owner = company.Owner
        if owner.date_joined < utility.monthdelta(timezone.now(), 1):
            #expire the company and send the email
            company.StripeBillingToken = 'expired'
            company.save()
            TO_EMAIL = owner.email
            FROM_EMAIL = "noreply@golinkstr.com"
            SUBJECT = "Your Linkstr Trial has Expired"
            BODY = constants.EXPIRED_EMAIL
            try:
                mail.send_mail(FROM_EMAIL, TO_EMAIL, SUBJECT, BODY)
            except Exception, e:
                logging.debug(str(e))
    return HttpResponse('OK', status=200)


