from asgiref.sync import async_to_sync
from channels.generic.websocket import JsonWebsocketConsumer
from channels import exceptions
from .models.Message import Message
from .models.ChatRoom import ChatRoom
from .task import run_stock_bot
import re

class ChatConsumer(JsonWebsocketConsumer):

    def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name.replace(" ", "")


        try:
            self.room_id = ChatRoom.objects.get(name=self.room_name, participants=self.scope['user'].id)
        except ChatRoom.DoesNotExist:
            raise exceptions.DenyConnection()


        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )

        self.accept()

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    def receive_json(self, content):
        # Send message to room group
        if not content['message'].startswith('/stock='):
            Message.objects.create(
                user=self.scope['user'], chat=self.room_id, **content)

            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    "user": self.scope['user'].username,
                    **content
                }
            )
        else:
            stock_code = re.search('(?<==)([^\s]+)', content['message']).group(0)
            self.send_json(self.chat_response(**{"user":"bot", "message":f"Getting stock market data for {stock_code}..."}))
            run_stock_bot.delay(self.get_group_scope(content))

    # Receive message from room group
    def chat_message(self, content):
        self.send_json(self.chat_response(**content))
    
    def chat_response(self, **kwargs):
        itself = self.scope['user'].username == kwargs.get('user')
        return {'itself': itself, 'from':kwargs.get('user'), 'message': kwargs.get('message')}

    def get_group_scope(self, content):
        return {
                "group":self.room_group_name,
                "own_channel": self.channel_name,
                'type': 'chat_message',
                "user": self.scope['user'].username,
                **content
                }



