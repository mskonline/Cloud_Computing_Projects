$(document).ready(function(){
	
	$.appendResult = function(obj){
		var tbody = $('#resultsTable tbody');
		tbody.html('');
		
		var thead = $('#resultsTable thead');
		thead.html('');
		
		$('#loadingDiv').hide();
		var msgDiv = $('#rmessage');
		
		if(obj.status === 'error'){
			msgDiv.html('<span style="color:red">' + obj.message + '</span>');
			return;
		}
		
		if(obj.data.length == 0){
			msgDiv.html('Total rows fetched : 0');
			return;
		}
		
		var keys = [];
	    for(var key in obj.data[0]){
	    	keys.push(key);
	    }
		
	    var str = '<tr>';
	    for(var i = 0; i < keys.length; ++i){
	    	str = str + '<td>' + keys[i] + '</td>';
	    }
	    str = str + '</tr>';
	    
	    thead.append(str);
	    
	    
	    for(var j = 0; j < obj.data.length; ++j) {
	    	str = '<tr>';
		    for(var i = 0; i < keys.length; ++i){
		    	str = str + '<td>' + obj.data[j][keys[i]] + '</td>';
		    }
		    str = str + '</tr>';
		    tbody.append(str);
	    }
	    
	    $('#tableDiv').show();
	    msgDiv.html('Total rows fetched : <b>' + obj.data.length + '</b> in <b>' + obj.timeInmsecs + '</b> msecs');
	};
	
	$.fetchResults = function(){
		var queryStr = $('#queryText').val();
		
		if(queryStr === ''){
			$.showMessage('Enter a query.');
			return;
		}
			
		$('#tableDiv').hide();
		$('#rmessage').html('');
		$('#loadingDiv').show();
		
		$.ajax({
	        url: '/jsonResult',
	        type: 'POST',
	        data : {query : queryStr},
	        success: function(data, textStatus, jqXHR)
	        {
	        	var obj = JSON.parse(data);
	        	$.appendResult(obj);
	        },
	        error: function(jqXHR, textStatus, errorThrown)
	        {
	            console.log('ERRORS: ' + textStatus);
	        }
	    });
	}
	
	$.showMessage = function(msg){
		$('<div></div>').dialog({
			modal: true,
			title: "Error",
			open: function() {
			  var markup = '<br>' + msg;
			  $(this).html(markup);
			},
			buttons: {
			  Close: function() {
				$(this).dialog("close");
			  }
			}
       });
	};
	
	$('#executeBtn').click(function(){
		$.fetchResults();
	})
	
	$('#clearBtn').click(function(){
		$('#queryText').val('');
		var tbody = $('#resultsTable tbody');
		tbody.html('');
		
		var thead = $('#resultsTable thead');
		thead.html('');
		
		$('#rmessage').html('');
	});
	
	$('#queryText').on('keypress', function (event) {
		 if(event.which === 13){
			 $.fetchResults();
		 }
	});
});