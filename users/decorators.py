import jwt
from rest_framework.response import Response
from datetime import datetime, timedelta
from users.models import User
from functools import wraps
from rest_framework.decorators import renderer_classes
from rest_framework.renderers import JSONRenderer
from django.conf import settings


def login_required(view_function):
    @wraps(view_function)
    def wrap(request, *args, **kwargs):
        print(request.headers)
        try:
            jwt_token = request.headers.get('Authorization')
            if jwt_token is None:
                response = Response({
                    'detail': "Authorization token missing",
                }, status=401)
                return response

        except Exception as e:
            print("above exception response")
            return Response({
                'details': str(e)
            }, status=500)
        try:
            jwt_token = jwt_token.split()[1]
            print(jwt_token)
            user_id = jwt.decode(
                jwt_token, settings.SECRET_TOKEN_KEY, algorithms=[settings.ALGORITHM])['id']
            request.user = User.objects.get(pk=user_id)
            print(request.user)
        except jwt.ExpiredSignatureError:
            return Response({
                'detail': "Access token expired."
            }, status=403)
        except Exception as e:
            return Response({
                'detail': str(e)
            }, status=500)
        return view_function(request, *args, **kwargs)
    return wrap
