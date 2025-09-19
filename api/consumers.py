# consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import ClassRoom

class ClassroomConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Join classroom group
        self.room_group_name = "classroom"
        
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        print(f"✅ Client connected to classroom updates")
        
        # Send initial classroom data when client connects
        await self.send_initial_classroom_data()

    async def disconnect(self, close_code):
        # Leave classroom group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        print(f"❌ Client disconnected from classroom updates")

    async def receive(self, text_data):
        """Handle messages from WebSocket"""
        try:
            text_data_json = json.loads(text_data)
            message_type = text_data_json.get('type', 'ping')
            
            if message_type == 'ping':
                await self.send(text_data=json.dumps({
                    'type': 'pong',
                    'message': 'Connection alive'
                }))
            elif message_type == 'get_classrooms':
                await self.send_initial_classroom_data()
                
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Invalid JSON'
            }))

    async def classroom_message(self, event):
        """Handle classroom update messages from group"""
        message = event['message']
        
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'classroom_update',
            'data': json.loads(message)
        }))
        print(f"📤 Sent classroom update: {message}")

    @database_sync_to_async
    def get_all_classrooms(self):
        """Get all classrooms from database"""
        return list(ClassRoom.objects.values('id', 'name', 'is_active'))

    async def send_initial_classroom_data(self):
        """Send initial classroom data to client"""
        try:
            classrooms = await self.get_all_classrooms()
            await self.send(text_data=json.dumps({
                'type': 'initial_data',
                'classrooms': classrooms
            }))
            print(f"📤 Sent initial classroom data: {len(classrooms)} rooms")
        except Exception as e:
            print(f"❌ Error sending initial data: {e}")


class MeetingConsumer(AsyncWebsocketConsumer):
    """Consumer for meeting rooms (your existing functionality)"""
    
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'meeting_{self.room_name}'

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()
        print(f"✅ Client connected to meeting room: {self.room_name}")

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        print(f"❌ Client disconnected from meeting room: {self.room_name}")

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message
            }
        )

    async def chat_message(self, event):
        message = event['message']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message
        }))