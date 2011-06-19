$(document).ready(function(){
	var params = get_params();
	$('#main_table').dataTable( {
		"aaSorting": [[ 1, "asc" ]],
		<!-- PAGINATION_FLAG -->
		"bJQueryUI": true,
		"sPaginationType": "full_numbers"
	} );

	if (params["showSave"] != "true") {
		$('#sm_save').hide();
	}
});
