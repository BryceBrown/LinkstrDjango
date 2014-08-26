from FrontEnd.models import *
from django.contrib.auth.models import User
from rest_framework import serializers
from django.db.models import Sum
from datetime import datetime, date, timedelta



class InterstitialSerializer(serializers.ModelSerializer):
	Company = serializers.PrimaryKeyRelatedField()

	class Meta:
		model = Intersticial
		fields = ('id', 'Name', 'DisplayChance', 'Company', 'Url', 'AdClickUrl', 'Active')

class DomainSerializer(serializers.ModelSerializer):
	Company = serializers.PrimaryKeyRelatedField()
	Intersticial = InterstitialSerializer()

	class Meta:
		model = SupportedDomain
		fields = ('id','Domain', 'Company', 'Intersticial')

class CompanySerializer(serializers.ModelSerializer):
	Domains = DomainSerializer(many=True)

	class Meta:
		model = Company
		fields = ('id', 'Name', 'PackageLevel', 'Domains')

class UserSerializer(serializers.ModelSerializer):
	Username = serializers.Field('User.username')
	Email = serializers.Field('User.email')

	class Meta:
		model = ExtendedUser
		fields = ('id', 'Username', 'Email', 'IsAdmin', 'AccountActivated')

class AgentTypeSerializer(serializers.ModelSerializer):
	class Meta:
		model = LinkAgentType
		fields = ('AgentType',)

class LanguageSerializer(serializers.ModelSerializer):
	class Meta:
		model = LinkLanguage
		fields = ('Language',)

class LinkTagSerializer(serializers.ModelSerializer):
	class Meta:
		model = LinkTag
		fields = ('Tag',)

class LinkSerializer(serializers.ModelSerializer):
	Domain = serializers.PrimaryKeyRelatedField()
	User = serializers.PrimaryKeyRelatedField()
	Tags = serializers.SerializerMethodField('getTagArray')
	LinkTitle = serializers.CharField(max_length=255, required=False)

	def getTagArray(self, obj):
		tags = []
		for tag in obj.Tags.all():
			tags.append(tag.Tag)
		return tags

	class Meta:
		model = RedirectLink
		fields = ('id', 'LinkTitle', 'UrlKey', 'RedirectUrl', 'Domain', 'User', 'Tags',)

class StatsSerializer(serializers.ModelSerializer):
	AgentTypes = AgentTypeSerializer(many=True)
	Languages = LanguageSerializer(many=True)

	class Meta:
		model = LinkStat
		fields = ('Referer', 'TimeClicked', 'AgentTypes', 'Languages')

class ClickTotalSerializer(serializers.ModelSerializer):
	TotalClicked = serializers.Field('TotalClicked')

	class Meta:
		model = LinkClickTotal
		fields = ('TotalClicked', 'Date')

class DomainStatsSerializer(serializers.ModelSerializer):
	Links = serializers.SerializerMethodField('get_num_links')
	Clicks = serializers.SerializerMethodField('get_num_clicks')
	UniqueVisitors = serializers.SerializerMethodField('get_num_unique_visitors')

	class Meta:
		model = SupportedDomain
		fields = ('Links', 'Clicks', 'UniqueVisitors',)

	def get_num_links(self, obj):
		return obj.Links.count()

	def get_num_clicks(self, obj):
		return LinkClickTotal.objects.filter(Link__Domain=obj).aggregate(Sum('TotalClicked'))['TotalClicked__sum']

	def get_num_unique_visitors(self, obj):
		return LinkStat.objects.filter(Link__Domain=obj).values('IpAddress').distinct().count()

class RefererStatsSerializer(serializers.Serializer):
	Referer = serializers.CharField(max_length=2000)
	Clicks = serializers.IntegerField()

class LinkCountryStatsSerializer(serializers.Serializer):
	Country = serializers.CharField(max_length=100)
	CountryCode = serializers.CharField(max_length=3)
	Clicks = serializers.IntegerField()

class DomainStatsSerializer2(serializers.ModelSerializer):
	TotalClicks = serializers.SerializerMethodField('get_num_clicks')
	CountriesReached = serializers.SerializerMethodField('get_unique_countries')
	UniqueVisitors = serializers.SerializerMethodField('get_num_unique_visitors')
	UniqueSources = serializers.SerializerMethodField('get_unique_sources')

	class Meta:
		model = SupportedDomain
		fields = ('TotalClicks', 'CountriesReached', 'UniqueVisitors', 'UniqueSources',)

	def get_num_clicks(self, obj):
		return LinkClickTotal.objects.filter(Link__Domain=obj).filter(Date__gte=(date.today() - timedelta(days=1))).aggregate(Sum('TotalClicked'))['TotalClicked__sum']

	def get_num_unique_visitors(self, obj):
		return LinkStat.objects.filter(Link__Domain=obj).filter(TimeClicked__gte=(date.today() - timedelta(days=1))).values('IpAddress').distinct().count()

	def get_unique_sources(self, obj):
		return LinkStat.objects.filter(Link__Domain=obj).filter(TimeClicked__gte=(date.today() - timedelta(days=1))).values('Referer').distinct().count()

	def get_unique_countries(self, obj):
		return LinkStat.objects.filter(Link__Domain=obj).filter(TimeClicked__gte=(date.today() - timedelta(days=1))).values('CountryCode').distinct().count()

class PendingUserSerializer(serializers.ModelSerializer):
	Company = CompanySerializer()

	class Meta:
		model = PendingUserRegistration
		fields = ('id', 'Email', 'Company')


class CompanyInfoSerializer(serializers.ModelSerializer):
	Users = UserSerializer(many=True)
	Domains = DomainSerializer(many=True)
	Intersticials = InterstitialSerializer(many=True)
	PendingUsers = PendingUserSerializer(many=True)

	class Meta:
		model = Company
		fields = ('Name', 'PackageLevel', 'Users', 'Domains', 'Intersticials', 'PendingUsers')

class InterstitialStatSerializer(serializers.ModelSerializer):
	Intersticial = serializers.PrimaryKeyRelatedField()
	Link = serializers.PrimaryKeyRelatedField()
	TimeGathered = serializers.DateTimeField(required=False)

	class Meta:
		model = InterstitialStat
		fields = ('Intersticial', 'Link', 'ActionTaken', 'TimeTaken', 'TimeGathered')

class OverallInterStatSerializer(serializers.ModelSerializer):
	Intersticial = serializers.PrimaryKeyRelatedField()

	class Meta:
		model = AggregateInterstitialStat
		fields = ('Intersticial', 'AdClicked', 'ButtonClicked', 'RedirectOcurred', 'AverageTimeTaken', 'Date')

class OverallInterStatAggregateSerializer(serializers.Serializer):
	AdsClicked = serializers.IntegerField()
	ButtonsClicked = serializers.IntegerField()
	RedirectOcurred = serializers.IntegerField()