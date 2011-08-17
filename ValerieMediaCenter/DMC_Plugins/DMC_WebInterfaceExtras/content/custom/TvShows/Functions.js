$(document).ready(function(){
	var params = get_params();
	var i = 1,timer;

	$('#main_table').dataTable( {
		"sScrollY": 768,
		"aaSorting": [[ 1, "asc" ]],
		<!-- PAGINATION_FLAG -->
		"bJQueryUI": true,
		"sPaginationType": "full_numbers"
	} );

	if (params["showSave"] != "true") {
		$('#sm_save').hide();
	}
	else
	{
		window.setInterval ( "blink('#sm_save')", 1500 );
	}
		
});
