$(document).ready(function(){
	var params = get_params();
	$('#main_table').dataTable( {
		"sScrollY": 768,
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
});
