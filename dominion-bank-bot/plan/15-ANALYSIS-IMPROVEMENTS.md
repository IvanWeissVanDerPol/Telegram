# 15 - Plan Analysis & Improvements

## Executive Summary

After reviewing all 14 planning documents, here are the key findings and recommendations.

---

## 🔴 Critical Issues

### 1. Database Schema is Outdated

**Problem:** `02-DATABASE.md` only has 2 tables (users, transactions), but the project now needs:

| Missing Table | Needed For |
|--------------|------------|
| `profiles` | Bio, tags, kinks, limits |
| `relationships` | Collars, contracts, ownership |
| `punishments` | Calabozo, humiliation, penitencia |
| `auctions` | Active auctions, bids |
| `items` | Shop items, inventory |
| `imports` | Import history, rollback |
| `admins` | Admin levels, permissions |
| `settings` | Bot config, notification prefs |
| `events` | IRL events tracking |
| `achievements` | Badges, milestones |

**Action:** Update `02-DATABASE.md` with complete schema.

---

### 2. Command Name Conflicts

**Problem:** Same command names used differently across documents:

| Command | 03-COMMANDS | 10-COMMANDS-DETAIL | 12-BDSM |
|---------|-------------|--------------------|---------|
| `/castigar` | Admin remove coins | Admin remove coins | BDSM punishment |
| `/calabozo` | Ranking | Ranking | Lock in dungeon |
| `/marcas` | Transaction history | Transaction history | (not mentioned) |

**Action:** Rename to avoid conflicts:
- `/castigar` (admin) → `/quitar` or `/descontar`
- `/calabozo` (ranking) → `/ranking` or `/top`
- Keep `/calabozo` for dungeon feature

---

### 3. Inconsistent Command Names

**Problem:** `03-COMMANDS.md` uses old themed names, `10-COMMANDS-DETAIL.md` uses simpler names.

| Old (03) | New (10) | Final? |
|----------|----------|--------|
| `/micollar` | `/ver` | Need to decide |
| `/servir` | `/dar` | Need to decide |
| `/recompensar` | `/dar_admin` | Need to decide |

**Action:** Update `09-NAMING-OPTIONS.md` with final decisions, then update all docs.

---

### 4. Missing Features in Database

**Problem:** These features are documented but not in DB schema:

- ❌ Debt/negative balance tracking
- ❌ User roles (Dom/Sub/etc)
- ❌ Tags and kinks
- ❌ Privacy settings
- ❌ Collar/ownership relationships
- ❌ Contracts with expiration
- ❌ Dungeon/jail status
- ❌ Auction system
- ❌ Import history
- ❌ Google Sheets sync state

---

## 🟡 Moderate Issues

### 5. No Cooldown System Documented

**Problem:** BDSM commands like `/azotar`, `/nalgada` could be spammed.

**Recommendation:** Add cooldowns:
```
| Command | Cooldown | Per User |
|---------|----------|----------|
| /azotar @user | 5 min | Same target |
| /nalgada @user | 1 min | Same target |
| /calabozo @user | 30 min | Same target |
| /tributo @user | 24h | Same target |
```

---

### 6. No Rate Limiting

**Problem:** Users could flood the bot with commands.

**Recommendation:** Add to `06-VALIDATIONS.md`:
- 30 commands per minute per user
- 10 transfers per hour
- 5 admin commands per minute

---

### 7. No Consent System

**Problem:** Some BDSM commands affect other users without consent.

| Command | Needs Consent? |
|---------|---------------|
| `/collar @user` | ✅ Yes (documented) |
| `/azotar @user` | ❓ Not defined |
| `/humillar @user` | ❓ Not defined |
| `/calabozo @user` | ❓ Not defined |

**Recommendation:** Define consent rules:
- **Always consent:** `/collar`, `/contrato`, `/desafio`
- **No consent (fun):** `/nalgada`, `/reverencia`
- **Admin override:** `/calabozo`, `/castigar`

---

### 8. No Escape/Appeal System

**Problem:** If someone is locked in `/calabozo` or `/jaula`, they have no recourse.

**Recommendation:** Add:
- `/suplicar` - Request early release (with cost)
- `/apelar` - Send appeal to admins
- Auto-release after max time

---

### 9. SQLite Limitations Not Addressed

**Problem:** SQLite has issues for production:
- File locks with multiple connections
- No concurrent writes
- Lost on container restart (Railway)

**Recommendation:** Add section in `08-DEPLOYMENT.md`:
- For <100 users: SQLite with Volume
- For 100+ users: Migrate to PostgreSQL (free on Railway)

---

## 🟢 Suggestions for Improvement

### 10. Add Transaction Categories

**Current:** All transactions have simple `type`.

**Better:** Add categories for filtering:
```
| Type | Category | Description |
|------|----------|-------------|
| transfer | economy | User to user |
| admin_add | admin | Admin gave |
| punishment | bdsm | Castigar, azotar |
| auction | economy | Auction win |
| tribute | bdsm | Tributo, ofrenda |
| import | system | Excel import |
```

---

### 11. Add Notification Preferences per User

**Current:** Global notification settings.

**Better:** Let users choose:
```
/notificaciones
☑️ Recibir cuando me envían SC
☑️ Recibir cuando me castigan
☐ Recibir cuando me mencionan en ranking
☑️ Recibir recordatorios de deuda
```

---

### 12. Add Command Aliases

**Problem:** Users might try different command names.

**Recommendation:**
```
| Primary | Aliases |
|---------|---------|
| /ver | /saldo, /balance, /micollar |
| /dar | /enviar, /transferir, /servir |
| /ranking | /top, /leaderboard, /calabozo |
```

