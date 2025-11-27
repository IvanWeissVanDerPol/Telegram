# System Database Tables

## Table: `imports`

Import history for tracking and rollback.

| Column | Type | Description |
|--------|------|-------------|
| `id` | INTEGER PK | Import ID |
| `admin_id` | INTEGER | Who imported |
| `filename` | TEXT | File name |
| `source` | TEXT | excel/google_sheets |
| `rows_processed` | INTEGER | How many rows |
| `rows_failed` | INTEGER | How many failed |
| `event_name` | TEXT | Event name if applicable |
| `rolled_back` | BOOLEAN | If undone |
| `created_at` | TIMESTAMP | When imported |

```sql
CREATE TABLE imports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    admin_id INTEGER NOT NULL,
    filename TEXT,
    source TEXT DEFAULT 'excel',
    rows_processed INTEGER DEFAULT 0,
    rows_failed INTEGER DEFAULT 0,
    event_name TEXT,
    rolled_back BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## Table: `audit_log`

All actions for debugging.

| Column | Type | Description |
|--------|------|-------------|
| `id` | INTEGER PK | Log ID |
| `user_id` | INTEGER | Who did it |
| `action` | TEXT | What command |
| `target_id` | INTEGER | Who was affected |
| `details` | TEXT | JSON with details |
| `created_at` | TIMESTAMP | When |

```sql
CREATE TABLE audit_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    action TEXT NOT NULL,
    target_id INTEGER,
    details TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## Table: `achievements`

Badge/achievement definitions.

| Column | Type | Description |
|--------|------|-------------|
| `id` | INTEGER PK | Badge ID |
| `name` | TEXT | Badge name |
| `emoji` | TEXT | Badge emoji |
| `description` | TEXT | How to earn |
| `type` | TEXT | auto/manual |
| `requirement` | TEXT | JSON criteria |

```sql
CREATE TABLE achievements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    emoji TEXT,
    description TEXT,
    type TEXT DEFAULT 'auto',
    requirement TEXT
);
```

---

## Table: `user_badges`

Badges earned by users.

| Column | Type | Description |
|--------|------|-------------|
| `user_id` | INTEGER | Who earned |
| `achievement_id` | INTEGER | Which badge |
| `awarded_by` | INTEGER | Admin (if manual) |
| `created_at` | TIMESTAMP | When earned |

```sql
CREATE TABLE user_badges (
    user_id INTEGER,
    achievement_id INTEGER,
    awarded_by INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, achievement_id)
);
```

---

## Table: `google_sheets_sync`

Google Sheets connection state.

| Column | Type | Description |
|--------|------|-------------|
| `id` | INTEGER PK | Config ID |
| `sheet_url` | TEXT | Sheet URL |
| `sheet_id` | TEXT | Google Sheet ID |
| `last_sync` | TIMESTAMP | Last sync time |
| `sync_interval` | INTEGER | Minutes between syncs |
| `live_mode` | BOOLEAN | Fast sync during events |
| `active` | BOOLEAN | Is connected |

```sql
CREATE TABLE google_sheets_sync (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sheet_url TEXT NOT NULL,
    sheet_id TEXT NOT NULL,
    last_sync TIMESTAMP,
    sync_interval INTEGER DEFAULT 5,
    live_mode BOOLEAN DEFAULT FALSE,
    active BOOLEAN DEFAULT TRUE
);
```

---

## Table: `cooldowns`

Per-user command cooldowns.

| Column | Type | Description |
|--------|------|-------------|
| `user_id` | INTEGER | Who |
| `command` | TEXT | Which command |
| `target_id` | INTEGER | Target (if applicable) |
| `expires_at` | TIMESTAMP | When can use again |

```sql
CREATE TABLE cooldowns (
    user_id INTEGER,
    command TEXT,
    target_id INTEGER,
    expires_at TIMESTAMP NOT NULL,
    PRIMARY KEY (user_id, command, target_id)
);
```
