# Current Tasks - Geek Cafe SaaS SDK

**Version:** 0.7.0  
**Last Updated:** October 16, 2025  
**Current Focus:** Phase 1 - Core Platform Features

---

## 🎯 Active Work: Phase 1 Platform Models

We're implementing the high-priority platform-shared models from the domain model glossary.

### Reference Documents
- **Model Checklist:** `/docs/_working/platform-models-todo.md`
- **Domain Models:** `/docs/_working/domain-models.md`
- **Lineage Summary:** `/LINEAGE_IMPLEMENTATION_SUMMARY.md`

---

## ✅ Recently Completed (v0.7.0)

### File Lineage System
- ✅ Extended File model with lineage fields
- ✅ Created `FileLineageService` with 6 methods
- ✅ Created 9 Lambda handlers for lineage operations
- ✅ Comprehensive test suite (18 tests)
- ✅ Complete documentation (user guide + API reference)
- ✅ **Fixed bug:** Added `derived_file_count` to allowed update fields
- ✅ **Fixed bug:** Re-fetch pattern to avoid race conditions

**Location:** `src/geek_cafe_saas_sdk/domains/files/`

---

## 📋 Phase 1 Task List (In Progress)

### 1. ✅ Payments Domain (COMPLETE)

**Status:** Fully Implemented with Handlers, Tests, and Documentation  
**Priority:** ⭐ High

**Models to Create:**
- [x] `BillingAccount` - Payor/payee config; Stripe customer, currency, tax
- [x] `PaymentIntentRef` - PSP intent reference & status
- [x] `Payment` - Settled payment record (gross, fees, net)
- [x] `Refund` - Reversal metadata

**Tasks:**
```
[x] Create domain structure
    [x] src/geek_cafe_saas_sdk/domains/payments/
    [x] src/geek_cafe_saas_sdk/domains/payments/models/
    [x] src/geek_cafe_saas_sdk/domains/payments/services/
    [x] src/geek_cafe_saas_sdk/domains/payments/handlers/

[x] Implement BillingAccount model
    [x] Model class with all fields (PSP, currency, tax, address)
    [x] Validation logic
    [x] Helper methods (balance, address formatting)

[x] Implement PaymentIntentRef model
    [x] Model class with PSP fields
    [x] Status tracking with history
    [x] Webhook counter & error tracking

[x] Implement Payment model
    [x] Model class (gross, fees, net)
    [x] Link to BillingAccount
    [x] Immutable settlement logic
    [x] Refund & dispute tracking

[x] Implement Refund model
    [x] Model class with PSP fields
    [x] Status tracking
    [x] Validation logic

[x] Create PaymentService
    [x] create_billing_account()
    [x] get_billing_account()
    [x] update_billing_account()
    [x] create_payment_intent()
    [x] get_payment_intent()
    [x] update_payment_intent_status()
    [x] record_payment()
    [x] get_payment()
    [x] list_payments()
    [x] create_refund()
    [x] get_refund()
    [x] update_refund_status()

[x] Create test suite (24 tests, all passing)
    [x] Test BillingAccount CRUD
    [x] Test PaymentIntent lifecycle
    [x] Test Payment creation
    [x] Test Refund logic
    [x] Test validation
    [x] Test helper methods

[x] Create handlers (9 Lambda handlers)
    [x] POST /billing-accounts (create)
    [x] GET /billing-accounts/{id} (get)
    [x] PATCH /billing-accounts/{id} (update)
    [x] POST /payment-intents (create)
    [x] GET /payment-intents/{id} (get)
    [x] POST /payments (record)
    [x] GET /payments/{id} (get)
    [x] GET /payments (list)
    [x] POST /refunds (create)
    [x] GET /refunds/{id} (get)

[x] Documentation
    [x] README.md - Module overview
    [x] 01-getting-started.md - Quick start guide
    [x] 06-api-reference.md - Complete API documentation
    [x] Handler README - Deployment guide
```

---

### 2. ⏳ Subscriptions Domain

**Status:** Pending  
**Priority:** ⭐ High

**Models to Create:**
- [ ] `Plan` - Tier definitions (limits, features)
- [ ] `Addon` - Billable modules (Chat, Requests, Voting)
- [ ] `Subscription` - Active plan/add-ons + term, price
- [ ] `UsageRecord` - Metered usage events (standard priority)
- [ ] `Discount` - Promo codes, credits (standard priority)

**Tasks:**
```
[ ] Create domain structure
[ ] Implement Plan model
[ ] Implement Addon model
[ ] Implement Subscription model
[ ] Create SubscriptionService
[ ] Create test suite
[ ] Create handlers
[ ] Documentation
```

---

### 3. ⏳ Notifications Domain

**Status:** Pending  
**Priority:** ⭐ High

**Models to Create:**
- [ ] `Notification` - In-app/email/SMS event state (queued→sent)
- [ ] `NotificationPreference` - Per-user channel prefs & quiet hours
- [ ] `WebhookSubscription` - Outbound events (standard priority)

