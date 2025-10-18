"""
Lambda handler for updating addons.

Admin endpoint - requires authentication.
"""

from typing import Dict, Any
from geek_cafe_saas_sdk.lambda_handlers import create_handler
from geek_cafe_saas_sdk.domains.subscriptions.services import SubscriptionManagerService


handler_wrapper = create_handler(
    service_class=SubscriptionManagerService,
    require_body=True,
    convert_case=True
)


def handler(event: Dict[str, Any], context: Any, injected_service=None) -> Dict[str, Any]:
    """
    Update an addon.
    
    Path parameters:
    - addonId: Addon ID
    
    Body contains fields to update
    
    Returns 200 with updated addon
    """
    return handler_wrapper.execute(event, context, update_addon, injected_service)


def update_addon(
    event: Dict[str, Any],
    service: SubscriptionManagerService,
    user_context: Dict[str, str]
) -> Any:
    """
    Business logic for updating an addon.
    """
    path_params = event.get("pathParameters") or {}
    addon_id = path_params.get("addon_id")
    
    if not addon_id:
        raise ValueError("addon_id is required in path")
    
    payload = event["parsed_body"]
    
    result = service.update_addon(
        addon_id=addon_id,
        updates=payload
    )
    
    return result
