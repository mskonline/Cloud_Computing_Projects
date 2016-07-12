$(document).ready(function(){

	$.loginFunc = function(){
		var username = $('#username').val();
		var password = $('#passwd').val();

		if(username == '' || password == '') {
			alert('Please enter all the details');
			return;
		}

		$.ajax({
	        url: '/login',
	        type: 'POST',
	        data: {'username':username, 'password':password},
	        success: function(data, textStatus, jqXHR)
	        {
	        	var obj = JSON.parse(data);

	        	if(obj.status === "true")
	        		window.location = "/";
	        	else
	        		alert('Invalid username or password');
	        },
	        error: function(jqXHR, textStatus, errorThrown)
	        {
	            console.log('ERRORS: ' + textStatus);
	        }
	    });
	}

	$('#passwd').on('keypress', function (event) {
		 if(event.which === 13){
		    //$(this).attr("disabled", "disabled");
		    $.loginFunc();
		 }
    });


	$('#loginBtn').click(function(){
		$.loginFunc();
	});
});