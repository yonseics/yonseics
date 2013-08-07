SyntaxHighlighter (http://code.google.com/p/syntaxhighlighter/) is an incredible code syntax highlighting tool. It's 100% Java Script based and it doesn't care what you have on your server.  I believe any IT blog should have it. I needed to use this tool in my site, I use tinymce WYSIWYG, so I said this tool must work on tinymce.

Someone here (http://blog.daemon.com.au/go/blog-post/getting-tinymce-to-play-nice-with-dp-syntaxhighlighter)  pointed out that you need to wrap the code inside textarea. I quote this from his blog 

“One of the great features of tinyMCE is the way it tries to clean up mangled HTML. It's not perfect but it does a bang up job. One of its approaches to this problem is to strip out all HTML elements it doesn't consider to be valid. This typically includes textarea by default.
You can add to the valid elements in tinyMCE by adjusting the config slightly. Make sure you include all the relevant attributes you might need.
”

Since I can’t ask my site visitors to add the code every time they post a snippet of a code, so I wrote a plug-in for tinymce. This plug-in works only on tinymce 2.X. I will work to provide support for tinymce 3.X very soon.  To get it working you need first to download  SyntaxHighlighter and follow the installation steps. Then follow extract the attached file into the tinymce  plugins folder. Then in the tinymce init function make sure you include the Bold lines.

<script language="javascript" type="text/javascript">
	tinyMCE.init({
	mode : "textareas",
	theme : "advanced",
	theme_advanced_toolbar_location : "top",
	auto_resize:false,
	extended_valid_elements: "textarea[name|class|cols|rows]",   // Make sure you add this
    remove_linebreaks : false,   // Make sure you add this
	width:720,
    plugins : 'preview,CodeHighlighting',
    theme_advanced_toolbar_align : "right",
    theme_advanced_buttons1_add : " fontselect,fontsizeselect,zoom",
    theme_advanced_buttons2_add : "preview,separator,forecolor,backcolor",
    theme_advanced_buttons3_add_before : "tablecontrols, CodeHighlighting"  // Make sure you add this
    
});
</script>

This is the popup screen for the CodeHighlighting plugin.

Hope this helps
