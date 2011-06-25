$(document).ready(function(){

	var debug = false;
	
	/* parse values from URL */	
	var params = get_params();
	
	$("#form1_type").val(params["type"]);
	$("#form2_type").val(params["type"]);
	$("#form3_type").val(params["type"]);
	
	if (debug) {alert(params["modus"]);}
	
	if (params["modus"] != "new") {
		document.getElementById('oldImdbId').value = params["oldImdbId"];
	}
	
	if (params["type"] == "isMovie") {
		$("#header").html("Movie");
	
	} else if (params["type"] == "isTvShow") {
		$("#header").html("TvShow");
		//for now we romove them because thoes functions are not implemented
		$("#form1").remove();
		$("#form2").remove();
		
	} else if (params["type"] == "isEpisode") {
		$("#header").html("Episode");
		
		//for now we romove them because thoes functions are not implemented
		$("#form1").remove();
		$("#form2").remove();
		/*
		$("#form1_idName").html("TheTvDbId");
		$("#form1_explain").html("(e.g. 123456)");
		$("#form1_idType").attr("name","TheTvDbId");
		$("#form1_submit").val("by TheTvDbId");
		*/
	
		

		
	} else {
		alert("Error - no type in params");
	}
	
	if (params["modus"] == "new") {
		//nothing to do for now
	} else {
		fillTable(params, true);
		document.forms["form1"].submit();
	}
});


function fillTable(params) {
	/* fill complete structure with data */
	document.getElementById('form1_type').value = params["type"];
	document.getElementById('usepath').value = params["usePath"];	
	document.getElementById('form1_idType').value = params["ImdbId"];
	document.getElementById('path').value = params["Path"];
	document.getElementById('filename').value = params["Filename"];
	document.getElementById('extension').value = params["Extension"];
}

