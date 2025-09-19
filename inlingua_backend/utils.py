from django.conf import settings

def get_turn_info():
    """
    Get TURN server information from settings
    """
    return {
        'numb_turn_credential': settings.NUMB_TURN_CREDENTIAL,
        'numb_turn_username': settings.NUMB_TURN_USERNAME,
    }