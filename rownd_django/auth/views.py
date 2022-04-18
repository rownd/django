import json
from django.http import HttpResponse
from django.contrib.auth import authenticate, login
from django.views.decorators.http import require_POST

@require_POST
def session_authenticate(request):
    if request.user.is_authenticated:
        return HttpResponse(status=200, content=json.dumps({ 'message': 'Already authenticated' }))

    token = request.headers.get("Authorization")

    if not token:
        return HttpResponse(status=401)

    token = token.split(" ")[1]
    
    user = authenticate(request, token=token)
    if user is not None:
        login(request, user)
        return HttpResponse(status=200, content=json.dumps({ 'message': 'Authentication successful', 'should_refresh_page': True }))
    else:
        return HttpResponse(status=401)