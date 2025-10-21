# RequestContext Migration Plan

## 🎯 Overview

We're refactoring from passing `user_context: Dict` to every method to using a centralized `RequestContext` (security token service). This provides:

1. **Single Source of Truth** - All security logic in one place
2. **Automatic Security** - DatabaseService auto-validates tenant access
3. **Cleaner APIs** - No `user_context` parameter on every method
4. **Better Audit** - Automatic `created_by`/`updated_by` tracking

## 📋 Phase 1: Infrastructure (COMPLETE ✅)

### Files Created:
- ✅ `src/geek_cafe_saas_sdk/core/request_context.py` - Security token service
- ✅ Updated `src/geek_cafe_saas_sdk/services/database_service.py` - Integrated RequestContext

### Key Changes:
1. **RequestContext** separates authenticated user (JWT) from target resource (path)
2. **DatabaseService** now accepts `request_context` in `__init__`
3. **Automatic validation** in `_save_model()` and `_get_model_by_id_with_tenant_check()`

## 📋 Phase 2: Update Services (IN PROGRESS)

### Pattern - Service Initialization:

**BEFORE:**
```python
class VoteService(DatabaseService):
    def create(self, tenant_id: str, user_id: str, user_context: Dict, **kwargs):
        # Security validation here (or nowhere!)
        vote = Vote()
        vote.tenant_id = tenant_id
        # ... set fields
        return self._save_model(vote)
```

**AFTER:**
```python
class VoteService(DatabaseService):
    def create(self, tenant_id: str, user_id: str, **kwargs):
        # Security validated automatically by DatabaseService!
        # Set target for validation
        self.request_context.set_targets(tenant_id=tenant_id, user_id=user_id)
        
        vote = Vote()
        vote.tenant_id = tenant_id
        vote.user_id = user_id
        # ... set fields
        
        # Automatic security + audit trail
        return self._save_model(vote)  
```

### Pattern - Lambda Handlers:

**BEFORE:**
```python
def lambda_handler(event, context):
    user_context = LambdaEventUtility.get_user_context(event)
    
    vote_service = VoteService(dynamodb, table_name)
    
    return vote_service.create(
        tenant_id=tenant_id,
        user_id=user_id,
        user_context=user_context,  # ❌ Passed everywhere
        target_id=target_id
    )
```

**AFTER:**
```python
def lambda_handler(event, context):
    # Extract security context from JWT
    user_context_dict = LambdaEventUtility.get_user_context(event)
    request_context = RequestContext(user_context_dict)
    
    # Initialize service with security context
    vote_service = VoteService(dynamodb, table_name, request_context)
    
    # Clean API - no user_context needed!
    return vote_service.create(
        tenant_id=tenant_id,
        user_id=user_id,
        target_id=target_id
    )
```

## 📋 Phase 3: Update Tests

### Pattern - Test Fixtures:

**BEFORE:**
```python
@pytest.fixture
def user_context():
    return {
        'user_id': 'user-123',
        'tenant_id': 'tenant-123',
        'roles': [],
        'permissions': [],
        'email': 'test@example.com',
        'inboxes': []
    }

def test_create_vote(vote_service, user_context):
    result = vote_service.create(
        tenant_id='tenant-123',
        user_id='user-123',
        user_context=user_context,  # ❌ Passed to every call
        target_id='target-1'
    )
```

**AFTER:**
```python
@pytest.fixture
def request_context():
    """Fixture for request security context."""
    user_context = {
        'user_id': 'user-123',
        'tenant_id': 'tenant-123',
        'roles': [],
        'permissions': [],
        'email': 'test@example.com',
        'inboxes': []
    }
    return RequestContext(user_context)

@pytest.fixture
def vote_service(mock_dynamodb, request_context):
    """Vote service with security context."""
    return VoteService(
        dynamodb=mock_dynamodb,
        table_name="test_table",
        request_context=request_context  # ✅ Set once
    )

def test_create_vote(vote_service):
    # Clean test - no user_context parameter!
    result = vote_service.create(
        tenant_id='tenant-123',
        user_id='user-123',
        target_id='target-1'
    )
```

## 🔧 Migration Steps

### Step 1: Update Service __init__ Methods

For each service in `src/geek_cafe_saas_sdk/domains/*/services/`:

```python
class MyService(DatabaseService):
    def __init__(self, dynamodb=None, table_name=None, request_context=None):
        super().__init__(
            dynamodb=dynamodb,
            table_name=table_name,
            request_context=request_context  # ✅ Add this
        )
```

### Step 2: Remove user_context Parameters

From ALL service methods:
- ❌ Remove `user_context: Dict[str, Any]` from parameters
- ✅ Keep `tenant_id` and `user_id` (needed for resource creation)
- ✅ Security validation now automatic in `_save_model()`

### Step 3: Update Method Bodies

```python
def create(self, tenant_id: str, user_id: str, **kwargs):
    # Set targets for security validation
    self.request_context.set_targets(tenant_id=tenant_id, user_id=user_id)
    
    # Create model
    model = MyModel()
    model.tenant_id = tenant_id
    model.user_id = user_id
    
    # Automatic security + audit
    return self._save_model(model)
```

### Step 4: Update Lambda Handlers

```python
from geek_cafe_saas_sdk.core.request_context import RequestContext

def lambda_handler(event, context):
    # Initialize security context
    user_context = LambdaEventUtility.get_user_context(event)
    request_context = RequestContext(user_context)
    
    # Create service with context
    service = MyService(
        dynamodb=DynamoDB(),
        table_name=os.getenv("TABLE_NAME"),
        request_context=request_context
    )
    
    # Use service (no user_context needed!)
    return service.create(...)
```

### Step 5: Update Test Fixtures

```python
@pytest.fixture
def request_context():
    return RequestContext({
        'user_id': 'test-user',
        'tenant_id': 'test-tenant',
        'roles': ['user'],
        'permissions': [],
        'email': 'test@example.com',
        'inboxes': []
    })

@pytest.fixture
def my_service(mock_db, request_context):
    return MyService(
        dynamodb=mock_db,
        table_name="test_table",
        request_context=request_context
    )
```

## ✅ Benefits

1. **Security by Default** - Can't forget to validate tenant access
2. **Audit Trail** - Automatic `created_by`/`updated_by` population
3. **Cleaner Code** - No `user_context` parameter everywhere
4. **Single Source** - All security logic in RequestContext
5. **Better Testing** - Set context once in fixture

## 🎯 Next Steps

1. **Pick a domain** to migrate (e.g., voting)
2. **Update services** in that domain
3. **Update handlers** for that domain
4. **Update tests** for that domain
5. **Verify all tests pass**
6. **Repeat** for remaining domains

## 📊 Progress Tracking

### Domains:
- [ ] voting
- [ ] auth
- [ ] communities
- [ ] events
- [ ] files
- [ ] messaging
- [ ] analytics
- [ ] tenants
- [ ] subscriptions

### Current Status:
- **Infrastructure**: ✅ Complete
- **Services**: 🔄 Ready to migrate
- **Handlers**: 🔄 Ready to migrate
- **Tests**: 🔄 Ready to migrate
- **Target**: 100% tests passing with new pattern
