var activeDomain = null;
var activeLink = null;
var mLinks = [];
var mDomains = [];
const linkPageSize = 8;
var currentPage = 1;
var tour;
var currentElement;
var linkStats;

//Array of colors


$.get('/api/Domains', function(domains){
	mDomains = domains;
	if(domains.length > 0) {
		setActiveDomain(domains[0]);
		if(domains.length > 1){
			console.log("Got mulitple domains");
			for(var i=0;i<domains.length;i++){
				$('#DomainSelectControl').append('<option value="' + i + '">' + domains[i].Domain + '</option>');
			}
			$('#ActiveDomain').click(function(){
				$('#SwitchDomainModal').modal('show');
			});
		}
	}
});

function setActiveDomain(domain){
	activeDomain = domain;
	loadDomainStats(domain);
	$('#currentDomain').text(domain.Domain);
	refreshLinks(domain.id);
}

function refreshLinks(domainId){
	var query = "?q=" + $('#SearchTextBox').val();
	if(query === "?q="){
		query = "";
	}
	$.get('/api/Domains/' + domainId + '/Links/' + query, function(links){
		mLinks = links;
		console.log(mLinks.length);
		loadLinks();
	});
}

function loadLinks(){
	$('#links').empty();
	console.log("Loading Links...");
	var start = (currentPage - 1) * linkPageSize;
	var end = currentPage * linkPageSize;
	console.log("Start - " + start);
	console.log("End - " + end);

	var animationCounter = 1;
	var tmpLinkRef = [];
	var linkAddedCounter = 0;
	while(start < end && start < mLinks.length){
		var linkText = mLinks[start].LinkTitle;
		if(linkText.length == 0){
			linkText = mLinks[start].RedirectUrl + " - " + mLinks[start].UrlKey;
			if (linkText.length >=40){
				linkText = mLinks[start].RedirectUrl.substring(0, 30) + " - " + mLinks[start].UrlKey;
			}
		}
		if (mLinks[start].LinkTitle != '' && linkText.length >=40){
			linkText = mLinks[start].LinkTitle.substring(0, 30);
		}
		var linkRef = $("<a class='list-group-item fly_in_left' data-redirect-url='" + mLinks[start].UrlKey +  "' data-href='" + mLinks[start].RedirectUrl + "' linkId='" + mLinks[start].id + "'>" + linkText + "</a>").click(function(sender){
			//Link was clicked, query and load stats
			activeLink = {
				id: jQuery(this).attr("linkId"),
				UrlKey: jQuery(this).attr("data-redirect-url"),
				RedirectUrl: jQuery(this).attr("data-href"),
			}
			var mText = jQuery(this).attr("data-href");
			if (mText.length >=40){
				mText = mText.substring(0, 30) + "... - ";
			}
			$('#StatTitle').text(mText);
			$('#StatTitle').attr('href', jQuery(this).attr("data-href"));
			loadLinkStats(activeLink, "Month");
		});
		tmpLinkRef.push(linkRef);
		setTimeout(function(){
			$('#links').append(tmpLinkRef[linkAddedCounter]);
			linkAddedCounter++;
		}, 50 * animationCounter);
		start++;
		animationCounter++;
	}
}

function loadDomainStats(domain) {
	//TODO Overall Domain Stats
	showDomainStats();
	$('#DomainStatsName').text(domain.Domain);
	$.get('/api/Domains/' + domain.id + '/Stats/', function(stats){
		showElement($('#DomainStatsDiv'));
		$('#NumCountries').text(GetReadableNumberFromNumber(stats.CountriesReached));
		$('#NumSources').text(GetReadableNumberFromNumber(stats.UniqueSources));
		$('#NumVisitors').text(GetReadableNumberFromNumber(stats.UniqueVisitors));
		$('#NumClicks').text(GetReadableNumberFromNumber(stats.TotalClicks));
		loadDomainChart(stats);
	});
}

