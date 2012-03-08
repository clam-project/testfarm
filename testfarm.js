function togglesize(id)
{
	var element = document.getElementById(id);
	if (!element) return; 

	// don't touch below line
	var hideId = id + "____hide";
	var moreId = id + "____more";

	var hideElem = document.getElementById(hideId);
	var showElem = document.getElementById(moreId);

	if (! hideElem || ! showElem)
	{
		var html = element.innerHTML;
		var stringLength = html.length;

		var moreLink = "<div>[<a href=\"javascript:void(0)\" onclick=\"togglesize('" + id + "')\">display more</a>]</div>";
		var lessLink = "<div>[<a href=\"javascript:void(0)\" onclick=\"togglesize('" + id + "')\">display less</a>]</div>";
		var newHtml =
			html +
			"<span class='more' style='display:none;' id='" + hideId + "'>" + lessLink + "</span>" +
			"<span class='more' id='" + moreId + "'>"+ moreLink +"</span>" +
			""
			;
		document.getElementById(id).innerHTML = newHtml;
	}
    
	if (hideElem.style.display == 'none')
	{
		hideElem.style.display = '';
		showElem.style.display = 'none';
		element.style.height = "auto";
		element.style['overflow-y'] = 'auto';
	}
	else
	{
		hideElem.style.display = 'none';
		showElem.style.display = '';
		element.style.height = "8em";
		element.style['overflow-y'] = 'hidden';
	}
}
