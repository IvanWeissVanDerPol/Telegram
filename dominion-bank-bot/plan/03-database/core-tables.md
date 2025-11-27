# Core Database Tables

## Table: `users`

Primary user accounts and balances.

| Column | Type | Description |
|--------|------|-------------|
| `user_id` | INTEGER PK | Telegram user ID |
| `username` | TEXT | @username (nullable) |
| `first_name` | TEXT | Display name |
| `balance` | INTEGER | Current SadoCoins |
| `status` | TEXT | active/deactivated/banned |
| `created_at` | TIMESTAMP | First seen |
| `updated_at` | TIMESTAMP | Last activity |

```sql
CREATE TABLE users (
    user_id INTEGER PRIMARY KEY,
    username TEXT,
    first_name TEXT,
    balance INTEGER DEFAULT 0,
    status TEXT DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
);
```

---

## Table: `transactions`

All coin movements for history/audit.

| Column | Type | Description |
|--------|------|-------------|
| `id` | INTEGER PK | Auto-increment |
| `type` | TEXT | transfer/admin_add/admin_remove/etc |
| `category` | TEXT | economy/admin/bdsm/system |
| `from_user_id` | INTEGER | Sender (null for mints) |
| `to_user_id` | INTEGER | Receiver (null for burns) |
| `amount` | INTEGER | SadoCoins moved |
| `admin_id` | INTEGER | Admin who did it (if applicable) |
| `note` | TEXT | Optional description |
| `import_id` | INTEGER | If from import |
| `created_at` | TIMESTAMP | When it happened |

```sql
CREATE TABLE transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    type TEXT NOT NULL,
    category TEXT DEFAULT 'economy',
    from_user_id INTEGER,
    to_user_id INTEGER,
    amount INTEGER NOT NULL,
    admin_id INTEGER,
    note TEXT,
    import_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (from_user_id) REFERENCES users(user_id),
    FOREIGN KEY (to_user_id) REFERENCES users(user_id)
);
```

### Transaction Types

| Type | Category | from_user | to_user |
|------|----------|-----------|---------|
| `transfer` | economy | Sender | Receiver |
| `admin_add` | admin | NULL | Receiver |
| `admin_remove` | admin | User | NULL |
| `tribute` | bdsm | Giver | Receiver |
| `auction_win` | bdsm | Winner | Seller |
| `import` | system | NULL | User |

---

## Table: `admins`

Admin users and permission levels.

| Column | Type | Description |
|--------|------|-------------|
| `user_id` | INTEGER PK | Telegram user ID |
| `level` | TEXT | admin/super_admin |
| `added_by` | INTEGER | Who made them admin |
| `created_at` | TIMESTAMP | When added |

```sql
CREATE TABLE admins (
    user_id INTEGER PRIMARY KEY,
    level TEXT DEFAULT 'admin',
    added_by INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);
```

### Permission Levels

| Level | Permissions |
|-------|-------------|
| `admin` | Give/remove coins, check balances, import |
| `super_admin` | + Add/remove admins, stats, backup |
