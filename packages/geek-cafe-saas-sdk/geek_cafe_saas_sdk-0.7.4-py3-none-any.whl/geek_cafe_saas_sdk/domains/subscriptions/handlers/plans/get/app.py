"""
Lambda handler for getting a subscription plan.

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
    Get a subscription plan by ID.
    
    Path parameters:
    - planId: Plan ID
    
    Returns 200 with plan details
    """
    return handler_wrapper.execute(event, context, get_plan, injected_service)


def get_plan(
    event: Dict[str, Any],
    service: SubscriptionManagerService,
    user_context: Dict[str, str]
) -> Any:
    """
    Business logic for getting a plan.
    """
    path_params = event.get("pathParameters") or {}
    plan_id = path_params.get("plan_id")
    
    if not plan_id:
        raise ValueError("plan_id is required in path")
    
    result = service.get_plan(plan_id=plan_id)
    
    return result
