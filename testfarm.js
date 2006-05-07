function togglesize(id)
{
  var textCutoff = 150;
  
  // don't touch below line
  //var innerHideSpanPostfix1 = "____hide1";
  var innerHideSpanPostfix2 = "____hide2";
  //var innerMoreSpanPostfix1 = "____more1";
  var innerMoreSpanPostfix2 = "____more2";
  
//  var hideElement1 = document.getElementById(id + innerHideSpanPostfix1);
  var hideElement2 = document.getElementById(id + innerHideSpanPostfix2);
//  var moreElement1 = document.getElementById(id + innerMoreSpanPostfix1);
  var moreElement2 = document.getElementById(id + innerMoreSpanPostfix2);
  
  if (/*hideElement1 &&*/ hideElement2 && /*moreElement1 &&*/ moreElement2)
  {
    if (hideElement2.style.display == 'none')
    {
      //hideElement1.style.display = '';
      hideElement2.style.display = '';
      //moreElement1.style.display = 'none';
      moreElement2.style.display = 'none';
    }
    else
    {
    //  hideElement1.style.display = 'none';
      hideElement2.style.display = 'none';
    //  moreElement1.style.display = '';
      moreElement2.style.display = '';
    }
  }
  else
  {
    var element = document.getElementById(id);
    
    if (element)
    {
      var html = element.innerHTML;
      
      var stringLength = html.length;
      
      //var hideID1 = id + innerHideSpanPostfix1;
      var hideID2 = id + innerHideSpanPostfix2;
     // var moreID1 = id + innerMoreSpanPostfix1;
      var moreID2 = id + innerMoreSpanPostfix2;
      
      var moreLink = "<span style=\"color:#9370DB; font-weight:bold\">[<a href=\"javascript:void(0)\" onclick=\"togglesize('" + id + "')\">display more...</a>]</span>";
      var lessLink = "<span style=\"color:#9370DB; font-weight:bold\">[<a href=\"javascript:void(0)\" onclick=\"togglesize('" + id + "')\">display less...</a>]</span>";
      
      if (stringLength > textCutoff)
      {
        var newHtml =
        
       // "<span id=\"" + moreID1 + "\">" + moreLink + "</span>" +
        //"<span style=\"display:none\" id=\"" + hideID1 + "\">" + lessLink +  "</span><br/><br/>" +
        
        html.substring(0,textCutoff) +
        
        "<br/><span style=\"color:#9370DB; font-weight:bold\" id=\"" + moreID2 + "\">"+ moreLink +"</span>" +
        
        "<span style=\"display:none\" id=\"" + hideID2 + "\">" +
          html.substring(textCutoff,stringLength) + "<br/><br/>" + lessLink +
        "</span>"
        ;
        
        document.getElementById(id).innerHTML = newHtml;
      }
    }
  }
}
