from autobahn.exception import Disconnected
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.contrib.auth.models import AnonymousUser
from user.models import User
from .models import RoomChat
from channels.layers import get_channel_layer
import json


@database_sync_to_async
def get_user(user_id):
    try:
        return User.objects.get(id=user_id)
    except User.DoesNotExist:
        return AnonymousUser()


class RoomConsumer(AsyncJsonWebsocketConsumer):
    @database_sync_to_async
    def get_room(self, room_id):
        return RoomChat.objects.prefetch_related('members').get(pk=room_id)

    async def connect(self):
        await self.accept()
        self.chat_room = self.scope["url_route"]["kwargs"]["roomId"]
        try:
            room = await self.get_room(room_id=self.chat_room)
            if self.scope['user'] in room.members.all():
                await self.channel_layer.group_add(self.chat_room, self.channel_name)
                print('User', self.scope['user'].pk, ' connected to room ', self.chat_room)
                await self.send_json({
                    'alert': 'User' + str(self.scope['user'].pk) + ' connected to room ' + self.chat_room + ' successfully'
                })
            else:
                await self.send_json({
                    'alert': 'User' + str(
                        self.scope['user'].pk) + ' dont join to room ' + self.chat_room
                })
                await self.close()
        except (RoomChat.DoesNotExist, Disconnected):
            await self.send_json({
                'alert': 'Room' + str(self.chat_room) + ' does not exist'
            })
            await self.close()

    async def disconnect(self, close_code):
        print('User', self.scope['user'].pk, ' disconnected from', self.chat_room, 'close code ', str(close_code))
        await self.channel_layer.group_discard(self.chat_room, self.channel_name)

    async def receive_json(self, content, **kwargs):
        print('WebSocket message received:', content)
        # Do something with the message content, e.g.:
        response = {'type': 'echo', 'data': content}
        await self.send_json(response)

    async def message(self, content, close=False):
        """
        Encode the given content as JSON and send it to the client.
        """
        await super().send(text_data=await self.encode_json(content), close=close)
