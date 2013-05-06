/*
To use this include these lines in your html head:

<script language="javascript" type="text/javascript" src="jquery.js"></script>
<script type="text/javascript" src="https://www.google.com/jsapi"></script>
<script type="text/javascript" src="plot.js"></script>

And you can start using:
<div class='plot' src="mydatafile" />

where mydatafile is a file containing a javascript array.

*/

google.load("visualization", "1", {packages:["corechart"]});
google.setOnLoadCallback(renderPlots);
function renderPlots()
{
	$('.plot').each(function(i,obj)
	{
		var options = {
			"vAxis.textPosition" : "none",
			"hAxis.textPosition" : "none",
			"legend.position" : "none",
			"backgroundColor" : "#fbfbfa",
		};
		var src = $(obj).attr("src");
		var jsonData = $.ajax({
			url: src,
			dataType: "json",
			async: false
		}).responseText;

		var arrayData = eval(jsonData);

		// Create our data table out of JSON data loaded from server.
		var data = google.visualization.arrayToDataTable(arrayData);
		var chart = new google.visualization.LineChart(obj);
		chart.draw(data, options);
	})
}


