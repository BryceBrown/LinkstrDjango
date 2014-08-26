from FrontEnd.models import *
from FrontEnd.serializers import *
from FrontEnd import utility
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.http import Http404, HttpResponse, HttpResponseRedirect
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from FrontEnd.permissions import *
from rest_framework import authentication, permissions, status, generics, mixins
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
from rest_framework.views import APIView
from datetime import datetime, date, timedelta
from django.db.models import Count
from django.db.models import Q
from django.contrib.auth import authenticate
import json
import urllib2
from BeautifulSoup import BeautifulSoup



class DomainList(APIView):
	#Give back a list of domains that user has access to
	def get(self, request, format=None):
		if not request.user.is_authenticated():
			return HttpResponse('', status=401)
		userExt = request.user.ExtUser
		domains = SupportedDomain.objects.filter(Q(Company=userExt.Company))
		serializer = DomainSerializer(domains, many=True)
		return Response(serializer.data)

	#for creating and updating Domains
	def post(self, request, format=None):
		if not request.user.is_authenticated():
			return HttpResponse('', status=401)

		dData = request.DATA.copy()
		dData['Company'] = request.user.ExtUser.Company.id
		if 'id' in dData:
			domain = get_object_or_404(SupportedDomain, pk=dData['id'])
			if domain.Company != request.user.ExtUser.Company:
				return HttpResponse('', status=404)
			serializer = DomainSerializer(domain, dData)
			if serializer.is_valid():
				serializer.save()
				interData = dData['Intersticial']
				if interData:
					inter = get_object_or_404(Intersticial, pk=interData['id'])
					if inter.Company != domain.Company:
						return HttpResponse('', status=401)
					if domain.Intersticial != inter:
						domain.Intersticial = inter
						serializer = DomainSerializer(domain)
				else:
					domain.Intersticial = None;
				domain.save()
				return Response(serializer.data)
			else:
				return Response(serializer.errors)
		else:
			serializer = DomainSerializer(dData)
			if serializer.is_valid():
				if 'goli.us' in dData['Domain']:
					return HttpResponse('', status=401)
				serializer.save()
				interData = dData['Intersticial']
				if interData:
					inter = get_object_or_404(Intersticial, pk=interData['id'])
					nDomain = serializer.object
					if inter.Company != nDomain.Company:
						return HttpResponse('', status=401)
					if nDomain.Intersticial != inter:
						nDomain.Intersticial = inter
						nDomain.save()
						serializer = DomainSerializer(nDomain)
				return Response(serializer.Data)
			else:
				return Response(serializer.errors)

class DomainNode(APIView):

	def get(self, request, pk, format=None):
		if not request.user.is_authenticated():
			return HttpResponse('', status=401)
		domain = get_object_or_404(SupportedDomain, pk=pk)
		if domain.Company != request.ExtUser.Company:
			return HttpResponse('', status=401)
		serializer = DomainSerializer(domain)
		return Response(serializer.data)

class RedirectUrlsForDomain(APIView):

	#TODO Sort by newest first
	def get(self, request, pk, format=None):
		if not request.user.is_authenticated():
			return HttpResponse('', status=401)
		userExt = request.user.ExtUser
		domain = get_object_or_404(SupportedDomain, pk=pk)
		if userExt.Company != domain.Company and domain.Domain != 'goli.us':
			return HttpResponse('', status=401)
		links = RedirectLink.objects.filter(Domain=domain).filter(IsActive=True)
		if domain.Domain == 'goli.us':
			links = links.filter(User=userExt)
		if 'q' in request.GET:
			q = request.GET['q']
			links = links.filter(Q(RedirectUrl__contains=q) | Q(LinkTitle__contains=q))
		links = links.order_by('-TimeGenerated')
		serializer = LinkSerializer(links, many=True)
		return Response(serializer.data)

