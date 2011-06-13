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
