import json
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from rownd_django.settings import rownd_settings

def conditional_csrf_exempt(func):
    if rownd_settings.CSRF_PROTECT_ROUTES == True:
        # Do not apply the decorator to the function
        return func
    else:
        # Apply the decorator and return the new function
        return csrf_exempt(func)

@conditional_csrf_exempt
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
    
@conditional_csrf_exempt
@require_POST
def session_sign_out(request):
    logout(request);
    return HttpResponse(status=200, content=json.dumps({ 'message': 'Sign-out successful', 'should_refresh_page': True }))