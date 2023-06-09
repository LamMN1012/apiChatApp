from django.db.models import Q

from chat.models import RoomChat
from notification.models import Notification
from user.models import User
from .models import Friend
from .serializers import FriendSerializer, FriendDetailSerializer
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response


# Create your views here.

class AddFriendView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = FriendSerializer
    queryset = Friend.objects.all()

    def create(self, request, *args, **kwargs):
        if Friend.objects.filter((Q(requestID=request.user.id) & Q(responseID=request.data.get('responseID'))) | Q(
                requestID=request.data.get('responseID')) & Q(responseID=request.user.id)).exists():
            return Response({'detail': 'You are already friends or are waiting for their response.'},
                            status=status.HTTP_400_BAD_REQUEST)
        serializer = self.get_serializer(data={
            'requestID': request.user.id,
            'responseID': request.data.get('responseID'),
        })
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        responser = User.objects.get(id=request.data.get('responseID'))
        Notification.objects.create(
            senderID=request.user,
            receiverID=responser,
            type='friend-add-' + str(serializer.data.get('id')),
            content='sent you a request to be a friend',
            read=False,
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


# Only use when status friend is True
class DeleteFriendView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = FriendSerializer
    queryset = Friend.objects.all()
    lookup_field = 'pk'


# Use when status friend is False and request.user == responseID
class RejectRequestFriendView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = FriendSerializer
    queryset = Friend.objects.all()
    lookup_field = 'pk'


# Use when status friend is False and request.user == requestID
class CancelRequestFriendView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = FriendSerializer
    queryset = Friend.objects.all()
    lookup_field = 'pk'


class AcceptFriendRequestView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = FriendSerializer
    queryset = Friend.objects.all()
    lookup_field = 'pk'

    def update(self, request, *args, **kwargs):
        friend = self.get_object()
        if friend.responseID == request.user:
            friend.status = 1
            friend.save()
            serializer = self.get_serializer(friend)
            requester = User.objects.get(id=serializer.data.get('requestID'))
            Notification.objects.create(
                senderID=request.user,
                receiverID=requester,
                type='friend-accept-' + str(serializer.data.get('id')),
                content='accepted your request to make a friend',
                read=False,
            )
            room_chat = RoomChat.objects.create()
            room_chat.members.set([requester, request.user])
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'You do not have permission to update this friend request.'},
                            status=status.HTTP_403_FORBIDDEN)


# other people send requests to current user and wait current user response
class FriendResponsesListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = FriendSerializer
    queryset = Friend.objects.all()

    def get_queryset(self):
        queryset = Friend.objects.filter(status=False, responseID=self.request.user)
        return queryset


# current user send requests to other people and wait other people response
class FriendRequestsListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = FriendSerializer
    queryset = Friend.objects.all()

    def get_queryset(self):
        queryset = Friend.objects.filter(status=False, requestID=self.request.user)
        return queryset


class FriendListView(generics.ListAPIView):
    serializer_class = FriendSerializer

    def get_queryset(self):
        user_id = self.kwargs.get('pk')
        queryset = Friend.objects.filter(status=True).filter(Q(requestID=user_id) | Q(responseID=user_id))
        return queryset


class FriendListDetailView(generics.ListAPIView):
    serializer_class = FriendDetailSerializer

    def get_queryset(self):
        user_id = self.kwargs.get('pk')
        queryset = Friend.objects.filter(status=True).filter(Q(requestID=user_id) | Q(responseID=user_id))
        return queryset