function loadDomainChart(domainStats){
	console.log("Loading Domain Chart...");
	var stats = [];
	stats.push({
		value: domainStats.CountriesReached,
		color: '#6a6161'
	});
	stats.push({
		value: domainStats.UniqueSources,
		color: '#0078ff'
	});
	stats.push({
		value: domainStats.UniqueVisitors,
		color: '#00a2ff'
	});
	stats.push({
		value: domainStats.TotalClicks,
		color: '#a9afb3'
	});
	$('#DomainDoughnutChartDiv').empty();
	$('#DomainDoughnutChartDiv').append(getChartCanvas('DomainDoughnutChart'));

	var ctx = document.getElementById("DomainDoughnutChart").getContext("2d");
	var myNewChart = new Chart(ctx).Doughnut(stats);
}

function  loadLinkStats(link, timeType) {
	showLinkStats();
	$.get('/api/Links/' + link.id + "/Stats/" + timeType, function(stats){
		linkStats = stats;
		// Start Loading 
		console.log("Got links");
		loadClicksButton();
	});
}

function getRefererData(stats){
	var referers = [];
	var counts = [];

	function compare(a,b) {
	  if (a.Clicks < b.Clicks)
	     return 1;
	  if (a.Clicks > b.Clicks)
	    return -1;
	  return 0;
	}
	stats.Referers.sort(compare);
	for(var i=0;i<stats.Referers.length;i++){
		var item = stats.Referers[i];
		referers.push(item.Referer);
		counts.push({ 
			value: item.Clicks,
			color: getRandomColor()
		});
	}
	return {
		Referers: referers,
		Clicks: counts
	}
}

function setUpRefererChart(data){
	$('#RefererChart').empty();
	$('#RefererChart').append(getChartCanvas('RefererDoughnutChart'));

	buildRefererTable(data);

	var ctx = document.getElementById("RefererDoughnutChart").getContext("2d");
	var myNewChart = new Chart(ctx).Doughnut(data.Clicks);
}

function buildRefererTable(data){
	$('#RefererTableBody').empty();
	var totalClicks = 0;
	for(var i=0;i<data.Clicks.length;i++){
		totalClicks += data.Clicks[i].value;
	}
	for(var i=0;i<data.Referers.length;i++){
		addRowToTable(data.Referers[i],
			'#RefererTableBody', 
			[data.Referers[i], data.Clicks[i].value, (data.Clicks[i].value / totalClicks) * 100], data.Clicks[i].color);
	}
}

function getDeviceData(stats){
	var devices = [];
	var counts = [];
	function compare(a,b) {
	  if (a.count < b.count)
	     return 1;
	  if (a.count > b.count)
	    return -1;
	  return 0;
	}
	stats.Devices.sort(compare);
	for(var i=0;i<stats.Devices.length;i++){
		var item = stats.Devices[i];
		devices.push(item.Device);
		counts.push({ 
			value: item.count,
			color: getRandomColor()
		});
	}
	return {
		Devices: devices,
		Clicks: counts
	}
}

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

function getBrowserData(stats){
	var browsers = [];
	var counts = [];
	function compare(a,b) {
	  if (a.count < b.count)
	     return 1;
	  if (a.count > b.count)
	    return -1;
	  return 0;
	}
	stats.Browsers.sort(compare);
	for(var i=0;i<stats.Browsers.length;i++){
		var item = stats.Browsers[i];
		browsers.push(item.Browser);
		counts.push({ 
			value:item.count,
			color: getRandomColor()
		});
	}
	return {
		Browsers: browsers,
		Clicks: counts
	}
}

function getOsData(stats){
	var OSs = [];
	var counts = [];

	function compare(a,b) {
	  if (a.count < b.count)
	     return 1;
	  if (a.count > b.count)
	    return -1;
	  return 0;
	}
	stats.OS.sort(compare);
	for(var i=0;i<stats.OS.length;i++){
		var item = stats.OS[i];
		OSs.push(item.OS);
		counts.push({ 
			value: item.count,
			color: getRandomColor()
		});
	}
	return {
		OSs: OSs,
		Clicks: counts
	}
}

