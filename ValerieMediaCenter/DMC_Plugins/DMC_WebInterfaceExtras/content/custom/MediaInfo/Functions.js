$(document).ready(function(){
	
	var params = get_params();
	
	if (params["mode"] == "done") {
		window.alert("Changes have been sent. Please note that you have to save to database after finishing your changes!");
		window.close();
		return;
	} else if (params["mode"] == "new_record") {
		$('#type').remove();
		$('#td_type').append('<select id="select_type"><option value="empty">---</option><option value="movies">Movie</option><option value="tvshows">Serie</option><option value="tvshowepisodes">Episode</option></select>');
		$('[name=method]').val("add");
		$('#imdbid').removeAttr("disabled"); 
		$('#thetvdbid').removeAttr("disabled"); 
		$('#select_type').change(function(){
			var selected_type = $(this).find('option:selected').val();
			$('[name=what]').val(selected_type);
			if (selected_type == 'movies' || selected_type == 'tvshows') {
				document.getElementById('season').value = -1;
				$('#season').attr("disabled", true); 
				document.getElementById('episode').value = -1;
				$('#episode').attr("disabled", true); 
		
			} else if (selected_type == 'tvshowepisodes') {
				document.getElementById('season').value = "";
				$('#season').removeAttr("disabled"); 
				document.getElementById('episode').value = "";
				$('#episode').removeAttr("disabled"); 
			}
		});
	} else {
		/* parse values from URL */
		var type = params["type"];
		var imdbid = params["ImdbId"];
		var thetvdbid = params["TheTvDbId"];
		var title = params["Title"];
		var season = params["Season"];
		var episode = params["Episode"];
		var plot = params["Plot"];
		var runtime = params["Runtime"];
		var year = params["Year"];
		var genres = params["Genres"];
		var tag = params["Tag"];
		var popularity = params["Popularity"];
		var path = params["Path"];
		var filename = params["Filename"];
		var extension = params["Extension"];
		
		/* fill complete structure with data */
		document.getElementById('type').value = type;
		document.getElementById('imdbid').value = imdbid;
		document.getElementById('thetvdbid').value = thetvdbid;
		document.getElementById('title').value = title;
		document.getElementById('season').value = season;
		document.getElementById('episode').value = episode;
		document.getElementById('plot').value = plot;
		document.getElementById('runtime').value = runtime;
		document.getElementById('year').value = year;
		document.getElementById('genres').value = genres;
		document.getElementById('tag').value = tag;
		document.getElementById('popularity').value = popularity;
		document.getElementById('path').value = path;
		document.getElementById('filename').value = filename;
		document.getElementById('extension').value = extension;
		
		/* modify tables corresponding to the type */
		if (type == "isMovie") {
			$('#tr_season').remove();
			$('#tr_episode').remove();
			$('#tr_thetvdbid').remove();
			$('#tr_tag').remove();
			
			$('[name=what]').val("movies");
			$("#duck_img").attr("src","http://val.duckbox.info/convertImg2/poster/" + imdbid + "_195x267.png");
			$("#duck_backdrop_img").attr("src","http://val.duckbox.info/convertImg2/backdrop/" + imdbid + "_320x180.png");
			
		} else if (type == "isTvShow") {
			$('#tr_tag').remove();
			$('#tr_season').remove();
			$('#tr_episode').remove();
			$('#tr_popularity').remove();
			$('#tr_runtime').remove();
			$('#tr_path').remove();
			$('#tr_filename').remove();
			$('#tr_extension').remove();
			
			$('[name=what]').val("tvshows");
			$("#duck_img").attr("src","http://val.duckbox.info/convertImg2/poster/" + thetvdbid + "_195x267.png");
			$("#duck_backdrop_img").attr("src","http://val.duckbox.info/convertImg2/backdrop/" + thetvdbid + "_320x180.png");
			
		} else if (type == "isEpisode") {
			
			$('[name=what]').val("tvshowepisodes");
			$("#duck_img").attr("src","http://val.duckbox.info/convertImg2/poster/" + thetvdbid + "_195x267.png");
			$("#duck_backdrop_img").attr("src","http://val.duckbox.info/convertImg2/backdrop/" + thetvdbid + "_320x180.png");
		
		}
	}
});



function get_params(){
	var searchString = decode(document.location.search);

	searchString = searchString.substring(1);

	var nvPairs = searchString.split("&");
	var result = new Array();
	for (var i = 0; i < nvPairs.length; i++){
		 var nvPair = nvPairs[i].split("=");
		 result[decode_utf8(nvPair[0])] = decode_utf8(nvPair[1]);
	}
	return result;
}

function decode(str) {
     return unescape(str.replace(/\+/g, " "));
}

function encode_utf8( s )
{
  return unescape( encodeURIComponent( s ) );
}

function decode_utf8( s )
{
  return decodeURIComponent( escape( s ) );
}
