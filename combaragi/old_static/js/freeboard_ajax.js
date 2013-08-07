;(function($) {
	// Globally keep track of all images by their unique hash.  Each item is an image data object.
  var page = 0;
  var more_clicked = false;
  var INIT_INTERVAL_COUNT = 5;
  var first_interval_count = INIT_INTERVAL_COUNT;
  var INIT_INTERVAL = 5000;
  var interval = INIT_INTERVAL;
  var SCROLL_PADDING = 600;

	var defaults = {
    more_button: "#get_more_feed",
    board_slug: ""
	};

  var ajax_board = this;
	$.ajax_board = function(settings) {
		$.extend(this, {
      IntervalInitialize: function() {
        first_interval_count = INIT_INTERVAL_COUNT;
        interval = INIT_INTERVAL;
      },
      moreEveryComments: function() {
        if (first_interval_count) {
          first_interval_count--;
        } else {
          interval = interval * 2;
        }
        $('.comment_input').each(function() {
          splited = $(this).attr("id").split("_");
          bulletin_id = splited[1];
          last_comment_id = splited[2];
          ajax_board.$.moreRecentComments(bulletin_id, last_comment_id);
        });
        setTimeout(ajax_board.$.moreEveryComments, interval);
      },
      moreContent: function(id) {
        $("#inbox_content_"+id).removeAttr("style");
        $("#more_"+id).hide();
        $.ajax({
          type: "GET",
          url: "/feed/more/content/"+id,
          dataType: "html",
          success: function(data){
            $("#inbox_content_"+id).html(data);
            $('#inbox_content_'+id+' a[rel*=lightbox]').lightBox({containerResizeSpeed: 0});
            $("#inbox_content_"+id+" *[rel=tooltip]").tipsy ({ gravity: 's', html: true });
          }
        });
        ajax_board.$.IntervalInitialize();
      },
      moreComments: function(id, cnt) {
        $("#more_comments_"+id).html('<img src="/static/images/loading.gif">');
        $.ajax({
          type: "GET",
          url: "/feed/more/comments/"+id+"/"+cnt+"/",
          dataType: "html",
          success: function(data){
            $("#more_comments_"+id).remove();
            $("#inbox_comments_"+id).prepend(data);
            $("#inbox_comments_"+id+" *[rel=tooltip]").tipsy ({ gravity: 's', html: true });
            /* for X button to delete comment */
            $("#inbox_comments_"+id+" .comment_delete_x:visible").hide();
            $("#inbox_table #inbox_body #inbox_comments_"+id+" .inbox_content").mouseover(function() {
              $(this).find('.comment_delete_x:hidden').show();
            })
            .mouseout(function(){
              $(this).find('.comment_delete_x:visible').hide();
            });
            /* //for X button to delete comment */
          }
        });
        ajax_board.$.IntervalInitialize();
      },
      moreRecentComments: function(bulletin_id, last_comment_id) {
        $.ajax({
          type: "GET",
          url: "/feed/more/recent_comments/"+bulletin_id+"/"+last_comment_id+"/",
          dataType: "html",
          success: function(data){
            $("#inbox_comments_"+bulletin_id).append(data);
            if ($("#inbox_comments_"+bulletin_id+" .inbox_content:visible").size()) {
              new_last_comment_id =
                $(
                  $("#inbox_comments_"+bulletin_id+" .inbox_content:visible")[
                    $("#inbox_comments_"+bulletin_id+" .inbox_content:visible").size()-1]
                 ).attr('id').split('_')[1];
              $("#comment-input_"+bulletin_id+"_"+last_comment_id).show();
              $("#comment-input_"+bulletin_id+"_"+last_comment_id).siblings("img").remove(); // remove loading img
              $("#comment-input_"+bulletin_id+"_"+last_comment_id).attr("id", "comment-input_"+bulletin_id+"_"+new_last_comment_id);
              /* for X button to delete comment */
              $("#inbox_comments_"+bulletin_id+" .comment_delete_x:visible").hide();
              $("#inbox_table #inbox_body #inbox_comments_"+bulletin_id+" .inbox_content").mouseover(function() {
                $(this).find('.comment_delete_x:hidden').show();
              })
              .mouseout(function(){
                $(this).find('.comment_delete_x:visible').hide();
              });
              /* //for X button to delete comment */
              $("#inbox_comments_"+bulletin_id+" *[rel=tooltip]").tipsy ({ gravity: 's', html: true });
            }
          }
        });
      },
      delete_comment: function(bulletin_id, comment_id) {
        $.ajax({
          type: "GET",
          url: "/board/comment/"+comment_id+"/ajax_delete/",
          dataType: "html",
          success: function(data){
            if (data == '성공') {
              $('#inbox-comment_'+comment_id+':visible').remove();
              new_last_comment_id = $($("#inbox_comments_"+bulletin_id+" .inbox_content:visible")[$("#inbox_comments_"+bulletin_id+" .inbox_content:visible").size()-1]).attr('id').split('_')[1];
              $("#inbox_comments_"+bulletin_id).parent().find("input").attr("id", "comment-input_"+bulletin_id+"_"+new_last_comment_id);
            }
            else {
              alert('댓글 삭제에 실패했습니다.\n조금 뒤에 다시 시도해 주세요.');
            }
          }
        });
        ajax_board.$.IntervalInitialize();
      },
      setGetMoreFeed:function() {
        $("#get_more_feed").unbind("click");
        $('#get_more_feed').click(function() {
          if (more_clicked) return false;
          more_clicked = true;
          var feed_url;
          if (ajax_board.$.board_slug) {
            feed_url = "/feed/more/" + ajax_board.$.board_slug + "/" + page;
          } else {
            feed_url = "/feed/more/"+page;
          }
          $('#get_more_feed').html('Loading...');
          $.ajax({
            type: "GET",
            url: feed_url,
            dataType: "html",
            timeout:5000,
            success: function(data) {
              if (data) {
                $("#inbox_table #inbox_body").append(data);
                $("#inbox_table #inbox_body .comment_input").focus(function() {
                  if ($(this).val() == "댓글을 입력하세요...") {
                    $(this).parent().parent().find(".comment_picture").show();
                    $(this).val("")
                    .removeClass("comment_help");
                    $(this).parent()
                    .removeClass("comment_box_full")
                    .addClass("comment_box_no_full");
                  }
                  ajax_board.$.IntervalInitialize();
                }).blur(function() {
                  if (!$(this).val()) {
                    $(this).val("댓글을 입력하세요...")
                    .addClass("comment_help");
                    $(this).parent()
                    .removeClass("comment_box_no_full")
                    .addClass("comment_box_full");
                    $(this).parent().parent().find(".comment_picture").hide();
                  }
                  ajax_board.$.IntervalInitialize();
                }).keydown(function(event) {
                  if (event.keyCode == '13') {
                    // 엔터쳤음.
                    // 여기서 ajax메시지를 보내주고 만약 성공하면 현재 댓글 수를 넣어서 보내준다.
                    // 일단 댓글다는 폼 자체를 없애고 그곳에 loading아이콘을 넣자.
                    if (!$(this).val()) return;
                    $(this).hide();
                    $(this).parent().append($('<img src="/static/images/loading.gif">'));
                    splited = $(this).attr("id").split("_");
                    bulletin_id = splited[1];
                    last_comment_id = splited[2];
                    $.ajax({
                      type: "POST",
                      url: "/board/comment/"+bulletin_id+"/ajax_append/",
                      data: {content:$(this).val()},
                      dataType: "html",
                      timeout:5000,
                      success: function(data){
                        ajax_board.$.moreRecentComments(bulletin_id, last_comment_id);
                      },
                      error: function() {
                        alert('알수 없는 에러 100. 관리자에게 문의해 주세요.');
                        // Error!
                        // 하지만 사용자는 반응을 기다릴 것이므로...걱정 안해도 됨.
                      }
                    });
                    $(this).val("");
                  }
                });
                $("#inbox_table #inbox_body .who *[rel=tooltip]").tipsy ({ gravity: 's', html: true });
                $('#get_more_feed').html('다음 글 보기');
                $(".comment_delete_x:visible").hide();
                $("#inbox_table #inbox_body .inbox_content").mouseover(function() {
                  $(this).find('.comment_delete_x:hidden').show();
                })
                .mouseout(function(){
                  $(this).find('.comment_delete_x:visible').hide();
                });
                page++;
              }
              else {
                $("#get_more_feed").html("더 이상 글이 없습니다.")
                  .unbind("click");
              }
              more_clicked = false;
            },
            error: function() {
              $('#get_more_feed').html('연결 상태가 좋지 않습니다. 다음 글 보기');
            }
          });
          return false;
        });
      }
    });
    $.extend(this, defaults, settings);
    // Setup Keyboard Navigation
    $(document).keydown(function(e) {
      var key = e.charCode ? e.charCode : e.keyCode ? e.keyCode : 0;
      switch(key) {
        case 34: // Page Down
          $(ajax_board.$.more_button).click();
          break;
      }
    });
    //setTimeout(ajax_board.$.moreEveryComments, interval);
    // 머시기 머시기
    this.setGetMoreFeed();
    this.IntervalInitialize();
    $(this.more_button).click();
    var more_button = this.more_button;
    $(window).scroll(function(){
      if ($(window).scrollTop() >= $(document).height() - $(window).height() - SCROLL_PADDING){
        $(more_button).click();
      }
    });
    return this;
  };
})(jQuery);
