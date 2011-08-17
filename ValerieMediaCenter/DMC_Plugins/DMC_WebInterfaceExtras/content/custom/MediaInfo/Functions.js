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
	var usePath = params["usePath"]; 	// => true/false (takes the values path/filename/extension from Rquest)
	var Id = params["Id"]; 	
	var ParentId = params["ParentId"];
	
	//DONE SECTION
	if (mode == "done") {
		//window.alert("Changes have been sent. Please note that you have to save to database after finishing your changes!");
		
		var parameters = "";
		if (typeof(ParentId)!= 'undefined') {
			parameters = parameters +"&ParentId="+ParentId;
		}		
		if (typeof(Id) != 'undefined') {
			parameters = parameters +"&Id="+Id;
		}
		//window.alert('/' + target + '?showSave=true'+parameters);
		window.open('/' + target + '?showSave=true'+parameters, '_self');
		return;
	
	} else if (mode == "error") {
		window.alert("An Error ocurred :(  Check the log please!");
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
		if (type == "isEpisode") {
			document.getElementById('ParentId').value = params["ParentId"];
		}
		
	
	// MANUAL EDIT OF AN EXISTING RECORD 
	} else if (mode == "edit") {
		if (debug) {alert(mode);}
		$('[name=what]').val(type);
		$('[name=oldImdbId]').val(params["ImdbId"]);

		if (type != "isMovie") {
			$("#special_features").hide();
		}
		
		/*fillTable(params, usePath);*/
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
		document.getElementById('id2').value = params["Id"]; /* debug only */
		document.getElementById('id').value = params["Id"];
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
			$("#duck_img").attr("src","/media/" + params["ImdbId"] + "_poster_195x267.png");
			$("#duck_backdrop_img").attr("src","/media/" + params["ImdbId"] + "_backdrop_320x180.png");
			
		} else if (params["type"] == "isTvShow" || params["type"] == "isEpisode") {
			$("#duck_img").attr("src","/media/" + params["TheTvDbId"] + "_poster_195x267.png");
			$("#duck_backdrop_img").attr("src","/media/" + params["TheTvDbId"] + "_backdrop_320x180.png");
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

function changePictures(media_type) {
	var reply = prompt("Please specify URL or PATH to the picture.", "user://http://my.url or user:///path/to/picture");
	//var reply = prompt("Please specify URL or PATH to the picture.", "user://http://img138.imageshack.us/img138/7311/iamlegendposter02.jpg");
	
	var params = get_params();
	var type = params["type"];
	var parameter = new Array();
	
	parameter["method"] = "change_arts";
	
	if (media_type == "poster") {
		parameter["media_type"] = "poster";
	
	} else if (media_type == "backdrop") {
		parameter["media_type"] = "backdrop";
	
	} else {
		alert("no media type defined");
	}
	
	parameter["media_source"] = reply;
	parameter["type"] = type
	parameter["Id"] = params["Id"]
	
	//if (type == "isMovie") {
	//	parameter["ImdbId"] = params["ImdbId"];
	//		
	//} else if (type == "isTvShow") {
	//	parameter["TheTvDbId"] = params["TheTvDbId"];	
	//
	//} else if (type == "isEpisode") {
	//	parameter["TheTvDbId"] = params["TheTvDbId"];
	//	parameter["Season"] = params["Season"];	
	//	parameter["Episode"] = params["Episode"];
	//} else {
	//	alert("no primary key set");
	//}

	if (reply == null) { return;} 
	
	var data = "";
	for (param in parameter) {
		data += param + "=" +  encodeURIComponent(parameter[param]) + "&";
	}

	$.ajax({
		url: "/action",
		type: "GET",
		data: data,
		success: function (returnCode) {
			if (returnCode== "success") {
				 location.reload();
			} else {
				alert('Error - Please try again');
			}
		}
	});

 }
 