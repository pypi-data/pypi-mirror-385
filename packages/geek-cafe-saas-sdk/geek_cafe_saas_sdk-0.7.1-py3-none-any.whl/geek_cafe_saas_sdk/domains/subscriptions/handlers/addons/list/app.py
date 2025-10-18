"""
Lambda handler for listing addons.

Public endpoint - no authentication required.
"""

from typing import Dict, Any
from geek_cafe_saas_sdk.lambda_handlers import create_handler
from geek_cafe_saas_sdk.domains.subscriptions.services import SubscriptionManagerService


handler_wrapper = create_handler(
    service_class=SubscriptionManagerService,
    require_auth=False,
    require_body=False,
    convert_case=True
)


def handler(event: Dict[str, Any], context: Any, injected_service=None) -> Dict[str, Any]:
    """
    List public addons.
    
    Query parameters:
    - status: Filter by status (default: "active")
    - category: Filter by category
    - limit: Max results (default: 50)
    
    Returns 200 with list of addons
    """
    return handler_wrapper.execute(event, context, list_addons, injected_service)


def list_addons(
    event: Dict[str, Any],
    service: SubscriptionManagerService,
    user_context: Dict[str, str]
) -> Any:
    """
    Business logic for listing addons.
    """
    params = event.get("queryStringParameters") or {}
    
    status = params.get("status", "active")
    category = params.get("category")
    limit = int(params.get("limit", "50"))
    
    result = service.list_addons(
        status=status,
        category=category,
        limit=limit
    )
    
    return result
