"""
Lambda handler for updating subscription plans.

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
    Update a subscription plan.
    
    Path parameters:
    - planId: Plan ID
    
    Body contains fields to update
    
    Returns 200 with updated plan
    """
    return handler_wrapper.execute(event, context, update_plan, injected_service)


def update_plan(
    event: Dict[str, Any],
    service: SubscriptionManagerService,
    user_context: Dict[str, str]
) -> Any:
    """
    Business logic for updating a plan.
    """
    path_params = event.get("pathParameters") or {}
    plan_id = path_params.get("plan_id")
    
    if not plan_id:
        raise ValueError("plan_id is required in path")
    
    payload = event["parsed_body"]
    
    result = service.update_plan(
        plan_id=plan_id,
        updates=payload
    )
    
    return result
