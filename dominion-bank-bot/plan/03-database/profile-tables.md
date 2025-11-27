# Profile Database Tables

## Table: `profiles`

Extended user profile information.

| Column | Type | Description |
|--------|------|-------------|
| `user_id` | INTEGER PK | Telegram user ID |
| `display_name` | TEXT | Preferred name |
| `pronouns` | TEXT | ella/el/elle |
| `age` | INTEGER | Age (optional) |
| `show_age` | TEXT | exact/range/hidden |
| `location` | TEXT | City/country |
| `main_role` | TEXT | Dom/Sub/Switch |
| `sub_roles` | JSON | Array of sub-roles |
| `experience_level` | TEXT | principiante/etc |
| `bio` | TEXT | Free text bio |
| `looking_for` | TEXT | What they seek |
| `availability` | TEXT | When available |
| `verified` | BOOLEAN | Admin verified |
| `profile_completeness` | INTEGER | 0-100% |
| `created_at` | TIMESTAMP | Profile created |
| `updated_at` | TIMESTAMP | Last edit |

```sql
CREATE TABLE profiles (
    user_id INTEGER PRIMARY KEY,
    display_name TEXT,
    pronouns TEXT,
    age INTEGER,
    show_age TEXT DEFAULT 'exact',
    location TEXT,
    main_role TEXT,
    sub_roles TEXT, -- JSON array
    experience_level TEXT,
    bio TEXT,
    looking_for TEXT,
    availability TEXT,
    verified BOOLEAN DEFAULT FALSE,
    profile_completeness INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);
```

---

## Table: `kinks` (Reference)

Predefined kink categories.

| Column | Type | Description |
|--------|------|-------------|
| `id` | INTEGER PK | Kink ID |
| `name` | TEXT | Kink name |
| `category` | TEXT | bondage/impact/etc |
| `description` | TEXT | Explanation |

---

## Table: `user_kinks`

User's kink preferences.

| Column | Type | Description |
|--------|------|-------------|
| `user_id` | INTEGER | User |
| `kink_id` | INTEGER | Kink reference |
| `level` | INTEGER | 1-3 stars |
| `direction` | TEXT | give/receive/both |
| `curious` | BOOLEAN | Still exploring |

```sql
CREATE TABLE user_kinks (
    user_id INTEGER,
    kink_id INTEGER,
    level INTEGER CHECK (level BETWEEN 1 AND 3),
    direction TEXT CHECK (direction IN ('give', 'receive', 'both')),
    curious BOOLEAN DEFAULT FALSE,
    PRIMARY KEY (user_id, kink_id)
);
```

---

## Table: `user_limits`

User's hard and soft limits.

| Column | Type | Description |
|--------|------|-------------|
| `user_id` | INTEGER | User |
| `limit_type` | TEXT | hard/soft |
| `description` | TEXT | What the limit is |

```sql
CREATE TABLE user_limits (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    limit_type TEXT CHECK (limit_type IN ('hard', 'soft')),
    description TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);
```

---

## Table: `user_settings`

Privacy and notification preferences.

| Column | Type | Description |
|--------|------|-------------|
| `user_id` | INTEGER PK | User |
| `privacy_level` | TEXT | public/members/verified |
| `notify_transfers` | BOOLEAN | DM on receive |
| `notify_mentions` | BOOLEAN | DM on ranking |
| `notify_bdsm` | BOOLEAN | DM on punishments |

```sql
CREATE TABLE user_settings (
    user_id INTEGER PRIMARY KEY,
    privacy_level TEXT DEFAULT 'members',
    notify_transfers BOOLEAN DEFAULT TRUE,
    notify_mentions BOOLEAN DEFAULT TRUE,
    notify_bdsm BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);
```
