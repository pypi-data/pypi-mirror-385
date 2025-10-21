# Complete Migration Example: VoteService

This document shows a complete before/after migration of the VoteService as a template for all other services.

## 📁 Files to Update

1. Service implementation
2. Lambda handler
3. Test file
4. Test fixtures

---

## 1️⃣ Service Implementation

### File: `src/geek_cafe_saas_sdk/domains/voting/services/vote_service.py`

#### BEFORE:
```python
from geek_cafe_saas_sdk.services.database_service import DatabaseService
from typing import Dict, Any

class VoteService(DatabaseService):
    def __init__(self, dynamodb=None, table_name=None):
        super().__init__(dynamodb=dynamodb, table_name=table_name)
    
    def create(self, tenant_id: str, user_id: str, user_context: Dict[str, Any], **kwargs) -> ServiceResult[Vote]:
        """Create a vote."""
        # Manual security validation (or none at all!)
        if not user_context:
            return ServiceResult.error_result("UNAUTHORIZED", "No user context")
        
        vote = Vote()
        vote.tenant_id = tenant_id
        vote.user_id = user_id
        vote.target_id = kwargs.get('target_id')
        vote.up_vote = kwargs.get('up_vote', 0)
        vote.down_vote = kwargs.get('down_vote', 0)
        
        # Manual audit trail
        vote.created_by = user_id
        vote.updated_by = user_id
        
        vote.prep_for_save()
        return self._save_model(vote)
    
    def get_by_id(self, resource_id: str, tenant_id: str, user_id: str, user_context: Dict[str, Any]) -> ServiceResult[Vote]:
        """Get vote by ID."""
        vote = self._get_model_by_id_with_tenant_check(resource_id, Vote, tenant_id)
        
        if not vote:
            return ServiceResult.error_result("NOT_FOUND", "Vote not found")
        
        return ServiceResult.success_result(vote)
```

#### AFTER:
```python
from geek_cafe_saas_sdk.services.database_service import DatabaseService
from geek_cafe_saas_sdk.core.request_context import RequestContext

class VoteService(DatabaseService):
    def __init__(self, dynamodb=None, table_name=None, request_context=None):
        super().__init__(
            dynamodb=dynamodb,
            table_name=table_name,
            request_context=request_context  # ✅ Pass context to parent
        )
    
    def create(self, tenant_id: str, user_id: str, **kwargs) -> ServiceResult[Vote]:
        """Create a vote."""
        # ✅ Set targets for security validation
        self.request_context.set_targets(tenant_id=tenant_id, user_id=user_id)
        
        vote = Vote()
        vote.tenant_id = tenant_id
        vote.user_id = user_id
        vote.target_id = kwargs.get('target_id')
        vote.up_vote = kwargs.get('up_vote', 0)
        vote.down_vote = kwargs.get('down_vote', 0)
        
        vote.prep_for_save()
        
        # ✅ Automatic security validation + audit trail
        return self._save_model(vote)
    
    def get_by_id(self, resource_id: str, tenant_id: str, user_id: str) -> ServiceResult[Vote]:
        """Get vote by ID."""
        # ✅ Automatic tenant validation (uses request_context internally)
        vote = self._get_model_by_id_with_tenant_check(resource_id, Vote, tenant_id)
        
        if not vote:
            return ServiceResult.error_result("NOT_FOUND", "Vote not found")
        
        return ServiceResult.success_result(vote)
```

### Key Changes:
1. ✅ Added `request_context` to `__init__` parameters
2. ✅ Passed `request_context` to `super().__init__()`
3. ❌ Removed `user_context: Dict` from all method signatures
4. ✅ Added `self.request_context.set_targets()` in methods
5. ❌ Removed manual audit trail (`created_by`, `updated_by`) - now automatic
6. ❌ Removed manual security validation - now automatic in `_save_model()`

---

## 2️⃣ Lambda Handler

### File: `src/geek_cafe_saas_sdk/domains/voting/handlers/votes/create/app.py`

