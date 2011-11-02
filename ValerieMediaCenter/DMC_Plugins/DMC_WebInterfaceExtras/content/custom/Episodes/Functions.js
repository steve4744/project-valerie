$(document).ready(function(){
	document.title = document.title + " - Episodes";
	var params = get_params();
	var message = params["msg"];
	
	$('#main_table').dataTable( {
		"sScrollY": 768,
		"aaSorting": [[ 1, "asc" ]],
		<!-- PAGINATION_FLAG -->
		"bJQueryUI": true,
		"sPaginationType": "full_numbers"
	} );

	if (params["mode"] == "error") {
		window.alert("An Error ocurred :( \n\n" + message);
		return;
	}	
	if (params["showSave"] != "true") {
		$('#sm_save').hide();
	}
});

function zap(url){
	//alert(url);
	jQuery.ajax({
	  url: url,
	  context: document.body,
	  success: function(){
		//nothing to do for now;
	  }
	});
}
