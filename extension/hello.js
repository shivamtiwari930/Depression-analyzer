
var __name__ = "__main__";

function display() {
    //document.getElementById("result").innerHTML = a + b;
   // window.open("http://127.0.0.1:5000/"); 
// Requiring fs module in which  
// readFile function is defined. 
     var xhr = new XMLHttpRequest();
     xhr.open('GET', chrome.extension.getURL('depressionrating'), true);
     xhr.onreadystatechange = function()
     {
          if(xhr.readyState == XMLHttpRequest.DONE && xhr.status == 200)
         {
        //... The content has been read in xhr.responseText
         document.getElementById("result").innerHTML = xhr.responseText;
         }
};
xhr.send();


}


function details() {
    //document.getElementById("result").innerHTML = a + b;
    
// Requiring fs module in which  
// readFile function is defined. 
     var xhr = new XMLHttpRequest();
     xhr.open('GET', chrome.extension.getURL('detailsdisplay'), true);
     xhr.onreadystatechange = function()
     {
          if(xhr.readyState == XMLHttpRequest.DONE && xhr.status == 200)
         {
        //... The content has been read in xhr.responseText
         document.getElementById("detailsresult").innerHTML = xhr.responseText;
        

         }
};
xhr.send();

}
document.addEventListener('DOMContentLoaded', function() {
    var link = document.getElementById('compute');
    // onClick's logic below:
    link.addEventListener('click', function() {
	display();
    });
});


document.addEventListener('DOMContentLoaded', function() {
    var link = document.getElementById('details');
    // onClick's logic below:
    link.addEventListener('click', function() {
	details();
    });
});


