from django.contrib.auth.models import User, Group
from django.http import HttpResponse
from rest_framework import viewsets
from rest_framework import permissions

from rownd_django.auth.backend import RowndApiAuthentication
from .serializers import UserSerializer, GroupSerializer
from django.contrib.auth import authenticate, login
from django.shortcuts import render
from django.views.decorators.http import require_POST

import json

class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [RowndApiAuthentication]


class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [RowndApiAuthentication]

@require_POST
def rownd_authenticate(request):
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

def check_auth(request):
    return render(request, 'test.html', {
        'is_authenticated': request.user.is_authenticated,
        'user': request.user
    })

def index(request):
    return HttpResponse("Hello, world. You're at the rownd index.")
