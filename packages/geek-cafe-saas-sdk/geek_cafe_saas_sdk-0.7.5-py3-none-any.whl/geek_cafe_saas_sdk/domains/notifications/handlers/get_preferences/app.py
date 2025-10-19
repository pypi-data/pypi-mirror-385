"""Lambda handler for getting user notification preferences."""

from typing import Dict, Any
from geek_cafe_saas_sdk.lambda_handlers import create_handler
from geek_cafe_saas_sdk.domains.notifications.services import NotificationService


handler_wrapper = create_handler(
    service_class=NotificationService,
    require_body=False,
    convert_case=True
)


def handler(event: Dict[str, Any], context: Any, injected_service=None) -> Dict[str, Any]:
    """
    Get user notification preferences.
    
    GET /notifications/preferences
    """
    return handler_wrapper.execute(event, context, get_preferences, injected_service)


def get_preferences(
    event: Dict[str, Any],
    service: NotificationService,
    user_context: Dict[str, str]
) -> Any:
    """Business logic for getting preferences."""
    user_id = user_context.get("user_id")
    
    result = service.get_user_preferences(user_id)
    
    return result
