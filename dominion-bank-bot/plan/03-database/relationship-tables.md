# Relationship Database Tables

## Table: `collars`

Ownership/collar relationships.

| Column | Type | Description |
|--------|------|-------------|
| `id` | INTEGER PK | Collar ID |
| `owner_id` | INTEGER | Dom's user_id |
| `sub_id` | INTEGER | Sub's user_id |
| `collar_type` | TEXT | consideration/training/formal |
| `public` | BOOLEAN | Visible to others |
| `created_at` | TIMESTAMP | When collared |

```sql
CREATE TABLE collars (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    owner_id INTEGER NOT NULL,
    sub_id INTEGER NOT NULL UNIQUE,
    collar_type TEXT DEFAULT 'formal',
    public BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (owner_id) REFERENCES users(user_id),
    FOREIGN KEY (sub_id) REFERENCES users(user_id)
);
```

**Note:** `sub_id` is UNIQUE - a sub can only have one collar.

---

## Table: `contracts`

Formal agreements between users.

| Column | Type | Description |
|--------|------|-------------|
| `id` | INTEGER PK | Contract ID |
| `dom_id` | INTEGER | Dominant's user_id |
| `sub_id` | INTEGER | Submissive's user_id |
| `terms` | TEXT | Contract text |
| `status` | TEXT | pending/active/completed/broken |
| `starts_at` | TIMESTAMP | When it begins |
| `ends_at` | TIMESTAMP | When it ends (null = permanent) |
| `broken_by` | INTEGER | Who broke it (if broken) |
| `created_at` | TIMESTAMP | When proposed |

```sql
CREATE TABLE contracts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    dom_id INTEGER NOT NULL,
    sub_id INTEGER NOT NULL,
    terms TEXT NOT NULL,
    status TEXT DEFAULT 'pending',
    starts_at TIMESTAMP,
    ends_at TIMESTAMP,
    broken_by INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (dom_id) REFERENCES users(user_id),
    FOREIGN KEY (sub_id) REFERENCES users(user_id)
);
```

### Contract Statuses

| Status | Meaning |
|--------|---------|
| `pending` | Waiting for sub to sign |
| `active` | Both signed, in effect |
| `completed` | Ended naturally |
| `broken` | One party broke it |
| `expired` | Time ran out |

---

## Table: `pending_requests`

Pending collar/contract requests.

| Column | Type | Description |
|--------|------|-------------|
| `id` | INTEGER PK | Request ID |
| `type` | TEXT | collar/contract |
| `from_user_id` | INTEGER | Who requested |
| `to_user_id` | INTEGER | Who needs to accept |
| `reference_id` | INTEGER | Contract ID if contract |
| `expires_at` | TIMESTAMP | When request expires |
| `created_at` | TIMESTAMP | When sent |

```sql
CREATE TABLE pending_requests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    type TEXT NOT NULL,
    from_user_id INTEGER NOT NULL,
    to_user_id INTEGER NOT NULL,
    reference_id INTEGER,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```
