"""Lambda handler for updating user notification preferences."""

from typing import Dict, Any
from geek_cafe_saas_sdk.lambda_handlers import create_handler
from geek_cafe_saas_sdk.domains.notifications.services import NotificationService


handler_wrapper = create_handler(
    service_class=NotificationService,
    require_body=True,
    convert_case=True
)


def handler(event: Dict[str, Any], context: Any, injected_service=None) -> Dict[str, Any]:
    """
    Update user notification preferences.
    
    PATCH /notifications/preferences
    
    Body:
    {
        "emailEnabled": true,
        "smsEnabled": false,
        "quietHoursEnabled": true,
        "quietHoursStart": "22:00",
        "quietHoursEnd": "08:00",
        "doNotDisturb": false
    }
    """
    return handler_wrapper.execute(event, context, update_preferences, injected_service)


def update_preferences(
    event: Dict[str, Any],
    service: NotificationService,
    user_context: Dict[str, str]
) -> Any:
    """Business logic for updating preferences."""
    user_id = user_context.get("user_id")
    payload = event["parsed_body"]
    
    result = service.update_preferences(user_id, payload)
    
    return result
