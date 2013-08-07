def chat(request):
  return {
    'chat_maximized':request.chat_maximized,
    'chat_disabled':request.chat_disabled
  }