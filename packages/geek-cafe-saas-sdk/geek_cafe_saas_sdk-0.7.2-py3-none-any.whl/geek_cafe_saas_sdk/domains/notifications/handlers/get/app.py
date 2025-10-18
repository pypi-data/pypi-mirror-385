"""Lambda handler for getting a notification."""

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
    Get a notification by ID.
    
    GET /notifications/{notificationId}
    """
    return handler_wrapper.execute(event, context, get_notification, injected_service)


def get_notification(
    event: Dict[str, Any],
    service: NotificationService,
    user_context: Dict[str, str]
) -> Any:
    """Business logic for getting notification."""
    tenant_id = user_context.get("tenant_id")
    
    path_params = event.get("pathParameters") or {}
    notification_id = path_params.get("notification_id")
    
    if not notification_id:
        raise ValueError("notification_id is required in path")
    
    result = service.get_notification(tenant_id, notification_id)
    
    return result
