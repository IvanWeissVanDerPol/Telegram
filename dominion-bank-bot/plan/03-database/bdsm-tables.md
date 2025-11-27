# BDSM Feature Tables

## Table: `punishments`

Active humiliations, titles, penitencias.

| Column | Type | Description |
|--------|------|-------------|
| `id` | INTEGER PK | Punishment ID |
| `user_id` | INTEGER | Who is punished |
| `punisher_id` | INTEGER | Who punished them |
| `type` | TEXT | humiliation/penitencia/title |
| `description` | TEXT | The punishment text |
| `expires_at` | TIMESTAMP | When it ends |
| `completed` | BOOLEAN | If penitencia done |
| `created_at` | TIMESTAMP | When assigned |

```sql
CREATE TABLE punishments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    punisher_id INTEGER NOT NULL,
    type TEXT NOT NULL,
    description TEXT,
    expires_at TIMESTAMP,
    completed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);
```

---

## Table: `dungeon`

Users locked in calabozo or jaula.

| Column | Type | Description |
|--------|------|-------------|
| `user_id` | INTEGER PK | Who is locked |
| `locked_by` | INTEGER | Who locked them |
| `type` | TEXT | calabozo/jaula/encadenado |
| `reason` | TEXT | Why locked |
| `expires_at` | TIMESTAMP | Auto-release time |
| `created_at` | TIMESTAMP | When locked |

```sql
CREATE TABLE dungeon (
    user_id INTEGER PRIMARY KEY,
    locked_by INTEGER NOT NULL,
    type TEXT NOT NULL,
    reason TEXT,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);
```

### Dungeon Types

| Type | Duration | Restrictions |
|------|----------|--------------|
| `calabozo` | 1-4h | Can't transfer, auction |
| `jaula` | 2h | Can't use any commands |
| `encadenado` | 30m | Tied to another user |

---

## Table: `auctions`

Active auctions.

| Column | Type | Description |
|--------|------|-------------|
| `id` | INTEGER PK | Auction ID |
| `seller_id` | INTEGER | Who is being auctioned |
| `description` | TEXT | What they're offering |
| `starting_price` | INTEGER | Minimum bid |
| `current_bid` | INTEGER | Highest bid |
| `current_bidder` | INTEGER | Who has high bid |
| `ends_at` | TIMESTAMP | When auction ends |
| `status` | TEXT | active/completed/cancelled |
| `created_at` | TIMESTAMP | When started |

```sql
CREATE TABLE auctions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    seller_id INTEGER NOT NULL,
    description TEXT,
    starting_price INTEGER NOT NULL,
    current_bid INTEGER,
    current_bidder INTEGER,
    ends_at TIMESTAMP NOT NULL,
    status TEXT DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (seller_id) REFERENCES users(user_id)
);
```

---

## Table: `bids`

Bids on auctions.

| Column | Type | Description |
|--------|------|-------------|
| `id` | INTEGER PK | Bid ID |
| `auction_id` | INTEGER | Which auction |
| `bidder_id` | INTEGER | Who bid |
| `amount` | INTEGER | Bid amount |
| `created_at` | TIMESTAMP | When bid |

```sql
CREATE TABLE bids (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    auction_id INTEGER NOT NULL,
    bidder_id INTEGER NOT NULL,
    amount INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (auction_id) REFERENCES auctions(id),
    FOREIGN KEY (bidder_id) REFERENCES users(user_id)
);
```

---

## Table: `altars`

Passive income altars.

| Column | Type | Description |
|--------|------|-------------|
| `id` | INTEGER PK | Altar ID |
| `for_user_id` | INTEGER | Who receives daily SC |
| `built_by` | INTEGER | Who built it |
| `daily_amount` | INTEGER | SC per day |
| `created_at` | TIMESTAMP | When built |

```sql
CREATE TABLE altars (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    for_user_id INTEGER NOT NULL UNIQUE,
    built_by INTEGER NOT NULL,
    daily_amount INTEGER DEFAULT 10,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (for_user_id) REFERENCES users(user_id)
);
```
