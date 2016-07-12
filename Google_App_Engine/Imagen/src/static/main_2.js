$(document).ready(function(){
	$.user = JSON.parse(user.replace(/&#39;/g,'"'))
	$('#loggerinUser').html($.user.userName);
	$('#userGrp').html($.user.group);

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
	            	window.location = '/';
	            else
	                alert('Error in deleting file');
	        },
	        error: function(jqXHR, textStatus, errorThrown)
	        {
	            console.log('ERRORS: ' + textStatus);
	        }
	    });
	});

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
		$('.removeComment').unbind('click', $.removeComment);
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
		$.textArea = $($(this).parent().siblings('textarea'));
		$.commentText = $($(this).parent().siblings('div'));
		$.comment = $.textArea.val();

		var imgid = $(this).attr('imageId');

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
	        data: { imageId: imgid, comment : $.comment},
	        type: 'POST',
	        success: function(data, textStatus, jqXHR)
	        {
	        	var obj = JSON.parse(data);
	            if(obj.status === 'success'){
	            	$.textArea.val('');

	            	var cdiv = '<div class="commentBox"><div class="commentUser">' + $.user.userName +
	            	'<div style="float:right;margin-right: 5px;"><input class="removeComment" type="button" cid="'  +
	            	obj.cid + '" value="Delete"/></div>' +
	            	'</div><div class="commentData"> ' + obj.comment +'</div></div>';

	            	$.commentText.append(cdiv);
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
	};

	$.commentHandles();
	$('.addCommentButton').bind('click',$.addComment);
});