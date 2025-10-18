# Index Pattern Fixes - Summary

**Date:** October 17, 2025  
**Issue:** Models and services weren't following the established `_setup_indexes()` pattern

---

## ✅ Models Fixed (7/7)

All models now have `_setup_indexes()` methods that define their DynamoDB index structure:

### Subscriptions Domain
1. **Plan** ✅
   - Primary: `plan#{id}` / `METADATA`
   - GSI1: Status-based listing
   - GSI2: Lookup by plan_code

2. **Addon** ✅
   - Primary: `addon#{id}` / `METADATA`
   - GSI1: Status and category filtering
   - GSI2: Lookup by addon_code

3. **UsageRecord** ✅
   - Primary: `usage#{id}` / `METADATA`
   - GSI1: By tenant and subscription
   - GSI2: By addon for aggregation

4. **Discount** ✅
   - Primary: `discount#{id}` / `METADATA`
   - GSI1: By status
   - GSI2: Lookup by discount_code

### Notifications Domain
5. **Notification** ✅
   - Primary: `tenant#{tenant_id}#notification#{id}` / `METADATA`
   - GSI1: By recipient (user notification list)
   - GSI2: By tenant and state (processing queue)

6. **NotificationPreference** ✅
   - Primary: `preferences#{user_id}` / `METADATA`

7. **WebhookSubscription** ✅
   - Primary: `webhook#{tenant_id}#subscription#{id}` / `METADATA`
   - GSI1: By tenant (listing)

---

## 🔧 Service Pattern

Services should use DatabaseService helper methods:

### ✅ Correct Pattern
```python
# Creating/Saving
plan = Plan()
plan.plan_code = "pro"
plan.plan_name = "Pro Plan"
# ... set other fields ...

# Use helper method - automatically handles pk/sk from _setup_indexes()
result = self._save_model(plan)
```

### ❌ Incorrect Pattern (What I did)
```python
# Manual pk/sk assignment
item = plan.to_dictionary()
item["pk"] = f"PLAN#{plan.id}"
item["sk"] = "METADATA"
item["gsi1_pk"] = f"STATUS#{plan.status}"
# etc...

self.dynamodb.save(table_name=self.table_name, item=item)
```

---

## 📋 Services To Refactor

### 1. SubscriptionManagerService
**Methods needing fixes:**
- `create_plan()` - Use `_save_model()`
- `get_plan()` - Use `_get_model_by_id()`
- `update_plan()` - Use `_save_model()` after updates
- `create_addon()` - Use `_save_model()`
- `get_addon()` - Use `_get_model_by_id()`
- `create_usage_record()` - Use `_save_model()`
- `create_discount()` - Use `_save_model()`
- `get_discount()` - Use `_get_model_by_id()`
- All list methods - Use `_query_by_index()`

### 2. NotificationService
**Methods needing fixes:**
- `create_notification()` - Use `_save_model()`
- `get_notification()` - Use `_get_model_by_id()`
- `update_notification_state()` - Use `_save_model()`
- `list_notifications()` - Use `_query_by_index()`
- `update_preferences()` - Use `_save_model()`
- `create_webhook_subscription()` - Use `_save_model()`
- `get_webhook_subscription()` - Use `_get_model_by_id()`
- All other CRUD methods

---

## 🎯 Benefits of Correct Pattern

1. **Automatic Index Management** - boto3_assist handles all pk/sk/gsi generation
2. **Type Safety** - Models define their own indexes
3. **Consistency** - Same pattern across all domains
4. **Maintainability** - Changes to indexes only need model updates
5. **Less Code** - No manual key construction in services

---

## 📝 Next Steps

Refactoring both services to use the correct pattern throughout. This requires updating approximately 20-30 methods across both services.

---

**Status:** Models fixed ✅ | Services being refactored 🔧
