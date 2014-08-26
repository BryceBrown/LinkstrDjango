from django.contrib import sitemaps
from django.core.urlresolvers import reverse

class StaticViewMap(sitemaps.Sitemap):
	priority = 0.5
	changefreq = 'daily'

	def items(self):
		return ['index', 'about', 'signup', 'pricing', 'login', 'tour', 'dashboard', 'settings', 'documentation']

	def location(self, item):
		return reverse(item)
