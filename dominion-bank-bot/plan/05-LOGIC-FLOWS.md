# 05 - Logic Flows

Step-by-step logic for each operation.

---

## Flow: /start

```
┌─────────────────────────────────────────────┐
│              USER SENDS /start              │
└─────────────────────────────────────────────┘
                      │
                      ▼
        ┌─────────────────────────┐
        │  Extract user info:     │
        │  - user_id              │
        │  - username             │
        │  - first_name           │
        └─────────────────────────┘
                      │
                      ▼
        ┌─────────────────────────┐
        │  Does user exist in DB? │
        └─────────────────────────┘
                      │
           ┌──────────┴──────────┐
           │                     │
           ▼ NO                  ▼ YES
┌─────────────────────┐  ┌─────────────────────┐
│  Create new user:   │  │  Update last_seen   │
│  - balance = 0      │  │  (optional)         │
│  - created_at = now │  │                     │
└─────────────────────┘  └─────────────────────┘
           │                     │
           └──────────┬──────────┘
                      │
                      ▼
        ┌─────────────────────────┐
        │  Get user balance       │
        └─────────────────────────┘
                      │
                      ▼
        ┌─────────────────────────┐
        │  Send welcome message   │
        │  with balance           │
        └─────────────────────────┘
                      │
                      ▼
                    [END]
```

---

## Flow: /micollar (Check Balance)

```
┌─────────────────────────────────────────────┐
│            USER SENDS /micollar             │
└─────────────────────────────────────────────┘
                      │
                      ▼
        ┌─────────────────────────┐
        │  Get or create user     │
        │  (auto-register)        │
        └─────────────────────────┘
                      │
                      ▼
        ┌─────────────────────────┐
        │  Fetch balance from DB  │
        └─────────────────────────┘
                      │
                      ▼
        ┌─────────────────────────┐
        │  Is balance = 0?        │
        └─────────────────────────┘
                      │
           ┌──────────┴──────────┐
           │                     │
           ▼ YES                 ▼ NO
┌─────────────────────┐  ┌─────────────────────┐
│  Send zero balance  │  │  Send balance       │
│  message with hint  │  │  message            │
└─────────────────────┘  └─────────────────────┘
           │                     │
           └──────────┬──────────┘
                      │
                      ▼
                    [END]
```

---

## Flow: /servir (Transfer)

```
┌─────────────────────────────────────────────┐
│       USER SENDS /servir @user 100          │
└─────────────────────────────────────────────┘
                      │
                      ▼
        ┌─────────────────────────┐
        │  Parse command:         │
        │  - recipient (@user)    │
        │  - amount (100)         │
        └─────────────────────────┘
                      │
                      ▼
        ┌─────────────────────────┐
        │  Validate amount:       │
        │  Is it a positive int?  │
        └─────────────────────────┘
                      │
               ┌──────┴──────┐
               │             │
               ▼ NO          ▼ YES
     ┌──────────────┐        │
     │ Send error:  │        │
     │ Invalid      │        │
     │ amount       │        │
     └──────────────┘        │
               │             │
               ▼             ▼
            [END]   ┌─────────────────────────┐
                    │  Is recipient = sender? │
                    └─────────────────────────┘
                              │
                       ┌──────┴──────┐
                       │             │
                       ▼ YES         ▼ NO
             ┌──────────────┐        │
             │ Send error:  │        │
             │ Self-transfer│        │
             └──────────────┘        │
                       │             │
                       ▼             ▼
                    [END]   ┌─────────────────────────┐
                            │  Find recipient in DB   │
                            │  (or by @username)      │
                            └─────────────────────────┘
                                      │
                               ┌──────┴──────┐
                               │             │
                               ▼ NOT FOUND   ▼ FOUND
                     ┌──────────────┐        │
                     │ Send error:  │        │
                     │ User not     │        │
                     │ found        │        │
                     └──────────────┘        │
                               │             │
                               ▼             ▼
                            [END]   ┌─────────────────────────┐
                                    │  Get sender balance     │
                                    └─────────────────────────┘
                                              │
                                              ▼
                                    ┌─────────────────────────┐
                                    │  balance >= amount?     │
                                    └─────────────────────────┘
                                              │
                                       ┌──────┴──────┐
                                       │             │
                                       ▼ NO          ▼ YES
                             ┌──────────────┐        │
                             │ Send error:  │        │
                             │ Insufficient │        │
                             │ balance      │        │
                             └──────────────┘        │
                                       │             │
                                       ▼             ▼
                                    [END]   ┌─────────────────────────┐
                                            │  BEGIN TRANSACTION      │
                                            │  (atomic operation)     │
                                            └─────────────────────────┘
                                                      │
                                                      ▼
                                            ┌─────────────────────────┐
                                            │  Subtract from sender   │
                                            │  sender.balance -= amt  │
                                            └─────────────────────────┘
                                                      │
                                                      ▼
                                            ┌─────────────────────────┐
                                            │  Add to recipient       │
                                            │  recipient.balance +=   │
                                            └─────────────────────────┘
                                                      │
                                                      ▼
                                            ┌─────────────────────────┐
                                            │  Record transaction     │
                                            │  type: 'transfer'       │
                                            └─────────────────────────┘
                                                      │
                                                      ▼
                                            ┌─────────────────────────┐
                                            │  COMMIT TRANSACTION     │
                                            └─────────────────────────┘
                                                      │
                                                      ▼
                                            ┌─────────────────────────┐
                                            │  Send success to sender │
                                            └─────────────────────────┘
                                                      │
                                                      ▼
                                            ┌─────────────────────────┐
                                            │  Notify recipient       │
                                            │  (private message)      │
                                            └─────────────────────────┘
                                                      │
                                                      ▼
                                                    [END]
```