function setUpCountryBars(data){
	$('#WorldBarChartContainer').empty();
	$('#WorldBarChartContainer').append(getChartCanvas('WorldBarChartCanvas'));
	var chartOptions = {
		scaleOverride: true,
		scaleStepWidth: 1,
		scaleStartValue: 0,
		scaleSteps: getMaxOfArray(data.Clicks)
	};

	var chartData = {
		labels: data.Countries,
		datasets: [{
			data: data.Clicks
		}]
	};
	var ctx = document.getElementById("WorldBarChartCanvas").getContext("2d");
	var myNewChart = new Chart(ctx).Bar(chartData, chartOptions);
	
}

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

function getCountryBars(clickStatObj){
	var countries = [];
	var clicks = [];
	for(stat in clickStatObj.Countries){
		cStat = clickStatObj.Countries[stat];
		countries.push(cStat.Country);
		clicks.push(cStat.Clicks);
	}
	var data = {
		Countries: countries,
		Clicks: clicks
	};
	console.log(data);
	return data;
}

function getLinkClickData(clickStatObj){
	var linkSeries = [];
	var highestClickValue = 0;

	for(stat in clickStatObj.Clicks){
		cObj = clickStatObj['Clicks'][stat];
		var mX = Date.parse(cObj.Date);
		if(cObj.TotalClicked > highestClickValue){
			highestClickValue = cObj.TotalClicked;
		}
		var linkSeriesPoint = {
			x: mX / 1000,
			y: cObj.TotalClicked
		};
		linkSeries.push(linkSeriesPoint);
	}
	function compare(a,b) {
	  if (a.x < b.x)
	     return -1;
	  if (a.x > b.x)
	    return 1;
	  return 0;
	}
	linkSeries.sort(compare);
	console.log(linkSeries);

	//Grab the first one, add 3 days before it
	point = {
		x: Date.parse(new Date()) / 1000,
		y: 0
	}
	if(linkSeries.length > 0){
		point = linkSeries[0];
	}
	for(var i=1; i <= 3; i++ ){
		pointToAdd = {
			x: point.x - (i * 86400),
			y: 0
		};
		linkSeries.unshift(pointToAdd);
	}
	console.log(linkSeries);

	//If there are no clicks, set the highest to 10
	if(highestClickValue == 0){
		highestClickValue = 10;
	}
	var statData = {
		name: "Clicks",
		data: linkSeries,
		color: '#428bca',
		//Ohhh so ghetto. This is attached in order to add an additional return value so that we can calculate what the max of the series is and should be set at
		highestClicked: highestClickValue
	};

	return statData;
}