class SingleRedirectUrl(APIView):
	
	def get(self, request, pk, format=None):
		if not request.user.is_authenticated():
			return HttpResponse('', status=401)
		link = get_object_or_404(RedirectLink, pk=pk)
		if link.User.Company != request.user.ExtUser.Company:
			return HttpResponse('', status=401)
		serializer = LinkSerializer(link)
		return Response(serializer.data)


	def delete(self, request, pk, format=None):
		if not request.user.is_authenticated():
			return HttpResponse('', status=401)
		link = get_object_or_404(RedirectLink, pk=pk)
		if link.User.Company != request.user.ExtUser.Company:
			return HttpResponse('', status=401)
		link.IsActive = False
		link.save()
		return Response(status=status.HTTP_204_NO_CONTENT)

class RedirectUrl(APIView):

	def get(self, request, format=None):
		if not request.user.is_authenticated():
			return HttpResponse('', status=401)

		links = RedirectLink.objects.filter(User=request.user.ExtUser)
		serializer = LinkSerializer(links)
		return Response(serializer.data)

	def post(self, request, *args, **kwargs):
		if not request.user.is_authenticated():
			return HttpResponse('', status=401)

		mData = request.DATA.copy()
		hasDomain = False
		userExt = request.user.ExtUser

		#If there are no domains in the request
		if SupportedDomain.objects.get(id=mData['Domain']).Company != userExt.Company:
			return HttpResponse('', status=401)

		#If the link has already been generated, give that object
		prevLink = RedirectLink.objects.filter(RedirectUrl=mData['RedirectUrl']).filter(Domain__id=mData['Domain'])
		if hasDomain:
			prevLink = prevLink.filter(User=userExt)
		if prevLink.count() > 0:
			if not prevLink[0].IsActive:
				prevLink[0].IsActive = True
				prevLink[0].save()
			serializer = LinkSerializer(prevLink[0])
			return Response(serializer.data)

		#Grab the ExtUserid and new unique URL Key
		mData['User'] = userExt.id
		if 'UrlKey' in mData:
			prevLink = RedirectLink.objects.filter(Domain__id=mData['Domain']).filter(UrlKey=mData['UrlKey'])
			if prevLink.count() > 0:
				#Link has been used for this domain, return
				return HttpResponse('', status=400)
		else:
			mData['UrlKey'] = utility.getUniqueRedirectKeyForDomain(mData['Domain'])

		#Serialize and send the response
		try:
			title = BeautifulSoup(urllib2.urlopen(mData['RedirectUrl'])).title.string
			mData['LinkTitle'] = title
		except Exception, e:
			mData['LinkTitle'] = ''
			print "Error getting link title"
			print e
		serializer = LinkSerializer(data=mData)
		if serializer.is_valid():
			serializer.save()
			return Response(serializer.data)
		else:
			return Response(serializer.errors, status=400)


def getLinkStats(self, request, pk, dateStart=date(1970,1,1), format=None):
	if not request.user.is_authenticated():
		return HttpResponse('', status=401)
	link = get_object_or_404(RedirectLink, pk=pk)
	if link.User != request.user.ExtUser:
		return HttpResponse('', status=401)

	stats = LinkClickTotal.objects.filter(Link=link).filter(Date__gte=dateStart)
	clicks = LinkStat.objects.filter(Link=link).filter(TimeClicked__gte=dateStart)

	countryClicks = clicks.values('Country','CountryCode').annotate(Clicks=Count('CountryCode'))
	countrySerializer = LinkCountryStatsSerializer(countryClicks, many=True)

	refererClicks = clicks.values('Referer').annotate(Clicks=Count('Referer'))
	refererSerializer = RefererStatsSerializer(refererClicks, many=True)

	agentTypes = LinkAgentType.objects.filter(Stat__Link=link).filter(Stat__TimeClicked__gte=dateStart)
	browsers = agentTypes.values('Browser').annotate(count=Count('Browser'))
	operatingSystems = agentTypes.values('OS').annotate(count=Count('OS'))
	devices = agentTypes.values('Device').annotate(count=Count('Device'))


	clickSerializer = ClickTotalSerializer(stats, many=True)

	nDict = {
		'Clicks': clickSerializer.data,
		'Referers': refererSerializer.data,
		'Countries': countrySerializer.data,
		'Browsers': browsers,
		'OS': operatingSystems,
		'Devices': devices
	}

	return Response(nDict)

