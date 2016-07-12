$(document).ready(function(){

	$.user = JSON.parse(user.replace(/&#39;/g,'"'))
	$('#loggerinUser').html($.user.userName);
	$('#userGrp').html($.user.group);


	var tableRowWithDelete = '<tr  class="spaceUnder"><td class="nsubject">#ns#</td>' +
		'<td class="ntype">#nt#</td>' +
		'<td class="npriority">#np#</td>' +
		'<td class="nsize">#ns# bytes</td>' +
		'<td class="nuptime">#nupt#</td>' +
		'<td> <div class="deleteButton" rId="#rid#" dId="#did#">Delete</div> </td>' +
		'<td style="width: 85px"> <div class="viewButton" ctype="#ctp#" dId="#did#">View</div> </td></tr>';

	$.updateView = function(){
		$(".viewButton").click(function(){
			$.did = $(this).attr('dId');
			$.ctype = $(this).attr('ctype');

			var subject = $(this).parent().siblings('td.nsubject')[0].innerHTML;

			$('<div></div>').dialog({
				modal: true,
				width:752,
				height:640,
				title: subject,
				open: function() {
				  $(this).html('<div id="noteViewer"></div>');
				  $("#noteViewer").load("getNoteViewer",{did : $.did, ctype: $.ctype},function() {
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
			var rid = $(this).attr('rId');
			var dataid = $(this).attr('dId');

			$.ajax({
		        url: '/deleteNote',
		        data: {rid : rid, dataid : dataid},
		        type: 'GET',
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
	};

	$('#searchButton').click(function(){
		$.getFileList();
	});

	$('#sortButton').click(function(){
		$.getFileList();
	});

	$('#uploadImageButton').click(function(){
		$('<div></div>').dialog({
			modal: true,
			width:450,
			height:500,
			title: "Upload an Image",
			open: function() {
			  $(this).html('<div id="uploadImageForm"></div>');
			  $("#uploadImageForm").load("uploadImageform" ,function() {
				  $.updateFormHandles();
			  });
			},
			buttons: {
			  Cancel:function(){
				  $(this).dialog('destroy').remove()
			  },
			  Upload: function() {
				$('#imageUploadForm').submit();
			  }
			},
			close: function(){
				$(this).dialog('destroy').remove()
			}
       });
	});

	$('#uploadNoteButton').click(function(){
		$('<div></div>').dialog({
			modal: true,
			width:450,
			height:435,
			title: "Upload a Note",
			open: function() {
			  $(this).html('<div id="uploadNoteForm"></div>');
			  $("#uploadNoteForm").load("uploadNoteform" ,function() {
				  $.updateFormHandles();
			  });
			},
			buttons: {
			  Cancel:function(){
				  $(this).dialog('destroy').remove()
			  },
			  Upload: function() {
				$('#noteUploadForm').submit();
			  }
			},
			close: function(){
				$(this).dialog('destroy').remove()
			}
       });
	});

	$.getFileList = function(){
		$('#loadingDiv').show();
		$('#files').hide();
		$('#noImageDiv').hide();

		subject = $('#subjectText').val();
		orderBy = $('#sortOpts').val();
		order = $('#orderOpts').val();

		var tbody = $('#files tbody');
		tbody.html('');

		$.ajax({
	        url: '/listFiles',
	        data : {subject: subject, orderBy : orderBy, order: order},
	        type: 'POST',
	        success: function(data, textStatus, jqXHR)
	        {
	            if(typeof data.error === 'undefined')
	            {
	            	$('#loadingDiv').hide();
	            	var table = $('#files');
	            	var notes = JSON.parse(data);
	            	var row, type, img;

	            	for(var i = 0; i < notes.length; ++i){
	            		note = notes[i];

	            		if(note.contenttype == 'txt')
	            			type = 'Text';
	            		else
	            			type = 'Image';

	            		row = tableRowWithDelete.replace('#ns#', note.subject).replace('#nt#',type).replace('#np#', note.priority).replace(/#rid#/g, note._rid)
	            		.replace('#nupt#',note.uploadtime).replace('#ns#', note.size)
	            		.replace(/#did#/g, note.dataid).replace('#ctp#', note.contenttype);
	            		table.append(row);
	            	}

	            	if(notes.length > 0) {
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

	$.getFileList();

	$.updateFormHandles = function(){
		$('#imageUploadForm').on('submit', function(){
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