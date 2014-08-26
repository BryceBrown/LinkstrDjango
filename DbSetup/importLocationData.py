import os
import csv

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "LaasFrontEnd.settings")
from django.contrib.auth.models import User
from FrontEnd.models import *

def ImportLocationData():
	print "Importing Location Data"
	with open('DbSetup/GeoIPCountryWhois.csv', 'r') as f:
		countrReader = csv.reader(f)
		locations = []
		print "Parsing Csv..."
		for row in countrReader:
			locations.append(LightLocationInfo(IpAddressStart=row[0], 
				IpAddressEnd=row[1],
				IpNumberStart=int(row[2]),
				IpNumberEnd=int(row[3]),CountryCode=row[4],Country=row[5]))
		print "Done Parsing CSV. Creating..."
		LightLocationInfo.objects.bulk_create(locations)
		print "Done Creating"


