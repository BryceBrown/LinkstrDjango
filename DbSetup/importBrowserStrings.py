import os
import csv
import httpagentparser
import random

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "LaasFrontEnd.settings")
from django.contrib.auth.models import User
from FrontEnd.models import *


def ImportBrowserStrings():
	print "Importing Browser Data..."
	with open('DBSetup/browser_strings.csv', 'r') as f:
		browserReader = csv.reader(f)
		browsers = []

		print "Parsing Csv..."
		for row in browserReader:
			browsers.append(
				(httpagentparser.parse(row[2]), 
					row[2])
			)
		#now create 100 link clicks on twitter
		link = RedirectLink.objects.get(pk=1)
		print "Creating clicks..."
		stats = []
		for i in range(100):
			stats.append(LinkStat(Link=link, 
				IpAddress='192.186.1.1', 
				CountryCode='USA',
				Country='United States',
				Referer='t.co'))
		LinkStat.objects.bulk_create(stats)
		agents = []
		for stat in stats:
			browser = random.choice(browsers)
			agents.append(LinkAgentType(Stat=stat, AgentType=))
