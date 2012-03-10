function togglesize(id)
{
	function subItemsOfClass(node, className)
	{
		// Native support?
		if (node.getElementsByClassName)
			return node.getElementsByClassName(className);
		var children = node.getElementsByTagName("*");
		var result = []
		for (var i=0; i<children.lenght; i++)
			if (children[i].className == className)
				result.append(children[i]);
		return result;
	}
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

		var moreLink = "<div class='more' id='"+moreId+"' style='display:none;'>" +
			"[<a href='javascript:void(0)' onclick=\"togglesize('" + id + "')\">display more</a>]"+
			"</div>";
		var lessLink = "<div class='more' id='"+hideId+"'>"+
			"[<a href='javascript:void(0)' onclick=\"togglesize('" + id + "')\">display less</a>]"+
			"</div>";
		var newHtml = html + moreLink + lessLink;
			;
		document.getElementById(id).innerHTML = newHtml;
		return togglesize(id);
	}
	content = subItemsOfClass(element, 'plain_text') [0];
	if (showElem.style['display'] == 'none')
	{
		hideElem.style.display = 'none';
		showElem.style.display = '';
		content.style.height = "8em";
		content.style.overflowY = 'hidden';
	}
	else
	{
		hideElem.style.display = '';
		showElem.style.display = 'none';
		content.style.height = "auto";
		content.style.overflowY = 'auto';
	}
}
