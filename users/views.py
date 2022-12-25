import jwt
from django.contrib import messages
from django.contrib.auth.hashers import check_password, make_password
from django.db.models import Q
from django.db.utils import IntegrityError
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from rest_framework.exceptions import AuthenticationFailed, NotFound
from rest_framework.response import Response
from django.http import HttpRequest

from .decorators import login_required
from .models import Tokenstable, User
from .serializers import AuthUserSerializer, TokenSerializer, UserSerializer

from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings

# Create your views here.

# endPoint :- /api/auth/login/
# verify and login the User while creating the token.


@api_view(['POST'])
def login(request):
    username = request.data.get('username')
    password = request.data.get('password')
    # print(username, password)
    if username is None or password is None:
        raise AuthenticationFailed(detail="Fields are empty.",code=406)

    user = User.objects.filter(username=username).first()
    if user is None:
        raise NotFound(detail="User not found", code=404)

    try:
        instance = user
        user = AuthUserSerializer(user).data
    except Exception as e:
        return Response({
            'detail' : "Error in serializing the data -> Specific error is " + str(e)
        },status=500)

    # checking password
    if check_password(password, user.get('password')) == False:
        return Response({
            'detail': 'username or password is incorrect'
        }, status=401)

    # generating tokens
    try:
        access_token = instance.getAccessToken()
        refresh_token = instance.getRefreshToken()
        print('access_token => ', access_token)
        print('refresh_token => ', refresh_token)
    except Exception as e:
        return Response({
            'detail': "Error in generating tokens -> Specific error is " + str(e)
        },status=500)

    response = Response({
        'user': user,
        'access_token': access_token
    })
    response.set_cookie('jwt_refresh_token', refresh_token, httponly=True)
    return response

# endPoint :- /api/auth/register/
# verify and register a User while creating the token.


@api_view(['POST'])
def register(request):
    username = request.POST.get('username')
    password = request.POST.get('password')
    email = request.POST.get('email')
    if username is None or password is None or email is None:
        raise AuthenticationFailed(detail="Empty Fields",code=406)
    print("pass")
    print("username - "+ username,"pass - "+password,"email - " + email)
    # IntegrityError
    try:
        instance = User(username=username, email=email)
        instance.password = make_password(password)
        instance.save()
    except IntegrityError as e:
        return Response({
            'detail': "User already present -> " + str(e)
        }, status=409)
    except Exception as e:
        return Response({
            'detail': "Some database error has occured. " + str(e)
        },status=500)

    try:
        user = UserSerializer(instance).data
        access_token = instance.getAccessToken()
        refresh_token = instance.getRefreshToken()
    except Exception as e:
        return Response({
            'detail': "Error in serializing data or generating tokens -> Specific error is " + str(e)
        },status=500)

    print('access_token => ', access_token)
    print('refresh_token => ', refresh_token)
    response = Response({
        'user': user,
        'access_token': access_token
    })
    response.set_cookie('jwt_refresh_token', refresh_token, httponly=True)
    print(response)
    return response


@api_view(['GET'])
@login_required
def private(request):
    try:
        print(request.user)
        return Response({
            'detail': 'private route hit'
        })
    except Exception as e:
        return Response({
            'detail' : str(e)
        },status=500)


@api_view(['GET'])
def refresh(request):
    refresh_token = request.COOKIES.get('jwt_refresh_token')
    if refresh_token is None:
        return Response({
            'detail' : "No token present."
        },status=406)
    user = User.objects.filter(refreshToken=refresh_token).first()

    if user is None:
        return NotFound(detail="User not found", code=404)

    try:
        payload = jwt.decode(refresh_token, 'secret',
                             algorithms=[settings.ALGORITHM])
    except jwt.ExpiredSignatureError:
        return Response({
            'detail': "Token expired. Try again"
        }, status=403)
    except:
        return Response({
            'detail': "Some error occured."
        }, status=500)

    seralized_user = UserSerializer(user).data

    if seralized_user.get('id') != payload.get('id'):
        return Response(status=403)

    access_token = user.getAccessToken()

    return Response({
        'access_token': access_token,
        'user': seralized_user
    })


# /api/auth/reset_password?userid=id&token=token
# validate the token and reset otherwise throw the error

