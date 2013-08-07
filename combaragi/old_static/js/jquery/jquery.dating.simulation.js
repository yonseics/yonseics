;(function($) {
  var MSG_CHARACTOR_INTERVAL = 50;
  var msg_running = false;
  var msg_timer = null;
  var lefted_msg = true;
  var msg_idx = -1;
  var msg_string_idx = 0;
  var previous_guard_id = -1;

	var defaults = {
    dsdiv: '#dsdiv',
    message_set: '',
    background_img: '',
    AfterFinish: function() {}
	};

  var dslib = this;
	$.dslib = function(settings) {
		$.extend(this, {
      StartMessage: function() {
        msg_timer = setTimeout(dslib.$.RunMessage, MSG_CHARACTOR_INTERVAL);
        msg_running = true;
        msg_string_idx = 0;
      },
      StopMessage: function() {
        if (msg_running) {
          clearTimeout(msg_timer);
          msg_running = false;
        }
      },
      RunMessage: function() {
        var msg = dslib.$.GetMessage(msg_idx);
        if (msg.length == msg_string_idx) {
          dslib.$.StopMessage();
          return;
        }
        var current_char = msg.charAt(msg_string_idx++);
        dslib.$.text_area.append(current_char);
        msg_timer = setTimeout(dslib.$.RunMessage, MSG_CHARACTOR_INTERVAL);
      },
      ClearMessage: function() {
        dslib.$.text_area.text('');
      },
      OnFinish: function() {
        $('body').unbind('selectstart');
        this.AfterFinish();
      },
      NextMessage: function() {
        if (msg_idx == this.size() - 1) {
          this.OnFinish();
        }
        this.StopMessage();
        this.ClearMessage();
        msg_idx++
        if (msg_idx >= this.size()) return;
        if (previous_guard_id >= 0 && previous_guard_id != this.GetGuardId(msg_idx)) {
          lefted_msg = !lefted_msg;
        }
        this.image_field.html(this.GetImage(msg_idx));
        previous_guard_id = this.GetGuardId(msg_idx);
        this.StartMessage();
      },
      Click: function() {
        if (msg_running) {
          this.StopMessage();
          this.text_area.text(this.GetMessage(msg_idx));
        } else {
          this.NextMessage();
        }
      },
      Skip: function() {
        this.OnFinish();
        this.StopMessage();
        this.ClearMessage();
      },
      GetMessageObj: function(idx) {
        return this.messages[idx]['fields'];
      },
      GetMessage: function(idx) {
        return this.GetMessageObj(idx)['message'].split('<br />').join(' ');
      },
      GetImageUrl: function(idx) {
        return this.GetMessageObj(idx)['action_image'][0];
      },
      GetImage: function(idx) {
        var image = $('<img>').attr('src', this.GetImageUrl(idx));
        if (lefted_msg) {
          return image.addClass('left_aligned');
        } else {
          return image.addClass('right_aligned');
        }
      },
      GetGuardId: function(idx) {
        return this.GetMessageObj(idx)['action_image'][1];
      },
      size: function() {
        return this.messages.length;
      }
    });
    $.extend(this, defaults, settings);
    // Setup Keyboard Navigation
    $(document).keydown(function(e) {
      var key = e.charCode ? e.charCode : e.keyCode ? e.keyCode : 0;
      switch(key) {
        case 13: // enter
          dslib.$.Click();
          break;
      }
    }).click(function(e) {
      dslib.$.Click();
    });
    $('body').bind('selectstart', function(event) { event.preventDefault(); });
    var dsdiv = $(this.dsdiv);
    var image_field = $('<div></div>').attr('class', 'image-field');
    var text_field = $('<div></div>').attr('class', 'text-field');
    var text_area= $('<div></div>').attr('class', 'text-area');
    var skip_field = $('<div><a href="javascript:;">&nbsp;Skip&nbsp;</a></div>').attr('class', 'skip-field');
    dsdiv.append(image_field);
    text_field.append(text_area);
    dsdiv.append(text_field);
    dsdiv.append(skip_field);
    skip_field.find('a').click(function() {
      dslib.$.Skip();
    });
    this.image_field = image_field;
    this.text_area = text_area;
    if (this.background_img) {
      dsdiv.css('background', 'url(' + this.background_img + ') repeat left top');
    }

    //setTimeout(dslib.$.moreEveryComments, interval);
    // this.dsdiv에 만든다.
    this.messages = jQuery.parseJSON(this.message_set);
    this.NextMessage();
    for (var idx in this.messages) {
      var msg_obj = this.messages[idx]['fields'];
      var image = msg_obj['action_image'];
      var msg = msg_obj['message'];
    }
    return this;
  };
})(jQuery);
