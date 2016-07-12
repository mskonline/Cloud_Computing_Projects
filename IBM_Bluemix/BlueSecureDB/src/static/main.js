$(document).ready(function(){
	var browserTableRow = '<tr><td class="file">#fn#</td>' +
		'<td class="fdescription">#fd#</td>' +
		'<td class="fversion">#fv#</td>' +
		'<td class="fsize">#sz# bytes</td>' +
		'<td><div class="downloadButton" fileName="#fn#" version="#fv#">Download</div></td><td><div class="deleteButton" fileName="#fn#" version="#fv#">Delete</div></td></tr>';

	$("#tabs").tabs({
		  active: 1,
		  activate: function( event, ui )
		  {
			  if(ui.newTab.index() == 1) // Browse Tab
				  $.getFileList();
		  }
	});

	$('form').on('submit', function(){
		var fileInput = $('#fileInput');

		if(fileInput[0].files.length > 0){
			var sizeInBytes = fileInput[0].files[0].size;
			$('input[name=size]').val(sizeInBytes);

			if(sizeInBytes > 1048576 /* 1MB in bytes*/ ) {
				alert('File size needs to be less than 1MB');

				event.stopPropagation();
			    event.preventDefault();
			}
		} else {
			alert('Select file to upload');
			event.stopPropagation();
		    event.preventDefault();
		}
	});

	$.updateView = function(){
		$(".downloadButton").click(function(){
    		var fileName = $(this).attr('fileName');
    		var version = $(this).attr('version');
    		window.location = "/downloadFile/" + fileName + "/" + version;
    	});

		$(".deleteButton").click(function(){
			var fileName = $(this).attr('fileName');
			var version = $(this).attr('version');
			$.ajax({
		        url: '/deleteFile/' + fileName + "/" + version,
		        type: 'POST',
		        success: function(data, textStatus, jqXHR)
		        {
		        	var obj = JSON.parse(data);
		            if(obj.status === 'success')
		            	$.getFileList();
		            else
		                alert('Error in deleting file');
		        },
		        error: function(jqXHR, textStatus, errorThrown)
		        {
		            console.log('ERRORS: ' + textStatus);
		        }
		    });
		});
	}

	$.getFileList = function(){
		$('#loadingDiv').show();
		$('#files').hide();

		var tbody = $('#files tbody');
		tbody.html('');

		$.ajax({
	        url: '/listFiles',
	        type: 'POST',
	        success: function(data, textStatus, jqXHR)
	        {
	            if(typeof data.error === 'undefined')
	            {
	            	$('#loadingDiv').hide();
	            	var table = $('#files');
	            	var filesObj = JSON.parse(data);

	            	for(var i = 0; i < filesObj.files.length; ++i){
	            		var f = filesObj.files[i];
	            		//var d = new Date(f.lastModified);
	            		var r = browserTableRow.replace(/#fn#/g, f.filename).replace('#fd#',f.description).replace('#sz#', f.size).replace(/#fv#/g, f.version);
	            		table.append(r);
	            	}

	            	$('#files').show();
	            	$.updateView();
	            }
	            else
	            	alert('Error in listing files');
	        },
	        error: function(jqXHR, textStatus, errorThrown)
	        {
	            console.log('ERRORS: ' + textStatus);
	        }
	    });
	}

	$.getFileList();

	$('#logoutBtn').click(function(){
		window.location = '/logout';
	});
})