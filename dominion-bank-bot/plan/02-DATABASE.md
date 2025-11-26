# 02 - Database Schema

---

## Overview

We use **SQLite** - a simple file-based database.

- No server needed
- Just one file: `wallets.db`
- Perfect for small-medium bots
- Free forever

---

## Tables

We need **2 tables**:

### 1. `users` - Stores user balances

### 2. `transactions` - Stores all coin movements

---

## Table: `users`

Stores every user who interacts with the bot.

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| `user_id` | INTEGER | Telegram user ID (unique) | `123456789` |
| `username` | TEXT | @username (can be null) | `franco_bdsm` |
| `first_name` | TEXT | Display name | `Franco` |
| `balance` | INTEGER | Current latigazos | `500` |
| `created_at` | TIMESTAMP | When first seen | `2024-01-15 10:30:00` |
| `updated_at` | TIMESTAMP | Last activity | `2024-01-20 15:45:00` |

**Primary Key:** `user_id`

```
┌────────────┬─────────────┬────────────┬─────────┬─────────────────────┐
│  user_id   │  username   │ first_name │ balance │     created_at      │
├────────────┼─────────────┼────────────┼─────────┼─────────────────────┤
│ 123456789  │ franco_dom  │ Franco     │ 1500    │ 2024-01-15 10:30:00 │
│ 987654321  │ maria_sub   │ María      │ 300     │ 2024-01-16 14:20:00 │
│ 555555555  │ NULL        │ Pedro      │ 0       │ 2024-01-17 09:00:00 │
└────────────┴─────────────┴────────────┴─────────┴─────────────────────┘
```

**Notes:**
- `username` can be NULL (not everyone has @username)
- `balance` starts at 0 for new users
- `balance` can NEVER be negative

---

## Table: `transactions`

Records EVERY coin movement for history/audit.

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| `id` | INTEGER | Auto-increment ID | `1`, `2`, `3`... |
| `type` | TEXT | Type of transaction | `transfer`, `admin_add`, `admin_remove` |
| `from_user_id` | INTEGER | Who sent (null for admin_add) | `123456789` |
| `to_user_id` | INTEGER | Who received (null for admin_remove) | `987654321` |
| `amount` | INTEGER | How many latigazos | `100` |
| `admin_id` | INTEGER | Admin who did it (null for transfers) | `111111111` |
| `note` | TEXT | Optional note | `"Reward for event"` |
| `created_at` | TIMESTAMP | When it happened | `2024-01-20 15:45:00` |

**Primary Key:** `id` (auto-increment)

```
┌────┬──────────────┬──────────────┬────────────┬────────┬─────────────────────┐
│ id │     type     │ from_user_id │ to_user_id │ amount │     created_at      │
├────┼──────────────┼──────────────┼────────────┼────────┼─────────────────────┤
│ 1  │ admin_add    │ NULL         │ 123456789  │ 1000   │ 2024-01-15 10:30:00 │
│ 2  │ transfer     │ 123456789    │ 987654321  │ 200    │ 2024-01-16 14:20:00 │
│ 3  │ admin_remove │ 555555555    │ NULL       │ 50     │ 2024-01-17 09:00:00 │
│ 4  │ transfer     │ 987654321    │ 123456789  │ 100    │ 2024-01-18 11:00:00 │
└────┴──────────────┴──────────────┴────────────┴────────┴─────────────────────┘
```

---

## Transaction Types

| Type | Meaning | from_user_id | to_user_id |
|------|---------|--------------|------------|
| `transfer` | User sent to user | Sender | Receiver |
| `admin_add` | Admin gave coins | NULL | Receiver |
| `admin_remove` | Admin took coins | Victim | NULL |

---

## Database Operations Needed

### User Operations

| Function | Purpose | Used by |
|----------|---------|---------|
| `get_user(user_id)` | Get user by ID | All commands |
| `create_user(user_id, username, first_name)` | Create new user | /start, auto-create |
| `update_balance(user_id, new_balance)` | Set new balance | transfers, admin commands |
| `get_or_create_user(user_id, ...)` | Get existing or create new | All commands |
| `get_top_users(limit)` | Get users sorted by balance | /calabozo |

### Transaction Operations

| Function | Purpose | Used by |
|----------|---------|---------|
| `create_transaction(...)` | Record a transaction | All coin movements |
| `get_user_transactions(user_id, limit)` | Get user's history | /marcas |

---

## Example Queries

### Get user balance
```sql
SELECT balance FROM users WHERE user_id = 123456789;
```

### Transfer coins (2 updates + 1 insert)
```sql
-- Subtract from sender
UPDATE users SET balance = balance - 100 WHERE user_id = 123456789;

-- Add to receiver
UPDATE users SET balance = balance + 100 WHERE user_id = 987654321;

-- Record transaction
INSERT INTO transactions (type, from_user_id, to_user_id, amount)
VALUES ('transfer', 123456789, 987654321, 100);
```

### Get top 10 users
```sql
SELECT user_id, username, first_name, balance
FROM users
ORDER BY balance DESC
LIMIT 10;
```

### Get user's last 10 transactions
```sql
SELECT * FROM transactions
WHERE from_user_id = 123456789 OR to_user_id = 123456789
ORDER BY created_at DESC
LIMIT 10;
```

---

## Data Integrity Rules

| Rule | Implementation |
|------|----------------|
| Balance can't go negative | Check before update, reject if insufficient |
| User ID is unique | PRIMARY KEY constraint |
| Amount must be positive | Validate in code before insert |
| Transaction always recorded | Insert transaction in same operation as balance update |

---

## Auto-Create Users

When should we create a user record?

| Event | Create user? |
|-------|--------------|
| User sends `/start` | ✅ Yes |
| User sends `/micollar` | ✅ Yes (if not exists) |
| User sends `/servir` | ✅ Yes (if not exists) |
| User is mentioned in `/servir @user` | ✅ Yes (if not exists) |
| User is mentioned in `/recompensar @user` | ✅ Yes (if not exists) |

**Philosophy:** Create user record on first interaction, with 0 balance.

---

## Next: [03-COMMANDS.md](03-COMMANDS.md)
