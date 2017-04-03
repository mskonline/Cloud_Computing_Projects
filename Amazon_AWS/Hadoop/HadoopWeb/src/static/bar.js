$(document).ready(function(){
	var browserTableRow = '<tr><td class="file">#fn#</td>' +
		'<td class="flastmodified">#lm#</td>' +
		'<td class="fsize">#sz# bytes</td>' +
		'<td><div class="downloadButton" fileName="#fn#">Download</div></td><td><div class="deleteButton" fileName="#fn#">Delete</div></td></tr>';

	$("#tabs").tabs({
		  active: 1
	});

	$('form').on('submit', function(){
		$('input[name=uploadTime]').val(new Date().getTime());
	});
});