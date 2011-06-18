$(document).ready(function(){
	
	/* parse values from URL */	
	var params = get_params();
	if (params["modus"] == "new") {
		//nothing to do for now
	} else {
		fillTable(params, true);
		document.forms["addMovieByImdbId"].submit();
	}
});


function fillTable(params) {
	/* fill complete structure with data */
	document.getElementById('type').value = params["type"];
	document.getElementById('usepath').value = params["usePath"];	
	document.getElementById('imdbid').value = params["ImdbId"];
	document.getElementById('path').value = params["Path"];
	document.getElementById('filename').value = params["Filename"];
	document.getElementById('extension').value = params["Extension"];
}