class LinkStatistics(APIView):

	def get(self, request, pk, format=None):
		return getLinkStats(self, request, pk, format=format)

class MonthLinkStatistics(APIView):

	def get(self, request, pk, format=None):
		return getLinkStats(self, request, pk, utility.monthdelta(datetime.now(), -1), format)

class ThreeMonthLinkStatistics(APIView):

	def get(self, request, pk, format=None):
		return getLinkStats(self, request, pk, utility.monthdelta(datetime.now(), -3), format)
		
class DomainStats(APIView):

	def get(self, request, pk, format=None):
		if not request.user.is_authenticated():
			return HttpResponse('', status=401)
		domain = get_object_or_404(SupportedDomain, pk=pk)

		if domain.Domain == 'goli.us':
			statDict = {
				'TotalClicks': self.get_num_clicks(domain, request.user.ExtUser),
				'CountriesReached': self.get_unique_countries(domain, request.user.ExtUser),
				'UniqueVisitors': self.get_num_unique_visitors(domain, request.user.ExtUser),
				'UniqueSources': self.get_unique_sources(domain, request.user.ExtUser)
			}
			return Response(statDict)
		else:
			if request.user.ExtUser.Company != domain.Company:
				return HttpResponse('', status=403)
			serializer = DomainStatsSerializer2(domain)
			return Response(serializer.data)

	def get_num_clicks(self, obj, user):
		return LinkClickTotal.objects.filter(Link__Domain=obj).filter(Link__User=user).filter(Date__gte=(date.today() - timedelta(days=1))).aggregate(Sum('TotalClicked'))['TotalClicked__sum']

	def get_num_unique_visitors(self, obj, user):
		return LinkStat.objects.filter(Link__Domain=obj).filter(Link__User=user).filter(TimeClicked__gte=(date.today() - timedelta(days=1))).values('IpAddress').distinct().count()

	def get_unique_sources(self, obj, user):
		return LinkStat.objects.filter(Link__Domain=obj).filter(Link__User=user).filter(TimeClicked__gte=(date.today() - timedelta(days=1))).values('Referer').distinct().count()

	def get_unique_countries(self, obj, user):
		return LinkStat.objects.filter(Link__Domain=obj).filter(Link__User=user).filter(TimeClicked__gte=(date.today() - timedelta(days=1))).values('CountryCode').distinct().count()

class CompanySerializer(APIView):

	def get(self, request, format=None):
		if not request.user.is_authenticated():
			return HttpResponse('', status=401)
		company = request.user.ExtUser.Company
		serializer = CompanyInfoSerializer(company)
		return Response(serializer.data)

#just returns currently logged in user
class MeSerializer(APIView):

	def get(self, request, format=None):
		if not request.user.is_authenticated():
			return HttpResponse('', status=401)
		serializer = UserSerializer(request.user.ExtUser)
		return Response(serializer.data)

class InterstitialSingle(generics.RetrieveUpdateDestroyAPIView):
	queryset = Intersticial.objects.all()
	serializer_class = InterstitialSerializer
	permission_classes = (IsCompanies, IsAuthenticated, )

	def pre_save(self, obj):
		obj.Company = self.request.user.ExtUser.Company

class InterstitialList(APIView):

	def get(self, request, format=None):
		if not request.user.is_authenticated():
			return HttpResponse('', status=401)
		interstitials = Intersticial.objects.filter(Company=request.user.ExtUser.Company)
		serializer = InterstitialSerializer(interstitials, many=True)
		return Response(serializer.data)		

	def post(self, request, *args, **kwargs):
		if not request.user.is_authenticated():
			return HttpResponse('', status=401)
		cpy = request.DATA.copy()
		cpy['Company'] = request.user.ExtUser.Company.id
		serializer = InterstitialSerializer(data=cpy)
		if serializer.is_valid():
			serializer.save()
			return Response(serializer.data, status=status.HTTP_201_CREATED)
		else:
			return Response(serializer.errors, status=400)