#### BEFORE:
```python
from geek_cafe_saas_sdk.utilities.lambda_event_utility import LambdaEventUtility
from geek_cafe_saas_sdk.domains.voting.services.vote_service import VoteService
from boto3_assist.dynamodb.dynamodb import DynamoDB
import os

def lambda_handler(event, context):
    # Extract user context from JWT
    user_context = LambdaEventUtility.get_user_context(event)
    tenant_id = LambdaEventUtility.get_authenticated_user_tenant_id(event)
    user_id = LambdaEventUtility.get_authenticated_user_id(event)
    
    # Get request body
    body = LambdaEventUtility.get_body_from_event(event)
    
    # Create service
    vote_service = VoteService(
        dynamodb=DynamoDB(),
        table_name=os.getenv("DYNAMODB_TABLE_NAME")
    )
    
    # Call service (pass user_context)
    result = vote_service.create(
        tenant_id=tenant_id,
        user_id=user_id,
        user_context=user_context,  # ❌ Passed explicitly
        target_id=body.get('target_id'),
        up_vote=body.get('up_vote', 0),
        down_vote=body.get('down_vote', 0)
    )
    
    return service_result_to_response(result)
```

#### AFTER:
```python
from geek_cafe_saas_sdk.utilities.lambda_event_utility import LambdaEventUtility
from geek_cafe_saas_sdk.domains.voting.services.vote_service import VoteService
from geek_cafe_saas_sdk.core.request_context import RequestContext  # ✅ Import
from boto3_assist.dynamodb.dynamodb import DynamoDB
import os

def lambda_handler(event, context):
    # Extract user context from JWT
    user_context_dict = LambdaEventUtility.get_user_context(event)
    
    # ✅ Create security context
    request_context = RequestContext(user_context_dict)
    
    tenant_id = LambdaEventUtility.get_authenticated_user_tenant_id(event)
    user_id = LambdaEventUtility.get_authenticated_user_id(event)
    
    # Get request body
    body = LambdaEventUtility.get_body_from_event(event)
    
    # ✅ Create service with security context
    vote_service = VoteService(
        dynamodb=DynamoDB(),
        table_name=os.getenv("DYNAMODB_TABLE_NAME"),
        request_context=request_context  # ✅ Set once
    )
    
    # ✅ Clean API call (no user_context)
    result = vote_service.create(
        tenant_id=tenant_id,
        user_id=user_id,
        target_id=body.get('target_id'),
        up_vote=body.get('up_vote', 0),
        down_vote=body.get('down_vote', 0)
    )
    
    return service_result_to_response(result)
```

### Key Changes:
1. ✅ Import `RequestContext`
2. ✅ Create `request_context = RequestContext(user_context_dict)`
3. ✅ Pass `request_context` to service initialization
4. ❌ Remove `user_context` from service method calls

---

## 3️⃣ Test Fixtures

### File: `tests/conftest.py`

#### BEFORE:
```python
import pytest
from boto3_assist.dynamodb.dynamodb import DynamoDB

@pytest.fixture
def user_context():
    """Mock user context for tests."""
    return {
        'user_id': 'user-123',
        'tenant_id': 'tenant-123',
        'roles': [],
        'permissions': [],
        'email': 'test@example.com',
        'inboxes': []
    }

@pytest.fixture
def vote_service(mock_dynamodb):
    """Vote service for testing."""
    from geek_cafe_saas_sdk.domains.voting.services.vote_service import VoteService
    return VoteService(dynamodb=mock_dynamodb, table_name="test_table")
```

#### AFTER:
```python
import pytest
from boto3_assist.dynamodb.dynamodb import DynamoDB
from geek_cafe_saas_sdk.core.request_context import RequestContext  # ✅ Import

@pytest.fixture
def request_context():
    """Security context for tests."""
    user_context = {
        'user_id': 'user-123',
        'tenant_id': 'tenant-123',
        'roles': [],
        'permissions': [],
        'email': 'test@example.com',
        'inboxes': []
    }
    return RequestContext(user_context)  # ✅ Return RequestContext

@pytest.fixture
def vote_service(mock_dynamodb, request_context):
    """Vote service for testing."""
    from geek_cafe_saas_sdk.domains.voting.services.vote_service import VoteService
    return VoteService(
        dynamodb=mock_dynamodb,
        table_name="test_table",
        request_context=request_context  # ✅ Pass context
    )
```

