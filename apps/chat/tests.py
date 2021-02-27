from django.test import TestCase
from channels.testing import WebsocketCommunicator
from .models import ChatRoom
from django.contrib.auth.models import User
from channels.generic.websocket import WebsocketConsumer
from .task import run_stock_bot
# Create your tests here.

class TestConsumer(WebsocketConsumer):
    def connect(self):
        self.accept()

    def receive(self, text_data=None, bytes_data=None):
        self.send(text_data=text_data, bytes_data=bytes_data)

    def disconnect(self, code):
        ...

class ChatTesT(TestCase):
    def setUp(self) -> None:
        user = User.objects.create(username="testcase", email="email@testcase.com", password="testcase")
        user.save()
        chat = ChatRoom.objects.create(name="todo")
        chat.save()

        self.consumer_app = TestConsumer()

    def test_redirect_if_not_logged_in(self):
        resp = self.client.get('/chat/todo/')
        self.assertRedirects(resp, '/accounts/login/?next=/chat/todo/')


    # TODO implement test socket connection with real chat consumer     

    async def test_websocket(self):
    
        communicator = WebsocketCommunicator(self.consumer_app, '/ws/chat/todo/')

        connected, subprotocol = await communicator.connect()
        self.assertTrue(connected)

        # Test sending text
        await communicator.send_to(text_data="hello")
        response = await communicator.receive_from()
        self.assertEqual(response, "hello")

        # Close
        await communicator.disconnect()


    # TODO test with development channel the whole bot workflow

    def test_chat_bot(self):

        run_stock_bot({
                "group":"chat_todo",
                "own_channel":"test",
                "user":"bot",
                "message": "/stock=aapl.us"
            })