$(function() {
  $('a[href*=#]:not([href=#])').click(function() {
    if (location.pathname.replace(/^\//,'') == this.pathname.replace(/^\//,'') && location.hostname == this.hostname) {
      var target = $(this.hash);
      target = target.length ? target : $('[name=' + this.hash.slice(1) +']');
      if (target.length) {
        $('html,body').animate({
          scrollTop: target.offset().top
        }, 1000);
        return false;
      }
    }
  });
});

function getLinkCountryData(clickStatObj){
	stats = {};
	for(stat in clickStatObj.Countries){
		cStat = clickStatObj.Countries[stat];
		stats[cStat.CountryCode] = cStat.Clicks;
	}

	return stats;
}

function showLinkStats(){
	$('#DomainStatsDiv').addClass('hidden');
	$('#DomainStatsDiv').removeClass('show');
	$('#LinkStatsDiv').addClass('show');
	$('#LinkStatsDiv').removeClass('hidden');
}

function showDomainStats(){
	$('#LinkStatsDiv').addClass('hidden');
	$('#LinkStatsDiv').removeClass('show');
	$('#DomainStatsDiv').addClass('show');
	$('#DomainStatsDiv').removeClass('hidden');
}

function generateLink(urlInput, outerControl){
	var linkToRedirect = $(urlInput).val();
	if (ValidUrl(linkToRedirect)){
		$(outerControl).removeClass('has-error');
		linkToGetRedirectFrom = {
			RedirectUrl: linkToRedirect,
			Domain: activeDomain.id
		};
		console.log("Adding new Link");
		$.post('/api/Links/', linkToGetRedirectFrom, function(data){
			//$('#link').text(data.)
			console.log(data);
			if(data.UrlKey === undefined){
				data = data[0];
			}
			showModalForLink(data, activeDomain);
			refreshLinks(activeDomain.id);
		}).error(function (error) {
			console.log("Error posting Link");
			console.log(error);
			warnBadUrl(outerControl);
		});
	}else {
		warnBadUrl(outerControl);
	}
}

function warnBadUrl(control){
	if(($(control).attr('class').indexOf('has-error') == -1)){
		$(control).addClass('has-error');
	}
	alert('Not a valid URL');
}

function showModalForLink(link, domain){
	var redirText = domain.Domain + "/" + link.UrlKey;
	console.log(redirText);
	reddit_url = redirText;
	$('#FacebookShareLink').click(function(){
		FB.ui(
		  {
		    method: 'feed',
		    name: 'Facebook Dialogs',
		    link: redirText,
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
	});
	var fbShareLink = "<div class='fb-share-button' data-href='" + redirText + "' data-type='button'></div>";
	$('#FacebookShareLink').append(fbShareLink);
	var twitterString = "http://twitter.com/share?text=" + redirText
	$('#TwitterShareLink').attr("href", twitterString);
	$('#NewRedirDiv').text(redirText);
	$('#NewLinkModal').modal('show');
}

function deleteLink(link){
	$.ajax({
		url: '/api/Links/' + link.id + '/',
		type: 'DELETE',
		success: function(result){
			console.log("Success");
			refreshLinks(activeDomain.id);
			showDomainStats(activeDomain);
		}
	});
}

function setSectionText(element){
	var text = element.text();
	$('#SectionTitleButton').text(text);
}

function loadClicksButton(){
	showElement($('#ClickDiv'));
	var linkSeries = getLinkClickData(linkStats);
	setUpLinkClickGraph(linkSeries);
	setSectionText($('#ClicksButton'));
}

function showElement(element){
	if(currentElement != null){
		currentElement.removeClass('show');
		currentElement.addClass('hidden');
	}
	currentElement = element;
	element.addClass('show');
	element.removeClass('hidden');
}

//Assign event Handlers
$( document ).ready(function(){

	$('#ClicksButton').click(loadClicksButton);

	$('#CountriesButton').click(function(){
		showElement($('#CountryDiv'));
		var countrySeries = getLinkCountryData(linkStats);
		var countryBars = getCountryBars(linkStats);
		setUpWorldMap(countrySeries);
		setSectionText($('#CountriesButton'));
		//setUpCountryBars(countryBars);
	});

	$('#BrowsersButton').click(function(){
		showElement($('#BrowserDiv'));
		var browserData = getBrowserData(linkStats);
		setUpBrowserChart(browserData);
		setSectionText($('#BrowsersButton'));
	});

	$('#DevicesButton').click(function(){
		showElement($('#DeviceDiv'));
		var deviceData = getDeviceData(linkStats);
		setUpDeviceChart(deviceData);
		setSectionText($('#DevicesButton'));
	});

	$('#OSButton').click(function(){
		showElement($('#OSDiv'));
		var osData = getOsData(linkStats);
		setUpOsChart(osData);
		setSectionText($('#OSButton'));
	});

	$('#ClickSourceButton').click(function(){
		showElement($('#RefererDiv'));
		var refererData = getRefererData(linkStats);
		setUpRefererChart(refererData);
		setSectionText($('#ClickSourceButton'));
	});

	$('#PreviousPage').click(function(){
		console.log("Previous Page");
		if(currentPage > 1){
			currentPage--;
			console.log("changing page");
			loadLinks();
		}
	});

	$('#NextPage').click(function(){
		console.log("Next Page");
		console.log($('#links').children().length);
		if ($('#links').children().length == linkPageSize){
			console.log("changing page");
			currentPage++;
			loadLinks();
		}
	});

	$('#GenLinkButtonSmall').click(function(){
		generateLink('#ShortenUrlSmall', '#UrlLinkSmall');
	});

	$('#GenLinkButton').click(function(){
		generateLink('#ShortenUrl', '#UrlLink');
	});

	$('#ShortenUrl').keypress(function(e){
		if(e.which == 10 || e.which == 13){
			generateLink('#ShortenUrl', '#UrlLink');
		}
	});

	$('#GenCustomUrlButton').click(function(){
		$('#CustomLinkModal').modal('show');
		$('#CustomUrlToShorten').val($('#ShortenUrl').val());
	});

	$('#MonthLink').click(function(){
		if(activeLink != null) {
			loadLinkStats(activeLink, 'Month');
		}
	});

	$('#ThreeMonthLink').click(function(){
		if(activeLink != null) {
			loadLinkStats(activeLink, 'ThreeMonth');
		}
	});

	$('#AllTimeLink').click(function(){
		if(activeLink != null){
			loadLinkStats(activeLink, '');
		}
	});

	$('#ShareButton').click(function(){
		showModalForLink(activeLink, activeDomain);
	});

	$('#DeleteButton').click(function(){
		var redirText = activeDomain.Domain + "/" + activeLink.UrlKey + " <br /> " + activeLink.RedirectUrl;
		$('#LinkToDelete').empty();
		$('#LinkToDelete').append(redirText);
		$('#DeleteLinkModal').modal('show');
	});

	$('#ConfirmDeleteLink').click(function(){
		deleteLink(activeLink);
	});

	$('#GenerateCustomLinkButton').click(function(){
		var customRedirLink = {
			RedirectUrl: $('#CustomUrlToShorten').val(),
			UrlKey: $('#CustomUrlEnding').val()
		};
		console.log(customRedirLink);
		$.post('/api/Links/', customRedirLink, function(data){
			$('#CustomLinkModal').modal('hide');
			showModalForLink(data, activeDomain);
		}).error(function(err){
			console.log(err);
			alert("Ending has already been used");
		});
	});

	$('#ShowStats').click(function(){
		loadDomainStats(activeDomain.id);
	});

	$('#ConfirmSwitchDomain').click(function(){
		setActiveDomain(mDomains[$('#DomainSelectControl').val()]);
	});

	$('#SearchButton').click(function(){
		refreshLinks(activeDomain.id);
	});

	function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    	return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
	}

	$.ajaxSetup({
	    crossDomain: false, // obviates need for sameOrigin test
	    beforeSend: function(xhr, settings) {
	        if (!csrfSafeMethod(settings.type)) {
	            xhr.setRequestHeader("X-CSRFToken", $('[name="csrfmiddlewaretoken"]').attr('value'));
	        }
	    }
	});

	tour = new Tour();
	tour.addSteps([
		{
			element: "#UrlLink",
			title: "Shorten Link",
			content: "Enter Links in here and press the Go Button to get started."
		},
		{
			element: "#GenCustomUrlButton",
			title: "Custom Link",
			content: "If you have a premium account, you can generate custom shortened Urls"
		},
		{
			element: "#currentDomain",
			title: "Domain",
			content: "This is the currently selected domain. Some levels of premium accounts allow for mulitple domains."
		},
		{
			element: "#links",
			title: "Links",
			content: "This are all of the links that you have generated in the past."
		},
		{
			element: "#pagingButtons",
			title: "Paging",
			content: "Use these buttons to navigate pages of links (Currently, only 10 show at a time)"
		},
		{
			element: "#links",
			title: "Links",
			content: "Select a link to view click statistics on it"
		},
		{
			element: "#ShareButton",
			title: "Sharing",
			content: "Once you have generated a link, you may re-share it here."
		},

	]);
	tour.start();

});

