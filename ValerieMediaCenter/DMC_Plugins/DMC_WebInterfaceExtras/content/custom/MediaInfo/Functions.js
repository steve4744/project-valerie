//
//MEDIAINFO
//
$(document).ready(function(){

	var debug = false;
	
	/* parse values from URL */	
	var params = get_params();
	var mode = params["mode"];			// => done/edit/new_record/change_imdbid
	var target = params["target"]; 		// => movies/tvshows/episodes
	var type = params["type"]; 			// => isMovie/isTvShow/isEpisode
	var useData = params["useData"]; 	// => true/false
	var usePath = params["usePath"] 	// => true/false (takes the values path/filename/extension from Rquest)
	
	//DONE SECTION
	if (mode == "done") {
		window.alert("Changes have been sent. Please note that you have to save to database after finishing your changes!");
		if (typeof(thetvdbid) != 'undefined') {
			window.open('/' + target + '?showSave=true&TheTvDbId=' + thetvdbid, '_self');			
		} else {
			window.open('/' + target + '?showSave=true', '_self');
		}
		return;
	
	//ADD NEW RECORD 
	} else if (mode == "new_record") {
		if (debug) {alert(mode);}
		$('[name=method]').val("add");
		$('[name=what]').val(type);
		
		if (useData == "true") {
			fillTable(params, usePath);
		}
		
		$("#special_features").hide();
		
		changeTable(type);
		document.getElementById('type').value = params["type"];
	
	// MANUAL EDIT OF AN EXISTING RECORD 
	} else if (mode == "edit") {
		if (debug) {alert(mode);}
		$('[name=what]').val(type);
		$('[name=oldImdbId]').val(params["ImdbId"]);

		if (type != "isMovie") {
			$("#special_features").hide();
		}
		
		fillTable(params, usePath);
		changeTable(type);
		
		$("#tr_imdbid").hide();
	
	//CHANGE EXISTING RECORD BY CHANGING IMDBID
	} else if (mode == "change_imdbid") {
		if (debug) {alert(mode);}
		$('[name=what]').val(type);
		$('[name=oldImdbId]').val(params["oldImdbId"]);
		
		$("#special_features").hide();
		
		fillTable(params, usePath);
		changeTable(type);
		
		$("#tr_imdbid").hide();
	
	//SHOULD NOT HAPPEN :-)
	} else {
		alert("ERROR - no mode defined")
	}
});


function changeTable(table_type) {
	if (table_type == "isMovie") {
		$('#tr_season').remove();
		$('#tr_episode').remove();
		$('#tr_thetvdbid').remove();
		$('#tr_tag').remove();
	} else if (table_type == "isTvShow") {
		$('#tr_tag').remove();
		$('#tr_season').remove();
		$('#tr_episode').remove();
		$('#tr_popularity').remove();
		$('#tr_runtime').remove();
		$('#tr_path').hide();
		$('#tr_filename').hide();
		$('#tr_extension').hide();
		// dirty workaround until TvShow needs those information like a movie or episode
		document.getElementById('path').value = "/dummy/";
		document.getElementById('filename').value = new Date().getTime();
		document.getElementById('extension').value = "dmy";
		
	} else if (table_type == "isEpisode") {
		//for now nothing
	} else {
		alert("Error - no type found");
	}
}

function fillTable(params, usePath) {
		/* fill complete structure with data */
		document.getElementById('type').value = params["type"];
		document.getElementById('imdbid').value = params["ImdbId"];
		document.getElementById('thetvdbid').value = params["TheTvDbId"];
		document.getElementById('title').value = params["Title"];
		document.getElementById('season').value = params["Season"];
		document.getElementById('episode').value = params["Episode"];
		document.getElementById('plot').value = params["Plot"];
		document.getElementById('runtime').value = params["Runtime"];
		document.getElementById('year').value = params["Year"];
		document.getElementById('genres').value = params["Genres"];
		document.getElementById('tag').value = params["Tag"];
		document.getElementById('popularity').value = params["Popularity"];
		if (usePath == "true") {
			document.getElementById('path').value = params["Path"];
			document.getElementById('filename').value = params["Filename"];
			document.getElementById('extension').value = params["Extension"];
		}

		if (params["type"] == "isMovie") {
			$("#duck_img").attr("src","http://val.duckbox.info/convertImg2/poster/" + params["ImdbId"] + "_195x267.png");
			$("#duck_backdrop_img").attr("src","http://val.duckbox.info/convertImg2/backdrop/" + params["ImdbId"] + "_320x180.png");
			
		} else if (params["type"] == "isTvShow" || params["type"] == "isEpisode") {
			$("#duck_img").attr("src","http://val.duckbox.info/convertImg2/poster/" + params["TheTvDbId"] + "_195x267.png");
			$("#duck_backdrop_img").attr("src","http://val.duckbox.info/convertImg2/backdrop/" + params["TheTvDbId"] + "_320x180.png");
		}
}

function showAlternatives() {
	var params = get_params();
	var reply = prompt("Please specify your search string.", params["Title"]);
	if (reply == null) { return;} 
	urlString = "/alternatives?";
	urlString += "type=" + params["type"] + "&";
	urlString += "modus=existing&";
	urlString += "oldImdbId=" + params["ImdbId"] + "&";
	urlString += "Title=" + reply + "&";
	urlString += "Path=" + params["Path"] + "&";
	urlString += "Filename=" + params["Filename"] + "&";
	urlString += "Extension=" + params["Extension"];

	window.open(urlString, '_self');
}
