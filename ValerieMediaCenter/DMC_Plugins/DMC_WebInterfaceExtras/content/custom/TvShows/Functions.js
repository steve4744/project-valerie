$(document).ready(function(){
	$('#main_table').dataTable( {
		"aaSorting": [[ 1, "asc" ]],
		"bScrollInfinite": true,
		"bPaginate": false,
		"bJQueryUI": true,
		"sPaginationType": "full_numbers"
	} );
	$('#sm_save').hide();
});
