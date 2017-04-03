$(document).ready(function(){
	
	$.getRandomColor = function() {
	    var letters = '0123456789ABCDEF'.split('');
	    var color = '#';
	    for (var i = 0; i < 6; i++ ) {
	        color += letters[Math.floor(Math.random() * 16)];
	    }
	    return color;
	};
	
	$.doPlot = function(jsData){
		numClusters = jsData.numClusters;
		var scatterSeries = [];
		
		/*
		for(var i = 0; i < numClusters; ++i){
			var obj = {};
			
			obj.name = 'Cluster ' + (i + 1);
			obj.color = $.getRandomColor();
			obj.data = jsData['cluster_' + i];
			
			scatterSeries.push(obj);
		}*/
		
		
		var obj = {};
		obj.name = 'Centroids';
		obj.color = $.getRandomColor();
		obj.data = jsData['centroids'];
		
		scatterSeries.push(obj);
			
		/* Scatter chart */
		$('#scatterChartContainer').highcharts({
	        chart: {
	            type: 'scatter',
	            zoomType: 'xy'
	        },
	        title:{
	        	text: jsData.chartTitle
	        },
	        xAxis: {
	            title: {
	                enabled: true,
	                text: jsData.xaxis_label
	            },
	            startOnTick: true,
	            endOnTick: true,
	            showLastLabel: true
	        },
	        yAxis: {
	            title: {
	                text: jsData.yaxis_label
	            }
	        },
	        legend: {
	            layout: 'vertical',
	            align: 'left',
	            verticalAlign: 'top',
	            x: 100,
	            y: 70,
	            floating: true,
	            backgroundColor: (Highcharts.theme && Highcharts.theme.legendBackgroundColor) || '#FFFFFF',
	            borderWidth: 1
	        },
	        plotOptions: {
	            scatter: {
	                marker: {
	                    radius: 5,
	                    states: {
	                        hover: {
	                            enabled: true,
	                            lineColor: 'rgb(100,100,100)'
	                        }
	                    }
	                },
	                states: {
	                    hover: {
	                        marker: {
	                            enabled: false
	                        }
	                    }
	                },
	                tooltip: {
	                    headerFormat: '<b>{series.name}</b><br>'
	                    //pointFormat: '{point.x} person, {point.y} age'
	                }
	            }
	        },
	        series: scatterSeries
	    });
		
		var barSeries = [];
		var categoriesName = [];
		var obj = {};
		obj.name = 'Cluster points';
		
		var pointsData = [];
		var sortedPointsData = [];
		
		for(var i = 0; i < numClusters; ++i){
			pointsData.push(jsData['cluster_' + i].length);
			sortedPointsData.push(jsData['cluster_' + i].length);
		}
		
		sortedPointsData.sort(function(a,b){return a - b});
		
		var valarray = [];
		for(var i = 0; i < sortedPointsData.length; ++i){
			valarray.push(sortedPointsData[i])
			categoriesName.push('Cluster ' + (pointsData.indexOf(sortedPointsData[i]) + 1));
		}
		
		obj.data = valarray;
		
		barSeries.push(obj);
		
		/* Bar chart */
		$('#barChartContainer').highcharts({
	        chart: {
	            type: 'column'
	        },
	        title: {
	            text: 'Points in cluster'
	        },
	        xAxis: {
	            categories: categoriesName,
	            title: {
	                text: null
	            }
	        },
	        yAxis: {
	            min: 0,
	            title: {
	                text: 'Number of points',
	                align: 'high'
	            },
	            labels: {
	                overflow: 'justify'
	            }
	        },
	        tooltip: {
	            valueSuffix: ' counts'
	        },
	        plotOptions: {
	            bar: {
	                dataLabels: {
	                    enabled: true
	                }
	            }
	        },
	        legend: {
	            layout: 'horizontal',
	            align: 'bottom',
	            verticalAlign: 'top',
	            x: -40,
	            y: 80,
	            floating: true,
	            borderWidth: 1,
	            backgroundColor: ((Highcharts.theme && Highcharts.theme.legendBackgroundColor) || '#FFFFFF'),
	            shadow: true
	        },
	        credits: {
	            enabled: false
	        },
	        series: barSeries
	    });
		
		var bubbleSeries = [];
		var seriesdata = {};
		seriesdata.data = [];
		
		for(var i = 0; i < numClusters; ++i){
			var obj = {};
			
			obj.name = 'Cluster ' + (i + 1);
			obj.x = jsData["centroids"][i][0];
			obj.y = jsData["centroids"][i][1];
			obj.z = jsData["maxdist_" + i];
			
			seriesdata.data.push(obj);
		};
		
		bubbleSeries.push(seriesdata);
		
		$('#bubbleChartContainer').highcharts({

	        chart: {
	            type: 'bubble',
	            plotBorderWidth: 1,
	            zoomType: 'xy'
	        },

	        legend: {
	            enabled: false
	        },

	        title: {
	            text: 'Bubble chart'
	        },

	        subtitle: {
	            text: ''
	        },

	        xAxis: {
	            gridLineWidth: 1,
	            title: {
	                text: ''
	            },
	            labels: {
	                format: ''
	            },
	            plotLines: [{
	                color: 'black',
	                dashStyle: 'dot',
	                width: 2,
	                value: 65,
	                label: {
	                    rotation: 0,
	                    y: 15,
	                    style: {
	                        fontStyle: 'italic'
	                    },
	                    text: ''
	                },
	                zIndex: 3
	            }]
	        },

	        yAxis: {
	            startOnTick: false,
	            endOnTick: false,
	            title: {
	                text: ''
	            },
	            labels: {
	                format: 'r'
	            },
	            maxPadding: 0.2,
	            plotLines: [{
	                color: 'black',
	                dashStyle: 'dot',
	                width: 2,
	                value: 50,
	                label: {
	                    align: 'right',
	                    style: {
	                        fontStyle: 'italic'
	                    },
	                    text: '',
	                    x: -10
	                },
	                zIndex: 3
	            }]
	        },


	        plotOptions: {
	            series: {
	                dataLabels: {
	                    enabled: true,
	                    format: '{point.name}'
	                }
	            }
	        },

	        series: bubbleSeries
	    });
	};
	
	
	
	$.ajax({
        url: url,
        type: rmethod,
        data: cdata,
        success: function(data, textStatus, jqXHR)
        {
        	var jsData = JSON.parse(data.replace(/&#34;/g,'"'));
        	$.doPlot(jsData);
        },
        error: function(jqXHR, textStatus, errorThrown)
        {
            console.log('ERRORS: ' + textStatus);
        }
    });
});