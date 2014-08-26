import time
import random
import datetime
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "LaasFrontEnd.settings")
from django.contrib.auth.models import User
from FrontEnd.models import *

def RunDbSetup():
	#Only run this script once to populate the database after the first syncdb is ran
	print "Running db setup..."

	systemUsr = User(username='System', password='NA')
	systemUsr.save()

	tehowner = User.objects.get(username='tehowner')
	print "Creating companies..."
	cmp1 = Company(Name='Free Company', PackageLevel=1, Owner=tehowner)
	cmp1.save()

	cmp2 = Company(Name='Basic Company', PackageLevel=2, Owner=tehowner)
	cmp2.save()

	cmp3 = Company(Name='Pro Company', PackageLevel=3, Owner=tehowner)
	cmp3.save()

	print "Creating domains..."
	domain1 = SupportedDomain(Domain='goli.us', Company=cmp2)
	domain1.save()

	domain2 = SupportedDomain(Domain='objurity.com', Company=cmp3)
	domain2.save()

	domain3 = SupportedDomain(Domain='t.goli.us', Company=cmp3)
	domain3.save()

	usr1 = tehowner.ExtUser
	usr1.Company = cmp2
	usr1.AccountActivated = True
	usr1.ActivationCode = 'zzz'
	usr1.save()

	print "Creating links..."
	link1 = RedirectLink(UrlKey='zzz',Domain=domain1,RedirectUrl='https://twitter.com',User=usr1)
	link1.save()

	link = RedirectLink(UrlKey='dgfdd',Domain=domain1,RedirectUrl='https://www.google.com',User=usr1)
	link.save()

	link = RedirectLink(UrlKey='dfhne',Domain=domain1,RedirectUrl='https://www.google.com',User=usr1)
	link.save()

	link = RedirectLink(UrlKey='7iokgd',Domain=domain1,RedirectUrl='https://www.google.com',User=usr1)
	link.save()

	link = RedirectLink(UrlKey='123gfx',Domain=domain1,RedirectUrl='https://www.google.com',User=usr1)
	link.save()

	stitial = Intersticial(Name='test', DisplayChance=100, Active=True, Url='http://www.golinkstr.com', Company=cmp2)
	stitial.save()

	for m in range(5):
		m = m + 6
		for i in range(20):
			day = datetime.date(year=2013,month=(m + 1),day=(i + 1))
			nStat = InterstitialStat(Intersticial=stitial, 
				TimeTaken=(random.randint(0,15) * 1000),
				ActionTaken=random.randint(1,3),
				Link=link,
				TimeGathered=day)
			nStat.save()


	print "Creating stats..."
	for redirLnk in RedirectLink.objects.all():
		points = []
		for m in range(5):
			m = m + 6
			for i in range(20):
				day = datetime.date(year=2013,month=(m + 1),day=(i + 1))
				points.append(LinkClickTotal(Link=redirLnk,TotalClicked=random.randint(0,500),Date=day))
		LinkClickTotal.objects.bulk_create(points)

	print "DBSetup Finished..."
	#Now Create a bunch of LinkClickStats



