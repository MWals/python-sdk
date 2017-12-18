/* Copyright 2017 IBM All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

* A collection of functions to facilitate Pepper tablet interactions 
* This script file should be imbeded at the end of the <body>, after including 
* the robot's http://198.18.0.1/libs/qimessaging/2/qimessaging.js
*
* A qi object should be defined to receive the functions defined in this file
*
*/

if(!qi) {
  console.log("Define a qi object first: var qi=Object()");
}
qi.log=function(msg) {
    console.log("Qi LOG "+Date()+""+msg);
}
qi.debug=function(msg) {
    console.log("Qi DBG "+Date()+""+msg);
}

qi.robotIP="198.18.0.1";
qi.log("Starting with robotIP="+qi.robotIP);

// Locate the location where qimessaging was loaded from 
for (var sci=0;sci<document.scripts.length;sci++) {
  qi.log("scripts["+sci+"].src="+document.scripts[sci].src);
}
      
// Subscribe on a memory key
qi.subEvent=function(key,func) {
  qi.log("Subscribing to "+ key);
  return qi.mem.subscriber(key).then(function(subscriber) {
    return subscriber.signal.connect(function(value) {
      qi.log("Got Event value="+value+" for "+key);
      func(value);
    });
  });
}

qi.bindList=function(key,listId) {
  var list=document.getElementById(listId);
  qi.log("Subscribing list "+list+" to event "+key);
  qi.subEvent(key,function(value) {
    qi.log("Got Event value="+value+" of type "+(typeof value)+" for "+key);
    if(list.children) {
      for(var li=0;li<list.children.length;li++) {
        qi.log("Removing "+list.children[li]);
        list.removeChild(list.children[li]);
      }
    }
    if(value.length) {
      qi.log("Got "+value.length+" values");
      for (var cni=0;cni<value.length;cni++) {
        var li=document.createElement("LI");
        li.innerHTML=value[cni];
        list.appendChild(li);
      }
    } else {
      qi.log("No value.length");
      var li=document.createElement("LI");
      li.innerHTML=value;
      list.appendChild(li);
    }
  });
}
      
// Bind an event to an element
qi.bindElement=function(key,elem) {
    qi.log("Binding key "+key+" to element with id "+elem);
    if((typeof elem)=="string") {
      elem=document.getElementById(elem);
    }
    qi.subEvent(key,function(value) {
      qi.log("Setting "+elem+" to "+key+"="+value);
      elem.innerHTML=value;
    });
}

qi.bindHide=function(key,elem) {
  qi.log("Binding key "+key+" to element with id "+elem);
    if((typeof elem)=="string") {
      elem=document.getElementById(elem);
    }
    var notHide=(key[0]==='!');
    if(notHide) {
      key=key.substring(1);
    }
    qi.subEvent(key,function(value) {
      qi.log("Hiding "+elem+" for "+value);
      if(value==="true" || value==="1") value=true
      if(value==="false" || value==="0") value=false
      if((value && !notHide) || (!value && notHide)){
        elem.setAttribute("hidden","1");
      } else {
        elem.removeAttribute("hidden");
      }
    });
}

qi.bindElements=function() {
  // find all <b>,<i>,<p> elements
  for(var tagName of ["b","i","p","img","span","div"]) {
    all_elements=document.getElementsByTagName(tagName);
    for(var eli=0;eli<all_elements.length;eli++) {
      var this_elem=all_elements[eli];
      var qiMemKey=this_elem.getAttribute("qi-sub");
      if(qiMemKey) {
        qi.bindElement(qiMemKey,this_elem);
        this_elem.removeAttribute("qi-sub");
      }
      var qiHideKey=this_elem.getAttribute("qi-hide");
      if(qiHideKey) {
        qi.bindHide(qiHideKey,this_elem);
        this_elem.removeAttribute("qi-hide");
      }
    }
  }
}
                        
// bind mouse down event on button with input value to ALMemory Event
qi.bindInput=function(key,button,input) {
  qi.log("Binding key "+key+" to button "+button);
  if((typeof button)=="string") {
    button=document.getElementById(button);
  }
  if((typeof input)=="string") {
    input=document.getElementById(input);
  }
  
  button.onclick=function () {
    value=input.value;
    qi.log("value for "+input+"="+value+" publish on "+key);
    qi.mem.raiseEvent(key,value);
  }
}
            
// bind mouse down event on button to ALMemory Event
qi.bindButton=function(key,button,value) {
  qi.debug("Binding key "+key+" to button "+button+" of type "+(typeof button));
  if((typeof button)=="string") {
    button=document.getElementById(button);
  }
  button.onclick=function () {
    qi.debug("Onclick for "+button+" id="+button.id+" raising event "+key+"="+value);
    qi.mem.raiseEvent(key,value);
  }
}

// Bind all buttons thta have a qi-memkey and qi-memvalue attributes
qi.bindButtons=function() {
  // find all buttons
  all_buttons=document.getElementsByTagName("button");
  for(var bti=0;bti<all_buttons.length;bti++) {
    var this_button=all_buttons[bti];
    qi.debug("Button["+bti+"]="+this_button);
    var qiMemKey=this_button.getAttribute("qi-pub");
    if(qiMemKey) {
      var qiMemVal=this_button.getAttribute("qi-val");
      if(!qiMemVal) {
        var qiInput=this_button.getAttribute("qi-input");
        if(qiInput) {
          qi.bindInput(qiMemKey,this_button,qiInput);
        } else {
          qiMemVal=this_button.getAttribute("id");
        }
      }
      if(qiMemVal) {
        qi.bindButton(qiMemKey,this_button,qiMemVal);
        this_button.removeAttribute("qi-pub");
      }
    }
  }
}

qi.log("typeof(QiSession)="+(typeof QiSession));
QiSession(function(session) {
  try {
    qi.session=session;
    qi.log("Got session type="+(typeof session));
    return session.service("ALMemory").then(function (mem) {
      qi.log("Got Almemory type="+(typeof mem));
      qi.mem=mem;
      mem.raiseEvent("Watson/Init","OK");
      qi.bindButtons();
      qi.bindElements();
      qi.ready();
      return qi;
    }, function() {
        qi.log("AlMemory error");
        return qi;
    });  
  } catch(exc) {
    console.log("Exception "+exc);
  }  
}, function() {
    qi.log("QiSession Disconnected");
},
qi.robotIP);

