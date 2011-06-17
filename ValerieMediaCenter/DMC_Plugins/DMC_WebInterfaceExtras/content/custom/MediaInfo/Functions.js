//
//MEDIAINFO
//
$(document).ready(function(){
	
	/* parse values from URL */	
	var params = get_params();
	var mode = params["mode"];
	var target = params["target"];
	var type = params["type"];
	var useData = params["useData"];
	var usePath = params["usePath"]
	
	//DONE SECTION
	if (mode == "done") {
		window.alert("Changes have been sent. Please note that you have to save to database after finishing your changes!");
		if (typeof(thetvdbid) != 'undefined') {
			window.open('/' + target + '?showSave=true&TheTvDbId=' + thetvdbid, '_self');			
		} else {
			window.open('/' + target + '?showSave=true', '_self');
		}
		return;
	
	//NEW RECORD SECTION
	} else if (mode == "new_record") {

		$('[name=method]').val("add");
		$('[name=what]').val(type);
		
		if (useData == "true") {
			fillTable(params, usePath);
		}
		changeTable(type);
	
	//EDIT SECTION
	} else {
		$('[name=what]').val(type);
		
		fillTable(params, usePath);
		changeTable(type);
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
		$('#tr_path').remove();
		$('#tr_filename').remove();
		$('#tr_extension').remove();
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
