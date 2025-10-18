"""Lambda handler for listing webhook subscriptions."""

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
    List webhook subscriptions.
    
    GET /webhooks?activeOnly=true
    """
    return handler_wrapper.execute(event, context, list_webhooks, injected_service)


def list_webhooks(
    event: Dict[str, Any],
    service: NotificationService,
    user_context: Dict[str, str]
) -> Any:
    """Business logic for listing webhooks."""
    tenant_id = user_context.get("tenant_id")
    
    params = event.get("queryStringParameters") or {}
    active_only = params.get("active_only", "true").lower() == "true"
    
    result = service.list_webhook_subscriptions(
        tenant_id=tenant_id,
        active_only=active_only
    )
    
    return result
