from operator import le
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from asgiref.sync import sync_to_async
import json
import datetime
import uuid
from django.db.models import Q
from django.conf import settings
import os

class Notifications(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add("notifications", self.channel_name)
        await self.accept()

    async def disconnect(self, code):
        await self.channel_layer.group_discard("notifications", self.channel_name)
        await super().disconnect(code)

    async def notification_alerts(self, event):
        await self.send(
            text_data=json.dumps(
                {"title": event["title"], "description": event["description"], "time": event["time"],"permission": event["permission"]}
            )
        )
