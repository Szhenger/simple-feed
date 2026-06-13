import json
from channels.generic.websocket import AsyncWebsocketConsumer

class SynthesisFeedConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # In a real system, we extract the workspace_id from the JWT token in scope['user']
        self.workspace_id = self.scope['url_route']['kwargs']['workspace_id']
        self.group_name = f"feed_ws_{self.workspace_id}"

        # Join the Redis Pub/Sub group for this specific workspace
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        # Leave the group cleanly to prevent memory leaks
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def feed_update(self, event):
        """
        Handler for the 'feed.update' message type. 
        Pushes the JSON blob directly to the connected React client.
        """
        data = event['data']
        
        # We could route this back through the C++ kernel here if we needed 
        # to perform last-millisecond binary compression on massive data frames, 
        # but for text notifications, raw JSON is optimal.
        await self.send(text_data=json.dumps(data))
