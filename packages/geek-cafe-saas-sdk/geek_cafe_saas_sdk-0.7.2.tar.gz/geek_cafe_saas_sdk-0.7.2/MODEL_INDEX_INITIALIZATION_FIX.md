# Model Index Initialization Fix - Complete ✅

**Date:** October 17, 2025  
**Issue:** Models with `_setup_indexes()` method were not calling it in `__init__()`  
**Status:** FIXED

---

## 🐛 The Problem

Models defined `_setup_indexes()` methods but weren't calling them during initialization. This caused:
- Index lambdas not being created
- `_save_model()` failing because indexes weren't set up
- Manual pk/sk assignment still required in services (defeating the purpose)

### Example of the Bug

```python
class Addon(BaseModel):
    def __init__(self):
        super().__init__()
        self._addon_code: str = ""
        # ... other fields ...
        # ❌ MISSING: self._setup_indexes()
    
    def _setup_indexes(self):
        # Method defined but never called!
        primary = DynamoDBIndex()
        # ... index setup ...
```

**Result:** When service called `self._save_model(addon)`, the addon had no indexes configured, so boto3_assist couldn't generate pk/sk automatically.

---

## ✅ The Solution

Call `self._setup_indexes()` as the **LAST statement** in `__init__()`:

```python
class Addon(BaseModel):
    def __init__(self):
        super().__init__()
        self._addon_code: str = ""
        # ... all other fields ...
        
        # ✅ CRITICAL: Call as LAST line in __init__
        self._setup_indexes()
    
    def _setup_indexes(self):
        # Now this gets executed during model construction
        primary = DynamoDBIndex()
        # ... index setup ...
```

**Why last?** The index lambdas capture `self` properties. All properties must be initialized before creating the lambdas.

---

## 🔧 Models Fixed (7/7)

### Subscriptions Domain
1. ✅ **Plan** - Added `self._setup_indexes()` call
2. ✅ **Addon** - Added `self._setup_indexes()` call
3. ✅ **UsageRecord** - Added `self._setup_indexes()` call
4. ✅ **Discount** - Added `self._setup_indexes()` call

### Notifications Domain
5. ✅ **Notification** - Added `self._setup_indexes()` call
6. ✅ **NotificationPreference** - Added `self._setup_indexes()` call
7. ✅ **WebhookSubscription** - Added `self._setup_indexes()` call

---

## 📝 Documentation Updated

### Global Rule (Memory System)
Updated **MEMORY[1be0b373-ed19-4f8c-94a4-75db53b0759e]:**
- Title: "Model Index Pattern - _setup_indexes() Required and Called in __init__"
- Added requirement to call `self._setup_indexes()` at end of `__init__()`
- Added explanation of why it must be last

### Coding Standards Document
Updated `docs/guidelines/CODING_STANDARDS.md`:
- ✅ Added `self._setup_indexes()` call to example code
- ✅ Added explanation section: "Why _setup_indexes() must be called in __init__()"
- ✅ Updated Summary Checklist with new requirement
- ✅ Added critical warning about forgetting the call

---

## 🔧 Service Fixes

### SubscriptionManagerService

**Fixed `create_addon()`:**
```python
# Before - Manual save with commented pk/sk
addon.prep_for_save()
item = addon.to_dictionary()
# item["pk"] = f"ADDON#{addon.id}"  # Commented out
# item["sk"] = "METADATA"
self.dynamodb.save(table_name=self.table_name, item=item)

# After - Use helper method
addon.prep_for_save()
return self._save_model(addon)  # Automatic pk/sk from _setup_indexes()
```

**Fixed `get_addon()`:**
```python
# Before - Manual pk/sk construction
pk = f"ADDON#{addon_id}"
sk = "METADATA"
result = self.dynamodb.get(table_name=self.table_name, key={"pk": pk, "sk": sk})
addon.map(result["Item"])  # Plus bug: addon never instantiated

# After - Use helper method
addon = self._get_model_by_id(addon_id, Addon)
if not addon:
    return ServiceResult.error_result(...)
return ServiceResult.success_result(addon)
```

---

## 📊 Impact

