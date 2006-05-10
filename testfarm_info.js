// Script Source: CodeLifter.com
// Copyright 2003
// Do not remove this header
// Modified by TestFarm team

isIE=document.all;
isNN=!document.all&&document.getElementById;
isN4=document.layers;
isHot=false;
isShown=false;
header_info = "<table style=\"width: 100%; border:solid 1px; background-color: #eee;\">\n"
		+"<tr>\n"
		+"<td>\n"
footer_info = "</td>\n"
		+"</tr>\n"
		"</table>\n";

function ddInit(e){
	myLayer=isIE ? document.all.theLayer : document.getElementById("theLayer");
	layerLeft=isIE ? event.clientX : e.clientX;
	layerTop=isIE ? event.clientY : e.clientY;
	layerLeft += document.body.scrollLeft;
	layerTop += document.body.scrollTop;
	if(!inLayerArea(layerLeft, layerTop))
		hideMe();
}

function setPosition(){
	myLayer.style.left = layerLeft;
	myLayer.left = layerLeft;
	myLayer.style.top = layerTop - 30;	
	myLayer.top = layerTop - 30;
}

function inLayerArea(layerLeft, layerTop){
	if(!layerLeft || !layerTop)
		return false;
	if(layerLeft >= myLayer.left && layerLeft <= (myLayer.left + myLayer.offsetWidth)){ //betwee min and max width of the layer 
		if(layerTop >= myLayer.top && layerTop <= (myLayer.top + myLayer.offsetHeight)){
			return true;
		}
	}
	return false;
}


function ddN4(whatDog){
	if (!isN4) return;
	N4=eval(whatDog);
	N4.captureEvents(Event.MOUSEDOWN|Event.MOUSEUP);
	N4.onmousedown=function(e){
		N4.captureEvents(Event.MOUSEMOVE);
		N4x=e.x;
		N4y=e.y;
	}
	N4.onmousemove=function(e){
		if (isHot){
			N4.moveBy(e.x-N4x,e.y-N4y);
			return false;
		}
	}
	N4.onmouseup=function(){
		N4.releaseEvents(Event.MOUSEMOVE);
	}
}

function hideMe(){
	if (isIE||isNN) myLayer.style.visibility="hidden";
	else if (isN4) document.theLayer.visibility="hide";
	isShown=false;
}

function showMe(){
	if (isIE||isNN) myLayer.style.visibility="visible";
	else if (isN4) document.theLayer.visibility="show";
	isShown=true;
}


function get_info(info){
	var log_info =  header_info
		+"<p width=\"100%\" bgcolor=\"#FFFFFF\" style=\"padding:0px\"><a href = \"index2.html\">" +info+"</a></p>\n"
		+footer_info;
	if(!isShown) {
    		setPosition();
		showMe();
		myLayer.innerHTML = log_info;
	} 
	else {
		hideMe(); 
	}		
}

function details_info(theStatus, theLink){
	var log_info = header_info
		+"<p width=\"100%\" bgcolor=\"#FFFFFF\" style=\"padding:0px\">Status: "+theStatus+"</p>\n"
		+"<p width=\"100%\" bgcolor=\"#FFFFFF\" style=\"padding:0px\"><a href = \""+theLink+"\">View Log</a></p>\n"
		+footer_info;
	if(!isShown) {
    		setPosition();
		showMe();
		myLayer.innerHTML = log_info;
	} 
	else {
		hideMe(); 
	}
}