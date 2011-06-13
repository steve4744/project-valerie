$(document).ready(function(){
	var params = get_params();
	if (params["usePagination"] == "true") {
		$('#main_table').dataTable( {
			"sScrollY": 768,
			"aaSorting": [[ 1, "asc" ]],
			"bScrollInfinite": true,
			"bPaginate": false,
			"bJQueryUI": true,
			"sPaginationType": "full_numbers"
		} );
	} else {
		$('#main_table').dataTable( {
			"aaSorting": [[ 1, "asc" ]],
			"bScrollInfinite": true,
			"bPaginate": false,
			"bJQueryUI": true,
			"sPaginationType": "full_numbers"
		} );
	}
	$('#sm_save').hide();
});
