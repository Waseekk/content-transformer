# Admin Dashboard Features Document

This document tracks all admin dashboard features requested and their implementation status.

---

## Current Features (Implemented)

### 1. User Statistics Table
**Location:** `/my-dashboard` (Admin Section)

| Column | Description |
|--------|-------------|
| User | Full name + email |
| Role | Admin or User badge |
| Tier | Subscription tier (free/premium/enterprise) |
| Hard | Hard news generated count |
| Soft | Soft news generated count |
| Tokens (Used/Limit) | Tokens used this month / Monthly token limit |
| Translations (Used/Limit) | Translations used this month / Monthly translation limit (shows red if exceeded) |
| Enhance (Used/Limit) | Enhancements used this month / Monthly enhancement limit (shows red if exceeded) |
| Status | Active/Inactive badge |

### 2. Token Management
- **Monthly Token Limit:** 1,000,000 (essentially unlimited)
- **Auto-Assign Threshold:** 10,000 tokens
- **Auto-Assign Amount:** 100,000 tokens
- **API Endpoint:** `POST /api/auth/admin/set-tokens`

### 3. Enhancement Limits
- **Monthly Enhancement Limit:** 600 per user
- **Behavior:** Soft limit - warns but doesn't block when exceeded
- **Resets:** 1st of each month
- **API Endpoint:** `POST /api/auth/admin/set-enhancements`

### 4. Translation Limits
- **Monthly Translation Limit:** 600 per user
- **Behavior:** Soft limit - warns but doesn't block when exceeded
- **Resets:** 1st of each month
- **Tracking:** Automatically tracked when user translates content

### 5. Auto-Assign Tokens
- When user's tokens fall below threshold, auto-assign is triggered
- Admin can manually trigger: `POST /api/auth/admin/auto-assign-tokens/{user_id}`

### 6. User View vs Admin View
- **Regular Users:** Only see Translation and Enhancement limits with progress bars
- **Admin Users:** See full Token Balance banner + Admin Stats Table with all user data

---

## Admin API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/auth/admin/users` | List all users |
| GET | `/api/auth/admin/users-stats` | Get detailed stats for all users |
| POST | `/api/auth/admin/set-tokens` | Set user's token limit |
| POST | `/api/auth/admin/set-enhancements` | Set user's enhancement limit |
| POST | `/api/auth/admin/auto-assign-tokens/{user_id}` | Trigger auto-assign for user |

---

## Requested Features (To Be Implemented)

### High Priority

- [ ] **Admin Actions Column** - Add buttons to admin table for quick actions:
  - Set Tokens button (opens modal)
  - Set Enhancement Limit button (opens modal)
  - Auto-Assign Tokens button
  - View Details button

- [ ] **Admin Edit Modal** - Modal dialog for editing user limits:
  - Input for new token limit
  - Input for new enhancement limit
  - Checkbox for "Reset used count"
  - Save/Cancel buttons

- [ ] **Dedicated Admin Page** - Separate `/admin` route with:
  - User management section
  - System settings section
  - Analytics overview

### Medium Priority

- [ ] **User Search/Filter** - Search users by email or name
- [ ] **Sort Columns** - Click column headers to sort
- [ ] **Export to CSV** - Export user stats to CSV file
- [ ] **Bulk Actions** - Select multiple users for bulk token assignment

### Low Priority

- [ ] **Activity Log** - Track admin actions (who changed what)
- [ ] **Email Notifications** - Notify users when limits are changed
- [ ] **Scheduled Reports** - Auto-send weekly usage reports

---

## Configuration Values

Located in `backend/app/config.py`:

```python
# Token Management
DEFAULT_MONTHLY_TOKENS: int = 1000000
FREE_TIER_TOKENS: int = 1000000
PREMIUM_TIER_TOKENS: int = 1000000
TOKEN_RESET_DAY: int = 1
AUTO_ASSIGN_TOKENS_THRESHOLD: int = 10000
AUTO_ASSIGN_TOKENS_AMOUNT: int = 100000

# Enhancement Limits
DEFAULT_MONTHLY_ENHANCEMENTS: int = 600
FREE_TIER_ENHANCEMENTS: int = 600
PREMIUM_TIER_ENHANCEMENTS: int = 600

# Translation Limits
DEFAULT_MONTHLY_TRANSLATIONS: int = 600
FREE_TIER_TRANSLATIONS: int = 600
PREMIUM_TIER_TRANSLATIONS: int = 600
```

---

## Database Fields (User Model)

```python
# Token management
tokens_remaining: int
tokens_used: int
monthly_token_limit: int
token_reset_day: int

# Enhancement limits
monthly_enhancement_limit: int
enhancements_used_this_month: int

# Translation limits
monthly_translation_limit: int
translations_used_this_month: int
```

---

## Notes for Future Development

1. **Monthly Reset Logic** - Currently handled by User model methods. Consider adding Celery Beat task for automatic monthly resets.

2. **Enhancement Tracking** - Enhancement usage should be tracked when generating content. Need to call `user.use_enhancement()` in enhancement API.

3. **Admin UI Polish** - Current admin table is functional but could use:
   - Fixed header on scroll
   - Pagination for many users
   - Expandable row details

---

## Version History

| Date | Version | Changes |
|------|---------|---------|
| 2026-01-17 | 1.0 | Initial implementation - token/enhancement limits, admin stats table |
| 2026-01-17 | 1.1 | Added translation limits (600/month), soft limits (warn not block), admin/user role badges, tokens hidden from regular users |

---

*Last Updated: 2026-01-17*
