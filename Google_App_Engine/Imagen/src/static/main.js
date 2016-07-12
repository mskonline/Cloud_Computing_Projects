$(document).ready(function(){

	$.user = JSON.parse(user.replace(/&#39;/g,'"'))
	$('#loggerinUser').html($.user.userName);
	$('#userGrp').html($.user.group);


	var tableRowWithDelete = '<tr  class="spaceUnder"><td class="file">#in#</td>' +
		'<td class="iformat">#if#</td>' +
		'<td class="isize">#iz# bytes</td>' +
		'<td class="igroup">#ig#</td>' +
		'<td class="iuptime">#ipt#</td>' +
		'<td><div class="deleteButton" imgId="#imd#">Delete</div></td><td style="width: 85px"><div class="viewButton" imgId="#imd#">View</div></td></tr>';

	var tableRow = '<tr class="spaceUnder"><td class="file">#in#</td>' +
	'<td class="iformat">#if#</td>' +
	'<td class="isize">#iz# bytes</td>' +
	'<td class="igroup">#ig#</td>' +
	'<td class="iuptime" colspan ="2">#ipt#</td>' +
	'<td style="width: 85px"><div class="viewButton" imgId="#imd#">View</div></td></tr>';

	$.updateView = function(){
		$(".viewButton").click(function(){
			$.imgid = $(this).attr('imgid');

			$('<div></div>').dialog({
				modal: true,
				width:1220,
				height:640,
				title: "Image Viewer",
				open: function() {
				  $(this).html('<div id="imageViewer"></div>');
				  $("#imageViewer").load("getImageViewer",{imageId : $.imgid},function() {
					  $.commentHandles();
				  });
				},
				buttons: {
				  Close:function(){
					  $(this).dialog('destroy').remove()
				  }
				},
				close: function(){
					$(this).dialog('destroy').remove()
				}
	       });
		});

		$(".deleteButton").click(function(){
			var imgid = $(this).attr('imgid');

			$.ajax({
		        url: '/deleteImage',
		        data: {imageId : imgid},
		        type: 'POST',
		        success: function(data, textStatus, jqXHR)
		        {
		        	var obj = JSON.parse(data);
		            if(obj.status === 'success')
		            	$.getFileList('','');
		            else
		                alert('Error in deleting file');
		        },
		        error: function(jqXHR, textStatus, errorThrown)
		        {
		            console.log('ERRORS: ' + textStatus);
		        }
		    });
		});
	};

	$('#searchButton').click(function(){
		var imgName = $('#imgNameText').val();
		var grpName = $('#grpNameText').val();

		$.getFileList(imgName,grpName);
	});

	$('#uploadButton').click(function(){
		$('<div></div>').dialog({
			modal: true,
			width:450,
			height:400,
			title: "Upload an Image",
			open: function() {
			  $(this).html('<div id="uploadForm"></div>');
			  $("#uploadForm").load("uploadform" ,function() {
				  $.updateFormHandles();
			  });
			},
			buttons: {
			  Cancel:function(){
				  $(this).dialog('destroy').remove()
			  },
			  Upload: function() {
				$('#fileUploadForm').submit();
			  }
			},
			close: function(){
				$(this).dialog('destroy').remove()
			}
       });
	});

	$.getFileList = function(imgName, grpName){
		$('#loadingDiv').show();
		$('#files').hide();
		$('#noImageDiv').hide();

		var tbody = $('#files tbody');
		tbody.html('');

		$.ajax({
	        url: '/listFiles',
	        data : {imgname : imgName, grpname: grpName},
	        type: 'POST',
	        success: function(data, textStatus, jqXHR)
	        {
	            if(typeof data.error === 'undefined')
	            {
	            	$('#loadingDiv').hide();
	            	var table = $('#files');
	            	var images = JSON.parse(data);
	            	var row, template, img;

	            	for(var i = 0; i < images.length; ++i){
	            		img = images[i];

	            		if(img.userid === $.user.userId)
	            			template =  tableRowWithDelete;
	            		else
	            			template =  tableRow;

	            		row = template.replace(/#in#/g, img.name).replace('#if#',img.format).replace('#iz#', img.size).replace(/#imd#/g, img.imageid)
	            		.replace('#ig#', img.group).replace('#ipt#',img.uploadtime);
	            		table.append(row);
	            	}

	            	if(images.length > 0) {
		            	$('#files').show();
		            	$.updateView();
	            	} else {
	            		$('#noImageDiv').show();
	            	}
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

	$.getFileList('','');

	$.updateFormHandles = function(){
		$('#fileUploadForm').on('submit', function(){
			var fileInput = $('#fileInput');
			var formEvent = arguments[0];

			var comment = $('#upload_comment_textarea');

			if(comment.val().length > 100){
				alert("Comments can't be more than 100 Characters.");
				formEvent.stopPropagation();
				formEvent.preventDefault();
			}

			if(fileInput[0].files.length > 0){
				var sizeInBytes = fileInput[0].files[0].size;
				$('input[name=size]').val(sizeInBytes);

				if(sizeInBytes > 1048576 /* 1MB in bytes*/ ) {
					alert('File size needs to be less than 1MB');

					formEvent.stopPropagation();
					formEvent.preventDefault();
				}
			} else {
				alert('Select file to upload');
				formEvent.stopPropagation();
				formEvent.preventDefault();
			}
		});
	};

	$.commentHandles = function(){
		$('.addCommentButton').unbind('click',$.addComment);
		$('.removeComment').unbind('click', $.removeComment);
		$('.addCommentButton').bind('click',$.addComment);
		$('.removeComment').bind('click', $.removeComment);
	};

	$('#logoutBtn').click(function(){
		window.location = '/logout';
	});

	$('#changeGrpBtn').click(function(){
		$('<div></div>').dialog({
			modal: true,
			width:450,
			height:400,
			title: "Change your group",
			open: function() {
			  $(this).html('<div id="changeGrpDiv"></div>');
			  $("#changeGrpDiv").load("changeGrpForm" ,function() {
				  $.updateFormHandles();
			  });
			},
			buttons: {
			  Cancel:function(){
				  $(this).dialog('destroy').remove()
			  },
			  Submit: function() {
				$('#changeUserGroupForm').submit();
			  }
			},
			close: function(){
				$(this).dialog('destroy').remove()
			}
       });
	});

	$.addComment = function(){
		$.comment = $('#comment_textarea').val();
		if($.comment === '') {
			alert('Enter a comment');
			return;
		}

		if($.comment.length > 100){
			alert("Comments can't be more than 100 Characters.");
			return;
		}

		$.ajax({
	        url: '/addComment',
	        data: { imageId: $.imgid, comment : $.comment},
	        type: 'POST',
	        success: function(data, textStatus, jqXHR)
	        {
	        	var obj = JSON.parse(data);
	            if(obj.status === 'success'){
	            	$('#comment_textarea').val('');
	            	var cdiv = '<div id="commentBox"><div id="commentUser">' + $.user.userName +
	            	'<div style="float:right;margin-right: 5px;"><input class="removeComment" type="button" cid="'  +
	            	obj.cid + '" value="Delete"/></div>' +
	            	'</div><div id="commentData"> ' + obj.comment +'</div></div>';
	            	$('#commentText').append(cdiv);

	            	$.commentHandles();
	            }
	            else
	                alert('Error in deleting file');
	        },
	        error: function(jqXHR, textStatus, errorThrown)
	        {
	            console.log('ERRORS: ' + textStatus);
	        }
	    });
	};

	$.removeComment = function(){
		var commentid = $(this).attr('cid');
		$.cBox = $(this).parent().parent().parent();
		$.ajax({
	        url: '/deleteComment',
	        data: {cid : commentid},
	        type: 'POST',
	        success: function(data, textStatus, jqXHR)
	        {
	        	var obj = JSON.parse(data);
	            if(obj.status === 'success'){
	            	$.cBox.remove();
	            }
	            else
	                alert('Error in deleting file');
	        },
	        error: function(jqXHR, textStatus, errorThrown)
	        {
	            console.log('ERRORS: ' + textStatus);
	        }
	    });
	}
});