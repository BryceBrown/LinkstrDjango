
var linkstr_dashboard = angular.module('linkstr_dashboard', ['ngRoute']);

linkstr_dashboard.config(['$routeProvider', '$httpProvider',
function ($routeProvider, $httpProvider) {
	$routeProvider
		.when('/Stats', {
			templateUrl: '/static/templates/dashboard/stats.html',
			controller: 'statsCtrl'	
		}).when('/Links', {
			templateUrl: '/static/templates/dashboard/links.html',
			controller: 'linksCtrl'
		}).when('/Reports', {
			templateUrl: '/static/templates/dashboard/reports.html',
			controller: 'reportsCtrl'
		}).when('/MyAds', {
			templateUrl: '/static/templates/dashboard/ads.html',
			controller: 'myAdsCtrl'
		}).when('/Domains', {
			templateUrl: '/static/templates/dashboard/domains.html',
			controller: 'domainsCtrl'
		}).when('/Links/:linkId', {
			templateUrl: '/static/templates/dashboard/linkStat.html',
			controller: 'linkStatCtrl'
		}).otherwise({
            redirectTo: '/Stats'
        });

        $httpProvider.defaults.xsrfCookieName = 'csrftoken';
		$httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken';
}]).config(['$provide', function($provide){
    $provide.decorator('$rootScope', ['$delegate', function($delegate){

        Object.defineProperty($delegate.constructor.prototype, '$onRootScope', {
            value: function(name, listener){
                var unsubscribe = $delegate.$on(name, listener);
                this.$on('$destroy', unsubscribe);
            },
            enumerable: false
        });


        return $delegate;
    }]);
}]).factory('linkSvc', ['$http', '$location', 
function ($http, $location) {

	var activeInterstitial = null;
	var interstitials = null;

	var activeDomain = null;
	var domains = null;

	var activeLink = null;

	return {

		setActiveLink: function(link) {
			activeLink = link;
		},

		getActiveLink: function(){
			return activeLink;
		},

		getActiveLinkById: function(id){
			if (activeLink) {
				return {
					then: function(fnc){
						fnc(activeLink);
					}
				};
			}else{
				return $http.get('/api/Links/' + id).then(function(results){
					activeLink = results.data;
					return activeLink;
				});
			}
		},

		setActiveDomain: function(domain) {
			activeDomain = domain;
		},

		getActiveDomain: function() {
			return this.getDomains().then(function(domains){
				return activeDomain;
			});
		},

		setActiveInterstitial: function(stitial) {
			activeInterstitial = stitial;
		},

		getDomains: function () {
			return $http.get('/api/Domains/')
				.then(function(results){
					domains = results.data;
					if(domains.length > 0 && !activeDomain){
						activeDomain = domains[0];
					}
					return domains;
				});
		},

		getStatsForDomain: function () {
			return this.getActiveDomain().then(function(domain){
				return $http.get('/api/Domains/' + domain.id + '/Stats/')
				.then(function(results){
					return results.data;
				});
			})
		},

		getLinks: function (query) {
			return this.getActiveDomain().then(function(domain){
				return $http.get('/api/Domains/' + domain.id + '/Links/' + query)
				.then(function(results){
					return results.data;
				});
			})
		},

		getStatsForLink: function (linkId) {
			return $http.get('/api/Links/' + linkId + '/Stats/')
			.then(function(results){
				return results.data;
			});
		},

		getShortenedUrl: function (link) {
			return $http.post('/api/Links/', link)
			.then(function(result){
				return results.data;
			});
		},

		getInterstitials: function () {
			if (!interstitials) {
				interstitials = $http.get('/api/Interstitials/')
				.then(function(results){
					return results.data;
				});
			}
			return interstitials;
		},

		getInterstitialStats: function (interId, timestamp) {
			return $http.get('/api/Interstitials/' + interId + "/Stats/?from=" + timestamp)
			.then(function(results){
				return results.data;
			});
		},

		getOverallInterstitialStats: function(interId, timestamp) {
			return $http.get('/api/Interstitials/' + interId + '/OverallStats/?from=' + timestamp)
			.then(function(results){
				return results.data;
			})
		},

		updateInterstitial: function(interstitial) {
			return $http.put('/api/Interstitials/' + interstitial.id, interstitial)
			.then(function(result){
				return result.data;
			});
		},

		saveInterstitial: function(interstitial) {
			return $http.post('/api/Interstitials/', interstitial)
			.then(function(result){
				return result.data;
			});
		},

		deleteInterstitial: function(interstitial) {
			return $http.delete('/api/Interstitials/' + interstitial.id, interstitial)
			.then(function(result){
				return result.data;
			});
		},

		generateLink: function(link) {
			return $http.post('/api/Links/', link).then(function(result){
				return result.data;
			});
		},

		deleteLink: function(link) {
			return $http.delete('/api/Links/', link).then(function(result){

			});
		},

		saveDomain: function(domain) {
			return $http.post('/api/Domains/', domain).then(function(result){
				return result.data;
			});
		}

	};
}]).controller('mainCtrl',['$scope', '$rootScope', '$location', 'linkSvc', 
function ($scope, $rootScope, $location, linkSvc) {

	$scope.domains = linkSvc.domains;
	$scope.currentDomain = linkSvc.activeDomain;
	$scope.interstitials = null;
	$scope.activeLink = {};

	$scope.RedirectUrl = "";
	$scope.UrlKey = "";

	$scope.activeSection = "";

	$scope.linkText = "asdasd";

  	$scope.$on('linkShare', function(event, link) {
  		$scope.activeLink = link;
  		$scope.linkText = $scope.currentDomain.Domain + '/' + link.UrlKey;
  		$('#NewLinkModal').modal('show');
  	});

	$scope.getFullUrl = function() {
		return $scope.currentDomain.Domain + '/' + $scope.activeLink.UrlKey;
	};

	$scope.showCustomize = function () {
		$('#CustomLinkModal').modal('show');
	};

	$scope.switchDomain = function() {
		$scope.prevDomain = $scope.currentDomain;
		$('#SwitchDomainModal').modal('show');
	};

	$scope.selectDomain = function() {
		linkSvc.setActiveDomain($scope.currentDomain);
		$('#SwitchDomainModal').modal('hide');
		$rootScope.$emit('dChange', '');
		$location.path('/Links');
	};

	$scope.closeSelectDomainModal = function() {
		$scope.currentDomain = $scope.prevDomain;
		$('#SwitchDomainModal').modal('hide');
	}

	$scope.shortenLink = function () {
		$scope.linkToShorten = {
			RedirectUrl: $scope.RedirectUrl,
			Domain: $scope.currentDomain.id
		};
		linkSvc.generateLink($scope.linkToShorten).then(function(link){
			$scope.activeLink = link;
			$scope.linkText = $scope.currentDomain.Domain + '/' + link.UrlKey;
			$('#NewLinkModal').modal('show');
			$rootScope.$emit('linksChanged', link);
		});
	};

	$scope.shortenCustomizeLink = function() {
		$scope.linkToShorten = {
			RedirectUrl: $scope.RedirectUrl,
			UrlKey: $scope.UrlKey,
			Domain: $scope.currentDomain.id
		};
		linkSvc.generateLink($scope.linkToShorten).then(function(link){
			$scope.activeLink = link;
			$scope.linkText = $scope.currentDomain.Domain + '/' + link.UrlKey;
			$('#NewLinkModal').modal('show');
			$rootScope.$emit('linksChanged', link);
		});
		$('#CustomLinkModal').modal('hide');
	};

	$scope.redditShare = function(){
		window.location = 'http://www.reddit.com/submit?url=' + getFullUrl();
	};

	$scope.twitterShare = function(){

	};

	$scope.facebookShare = function(){
		FB.ui(
		  {
		    method: 'feed',
		    name: 'Facebook Dialogs',
		    link: $scope.getFullUrl(),
		    redirect_uri: 'https://www.facebook.com',
		    description: 'Dialogs provide a simple, consistent interface for applications to interface with users.'
		  },
		  function(response) {
		    if (response && response.post_id) {
		      console.log('Post was published.');
		    } else {
		      console.log('Post was not published.');
		    }
		  }
		);
	};

	$scope.isActive = function (viewLocation) { 
        return viewLocation === $location.path();
    };

    linkSvc.getDomains().then(function(res){
    	$scope.domains = res;
    	if ($scope.domains.length > 0) {
    		$scope.currentDomain = $scope.domains[0];
    	}
    })

    linkSvc.getInterstitials().then(function(stitials){
    	$scope.interstitials = stitials;
    });

}]).controller('statsCtrl',['$scope', '$rootScope', '$location', 'linkSvc', function ($scope, $rootScope, $location, linkSvc){

	$scope.activeInterstitial = null;
	$scope.interstitials = null;
	$scope.fromTime = 0;


	function loadOverallInterstitialStats(inerstitialStats){
		chartData = [{
			name: 'Ad Clicked',
			value: inerstitialStats.AdsClicked,
			color: '#0078ff'
		},
		{
			name: 'Buttons Clicked',
			value: inerstitialStats.ButtonsClicked,
			color: '#a9afb3'
		},
		{
			name: 'Redirects Occurred',
			value: inerstitialStats.RedirectOcurred,
			color: '#6a6161'
		}];
		chartData.sort(compareValue);


		$('#OverallStatsChart').empty();
		$('#OverallStatsChart').append(getChartCanvas('OverallInterstitialChart'));

		buildOverallTable(chartData);

		var ctx = document.getElementById("OverallInterstitialChart").getContext("2d");
		var myNewChart = new Chart(ctx).Doughnut(chartData);
	}

	function buildOverallTable(overallData){
		$('#OverallTableBody').empty();
		var totalClicks = 0;
		for(var i=0;i<overallData.length;i++){
			totalClicks += overallData[i].value;
		}
		$scope.totalClicks = 0;
		for(var i=0;i<overallData.length;i++){
			$scope.totalClicks += overallData[i].value;
			var percentage = overallData[i].value == 0 ? 0 :  ((overallData[i].value / totalClicks) * 100).toFixed(2);
			addRowToTable(overallData[i].name,
				'#OverallTableBody', 
				[overallData[i].name, overallData[i].value, percentage], overallData[i].color);
		}
	}

	$scope.changeInterstitial = function(){
		$('#InterstitialModal').modal('show');
	}

	$scope.previewInterstitial = function(){

	}

	$scope.configureInterstitial = function(){
		$('#ConfigureInterstitialModal').modal('show');
	}

	$scope.loadInterstitialStats = function(){
		linkSvc.getOverallInterstitialStats($scope.activeInterstitial.id, $scope.fromTime)
		.then(function(stats){
			loadOverallInterstitialStats(stats);
		});
	}

	linkSvc.getInterstitials().then(function(Interstitials){
		$scope.interstitials = Interstitials;
		if($scope.interstitials.length > 0){
			$scope.activeInterstitial = $scope.interstitials[0];
			$scope.loadInterstitialStats($scope.activeInterstitial);
		}
	});


}]).controller('linksCtrl',['$scope', '$rootScope', '$location', 'linkSvc', function ($scope, $rootScope, $location, linkSvc){

	$scope.links = null;
	$scope.activeLink = null;
	$scope.query = "";
	var stats = null;

	$scope.currentPage = 1;
	$scope.pageSize = 10;
	$scope.filteredLinks = null;

	$scope.nextPage = function(){
		if (($scope.currentPage * $scope.pageSize) >= $scope.links.length) {
			return;
		}

		$scope.currentPage += 1;
		filterPages();
	};

	$scope.previousPage = function(){
		if ($scope.currentPage == 1) {
			return;
		}

		$scope.currentPage -= 1;
		filterPages();
	};

	function filterPages(){
	   	var begin = (($scope.currentPage - 1) * $scope.pageSize)
	    	, end = begin + $scope.pageSize;

		$scope.filteredLinks = $scope.links.slice(begin, end);
	};

	$scope.$onRootScope('dChange', function(event, args){
		getLinks();
	});

	$scope.$onRootScope('linksChanged', function(event, link){
		getLinks();
	});

	$scope.searchButton = function(){
		linkSvc.getLinks($scope.query)
		.then(function(links){

		})
	};

	$scope.showLinkStats = function(link){
		//load stats for link
		linkSvc.setActiveLink(link);
		$location.path('/Links/' + link.id);
	};

	$scope.shareLink = function(link){
		linkSvc.setActiveLink(link);
		$scope.activeLink = link;

	};

	$scope.deleteLink = function(link, $index){
		linkSvc.deleteLink(link).then(function(){
			$scope.interstitials.splice($index,1);	
		});
	};

	var loadLinkStats = function(link){
		$scope.activeLink = link;
		linkSvc.getStatsForLink(link.id)
		.then(function(results){
			stats = results;
			//loadStatsCharts(stats);
		});
	};

	var getLinks = function (){
		linkSvc.getLinks($scope.query).then(function(links){
			$scope.links = links;
			for (var i = 0; i < links.length; i++) {
				links[i].RedirectUrlShort = shortText(links[i].RedirectUrl, 60);
				links[i].LinkTitleShort = shortText(links[i].LinkTitle, 60);
			};
			if (links.length > 0) {
				loadLinkStats(links[0]);
			}
			filterPages();
		});
	};

	getLinks();


}]).controller('reportsCtrl',['$scope', '$rootScope', '$location', 'linkSvc', 
function ($scope, $rootScope, $location, linkSvc){
	//TODO
}]).controller('myAdsCtrl',['$scope', '$rootScope', '$location', 'linkSvc', 
function ($scope, $rootScope, $location, linkSvc){

	$scope.activeInterstitial = null;
	$scope.interstitials = null;
	$scope.currentIndex = -1;
	$scope.errorInSubmission = false;

	$scope.newInterstitial = function(){
		$scope.activeInterstitial = {DisplayChance:100, Active:true};
		$('#InterstitialModal').modal('show');
	};

	$scope.editInterstitial = function(stitial, index){
		$scope.currentIndex = index;
		$scope.activeInterstitial = stitial;
		$('#InterstitialModal').modal('show');
	};

	$scope.saveInterstitial = function(){
		$scope.errorInSubmission = !$scope.interstitialForm.$valid;
		if(!$scope.errorInSubmission){
			if ($scope.activeInterstitial.id) {
			linkSvc.updateInterstitial($scope.activeInterstitial);
			}else{
				linkSvc.saveInterstitial($scope.activeInterstitial).then(function(result){
					$scope.interstitials.push(result);
				});
			}
			$('#InterstitialModal').modal('hide');
		}
	};

	$scope.deleteInterstitial = function(){
		if ($scope.activeInterstitial.id) {
			linkSvc.deleteInterstitial($scope.activeInterstitial).then(function(){
				$scope.interstitials.splice($scope.currentIndex,1);	
			});
		}
	};

	linkSvc.getInterstitials().then(function(Interstitials){
		$scope.interstitials = Interstitials;
	});

}]).controller('domainsCtrl',['$scope', '$rootScope', '$location', 'linkSvc', 
function ($scope, $rootScope, $location, linkSvc){

	$scope.domains = null;
	$scope.currentDomain = null;
	$scope.interstitials = null;

	$scope.selectedInter = null;

	$scope.editDomain = function(domain){
		$scope.currentDomain = domain;
		$scope.selectedInter = null;
		if(domain.Intersticial){
			for (var i = 0; i < $scope.interstitials.length; i++) {
				if($scope.interstitials[i].id == domain.Intersticial.id){
					$scope.selectedInter = $scope.interstitials[i];
				}
			}
		}
		$('#EditDomainModal').modal('show');
	};

	$scope.saveEditDomain = function(currentDomain){
		$('#EditDomainModal').modal('hide');
		currentDomain.Intersticial = $scope.selectedInter;
		linkSvc.saveDomain(currentDomain).then(function(){
			refreshDomains();
		});
	};

	$scope.newDomain = function() {
		$scope.currentDomain = {};
		$('#EditDomainModal').modal('show');
	};

	function refreshDomains() {
		linkSvc.getDomains().then(function(res){
	    	$scope.domains = res;
	    });
	}

	refreshDomains();
	linkSvc.getInterstitials().then(function(inters){
		$scope.interstitials = inters;
	});

}]).controller('linkStatCtrl',['$scope', '$rootScope', '$location', '$routeParams', 'linkSvc', 
function ($scope, $rootScope, $location, $routeParams, linkSvc){

	$scope.linkId = $routeParams.linkId;
	$scope.currentSection = "Clicks";
	$scope.stats = null;

	$scope.shareLink = function(){
  		$scope.$emit('linkShare', linkSvc.getActiveLink());
	};

	$scope.clickStats = function(){
		$scope.currentSection = "Clicks";
		setUpLinkClickGraph(getLinkClickData($scope.stats));
	};

	$scope.countryStats = function(){
		$scope.currentSection = "Countries";
		var countrySeries = getLinkCountryData($scope.stats);
		setTimeout(function(){
			setUpWorldMap(countrySeries);
		},1);
	};

	$scope.browserStats = function(){
		$scope.currentSection = "Browsers";
		setUpBrowserChart(getBrowserData($scope.stats));
	};

	$scope.deviceStats = function(){
		$scope.currentSection = "Devices";
		setUpDeviceChart(getDeviceData($scope.stats));
	};

	$scope.osStats = function(){
		$scope.currentSection = "Operating Systems";
		setUpOsChart(getOsData($scope.stats));
	};

	$scope.setPeriod = function(period){

	};

	//World map
	function setUpWorldMap(data){
		$('#WorldMapStats').empty();
		$('#WorldMapStats').vectorMap({
			map: 'world_mill_en',
	    	series: {
				regions: [{
    				values: data,
    				scale: ['#C8EEFF', '#0071A4'],
					normalizeFunction: 'linear'
    			}],
	    	},
          	onRegionLabelShow: function(e, el, code){
          		var clicks = data[code];
          		if(clicks === undefined){
          			clicks = 0;
          		}
           		el.html(el.html()+' (Clicks - ' + clicks + ')');
          	}
	    	
		});
	}

	//Link Clicks
	function setUpLinkClickGraph(data){
		$('#chart').empty();
		$('#chart').removeClass('rickshaw_graph');
		$('#y_axis').empty();
		var graph = new Rickshaw.Graph( {
			element: document.querySelector("#chart"),
			width: 800,
			height: 300,
	   		renderer: 'area',
	   		stroke: true,
	       	interpolation: 'linear',
			max: data.highestClicked + (.2 * data.highestClicked),
		    series: [data]
		});
		var hoverDetail = new Rickshaw.Graph.HoverDetail( {
		    graph: graph
		} );

		var x_axis = new Rickshaw.Graph.Axis.Time( { graph: graph } );

		var y_axis = new Rickshaw.Graph.Axis.Y( {
			        graph: graph,
			        tickFormat: Rickshaw.Fixtures.Number.formatKMBT,
			        element: document.getElementById('y_axis'),
		} );

		graph.render();
	}

	//Browser
	function buildBrowserTable(BrowserData){
		$('#BrowserTableBody').empty();
		var totalClicks = 0;
		for(var i=0;i<BrowserData.Clicks.length;i++){
			totalClicks += BrowserData.Clicks[i].value;
		}
		for(var i=0;i<BrowserData.Browsers.length;i++){
			addRowToTable(BrowserData.Browsers[i],
				'#BrowserTableBody', 
				[BrowserData.Browsers[i], BrowserData.Clicks[i].value, (BrowserData.Clicks[i].value / totalClicks) * 100], BrowserData.Clicks[i].color);
		}
	}

	function setUpBrowserChart(data){
		$('#BrowserChart').empty();
		$('#BrowserChart').append(getChartCanvas('BrowserDonutChart'));

		buildBrowserTable(data);

		var ctx = document.getElementById("BrowserDonutChart").getContext("2d");
		var myNewChart = new Chart(ctx).Doughnut(data.Clicks);
	}

	//Devices
	function setUpDeviceChart(data){
		$('#DeviceChart').empty();
		$('#DeviceChart').append(getChartCanvas('DeviceDoughnutChart'));

		buildDeviceTable(data);

		var ctx = document.getElementById("DeviceDoughnutChart").getContext("2d");
		var myNewChart = new Chart(ctx).Doughnut(data.Clicks);
	}

	function buildDeviceTable(data){
		$('#DevicesTableBody').empty();
		var totalClicks = 0;
		for(var i=0;i<data.Clicks.length;i++){
			totalClicks += data.Clicks[i].value;
		}
		for(var i=0;i<data.Devices.length;i++){
			addRowToTable(data.Devices[i],
				'#DevicesTableBody', 
				[data.Devices[i], data.Clicks[i].value, (data.Clicks[i].value / totalClicks) * 100], data.Clicks[i].color);
		}
	}

	//Operating Systems
	function buildOsTable(OSData){
		$('#OsTableBody').empty();
		var totalClicks = 0;
		for(var i=0;i<OSData.Clicks.length;i++){
			totalClicks += OSData.Clicks[i].value;
		}
		for(var i=0;i<OSData.OSs.length;i++){
			addRowToTable(OSData.OSs[i],
				'#OsTableBody', 
				[OSData.OSs[i], OSData.Clicks[i].value, Math.floor((OSData.Clicks[i].value / totalClicks) * 100)], OSData.Clicks[i].color);
		}
	}

	function setUpOsChart(data){
		$('#OSChart').empty();
		$('#OSChart').append(getChartCanvas('OsDonutChart'));
		

		var ctx = document.getElementById("OsDonutChart").getContext("2d");
		var myNewChart = new Chart(ctx).Doughnut(data.Clicks);

		buildOsTable(data);
	}


	linkSvc.getActiveLinkById($scope.linkId).then(function(link){
		$scope.link = link;
		$scope.link.displayUrl = shortText($scope.link.RedirectUrl, 30);
	});

	linkSvc.getStatsForLink($scope.linkId).then(function(stats){
		$scope.stats = stats;
		$scope.clickStats();
	});

}]);