**Tasks:**
```
[ ] Create domain structure
[ ] Implement Notification model
[ ] Implement NotificationPreference model
[ ] Create NotificationService
    [ ] send_notification()
    [ ] get_user_preferences()
    [ ] update_preferences()
    [ ] mark_as_read()
[ ] Multi-channel delivery (email, SMS, in-app, push)
[ ] Create test suite
[ ] Create handlers
[ ] Documentation
```

---

### 4. ⏳ Auth Enhancements

**Status:** Pending  
**Priority:** ⭐ High

**Models to Add:**
- [ ] `Invitation` - Tokenized invite to join a tenant/role
- [ ] `ApiKey` - Programmatic access for partners
- [ ] `AccessPolicy` - Role→permission matrix

**Tasks:**
```
[ ] Implement Invitation model
    [ ] Token generation
    [ ] Expiration logic
    [ ] Role assignment

[ ] Implement ApiKey model
    [ ] Key generation
    [ ] Scopes/permissions
    [ ] Revocation

[ ] Implement AccessPolicy model
    [ ] Role definitions
    [ ] Permission matrix
    [ ] Policy evaluation

[ ] Enhance AuthService
    [ ] create_invitation()
    [ ] accept_invitation()
    [ ] create_api_key()
    [ ] validate_api_key()
    [ ] check_permission()

[ ] Create test suite
[ ] Create handlers
[ ] Documentation
```

---

### 5. ⏳ Tenancy Enhancements

**Status:** Pending  
**Priority:** ⭐ High

**Models to Add:**
- [ ] `BrandingProfile` - Logos, colors, domain, email from-name
- [ ] `FeatureFlags` - Enabled modules/add-ons per tenant

**Tasks:**
```
[ ] Implement BrandingProfile model
    [ ] Logo URLs (light/dark)
    [ ] Color scheme
    [ ] Custom domain
    [ ] Email branding

[ ] Implement FeatureFlags model
    [ ] Feature toggles
    [ ] Module enablement
    [ ] Per-tenant overrides

[ ] Enhance TenancyService
    [ ] update_branding()
    [ ] get_branding()
    [ ] set_feature_flag()
    [ ] is_feature_enabled()

[ ] Create test suite
[ ] Create handlers
[ ] Documentation
```

---

### 6. ⏳ Compliance Domain

**Status:** Pending  
**Priority:** ⭐ High

**Models to Create:**
- [ ] `ConsentRecord` - Opt-ins (directory, SMS, data)
- [ ] `AuditEvent` - Immutable audit trail (actor, action, resource, ts)

**Tasks:**
```
[ ] Create domain structure
[ ] Implement ConsentRecord model
[ ] Implement AuditEvent model
[ ] Create ComplianceService
[ ] Create AuditService
[ ] Create test suite
[ ] Create handlers
[ ] Documentation
```

---

### 7. ⏳ Announcements Domain

**Status:** Pending  
**Priority:** ⭐ High

**Models to Create:**
- [ ] `Announcement` - Broadcast posts with priority & audience

**Tasks:**
```
[ ] Create domain structure
[ ] Implement Announcement model
    [ ] Title, content, priority
    [ ] Audience targeting
    [ ] Publish/expire dates
    [ ] Read tracking

[ ] Create AnnouncementService
    [ ] create_announcement()
    [ ] publish_announcement()
    [ ] get_announcements()
    [ ] mark_as_read()

[ ] Create test suite
[ ] Create handlers
[ ] Documentation
```

---

## 🎯 Success Criteria

Each domain should have:
- ✅ Models with full field definitions
- ✅ Service layer with CRUD + business logic
- ✅ Comprehensive test coverage (>80%)
- ✅ Lambda handlers for API endpoints
- ✅ User documentation
- ✅ API reference documentation

---

## 📦 After Phase 1

**Phase 2** (Standard Priority):
- Integrations Domain
- I18n Support
- Messaging Enhancements
- Events Enhancements
- Reservations Domain
- Directory
- Violations

**Phase 3** (Future):
- Monitoring
- Advanced Compliance
- Advanced Features

---

## 🔗 Quick Links

- **Domain Models Glossary:** `/docs/_working/dommain-models.md`
- **Platform Models Checklist:** `/docs/_working/platform-models-todo.md`
- **Test Pattern:** See `tests/test_file_lineage_service.py`
- **Handler Pattern:** See `domains/files/handlers/`
- **Documentation Pattern:** See `docs/help/file-system/`

---

## 🚀 Next Steps (After Restart)

1. **Continue with Payments Domain**
   - Create directory structure
   - Implement BillingAccount model
   - Implement PaymentIntentRef model
   - Implement Payment model

2. **Follow the File System pattern:**
   - Models in `/models`
   - Services in `/services`
   - Handlers in `/handlers`
   - Tests in `/tests`
   - Docs in `/docs/help/[domain]`

3. **Use existing code as templates:**
   - File model → Payment model
   - FileSystemService → PaymentService
   - test_file_lineage_service.py → test_payment_service.py

---

**Ready to resume!** Start with Payments domain structure creation.