### Before Fix
❌ Models couldn't use `_save_model()` - indexes not initialized  
❌ Services still needed manual pk/sk construction  
❌ Pattern inconsistent with Event model (which did call `_setup_indexes()`)  
❌ Defeated the purpose of the `_setup_indexes()` pattern

### After Fix
✅ Models work correctly with `_save_model()`  
✅ Services use helper methods exclusively  
✅ Pattern consistent across all models  
✅ Full benefits of `_setup_indexes()` pattern realized

---

## 🎓 Pattern Reference

### Complete Correct Pattern

```python
from boto3_assist.dynamodb.dynamodb_index import DynamoDBIndex, DynamoDBKey
from geek_cafe_saas_sdk.models.base_model import BaseModel

class MyModel(BaseModel):
    def __init__(self):
        super().__init__()
        
        # 1. Initialize all properties
        self._field1: str = ""
        self._field2: int = 0
        # ... all other fields ...
        
        # 2. CRITICAL: Call _setup_indexes() as LAST line
        self._setup_indexes()
    
    def _setup_indexes(self):
        """Setup DynamoDB indexes for queries."""
        
        # 3. Define primary index
        primary = DynamoDBIndex()
        primary.name = "primary"
        primary.partition_key.attribute_name = "pk"
        primary.partition_key.value = lambda: DynamoDBKey.build_key(("model", self.id))
        primary.sort_key.attribute_name = "sk"
        primary.sort_key.value = lambda: "METADATA"
        self.indexes.add_primary(primary)
        
        # 4. Define GSI indexes as needed
        gsi = DynamoDBIndex()
        gsi.name = "gsi1"
        gsi.partition_key.attribute_name = f"{gsi.name}_pk"
        gsi.partition_key.value = lambda: DynamoDBKey.build_key(("field", self.field_name))
        gsi.sort_key.attribute_name = f"{gsi.name}_sk"
        gsi.sort_key.value = lambda: DynamoDBKey.build_key(("timestamp", self.created_utc_ts))
        self.indexes.add_secondary(gsi)
```

### Service Usage (Automatic!)

```python
class MyService(DatabaseService[MyModel]):
    def create_item(self, **kwargs) -> ServiceResult[MyModel]:
        model = MyModel()
        model.field1 = kwargs.get("field1")
        # ... set other fields ...
        
        model.prep_for_save()
        return self._save_model(model)  # ✅ Automatic pk/sk from _setup_indexes()
    
    def get_item(self, item_id: str) -> ServiceResult[MyModel]:
        model = self._get_model_by_id(item_id, MyModel)  # ✅ Automatic pk/sk
        if not model:
            return ServiceResult.error_result("Not found", ErrorCode.NOT_FOUND)
        return ServiceResult.success_result(model)
```

---

## ✅ Verification Checklist

When creating a new model:

- [ ] Define `_setup_indexes()` method
- [ ] Call `self._setup_indexes()` as LAST line in `__init__()`
- [ ] Import `DynamoDBIndex` and `DynamoDBKey`
- [ ] Define at least a primary index
- [ ] Define GSI indexes as needed for queries
- [ ] Test that `_save_model()` works (saves to DynamoDB)
- [ ] Test that `_get_model_by_id()` works (retrieves from DynamoDB)

---

## 🎯 Key Takeaway

**The `_setup_indexes()` method is useless unless you call it in `__init__()`!**

Think of it like this:
1. `_setup_indexes()` **defines** the indexes
2. Calling it in `__init__()` **activates** the indexes
3. Without activation, the model has no indexes configured
4. Without indexes, helper methods can't generate keys automatically

**Always call `self._setup_indexes()` as the last line in your `__init__()` method!**

---

## 📈 Statistics

- **Models Fixed:** 7/7
- **Service Methods Fixed:** 2 (create_addon, get_addon)
- **Lines Changed:** ~15 (model __init__ calls)
- **Documentation Updated:** 2 files
- **Global Rules Updated:** 1
- **Pattern Now Consistent:** ✅ All models follow same pattern as Event model

---

**Status:** COMPLETE ✅  
**Pattern:** Fully documented and enforced  
**Future Models:** Will automatically follow this pattern via global rules
