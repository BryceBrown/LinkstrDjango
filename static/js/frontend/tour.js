
var linkstrTourApp = angular.module('linkstrTourApp', ['ngRoute']);

linkstrTourApp.config(['$routeProvider',
function ($routeProvider){
	$routeProvider.
		when('/Welcome', {
			templateUrl: '/static/templates/one.html',
			controller: 'welcomeCtrl'	
		}).
		when('/GenerateALink', {
			templateUrl: '/static/templates/two.html',
			controller: 'genLinkCtrl'	
		}).
		when('/CustomDomain', {
			templateUrl: '/static/templates/three.html',
			controller: 'customDomainCtrl'	
		}).
		when('/ViewStats', {
			templateUrl: '/static/templates/four.html',
			controller: 'statsCtrl'	
		}).
		when('/CreateAnInterstitial', {
			templateUrl: '/static/templates/five.html',
			controller: 'interstitialCtrl'	
		}).
		when('/ViewAReport', {
			templateUrl: '/static/templates/six.html',
			controller: 'reportCtrl'	
		}).
		when('/SignupNow', {
			templateUrl: '/static/templates/seven.html',
			controller: 'signupCtrl'	
		}).
		otherwise({
			redirectTo: '/Welcome'
		});
}]).controller('MainCtrl', function($scope, $rootScope, $location){

}).controller('welcomeCtrl', function ($scope, $location){

	$scope.next = function (){
		$location.path('/GenerateALink');
	};

}).controller('genLinkCtrl', function ($scope, $location, $http){
	$scope.url = "http://linkstr.wordpress.com";
	$scope.customEnding = "";
	$scope.domain = "t.goli.us"

	$scope.generateLink = function (){
		$scope.loading = true;
		$http.post('/api/AnonymousUrl/', { 
			RedirectUrl: $scope.url
		}).success(function(data, status){
			$scope.loading = false;
			$scope.generated_link = data;
		}).error(function(data, status){
			$scope.loading = false;
			console.log(data);
		});
	};

	$scope.customize = function (){
		$('#CustomLinkModal').modal('show');
	};

	$scope.generateCustomLink = function (){
		$scope.loading = true;
		$('#CustomLinkModal').modal('hide');
		$http.post('/api/AnonymousUrl/', { 
			RedirectUrl: $scope.url,
			UrlKey: $scope.customEnding
		}).success(function(data, status){
			$scope.loading = false;
			$scope.generated_link = data;
		}).error(function(data, status){
			$scope.loading = false;
			console.log(data);
		});
	}

	$scope.previous = function (){
		$location.path('/Welcome');
	};

	$scope.next = function (){
		$location.path('/CustomDomain');
	};

}).controller('customDomainCtrl', function ($scope, $location, $interval){

	$scope.current_domain = 0;
	$scope.domains = ["my.sportssite.com", "thebest.shoopingsite.com", "interesting.techblog.co"];


	$scope.previous = function (){
		$interval.cancel(myIntervalPromise);
		$location.path('/GenerateALink');
	};

	$scope.next = function (){
		$interval.cancel(myIntervalPromise);
		$location.path('/ViewStats');
	};

	var myIntervalPromise = $interval(function(){
		$scope.current_domain += 1;
		if ($scope.current_domain > $scope.domains.length - 1){
			$scope.current_domain = 0;
		}
	}, 5000);

}).controller('statsCtrl', function ($scope, $location){

	$scope.previous = function (){
		$location.path('/CustomDomain');

	};

	$scope.next = function (){
		$location.path('/CreateAnInterstitial');

	};

}).controller('interstitialCtrl', function ($scope, $location){

	$scope.previous = function (){
		$location.path('/ViewStats');

	};

	$scope.next = function (){
		$location.path('/ViewAReport');

	};

}).controller('reportCtrl', function ($scope, $location){

	$scope.previous = function (){
		$location.path('/CreateAnInterstitial');
	};

	$scope.next = function (){
		$location.path('/SignupNow');

	};

}).controller('signupCtrl', function ($scope, $location){

	$scope.previous = function (){
		$location.path('/ViewAReport');

	};

	$scope.signup = function (){
		//TODO
	};

});