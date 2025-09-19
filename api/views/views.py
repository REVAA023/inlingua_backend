from django.shortcuts import render
from django.http import JsonResponse

def websocket_test(request):
    """Test view to check WebSocket connectivity"""
    return JsonResponse({
        'status': 'WebSocket endpoint available',
        'websocket_url': 'ws://localhost:8000/ws/chat/',  # Adjust port as needed
        'message': 'Connect to this URL for WebRTC signaling'
    })