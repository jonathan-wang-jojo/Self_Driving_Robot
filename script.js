var buttons = document.querySelectorAll(".button");
var inputfield = document.getElementById("input");
console.log(buttons);
buttons.forEach((item, index)=>{
  console.log("what");
  item.addEventListener("click", (e)=>{
    console.log("what");
    var target = e.target;
    var id = target.id;
    var XHR = new XMLHttpRequest();
    var url ="http://192.168.1.28:5001/"+id +"?";
    url+= "d="+inputfield.value;
    XHR.open("GET", url, true);
    XHR.send();
  });
});
var inter = setInterval(()=>{
  var XHR = new XMLHttpRequest();
  var id = document.getElementById("terminal");
  XHR.open("GET", "http://192.168.1.28:5001/term", true);
  XHR.onload = ()=>{
      id.innerHTML = XHR.responseText;
  } 
  XHR.send()
}, 1000);
var inter = setInterval(()=>{
  
}, 1000);