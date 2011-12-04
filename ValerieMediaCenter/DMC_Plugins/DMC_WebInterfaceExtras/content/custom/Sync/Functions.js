$(document).ready(function(){

	var isRunning = $('#isRunning').val();
	var isFinished = $('#isFinished').val();
	var currentProgress = $('#currentProgress').val();
	var currentRange = $('#currentRange').val();
	
	if (isRunning == "False") { 
		$("#cancelSync").hide();
		$("#normalSync").show();
		$("#fastSync").show();		
	} else {
		$("#cancelSync").show();
		$("#normalSync").hide();
		$("#fastSync").hide();
		showSyncProgress(currentRange);
		showSyncLog();
	}
});


function showSyncLog() {
	dmurl = document.location.host;
	var i=0;
	for (i=0;i<=41;i++) { //because we have 40 lines of log
		url = "http://" + dmurl + "/syncronize?mode=getSyncLog&row=" + i;
		jQuery.get(url, function(data){
			data = data + "<br>";
			$("#syncLog").append(data);
		});
	}
}

function showSyncProgress(currentRange) {
	dmurl = document.location.host;
	url = "http://" + dmurl + "/syncronize?mode=getSyncPercentage";	
	
	$("#uploadprogressbar").progressBar();
	$("#uploadprogressbar").fadeIn();

	jQuery.get(url, function(currentProgress){
		percentage = Math.round(currentProgress / (currentRange / 100));
		$("#uploadprogressbar").progressBar(percentage);
	});
	
	
}

