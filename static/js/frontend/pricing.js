/*

$( document ).ready(function(){

	//build chart Data
	var stats = [];
	stats.push({
		value: 22,
		color: '#a9afb3'
	});
	stats.push({
		value: 18,
		color: '#0078ff'
	});
	stats.push({
		value: 3,
		color: '#00a2ff'
	});
	stats.push({
		value: 8,
		color: '#6a6161'
	});
	$('#OverallStatDiv').empty();
	$('#OverallStatDiv').append("<canvas id='OverallStatChart' height='300' width='300'></canvas>");

	

		var ctx = document.getElementById("OverallStatChart").getContext("2d");
		new Chart(ctx).Doughnut(stats);
	setTimeout(function(){
		var marketingData = {
			labels : ["March","April","May","June","July"],
			datasets : [
				{
					fillColor : '#a9afb3',
					strokeColor : '#6a6161',
					data : [72,89,44,33,60]
				},
				{
					fillColor : '#00a2ff',
					strokeColor : '#0078ff',
					data : [65,59,90,81,56]
				}
			]
		}
		$('#MarketingChartTwoDiv').empty();
		$('#MarketingChartTwoDiv').append("<canvas id='MarketingChartTwo' height='300' width='300'></canvas>");
		var ctx = document.getElementById("MarketingChartTwo").getContext("2d");
		new Chart(ctx).Radar(marketingData);
	}, 500);


	setTimeout(function(){

		var marketingDataTwo = {
			labels : ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"],
			datasets : [
				{
					fillColor : "rgba(220,220,220,0.5)",
					strokeColor : "rgba(220,220,220,1)",
					pointColor : "rgba(220,220,220,1)",
					pointStrokeColor : "#fff",
					data : [65,59,90,81,56,55,40]
				},
				{
					fillColor : "rgba(151,187,205,0.5)",
					strokeColor : "rgba(151,187,205,1)",
					pointColor : "rgba(151,187,205,1)",
					pointStrokeColor : "#fff",
					data : [28,48,40,19,96,27,100]
				}
			]
		};
		$('#MarketingChartThreeDiv').empty();
		$('#MarketingChartThreeDiv').append("<canvas id='MarketingChartThree' height='300' width='400'></canvas>");

		var ctx = document.getElementById("MarketingChartThree").getContext("2d");
		new Chart(ctx).Line(marketingDataTwo);
	}, 1000);
});*/


$( document ).ready(function(){

	$('#signup_button').click(function(e){
		$('#loginModal').modal('show');
	});

});