class LoginSerializer(APIView):

	def get(self, request, format=None):
		if not ('username' in request.GET) or not ('password' in request.GET):
			return  HttpResponse('', status=403)
		user = authenticate(username=request.GET['username'],password=request.GET['password'])
		if user is not None:
			token, created = Token.objects.get_or_create(user=user)
			data = {
				'token':token.key
			}
			return Response(data)
		else:
			return HttpResponse('', status=401)

class AnonUrl(APIView):

	def post(self, request, format=None):
		mData = request.DATA.copy()
		mData['Domain'] = SupportedDomain.objects.get(Domain='t.goli.us').id
		prevLink = RedirectLink.objects.filter(RedirectUrl=mData['RedirectUrl']).filter(Domain__id=mData['Domain'])

		if prevLink.count() > 0:
			serializer = LinkSerializer(prevLink[0])
			return Response(serializer.data)
		
		mData['User'] = User.objects.get(username='System').ExtUser.id
		if 'UrlKey' in mData:
			prevLink = RedirectLink.objects.filter(Domain__id=mData['Domain']).filter(UrlKey=mData['UrlKey'])
			if prevLink.count() > 0:
				#Link has been used for this domain, return
				return HttpResponse('', status=400)
		else:
			mData['UrlKey'] = utility.getUniqueRedirectKeyForDomain(mData['Domain'])
		title = ''
		try:
			title = BeautifulSoup(urllib2.urlopen(mData['RedirectUrl'])).title.string
		except Exception, e:
			print "Error getting link title"
			print e
		mData['LinkTitle'] = title
		serializer = LinkSerializer(data=mData)
		if serializer.is_valid():
			serializer.save()
			return Response(serializer.data)
		else:
			return Response(serializer.errors, status=400)

class InterstitialStatView(APIView):

	def get(self, request, format=None):
		mData = {}
		mData['ActionTaken'] = request.GET['action_taken']
		mData['Link'] = request.GET['linkid']
		mData['Intersticial'] = request.GET['inter_id']
		mData['TimeTaken'] = request.GET['time_taken']
		serializer = InterstitialStatSerializer(data=mData)
		if serializer.is_valid():
			serializer.save()
			stitial = serializer.object

			#save aggregate stat for interstitiial
			aggrStats = AggregateInterstitialStat.objects.filter(Intersticial=stitial.Intersticial).filter(Date=date.today())
			if len(aggrStats) != 0:
				aggrStat = aggrStats[0]
			else:
				aggrStat = AggregateInterstitialStat(Intersticial=stitial.Intersticial, Date=date.today())
			aggrStat.incrementAction(stitial.ActionTaken, stitial.TimeTaken)
			aggrStat.save()
			return Response('', status=200)
		else:
			return Response(serializer.errors, status=400)
	
class DomainIntetstitialStat(APIView):

	def get(self, request, pk, format=None):
		if not request.user.is_authenticated():
			return HttpResponse('', status=401)
		inter = get_object_or_404(Intersticial, pk=pk)
		if inter.Company != request.user.ExtUser.Company:
			return HttpResponse('', status=401)
		stats =  InterstitialStat.objects.filter(Intersticial=inter).filter(TimeGathered__gte=datetime.fromtimestamp(int(request.GET['from'])))
		serializer = InterstitialStatSerializer(stats, many=True)
		return Response(serializer.data)

class OverallInterstitialStat(APIView):

	def get(self, request, pk, format=None):
		if not request.user.is_authenticated():
			return HttpResponse('', status=401)
		inter = get_object_or_404(Intersticial, pk=pk)
		if inter.Company != request.user.ExtUser.Company:
			return HttpResponse('', status=401)
		stats = AggregateInterstitialStat.objects.filter(Intersticial=inter).filter(Date__gte=datetime.fromtimestamp(int(request.GET['from'])))
		aggrData = {
			'AdsClicked': 0,
			'ButtonsClicked': 0,
			'RedirectOcurred': 0
		}
		for stat in stats:
			aggrData['AdsClicked'] += stat.AdClicked
			aggrData['ButtonsClicked'] += stat.ButtonClicked
			aggrData['RedirectOcurred'] += stat.RedirectOcurred
		serializer = OverallInterStatAggregateSerializer(aggrData)
		return Response(serializer.data)