
function getMaxOfArray(numArray) {
    return Math.max.apply(null, numArray);
}


function addRowToTable(rowID, table, values, color){
	//Frist, clear table
	var row = "<tr id='" + rowID + "'>"
	for (var i = 0; i < values.length; i++) {
		var colorBox = "";
		if (i == 0) {
			colorBox = "<div style='background-color:" + color + ";' class='color_box'></div>"
		}
		var text = values[i];
		if(text.length > 30){
			text = text.substring(0, 30) + "...";
		}
		row += "<td>" + colorBox + "  " + text + "</td>";
	};
	row += "</tr>";
	$(table).append(row);
	//return $("#" + rowID);
}


function getRandomColor(){
	var letters = '0123456789ABCDEF'.split('');
    var color = '#';
    for (var i = 0; i < 6; i++ ) {
        color += letters[Math.round(Math.random() * 15)];
    }
    return color;
}


function GetReadableNumberFromNumber(number){
	if(number == null){
		return 0;
	}
	if(number > 1000000){
		var mil = Math.round((number / 1000000) * 100) / 100;
		return mil + "M";
	}
	if(number > 1000){
		var thou = Math.round((number / 1000) * 100) / 100;
		return thou + "K";
	}
	return number + "";
}

function ValidUrl(str) {
	//Fuck it for now.
	return str.length > 0;
}

function getChartSize() {
	if(screen.width < 400){
		return 250;
	}
	if(screen.width < 600){
		return 300;
	}
	if(screen.width < 992){
		return 400;
	}
	return 500;
}

function getChartCanvas(id){
	return "<canvas id='" + id + "'  width='" + getChartSize() + "' height='" + getChartSize() + "' ></canvas>";
}



function compareValue(a,b) {
  if (a.value < b.value)
     return 1;
  if (a.value > b.value)
    return -1;
  return 0;
}

function shortenLongUrl(url, key){
	var linkText = url + " - " + key;
	if (linkText.length >=40){
		linkText = url.substring(0, 30) + " - " + key;
	}
	return linkText;
}

function shortText(text, length){
	if (text.length > length) {
		text = text.substring(0, length) + "...";
	}
	return text;
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

	//Now that it is sorted, we need to fill in each in between day 
	var initLength = linkSeries.length;
	if (initLength > 0) {
		var currPos = 0;
		while(currPos < initLength - 2){
			point = linkSeries[currPos];
			var nextDay = point.x + 86400;
			while(nextDay <= linkSeries[currPos + 1].x){
				linkSeries.push({
					x: nextDay,
					y: 0
				});
				nextDay += 86400;
			}
			currPos += 1;
		}
	}
	linkSeries.sort(compare);

	//now grab the latest day, and add days to the current day
	if (linkSeries.length > 0) {
		var lastDay = linkSeries[linkSeries.length - 1];
		var today = Date.parse(new Date()) / 1000;
		var nextDay = lastDay.x + 86400;
		while(nextDay < today){
			linkSeries.push({
				x:nextDay,
				y:0
			});
			nextDay += 86400;
		}
	}

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

function getLinkCountryData(clickStatObj){
	stats = {};
	for(stat in clickStatObj.Countries){
		cStat = clickStatObj.Countries[stat];
		stats[cStat.CountryCode] = cStat.Clicks;
	}

	return stats;
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