# after succes redirect to /login
@csrf_exempt
@api_view(['POST', 'GET'])
def reset_password(request, token, userId):
    if request.method == "POST":
        try:
            user = User.objects.filter(id=userId).first()
            claimedUser = Tokenstable.objects.filter(resetToken=token).first()

            if user is None:
                raise NotFound(detail="User not found", code=404)

            if claimedUser is None:
                raise NotFound(detail="Token not found", code=404)

            serializedClaimedUser = TokenSerializer(claimedUser).data
            serializedUser = AuthUserSerializer(user).data
            password1 = request.POST.get('password1')
            password2 = request.POST.get('password2')

            if password1 is None or password2 is None:
                return Response({
                    'detail': "Empty passwords not allowed."
                }, status=406)

            # print(serializedClaimedUser)
            # print(serializedUser)
            # print(password1)
            # print(password2)

            # userId & token comes along with the reqest
            # claimedUser is extracted from tokenstable using token
            # userId is extracted using userId
            if serializedClaimedUser.get('userid') != userId:
                return Response({
                    'detail': "UNAUTHORIZED REQUEST."
                }, code=401)

            try:
                payload = jwt.decode(token, serializedUser.get(
                    'password'), algorithms=[settings.ALGORITHM])
            except jwt.ExpiredSignatureError:
                claimedUser.delete()
                return Response({
                    'detail': "Token expired. Try again"
                }, status=403)
            except:
                return Response({
                    'detail': "Some error occured."
                }, status=500)

            # print(payload)

            # check for the status code once
            if payload.get('id') != serializedUser.get('id'):
                return Response(status=400)

            if password1 != password2:
                return Response({
                    'detail': "Password don't match."
                }, status=406)

            user.password = make_password(password1)
            user.save()
            claimedUser.delete()

            return Response({
                'status': True,
                'detail': "Password updated successfully."
            })
        except Exception as e:
            return Response({
                'detail': str(e)
            }, status=500)

    elif request.method == "GET":
        print(token)
        print(userId)
        return render(request, 'reset_password.html', {"token": token, 'userId': userId})

# payload = jwt.decode(refresh_token, 'secret', algorithms=[settings.ALGORITHM])

# /api/auth/resetpassword/?username=user_name


@ api_view(['GET'])
def resetpasssord(request):
    try:
        username = request.GET.get('username')
        print(username)

        user = User.objects.filter(Q(username=username)).first()
        if user is None:
            # Username is not valid
            raise NotFound(detail="User not found", code=404)

        serialized_user = UserSerializer(user).data
        reset_token = user.getPasswordRefreshToken()
        print(reset_token)
        print(serialized_user.get('email'))
        print(HttpRequest.get_host(request))

        context = {
            'link': str("https://" + str(HttpRequest.get_host(request)) + "/api/auth/reset/" + str(reset_token) + "/" + str(user.id) + "/"),
        }
        print(context)

        msg_plain = render_to_string('email.txt')
        msg_html = render_to_string('email.html', {'context': context})

        try:
            token = Tokenstable(userid=user.id, resetToken=reset_token)
            token.save()
            try:
                send_mail("Password reset request",
                          msg_plain,
                          settings.EMAIL_HOST_USER,
                          [serialized_user.get('email')],
                          html_message=msg_html)
                return Response({
                    'status': True

                })
            except:
                # Error of the email service
                return Response({
                    'status': False,
                    'detail': "Some network problem with the email service" + str(e),
                }, status=503)

        except Exception as e:
            # Another password request before previous request is completed
            return Response({
                'status': False,
                'detail': str(e),
            }, status=208)
    except Exception as e:
        return Response({
            'detail': str(e)
        }, status=500)


@ api_view(["GET"])
def test(request, testNo):
    print(testNo)
    return Response(status=400)

# seperate this view
# expected route - /api/logout not /api/auth/logout


@ api_view(['GET'])
def logout(request):
    try:
        refresh_token = request.COOKIES.get('jwt_refresh_token')
        print(refresh_token)

        if refresh_token is None:
            # Problem with the refresh token
            return Response({
                'detail': "No user logged in."
            }, status=204)

        user = User.objects.filter(refreshToken=refresh_token).first()
        serialized_user = UserSerializer(user).data
        print(serialized_user)
        if user is None:
            response = Response({
                'detail': "No user corresponding to the token.",
            }, status=204)
            response.delete_cookie('jwt_refresh_token')
            return response

        user.refreshToken = ""
        user.save()
        serialized_user = UserSerializer(user).data

        print(serialized_user)
        # Successfully logged out
        response = Response({
            'detail': "Successfully logged out."
        }, status=200)
        response.delete_cookie('jwt_refresh_token')

        return response
    except Exception as e:
        # Any server error that can occur.
        return Response({
            'detail': str(e)
        }, status=500)
