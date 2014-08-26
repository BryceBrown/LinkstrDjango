
var logged = false;
var startTime;
var refId;
/*(0,'AddClicked'),
(1,'ButtonClicked'),
(2,'RedirectOccurred')*/
function logInterstitialStat(data, redirectUrl){
	if(!logged){
		logged = true;
		data.Intersticial = interstitialId;
		data.Link = linkId;
		data.TimeTaken =  (new Date()).getTime() - startTime;

		var xmlHttp = null;

	    xmlHttp = new XMLHttpRequest();
	    xmlHttp.open( "GET", baseUrl + "api/InterstitialStat?" + getStatQueryString(data), false );
	    try{
	    	xmlHttp.send( null );
	    }catch(e){}
		window.location = redirectUrl;
	}
}

function getStatQueryString(data){
	var qStr = "";
	qStr += "linkid=" + data.Link;
	qStr += "&inter_id=" + data.Intersticial;
	qStr += "&time_taken=" + data.TimeTaken;
	qStr += "&action_taken=" + data.ActionTaken;
	qStr += "&callback=?"
	return qStr;
}


$( document ).ready(function(){
	
	$('#NextButton').click(function(){
		logInterstitialStat({
			ActionTaken: 1
		}, urlToRedirectTo);
	});

	$('#ad_frame').click(function() {
		logInterstitialStat({
			ActionTaken: 0
		}, addUrl);
	});

	refId = setInterval(function(){
		if(intervalTime <= 0){
			$("#RedirectCountDown").text("Redirecting...");
			clearInterval(refId);
			logInterstitialStat({
				ActionTaken: 2
			}, urlToRedirectTo);
		}
		var timeToRedirect = intervalTime / 1000;
		if (timeToRedirect <= 0) {
			$("#RedirectCountDown").text("Redirecting...");
		}else{
			$("#RedirectCountDown").text("You will be redirected in:" + timeToRedirect);
		}
		intervalTime -= 1000;
	}, 1000);

	startTime = (new Date()).getTime();
});
