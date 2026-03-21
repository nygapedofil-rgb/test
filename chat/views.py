import json

from django.contrib.auth import authenticate, get_user_model
from django.shortcuts import render
import uuid

from django.shortcuts import render

from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
import hashlib
from django.contrib.auth import authenticate, login
from django.shortcuts import get_object_or_404
# Create your views here.
import jwt
from django.conf import settings
from .models import *

User = get_user_model()
@csrf_exempt
def api_login(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)
    try:
        data = json.loads(request.body)
        username = data.get("username")
        password = data.get("password")
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)

    if not username or not password:
        return JsonResponse({"error": "missing credentials"}, status=400)

    user = authenticate(username=username, password=password)
    if user is None:
        return JsonResponse({"error": "invalid credentials"}, status=401)


    payload = {
        "user_id": user.id ,
        'jti': str(uuid.uuid4()),

    }

    token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")

    return JsonResponse({"token": token})

@csrf_exempt
def api_set_public_key(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)
    try:
        data = json.loads(request.body)
        username = data.get("username")
        password = data.get("password")
        public_key = data.get("public_key")
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)
    if not username or not password:
        return JsonResponse({"error": "missing credentials"}, status=400)
    user = authenticate(username=username, password=password)
    if user is None:
        return JsonResponse({"error": "invalid credentials"}, status=401)

    id_user = user.id
    try:
        obj = PublicKey.objects.get(id=id_user)
        obj.public_key = public_key
    except Exception as e:
        print(e)
        obj = PublicKey.objects.create(id_user=id_user, public_key=public_key)


    return JsonResponse({'status': 'ok'})

@csrf_exempt
def api_get_public_key(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)
    try:
        data = json.loads(request.body)
        username = data.get("username")
        password = data.get("password")
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)

    if not username or not password:
        return JsonResponse({"error": "missing credentials"}, status=400)
    user = authenticate(username=username, password=password)
    if user is None:
        return JsonResponse({"error": "invalid credentials"}, status=401)

    user_id = user.id

    obj = PublicKey.objects.get(id_user=user_id)
    public_key = obj.public_key
    return JsonResponse({'status': 'ok', 'public_key': public_key})



