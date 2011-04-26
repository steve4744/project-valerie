function applyFilter(phrase, _id){
	var words = phrase.value.toLowerCase().split(" ");
	var table = document.getElementById(_id);
	var ele;
	for (var r = 1; r < table.rows.length; r++){
		ele = table.rows[r].innerHTML.replace(/<[^>]+>/g,"");
	        var displayStyle = 'none';
	        for (var i = 0; i < words.length; i++) {
		    if (ele.toLowerCase().indexOf(words[i])>=0)
			displayStyle = '';
		    else {
			displayStyle = 'none';
			break;
		    }
	        }
		table.rows[r].style.display = displayStyle;
	}
}
function resetFilter(_id) {
	document.getElementById('filter').value = '';
	var table = document.getElementById(_id);
	for (var r = 1; r < table.rows.length; r++){
		displayStyle = '';
		table.rows[r].style.display = displayStyle;
	}
}
