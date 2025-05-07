from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed, NotFound
from .serializers import UserSerializer
from .models import User
import jwt, datetime
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError
from django.conf import settings
from django.core.mail import send_mail
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags

# Create your views here.

class RegisterView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)



class LoginView(APIView):
    def post(self,request):
        email = request.data['email']
        password = request.data['password']

        user = User.objects.filter(email=email).first()

        if user is None:
           raise AuthenticationFailed('User not found!')
        
        if not user.check_password(password):
             raise AuthenticationFailed('Incorrect password!')
        

        payload = {
            'id': user.id,
            'exp': datetime.datetime.utcnow()+datetime.timedelta(minutes=60),
            'iat': datetime.datetime.utcnow(),
        }

        token = jwt.encode(payload, 'secret', algorithm='HS256') #.decode('utf-8')

        return Response({
            'message': 'Login Successful',
            'token': token
        })
    

class UserView(APIView):
    def get(self, request):
        auth_header = request.headers.get('Authorization')

        if not auth_header:
            raise AuthenticationFailed('Authorization header missing.')

        try:
            # Expecting header format: Bearer <token>
            token = auth_header.split(' ')[1]
            payload = jwt.decode(token, 'secret', algorithms=['HS256'])
        except IndexError:
            raise AuthenticationFailed('Token not provided properly.')
        except ExpiredSignatureError:
            raise AuthenticationFailed('Token expired.')
        except InvalidTokenError:
            raise AuthenticationFailed('Invalid token.')

        user = User.objects.filter(id=payload['id']).first()

        if user is None:
            raise AuthenticationFailed('User not found.')

        return Response({
            'id': user.id,
            'email': user.email,
            'username': user.username  # or any fields you want to return
        })


class UserListView(APIView):
    # permission_classes = [IsAuthenticated]  # Optional: uncomment if JWT protection is needed

    def get(self, request):
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)
    

class ForgotPasswordView(APIView):
    def post(self, request):
        email = request.data.get('email')
        user = User.objects.filter(email=email).first()
        if not user:
            raise NotFound("User with this email does not exist")

        payload = {
            'id': user.id,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30),
            'iat': datetime.datetime.utcnow()
        }

        token = jwt.encode(payload, 'reset-secret', algorithm='HS256')

        reset_url = f"http://localhost:8000/reset-password?token={token}"

        html_content = render_to_string("reset_password.html", {
            'user': user,
            'reset_url': reset_url
        })
        text_content = strip_tags(html_content)

        # Create and send email
        email_message = EmailMultiAlternatives(
            subject="Reset Your Password",
            body=text_content,
            from_email="noreply@yourdomain.com",
            to=[user.email]
        )
        email_message.attach_alternative(html_content, "text/html")
        email_message.send()

        return Response({
            "message": "Password reset email has been sent to your email address."
        })
        # Here you'd send an email with the token. For now, we return it directly.
        # return Response({
        #     "message": "Password reset token generated.",
        #     "reset_token": token  # In production, do not send token in response
        # })
    

class ResetPasswordView(APIView):
    def post(self, request):
        token = request.data.get('token')
        new_password = request.data.get('new_password')

        try:
            payload = jwt.decode(token, 'reset-secret', algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed("Reset token expired")
        except jwt.DecodeError:
            raise AuthenticationFailed("Invalid token")

        user = User.objects.filter(id=payload['id']).first()
        if not user:
            raise NotFound("User not found")

        user.set_password(new_password)
        user.save()

        return Response({"message": "Password reset successful."})
    


