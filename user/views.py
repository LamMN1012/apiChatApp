from django.core.signing import Signer
from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import UserSerializer, MyTokenObtainPairSerializer, UserProfileSerializer
from .models import User
from rest_framework_simplejwt.views import TokenObtainPairView
signer = Signer(salt='extra')


# Create your views here.
class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer


class TestAPIView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data, many=False)
        serializer.is_valid()
        print(serializer.data)

        return Response('OK', status=status.HTTP_201_CREATED)


class UserRegisterAPIView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def create(self, request, *args, **kwargs):
        """
        data = {
            'first_name': 'Clark',
            'last_name': 'Le',
            'email': '',
            'password': 'Lnha2001',
            'confirm_password': 'Lnha2001',
            'gender': 'female',
            'birthday': '2023-02-09T17:00:00.000Z'
        }
        """
        print(request.data)
        if User.objects.filter(email=request.data['email']).exists():
            return Response('Your email existed!', status=status.HTTP_400_BAD_REQUEST)
        elif len(request.data['password']) < 6:
            return Response('Password must be at least 6 characters!', status=status.HTTP_400_BAD_REQUEST)
        elif request.data['password'] != request.data['confirm_password']:
            return Response('Confirm Password does not match!', status=status.HTTP_400_BAD_REQUEST)
        else:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            print(serializer.data)
            headers = self.get_success_headers(serializer.data)
            return Response({'token': serializer.data['id']}, status=status.HTTP_201_CREATED, headers=headers)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getMyProfile(request):
    user = request.user
    serializer = UserProfileSerializer(user, many=False)
    return Response(serializer.data, status.HTTP_200_OK)


class MyProfileView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserProfileSerializer

    def get_object(self):
        return self.request.user


class UserProfileView(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserProfileSerializer
    lookup_field = 'pk'


class UpdateMyProfileView(generics.UpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)


class ValidatePassword(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        password = request.data.get('password', None)
        user = User.objects.get(email=request.user.email)
        return Response(data={"status": user.check_password(password)}, status=status.HTTP_200_OK)
        # if serializer.is_valid():
        #     serializer.save()
        #     return Response(serializer.data, status=status.HTTP_201_CREATED)
        # return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
