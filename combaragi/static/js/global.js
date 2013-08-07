function MoveTo(url) {
  window.location.href=url;
}

// 현재 포지션을 새 창으로 받아와서 id에 넣어준다.
function getPosition(id) {
	var style ="dialogWidth:600px;dialogHeight:440px";
    retVal = window.showModalDialog("/map/position/",window,style);
	$('#'+id)[0].value = retVal.x+','+retVal.y;
	// 여기서 값이 바뀌므로, 위치 확인 및 기타 정보의 값을 추가로 해준다.
	if($("#pos_del_btn"))
		$("#pos_del_btn").show();
}

// 현재 위치를 새 창으로 표시해 준다.
function showPosition(id) {
	if ($('#'+id)[0] && $('#'+id)[0].value) {
		var style ="dialogWidth:600px;dialogHeight:440px";
		window.showModalDialog("/map/show/"+$('#'+id)[0].value+"/",window,style);
	}
	else {
		alert("위치가 지정되지 않았습니다.");
	}
}

function openWindow(URL, name, width, height) {
	window.open( URL, name, 'width='+width+',height='+height+',toolbar=0,menubar=0,status=0,location=0,directories=0,resizable=1,scrollbars=0' )
}

// 위치를 삭제한다.
function deletePosition(id) {
	if ($('#'+id)[0] && $('#'+id)[0].value) {
		 $('#'+id)[0].value = '';
		if($("#pos_del_btn"))
			$("#pos_del_btn").hide();
	}
}

// 해당 division을 인쇄한다.
function printMap() {
	window.open('/map/print/')
}

var preventReload; 
// 의도되지 않은 새로고침을 방지하여 줍니다.
function preventReloading(){ 
	preventReload = false;
	$('input').keyup(function(event) {
		if ($(this).val()) {
			preventReload = true;
		}
		else {
			preventReload = false;
		}
	});
	$('textarea').keyup(function(event) {
		if ($(this).val()) {
			preventReload = true;
		}
		else {
			preventReload = false;
		}
	});
	$('form').submit(function() { preventReload=false; });

	window.onbeforeunload = function (evt) {
		if(preventReload) {
			var message = '작업이 저장되지 않았습니다. 페이지를 나가시겠습니까?';
			if (typeof evt == 'undefined') {//IE
				evt = window.event;
			}
			if (evt) {
				evt.returnValue = message;
			}
			return message;
		}
	}
} 

// ajax 로 url로 보낸 뒤에 confirm 을 실행하고 결과를 ticket으로 replace한다.
function ajaxReplace(id, url, tval) {
	$('#'+id).click(function() {
		$.ajax({
			type: "GET",
			url: url+"?tval="+ tval,
			dataType: "script",
			success: function(data){
				$( "#"+id ).replaceWith($("<span class='ticket open'>"+data+"</span>"));
			}
		});
		return false;
	});
}

function confirmDefault(id, msg) {
	$('#'+id).confirm({
		msg:msg+'  ',
		timeout:3000,
		dialogShow:'fadeIn',
		dialogSpeed:'slow',
		buttons: {
			wrapper:'<button type="button" class="btn"></button>',
			//ok:'<span><img src="/static/images/board/yes.png"></span>',
			//cancel:'<span><img src="/static/images/board/no.png"></span>',
			ok:'<span>네</span>',
			cancel:'<span>아니오</span>',
			separator:'  '
		}
	});
}
// ajax 로 url로 보낸 뒤에 confirm 을 실행하고 결과를 ticket으로 replace한다.
function ajaxConfirmReplace(id, url, msg, tval) {
	ajaxReplace(id, url, tval);
	confirmDefault(id, msg);
}

function confirmGo(id, msg, url) {
	$('#'+id).click(function() {
		window.location.replace(url);
		return false;
	});
	confirmDefault(id, msg);
}

function confirmExecute(id, msg, successFunc) {
	$('#'+id).click(successFunc);
	confirmDefault(id, msg);
}

$(document).ajaxSend(function(event, xhr, settings) {
  function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
      var cookies = document.cookie.split(';');
      for (var i = 0; i < cookies.length; i++) {
        var cookie = jQuery.trim(cookies[i]);
        // Does this cookie string begin with the name we want?
        if (cookie.substring(0, name.length + 1) == (name + '=')) {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }
  function sameOrigin(url) {
    // url could be relative or scheme relative or absolute
    var host = document.location.host; // host + port
    var protocol = document.location.protocol;
    var sr_origin = '//' + host;
    var origin = protocol + sr_origin;
    // Allow absolute or scheme relative URLs to same origin
    return (url == origin || url.slice(0, origin.length + 1) == origin + '/') ||
      (url == sr_origin || url.slice(0, sr_origin.length + 1) == sr_origin + '/') ||
      // or any other URL that isn't scheme relative or absolute i.e relative.
      !(/^(\/\/|http:|https:).*/.test(url));
  }
  function safeMethod(method) {
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
  }

  if (!safeMethod(settings.type) && sameOrigin(settings.url)) {
    xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
  }
});
