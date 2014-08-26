from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token

# Create your models here.

mActions = (
        (0,'AddClicked'),
        (1,'ButtonClicked'),
        (2,'RedirectOccurred')
    )

class Company(models.Model):
    PACKAGE_LEVEL_CHOICES = (
        (2,'Basic'),
        (3,'Pro'),
        (4,'Enterprise')
    )
    Name = models.CharField(max_length=100)
    PackageLevel = models.IntegerField(default=2, choices=PACKAGE_LEVEL_CHOICES)
    Owner = models.ForeignKey(User)
    StripeBillingToken = models.CharField(max_length=500, default='')

    def getMaxUsers(self):
        if self.PackageLevel == 2:
            return 1
        if self.PackageLevel == 3:
            return 5
        if self.PackageLevel == 4:
            return 1000000
        #crap
        return 1

    def __unicode__(self):
        return self.Name

class Intersticial(models.Model):
    Name = models.CharField(max_length=100)
    DisplayChance = models.IntegerField(default=100)
    Active = models.BooleanField(default=True)
    Url = models.CharField(max_length=2000)
    AdClickUrl = models.CharField(max_length=2000)
    Company = models.ForeignKey(Company, related_name="Intersticials")


    def __unicode__(self):
        return self.Company.Name + ' - ' + self.Name

class SupportedDomain(models.Model):
    Domain = models.CharField(max_length=500, db_index=True)
    Company = models.ForeignKey(Company, related_name='Domains')
    Intersticial = models.ForeignKey(Intersticial, related_name='Domains', null=True, default=None)

    def __unicode__(self):
        return self.Domain

class ExtendedUser(models.Model):
    User = models.OneToOneField(User, related_name='ExtUser')
    Company = models.ForeignKey(Company, null=True, related_name='Users')
    NewsLetter = models.BooleanField(default=True)
    IsAdmin = models.BooleanField(default=True)
    ActivationCode = models.CharField(default='', max_length=50)
    AccountActivated = models.BooleanField(default=False)

    def __unicode__(self):
        return self.User.username

class UserInvites(models.Model):
    Company = models.ForeignKey(Company, related_name='Invites')
    UserEmail = models.EmailField(max_length=254)
    ActivationCode = models.CharField(max_length=50)


class RedirectLink(models.Model):
    UrlKey = models.CharField(max_length=20)
    Domain = models.ForeignKey(SupportedDomain, related_name='Links')
    RedirectUrl = models.CharField(max_length=2000)
    User = models.ForeignKey(ExtendedUser, null=True)
    TimeGenerated = models.DateTimeField(auto_now=True)
    NoIntersticial = models.BooleanField(default=False)
    IsActive = models.BooleanField(default=True)
    LinkTitle = models.CharField(max_length=255, default='', blank=True)

    def __unicode__(self):
        return self.Domain.Domain + ' - ' + self.RedirectUrl

class LinkStat(models.Model):
    Link = models.ForeignKey(RedirectLink, related_name='Stats')
    IpAddress = models.GenericIPAddressField()
    CountryCode = models.CharField(max_length=3)
    Country = models.CharField(max_length=100)
    Referer = models.CharField(max_length=2000)
    TimeClicked = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return self.Link.__unicode__() + ' - ' + str(self.TimeClicked)

class LinkAgentType(models.Model):
    Stat = models.ForeignKey(LinkStat, related_name='AgentTypes')
    AgentType = models.CharField(max_length=500)
    Browser = models.CharField(max_length=100)
    OS = models.CharField(max_length=50)
    Device = models.CharField(max_length=50)


class LinkLanguage(models.Model):
    Stat = models.ForeignKey(LinkStat, related_name='Languages')
    Language = models.CharField(max_length=50)

class LinkClickTotal(models.Model):
    Link = models.ForeignKey(RedirectLink, related_name='Totals')
    TotalClicked = models.IntegerField(default=0)
    Date = models.DateField()

    def __unicode__(self):
        return self.Link.__unicode__() + ' - ' + str(self.Date)

class LightLocationInfo(models.Model):
    CountryCode = models.CharField(max_length=2)
    Country = models.CharField(max_length=50)
    IpAddressStart = models.GenericIPAddressField()
    IpAddressEnd = models.GenericIPAddressField()
    IpNumberStart = models.BigIntegerField()
    IpNumberEnd = models.BigIntegerField()

class PendingUserRegistration(models.Model):
    Email = models.EmailField(max_length=254)
    Company = models.ForeignKey(Company, related_name='PendingUsers')

    def __unicode__(self):
        return self.Company.Name + " - " + self.Email
    
class LinkTag(models.Model):
    Link = models.ForeignKey(RedirectLink, related_name='Tags')
    Tag = models.CharField(max_length=100)

    def __unicode__(self):
        return self.Link.__unicode__() + ' - ' + self.Tag

class InterstitialStat(models.Model):
    ACTIONS = mActions
    Intersticial = models.ForeignKey(Intersticial, related_name='Stats')
    TimeTaken = models.IntegerField()
    ActionTaken = models.IntegerField(choices=ACTIONS)
    Link = models.ForeignKey(RedirectLink)
    TimeGathered = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return self.Link.__unicode__() + ' - ' + str(self.ActionTaken)

class AggregateInterstitialStat(models.Model):
    Intersticial = models.ForeignKey(Intersticial)
    AdClicked = models.IntegerField(default=0)
    ButtonClicked = models.IntegerField(default=0)
    RedirectOcurred = models.IntegerField(default=0)
    AverageTimeTaken = models.DecimalField(max_digits=12, decimal_places=4)
    Date = models.DateField()

    def __unicode__(self):
        return self.Intersticial.Name + ' - ' + str(self.Date)

    def getTotalClicks(self):
        return self.AdClicked + self.ButtonClicked + self.RedirectOcurred

    def incrementAction(self, action, timeTaken):
        preActions = self.getTotalClicks()
        postActions = preActions + 1
        time = self.AverageTimeTaken
        if not time:
            time = 0
        if action == 0:
            self.AdClicked += 1
        if action == 1:
            self.ButtonClicked += 1
        if action == 2:
            self.RedirectOcurred += 1
        self.AverageTimeTaken = 100 #round(((time * preActions) + timeTaken / postActions), 2)

class AccountCancellation(models.Model):
    cancellation_reasons = (
        (0, 'Cost too much'),
        (1, 'Bugs'),
        (2, 'Customer Service'),
        (3, 'Lack of features'),
        (4, 'No longer use'),
        (5, 'Another Product'),
        (6, 'Other')
    )
    CompanyCancelledFor = models.ForeignKey(Company)
    TimeCancelled = models.DateTimeField(auto_now=True)
    ReasonForCancelling = models.IntegerField(choices=cancellation_reasons)
    CancellationExplanation = models.CharField(max_length=10000)

class LinkstrAdminStat(models.Model):
    TimeGathered = models.DateTimeField(auto_now=True)
    Users = models.IntegerField()
    PendingRegistrations = models.IntegerField()
    Links = models.IntegerField()
    Clicks = models.IntegerField()
    Companies = models.IntegerField()
    PayingCompanies = models.IntegerField()

class LinkPageData(models.Model):
    Link = models.OneToOneField(RedirectLink)
    PageData = models.TextField()
    

#TODO User-Domain Permissios

#These 2 sections of code create a user profile when a user is created
def create_user_profile(sender, instance, created, **kwargs):  
    if created:  
       profile, created = ExtendedUser.objects.get_or_create(User=instance)
       Token.objects.create(user=instance)


post_save.connect(create_user_profile, sender=User) 