"""Lambda handler for listing notifications."""

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
    List notifications for current user.
    
    GET /notifications?unreadOnly=true&limit=50
    """
    return handler_wrapper.execute(event, context, list_notifications, injected_service)


def list_notifications(
    event: Dict[str, Any],
    service: NotificationService,
    user_context: Dict[str, str]
) -> Any:
    """Business logic for listing notifications."""
    user_id = user_context.get("user_id")
    
    params = event.get("queryStringParameters") or {}
    
    limit = int(params.get("limit", "50"))
    unread_only = params.get("unread_only", "false").lower() == "true"
    
    result = service.list_notifications(
        recipient_id=user_id,
        limit=limit,
        unread_only=unread_only
    )
    
    return result
