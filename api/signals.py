# signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import ClassRoom
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
import json

@receiver(post_save, sender=ClassRoom)
def classroom_update(sender, instance, **kwargs):
    print("🔔 Signal fired for:", instance.name)  # Debug
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        "classroom",
        {
            "type": "classroom_message",
            "message": json.dumps({
                "id": instance.id,
                "is_active": instance.is_active
            })
        }
    )

