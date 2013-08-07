$('#toogle_chat_enable').click(function(){
  var chat_disable = $.cookie("chat_disabled");
  if (chat_disable == '1') {
    $.cookie("chat_disabled", '0', { path: '/' });
    $('#chat_area embed').removeClass('chat_disabled');
    $('#chat_area').removeClass('chat_area_disabled');
    $('#chat_title').toggle();
    $('#toogle_chat_size').toggle();
    $('#toogle_chat_enable').html("숨기기");
  } else {
    $.cookie("chat_disabled", '1', { path: '/' });
    $('#chat_area embed').addClass('chat_disabled');
    $('#chat_area').addClass('chat_area_disabled');
    $('#chat_title').toggle();
    $('#toogle_chat_size').toggle();
    $('#toogle_chat_enable').html("보이기");
  }
});
$('#toogle_chat_size').click(function(){
  var chat_maximized = $.cookie("chat_maximized");
  if (chat_maximized == '1') {
    $.cookie("chat_maximized", '0', { path: '/' });
    $('#chat_area embed').removeClass('chat_maximized');
    $('#chat_area').removeClass('chat_area_maximized');
    $('#toogle_chat_size').html("크게");
  } else {
    $.cookie("chat_maximized", '1', { path: '/' });
    $('#chat_area embed').addClass('chat_maximized');
    $('#chat_area').addClass('chat_area_maximized');
    $('#toogle_chat_size').html("작게");
  }
});
if ($.cookie("chat_disabled") == '1') {
  $('#chat_area embed').addClass('chat_disabled');
  $('#chat_area').addClass('chat_area_disabled');
  $('#chat_title').toggle();
  $('#toogle_chat_size').toggle();
  $('#toogle_chat_enable').html("보이기");
}
if ($.cookie("chat_maximized") == '1') {
  $('#chat_area embed').addClass('chat_maximized');
  $('#chat_area').addClass('chat_area_maximized');
  $('#toogle_chat_size').html("작게");
}