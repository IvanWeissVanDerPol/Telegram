# Core Logic Flows

## Flow: /start

```
User sends /start
    │
    ▼
Extract user info (user_id, username, first_name)
    │
    ▼
User exists in DB?
    │
    ├─NO──► Create user (balance = 0)
    │
    └─YES─► Update last_seen
    │
    ▼
Get balance
    │
    ▼
Send welcome message
```

---

## Flow: /ver (Balance)

```
User sends /ver
    │
    ▼
Get or create user
    │
    ▼
Fetch balance from DB
    │
    ▼
Balance = 0?
    │
    ├─YES─► Send zero balance + hint
    │
    └─NO──► Send balance message
```

---

## Flow: /dar (Transfer)

```
User sends /dar @user 100
    │
    ▼
Parse: recipient, amount
    │
    ▼
Validate amount (positive int?)
    │
    ├─FAIL─► Send "invalid amount" error
    │
    ▼
Recipient = sender?
    │
    ├─YES──► Send "can't self-transfer" error
    │
    ▼
Find recipient in DB
    │
    ├─NOT FOUND─► Send "user not found" error
    │
    ▼
Get sender balance
    │
    ▼
balance >= amount?
    │
    ├─NO───► Send "insufficient balance" error
    │
    ▼
BEGIN TRANSACTION
    │
    ├── Subtract from sender
    ├── Add to recipient
    └── Record transaction
    │
COMMIT
    │
    ▼
Send success to sender
    │
    ▼
Notify recipient (DM)
```

---

## Flow: /ranking

```
User sends /ranking
    │
    ▼
Query: SELECT * ORDER BY balance DESC LIMIT 10
    │
    ▼
Result empty?
    │
    ├─YES─► Send "no users yet"
    │
    ▼
Format with medals (👑🥈🥉)
    │
    ▼
Get sender's position
    │
    ▼
Send ranking message
```

---

## Flow: /historial

```
User sends /historial
    │
    ▼
Get or create user
    │
    ▼
Query transactions (from_id OR to_id = user)
    │
    ▼
Result empty?
    │
    ├─YES─► Send "no history"
    │
    ▼
For each transaction:
    ├── Determine direction (sent/received)
    ├── Format with icon
    └── Calculate time ago
    │
    ▼
Send history + current balance
```
