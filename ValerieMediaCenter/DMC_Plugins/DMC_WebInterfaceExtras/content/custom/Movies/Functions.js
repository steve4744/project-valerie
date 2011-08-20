$(document).ready(function(){ 
	document.title = document.title + " - Movies";
	var params = get_params();
	$('#main_table').dataTable( {
		"aaSorting": [[ 1, "asc" ]],
		<!-- PAGINATION_FLAG -->
		"bJQueryUI": true,
		"sPaginationType": "full_numbers"
	} );

	if (params["mode"] == "error") {
			window.alert("An Error ocurred :(  Check the log please!");
		return;
	}	

	if (params["showSave"] != "true") {
		$('#sm_save').hide();
	}
	else
	{
		window.setInterval ( "blink('#sm_save')", 1500 );
	}

});