### Key Changes:
1. ✅ Import `RequestContext`
2. ✅ Rename `user_context` fixture to `request_context`
3. ✅ Return `RequestContext(user_context)` instead of dict
4. ✅ Add `request_context` parameter to service fixtures
5. ✅ Pass `request_context` to service initialization

---

## 4️⃣ Test Files

### File: `tests/test_vote_service.py`

#### BEFORE:
```python
def test_create_vote(vote_service, user_context):
    """Test creating a vote."""
    result = vote_service.create(
        tenant_id="tenant-123",
        user_id="user-456",
        user_context=user_context,  # ❌ Passed to every test
        target_id="target-1",
        up_vote=1,
        down_vote=0
    )
    
    assert result.success is True
    assert result.data.target_id == "target-1"
    assert result.data.created_by == "user-456"  # Manual audit trail

def test_get_vote_by_id(vote_service, user_context):
    """Test getting a vote by ID."""
    # Create vote first
    create_result = vote_service.create(
        tenant_id="tenant-123",
        user_id="user-456",
        user_context=user_context,  # ❌ Repeated
        target_id="target-1",
        up_vote=1
    )
    
    # Get vote
    get_result = vote_service.get_by_id(
        resource_id=create_result.data.id,
        tenant_id="tenant-123",
        user_id="user-456",
        user_context=user_context  # ❌ Repeated
    )
    
    assert get_result.success is True
```

#### AFTER:
```python
def test_create_vote(vote_service):  # ✅ No user_context parameter
    """Test creating a vote."""
    result = vote_service.create(
        tenant_id="tenant-123",
        user_id="user-456",
        # ✅ No user_context - already set in fixture
        target_id="target-1",
        up_vote=1,
        down_vote=0
    )
    
    assert result.success is True
    assert result.data.target_id == "target-1"
    assert result.data.created_by == "user-123"  # ✅ Automatic from request_context

def test_get_vote_by_id(vote_service):  # ✅ No user_context parameter
    """Test getting a vote by ID."""
    # Create vote first
    create_result = vote_service.create(
        tenant_id="tenant-123",
        user_id="user-456",
        # ✅ No user_context
        target_id="target-1",
        up_vote=1
    )
    
    # Get vote
    get_result = vote_service.get_by_id(
        resource_id=create_result.data.id,
        tenant_id="tenant-123",
        user_id="user-456"
        # ✅ No user_context
    )
    
    assert get_result.success is True
```

### Key Changes:
1. ❌ Remove `user_context` parameter from test functions
2. ❌ Remove `user_context=user_context` from all service calls
3. ✅ Tests are cleaner and shorter
4. ✅ Audit trail (`created_by`) is automatic from `request_context.authenticated_user_id`

---

## 📊 Summary of Changes

### Removed:
- ❌ `user_context: Dict[str, Any]` parameter from **all** service methods
- ❌ `user_context` parameter from **all** test functions
- ❌ Manual `created_by` / `updated_by` assignment
- ❌ Manual tenant security validation

### Added:
- ✅ `request_context: RequestContext` to service `__init__()`
- ✅ `request_context` fixture in tests
- ✅ `RequestContext` import in handlers
- ✅ `self.request_context.set_targets()` in service methods

### Automatic:
- ✅ Tenant access validation in `_save_model()`
- ✅ Audit trail (`created_by`, `updated_by`)
- ✅ Security validation in `_get_model_by_id_with_tenant_check()`

---

## ✅ Testing the Migration

Run tests after migration:
```bash
pytest tests/test_vote_service.py -v
```

All tests should pass with the new pattern!

## 🎯 Next Domain to Migrate

Use this same pattern for:
1. Auth services
2. Community services
3. Event services
4. File services
5. Messaging services
6. Analytics services
7. Tenant services
8. Subscription services