---

## Flow: /recompensar (Admin Add)

```
┌─────────────────────────────────────────────┐
│    ADMIN SENDS /recompensar @user 500       │
└─────────────────────────────────────────────┘
                      │
                      ▼
        ┌─────────────────────────┐
        │  Is sender in           │
        │  ADMIN_IDS list?        │
        └─────────────────────────┘
                      │
           ┌──────────┴──────────┐
           │                     │
           ▼ NO                  ▼ YES
┌─────────────────────┐          │
│  Send error:        │          │
│  "Not authorized"   │          │
└─────────────────────┘          │
           │                     │
           ▼                     ▼
        [END]         ┌─────────────────────────┐
                      │  Parse command:         │
                      │  - recipient            │
                      │  - amount               │
                      └─────────────────────────┘
                                 │
                                 ▼
                      ┌─────────────────────────┐
                      │  Validate amount        │
                      └─────────────────────────┘
                                 │
                          ┌──────┴──────┐
                          │             │
                          ▼ INVALID     ▼ VALID
                ┌──────────────┐        │
                │ Send error   │        │
                └──────────────┘        │
                          │             │
                          ▼             ▼
                       [END]   ┌─────────────────────────┐
                               │  Get or create          │
                               │  recipient user         │
                               └─────────────────────────┘
                                         │
                                         ▼
                               ┌─────────────────────────┐
                               │  Add to recipient       │
                               │  balance += amount      │
                               └─────────────────────────┘
                                         │
                                         ▼
                               ┌─────────────────────────┐
                               │  Record transaction     │
                               │  type: 'admin_add'      │
                               │  admin_id: sender       │
                               └─────────────────────────┘
                                         │
                                         ▼
                               ┌─────────────────────────┐
                               │  Confirm to admin       │
                               └─────────────────────────┘
                                         │
                                         ▼
                               ┌─────────────────────────┐
                               │  Notify recipient       │
                               └─────────────────────────┘
                                         │
                                         ▼
                                       [END]
```

---

## Flow: /castigar (Admin Remove)

