/*tinyMCE.init({
	mode : "textareas",
	theme : "advanced",
	theme_advanced_fonts : "Dotum=Dotum",
	theme_advanced_buttons1 : "fontsizeselect,forecolor,backcolor,bold,italic,underline,strikethrough,separator,justifyleft,justifycenter,justifyright, justifyfull,separator,bullist,numlist,outdent,indent,blockquote,separator,undo,redo,link,unlink,anchor,image,cleanup,code,separator,sub,sup,emotions",
	theme_advanced_buttons2 : "",
	theme_advanced_buttons3 : "",
	theme_advanced_toolbar_location : "top",
	theme_advanced_toolbar_align : "left"
});*/

$(function() {
		$('textarea.textareaContent').tinymce({
			// Location of TinyMCE script
				script_url : '/static/js/tinymce/jscripts/tiny_mce/tiny_mce.js',

				// 코드 Syntax Highlighting을 위한...
				extended_valid_elements : "textarea[cols|rows|disabled|name|readonly|class]",
			 	remove_linebreaks : false,   // Make sure you add this
				// 코드 Syntax Highlighting을 위한...
				
				// General options
				theme : "advanced",
				//plugins : "pagebreak,style,layer,table,save,advhr,advimage,advlink,emotions,iespell,inlinepopups,insertdatetime,preview,media,searchreplace,print,contextmenu,paste,directionality,fullscreen,noneditable,visualchars,nonbreaking,xhtmlxtras,template, syntaxhl",
				plugins : "table,emotions,inlinepopups,insertdatetime,preview,media,searchreplace,print,contextmenu,fullscreen,noneditable,visualchars,nonbreaking,xhtmlxtras,template,syntaxhl",
				language : "ko",

				// Theme options
				//theme_advanced_buttons1 : "save,newdocument,|,bold,italic,underline,strikethrough,|,justifyleft,justifycenter,justifyright,justifyfull,styleselect,formatselect,fontselect,fontsizeselect",
				//theme_advanced_buttons2 : "cut,copy,paste,pastetext,pasteword,|,search,replace,|,bullist,numlist,|,outdent,indent,blockquote,|,undo,redo,|,link,unlink,anchor,image,cleanup,help,code,|,insertdate,inserttime,preview,|,forecolor,backcolor",
				//theme_advanced_buttons3 : "tablecontrols,|,hr,removeformat,visualaid,|,sub,sup,|,charmap,emotions,iespell,media,advhr,|,print,|,ltr,rtl,|,fullscreen",
				//theme_advanced_buttons4 : "insertlayer,moveforward,movebackward,absolute,|,styleprops,|,cite,abbr,acronym,del,ins,attribs,|,visualchars,nonbreaking,template,pagebreak",
				//theme_advanced_buttons1 : "fontsizeselect,forecolor,backcolor,bold,italic,underline,strikethrough,|,justifyleft,justifycenter,justifyright, justifyfull,|,bullist,numlist,outdent,indent,blockquote,|,undo,redo,link,image,cleanup,code,|,sub,sup",
				//theme_advanced_buttons2 : "syntaxhl,|, tablecontrols,|,hr,removeformat,visualaid,charmap,emotions,media,advhr,|,print,|,search,replace,|,insertdate,inserttime,preview,|,fullscreen",
				theme_advanced_buttons1 : "fontsizeselect,forecolor,backcolor,bold,italic,underline,strikethrough,|,justifyleft,justifycenter,justifyright, justifyfull,|,blockquote,|,undo,redo,image,cleanup,code,|,sub,sup",
				theme_advanced_buttons2 : "syntaxhl,|, tablecontrols,|,hr,charmap,emotions,media,advhr,|,print,|,search,replace,|,preview,fullscreen",
				theme_advanced_buttons3 : "",
				theme_advanced_toolbar_location : "top",
				theme_advanced_toolbar_align : "left",
				theme_advanced_statusbar_location : "bottom",
				theme_advanced_resizing : true,
				theme_advanced_resize_horizontal : false,


				// Example content CSS (should be your site CSS)
				content_css : "/static/css/tinyMCEStyle.css",
				theme_advanced_fonts : "Dotum=Dotum",

				// Drop lists for link/image/media/template dialogs
				//template_external_list_url : "lists/template_list.js",
				//external_link_list_url : "lists/link_list.js",
				//external_image_list_url : "lists/image_list.js",
				//media_external_list_url : "lists/media_list.js",

				// Replace values for the template plugin
				//template_replace_values : {
				//		username : "Some User",
				//		staffid : "991234"
				//}
				setup : function(ed) {
					ed.onKeyPress.add( function(ed, e) {
						preventReload = true;
						//console.debug('Key press event: ' + e.keyCode);
					});
				}
		});
});

