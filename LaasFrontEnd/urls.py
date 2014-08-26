from django.conf.urls import patterns, include, url
from django.contrib import admin
from FrontEnd import api
from FrontEnd import views
from FrontEnd import postviews
from FrontEnd import sitemaps
from FrontEnd import tasks
from django.http import HttpResponse


admin.autodiscover()
sitemaps = {
    'staticpages': sitemaps.StaticViewMap
}

apiPatterns = patterns('',
    url(r'^Domains/$', api.DomainList.as_view(), name='DomainList'),
    url(r'^Domains/(?P<pk>[0-9]+)/Links/$', api.RedirectUrlsForDomain.as_view(), name='LinkList'),
    url(r'^Domains/(?P<pk>[0-9]+)/Stats/$', api.DomainStats.as_view(), name='DomainStats'),
    url(r'^Domains/(?P<pk>[0-9]+)/InterstitialStats/$', api.DomainIntetstitialStat.as_view(), name='DomainInterstitialStats'),
    url(r'^Links/(?P<pk>[0-9]+)/Stats/$',api.LinkStatistics.as_view()),
    url(r'^Links/(?P<pk>[0-9]+)/Stats/Month/$', api.MonthLinkStatistics.as_view(), name='MyLinksMonth'),
    url(r'^Links/(?P<pk>[0-9]+)/Stats/ThreeMonth/$', api.ThreeMonthLinkStatistics.as_view(), name='MyLinksMonth'),
    url(r'^Links/$', api.RedirectUrl.as_view(), name='MyLinksAllTime'),
    url(r'^Links/(?P<pk>[0-9]+)/$', api.SingleRedirectUrl.as_view(), name='MyLinksAllTime'),
    url(r'^CompanySettings/$', api.CompanySerializer.as_view(), name='CompanyInfo'),
    url(r'^Me/$', api.MeSerializer.as_view(), name='MeSerializer'),
    url(r'^Interstitials/(?P<pk>[0-9]+)/$', api.InterstitialSingle.as_view(), name='Interstitials'),
    url(r'^Interstitials/$', api.InterstitialList.as_view(), name='InterstitialList'),
    url(r'^AnonymousUrl/$', api.AnonUrl.as_view(), name='AnonymousUrl'),
    url(r'^Login/$', api.LoginSerializer.as_view(), name='LoginAPI'),
    url(r'^InterstitialStat/$', api.InterstitialStatView.as_view(), name='IntetstitilStatPost'),
    url(r'^Interstitials/(?P<pk>[0-9]+)/Stats/$', api.DomainIntetstitialStat.as_view(), name='IntetstitilStatPost'),
    url(r'^Interstitials/(?P<pk>[0-9]+)/OverallStats/$', api.OverallInterstitialStat.as_view(), name='IntetstitilStatPost'),
)

genericViews = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^About/$', views.about, name='about'),
    url(r'^Signup/$', views.betaSignup, name='signup'),
    url(r'^Pricing/$', views.pricing, name='pricing'),
    url(r'^AdminStatus/$', views.adminStatusPage, name='adminstatus'),
    url(r'^Logout/$', views.logoutPage, name='documentation'),
    url(r'^Documentation/$', views.documentation),
    url(r'^Login/$', views.loginView, name='login'),
    url(r'^Tour/$', views.tour, name='tour'),
    url(r'^Dashboard/$', views.dashboardView, name='dashboard'),
    url(r'^PleaseAuthenticate/$', views.pleaseAuthenticate),
    url(r'^Settings/$', views.mySettingsView, name='settings'),
    url(r'^Redirect404/$', views.redir404),
    url(r'^Activate/$', views.activateAccount),
    url(r'^WelcomeToBeta/$', views.betaWelcome),
    url(r'^TestAdd/$', views.testAdd),
    url(r'^robots\.txt$', lambda r: HttpResponse("User-agent: *\nDisallow: /admin/", mimetype="text/plain")),
    url(r'^sitemap\.xml$', 'django.contrib.sitemaps.views.sitemap', {'sitemaps': sitemaps}),
    #temporary for kupaday
    url(r'^kup_privacy_policy/$', views.kupadayPrivacyPolicy),
    url(r'^CancellationComplete/$', views.cancellationComplete),
    url(r'^CancelAccount/$', views.cancelAccount),


)

taskPatterns = patterns('',
    url(r'^save_admin_stats/$', tasks.storeAdminStat),
    url(r'^check_expired_companies/$', tasks.expireAccount),
)

planPatterns = patterns('',
    #url(r'^Basic/$', views.planFreeTrialBetaClick),
    url(r'^Pro/$', views.proPlan),
    #url(r'^Enterprise/$', views.planFreeTrialBetaClick),
    #url(r'^Compare/$', views.planFreeTrialBetaClick),
    #url(r'^Basic/Purchase/$', views.planFreeTrialBetaClick),
    url(r'^Pro/Purchase/$', views.plansPurchasePro),
    #url(r'^Enterprise/Purchase/$', views.planFreeTrialBetaClick),
)

postPatterns = patterns('',
    url(r'^Signup/$', postviews.postSignup),
    url(r'^Login/$', postviews.postLogin),
    url(r'^BasicSignup/$', postviews.postBasicSignup),
    url(r'^ProSignup/$', postviews.postProSignup),
    url(r'^EnterpriseSignup/$', postviews.postLogin),
    url(r'^AddEditDomain/$', postviews.addEditDomain),
    url(r'^DeleteDomain/$', postviews.deleteDomain),
    url(r'^DeleteUserInvite/$', postviews.deleteUserInvite),
    url(r'^AddUserInvite/$', postviews.addUserInvite),
    url(r'^RevokeUserAccount/$', postviews.revokeUserAccount),
    url(r'^EditUserAccount/$', postviews.editUserAccount),
    url(r'^AddEditInterstitial/$', postviews.addEditInterstitial),
    url(r'^DeleteInterstitial/$', postviews.deleteInterstitial),
    url(r'^CancelAccount/$', postviews.cancelAccount),
)

urlpatterns = patterns('',
    url(r'^', include(genericViews)),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^api/',include(apiPatterns)),
    url(r'^Post/',include(postPatterns)),
    url(r'^Plans/', include(planPatterns)),
    url(r'^Tasks/', include(taskPatterns))
)