```
┌─────────────────────────────────────────────┐
│      ADMIN SENDS /castigar @user 200        │
└─────────────────────────────────────────────┘
                      │
                      ▼
        ┌─────────────────────────┐
        │  Is sender admin?       │
        └─────────────────────────┘
                      │
           ┌──────────┴──────────┐
           │                     │
           ▼ NO                  ▼ YES
┌─────────────────────┐          │
│  "Not authorized"   │          │
└─────────────────────┘          │
           │                     │
           ▼                     ▼
        [END]         ┌─────────────────────────┐
                      │  Parse & validate       │
                      └─────────────────────────┘
                                 │
                                 ▼
                      ┌─────────────────────────┐
                      │  Find recipient         │
                      └─────────────────────────┘
                                 │
                          ┌──────┴──────┐
                          │             │
                          ▼ NOT FOUND   ▼ FOUND
                ┌──────────────┐        │
                │ "User not    │        │
                │ found"       │        │
                └──────────────┘        │
                          │             │
                          ▼             ▼
                       [END]   ┌─────────────────────────┐
                               │  recipient.balance >=   │
                               │  amount?                │
                               └─────────────────────────┘
                                         │
                                  ┌──────┴──────┐
                                  │             │
                                  ▼ NO          ▼ YES
                        ┌──────────────┐        │
                        │ OPTION A:    │        │
                        │ Reject       │        │
                        │ ─────────    │        │
                        │ OPTION B:    │        │
                        │ Set to 0     │        │
                        └──────────────┘        │
                                  │             │
                                  ▼             ▼
                               ┌─────────────────────────┐
                               │  Subtract from balance  │
                               │  (or set to 0)          │
                               └─────────────────────────┘
                                         │
                                         ▼
                               ┌─────────────────────────┐
                               │  Record transaction     │
                               │  type: 'admin_remove'   │
                               └─────────────────────────┘
                                         │
                                         ▼
                               ┌─────────────────────────┐
                               │  Confirm & notify       │
                               └─────────────────────────┘
                                         │
                                         ▼
                                       [END]
```

---

## Flow: /calabozo (Ranking)

```
┌─────────────────────────────────────────────┐
│            USER SENDS /calabozo             │
└─────────────────────────────────────────────┘
                      │
                      ▼
        ┌─────────────────────────┐
        │  Query: SELECT users    │
        │  ORDER BY balance DESC  │
        │  LIMIT 10               │
        └─────────────────────────┘
                      │
                      ▼
        ┌─────────────────────────┐
        │  Is result empty?       │
        └─────────────────────────┘
                      │
           ┌──────────┴──────────┐
           │                     │
           ▼ YES                 ▼ NO
┌─────────────────────┐  ┌─────────────────────┐
│  Send "no users     │  │  Format ranking:    │
│  yet" message       │  │  - Add medals       │
└─────────────────────┘  │  - Format numbers   │
           │             └─────────────────────┘
           │                     │
           │                     ▼
           │             ┌─────────────────────┐
           │             │  Get sender's       │
           │             │  position in        │
           │             │  ranking            │
           │             └─────────────────────┘
           │                     │
           │                     ▼
           │             ┌─────────────────────┐
           │             │  Send formatted     │
           │             │  ranking message    │
           │             └─────────────────────┘
           │                     │
           └──────────┬──────────┘
                      │
                      ▼
                    [END]
```

---

## Flow: /marcas (History)

```
┌─────────────────────────────────────────────┐
│             USER SENDS /marcas              │
└─────────────────────────────────────────────┘
                      │
                      ▼
        ┌─────────────────────────┐
        │  Get or create user     │
        └─────────────────────────┘
                      │
                      ▼
        ┌─────────────────────────┐
        │  Query transactions:    │
        │  WHERE from_id = user   │
        │  OR to_id = user        │
        │  ORDER BY date DESC     │
        │  LIMIT 10               │
        └─────────────────────────┘
                      │
                      ▼
        ┌─────────────────────────┐
        │  Is result empty?       │
        └─────────────────────────┘
                      │
           ┌──────────┴──────────┐
           │                     │
           ▼ YES                 ▼ NO
┌─────────────────────┐  ┌─────────────────────┐
│  Send "no history"  │  │  For each txn:      │
│  message            │  │  - Determine type   │
└─────────────────────┘  │  - Format message   │
           │             │  - Add time ago     │
           │             └─────────────────────┘
           │                     │
           │                     ▼
           │             ┌─────────────────────┐
           │             │  Combine all lines  │
           │             │  + current balance  │
           │             └─────────────────────┘
           │                     │
           │                     ▼
           │             ┌─────────────────────┐
           │             │  Send history       │
           │             │  message            │
           │             └─────────────────────┘
           │                     │
           └──────────┬──────────┘
                      │
                      ▼
                    [END]
```

---

## Atomic Operations

**IMPORTANT:** Balance updates must be atomic to prevent:
- Double spending
- Race conditions
- Data corruption

### What is atomic?
All steps happen together, or none happen.

### Example: Transfer
```
BEGIN TRANSACTION
  1. Check sender balance
  2. Subtract from sender
  3. Add to recipient
  4. Record transaction
COMMIT

If ANY step fails → ROLLBACK (undo all)
```

---

## Next: [06-VALIDATIONS.md](06-VALIDATIONS.md)
