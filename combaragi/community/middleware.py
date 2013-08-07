class ChatCookieMiddleware(object):
  def process_request(self, request):
    request.__class__.chat_maximized = request.COOKIES.get('chat_maximized', '0')
    request.__class__.chat_disabled = request.COOKIES.get('chat_disabled', '0')
    return None