---

### 13. Group vs Private Chat Behavior

**Problem:** Not documented how commands behave differently.

**Recommendation:** Add section:
```
| Command | Group Chat | Private Chat |
|---------|------------|--------------|
| /ver | Shows balance | Shows + stats |
| /dar | Works | Works |
| /perfil | Summary | Full details |
| /buscar | Disabled | Works |
| /kinksmatch | Disabled | Works |
```

---

### 14. Add Help Context

**Problem:** `/help` shows all commands, overwhelming for new users.

**Better:**
```
/help              → Basic commands
/help admin        → Admin commands
/help bdsm         → BDSM commands
/help economia     → Economy commands
/help [comando]    → Specific command help
```

---

### 15. Missing Error Recovery

**Problem:** No documentation on what happens when things fail.

**Recommendation:** Add to `05-LOGIC-FLOWS.md`:
- What if DB write fails mid-transfer?
- What if Telegram API is down?
- What if user deletes account?
- What if import crashes?

---

### 16. No Logging/Audit System

**Problem:** No way to debug issues or track admin actions.

**Recommendation:** Add `logs` table:
```
| Column | Description |
|--------|-------------|
| timestamp | When |
| user_id | Who |
| action | What command |
| details | Full data |
| ip/device | Security |
```

---

### 17. No Backup Strategy

**Problem:** Only `/backup` mentioned, no automatic backups.

**Recommendation:**
- Auto backup daily
- Keep 7 days of backups
- Export to Google Drive
- Test restore procedure

---

### 18. Language Consistency

**Problem:** Mix of Spanish and English in docs and messages.

**Recommendation:**
- All user messages: Spanish
- All docs: Can be English
- Variable names in code: English
- Command names: Spanish (for users)

---

## 📋 Action Items

### High Priority

| # | Task | Document to Update |
|---|------|-------------------|
| 1 | Update database schema with ALL tables | 02-DATABASE.md |
| 2 | Finalize command names | 09-NAMING-OPTIONS.md |
| 3 | Fix command conflicts | 10, 12 |
| 4 | Add cooldown system | 06-VALIDATIONS.md |
| 5 | Document consent rules | 12-BDSM-COMMANDS.md |

### Medium Priority

| # | Task | Document |
|---|------|----------|
| 6 | Add rate limiting | 06-VALIDATIONS.md |
| 7 | Document group vs private | New or 03 |
| 8 | Add command aliases | 10-COMMANDS-DETAIL.md |
| 9 | Expand error recovery | 05-LOGIC-FLOWS.md |
| 10 | Add audit logging | 02-DATABASE.md |

### Low Priority

| # | Task | Document |
|---|------|----------|
| 11 | Add notification prefs per user | 13-USER-PROFILES.md |
| 12 | Better help system | 10-COMMANDS-DETAIL.md |
| 13 | Backup strategy | 08-DEPLOYMENT.md |
| 14 | Language consistency pass | All docs |

---

## 📊 New Database Schema (Proposed)

```
┌─────────────────────────────────────────────────────────────┐
│                        CORE TABLES                          │
├─────────────────────────────────────────────────────────────┤
│ users          │ Basic user info + balance                  │
│ transactions   │ All coin movements                         │
│ admins         │ Admin users + permission levels            │
├─────────────────────────────────────────────────────────────┤
│                      PROFILE TABLES                         │
├─────────────────────────────────────────────────────────────┤
│ profiles       │ Extended profile (bio, busca, etc)         │
│ user_tags      │ User's tags (many-to-many)                 │
│ user_kinks     │ User's kinks with levels                   │
│ user_limits    │ User's hard limits                         │
│ user_settings  │ Privacy, notifications                     │
├─────────────────────────────────────────────────────────────┤
│                    RELATIONSHIP TABLES                      │
├─────────────────────────────────────────────────────────────┤
│ collars        │ Who owns who                               │
│ contracts      │ Active contracts + terms                   │
│ relationships  │ Couples, mentors                           │
├─────────────────────────────────────────────────────────────┤
│                      BDSM TABLES                            │
├─────────────────────────────────────────────────────────────┤
│ punishments    │ Active humiliations, penitencias           │
│ dungeon        │ Users in calabozo/jaula                    │
│ auctions       │ Active auctions                            │
│ bids           │ Bids on auctions                           │
├─────────────────────────────────────────────────────────────┤
│                      SYSTEM TABLES                          │
├─────────────────────────────────────────────────────────────┤
│ imports        │ Import history for rollback                │
│ events         │ IRL events                                 │
│ achievements   │ Badge definitions                          │
│ user_badges    │ Earned badges                              │
│ audit_log      │ All actions for debugging                  │
│ settings       │ Bot configuration                          │
└─────────────────────────────────────────────────────────────┘
```

---

## 🎯 Recommended Next Steps

1. **Decide on command names** - Fill `09-NAMING-OPTIONS.md` completely
2. **Update database schema** - Create comprehensive `02-DATABASE.md`
3. **Consolidate commands** - Merge 03, 10, 12 into one master list
4. **Define cooldowns** - Add to `06-VALIDATIONS.md`
5. **Then start coding** - With clear, consistent specs

---

## Questions to Answer

Before coding, decide:

1. **Themed or simple commands?** `/azotar` or `/whip`?
2. **Consent for all BDSM commands?** Or only some?
3. **Cooldowns?** Which commands, how long?
4. **PostgreSQL or SQLite?** Based on expected users
5. **Notifications?** DM for everything or selective?
6. **Debt punishment?** Auto-punishment or admin decides?
7. **Maximum amounts?** Cap on transfers, bids?
8. **Inactive users?** Delete after X months?
