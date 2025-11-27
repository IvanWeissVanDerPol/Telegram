# Admin Logic Flows

## Flow: /dar_admin (Give Coins)

```
Admin sends /dar_admin @user 500
    │
    ▼
Is sender in ADMIN_IDS?
    │
    ├─NO──► Send "not authorized" error
    │
    ▼
Parse: recipient, amount
    │
    ▼
Validate amount
    │
    ├─INVALID─► Send error
    │
    ▼
Get or create recipient
    │
    ▼
Add to recipient balance
    │
    ▼
Record transaction (type: admin_add)
    │
    ▼
Confirm to admin
    │
    ▼
Notify recipient (DM)
```

---

## Flow: /quitar (Remove Coins)

```
Admin sends /quitar @user 200
    │
    ▼
Is sender admin?
    │
    ├─NO──► Send "not authorized"
    │
    ▼
Parse & validate
    │
    ▼
Find recipient
    │
    ├─NOT FOUND─► Send error
    │
    ▼
Recipient balance >= amount?
    │
    ├─NO──► Allow going negative (DEBT)
    │
    ▼
Subtract from balance
    │
    ▼
Record transaction (type: admin_remove)
    │
    ▼
Confirm to admin
    │
    ▼
If now in debt: flag user
    │
    ▼
Notify user (DM)
```

---

## Flow: Import from Excel

```
Admin sends /importar + file
    │
    ▼
Is sender admin?
    │
    ├─NO──► Send error
    │
    ▼
Download file
    │
    ▼
Validate format (xlsx/csv)
    │
    ├─INVALID─► Send error
    │
    ▼
Parse rows
    │
    ▼
Validate each row:
    ├── Username format
    ├── Amount valid
    └── Type valid (add/remove/set)
    │
    ▼
Show preview + totals
    │
    ▼
Wait for "SI" confirmation
    │
    ▼
BEGIN TRANSACTION
    │
    For each row:
    ├── Get or create user
    ├── Apply change
    └── Record transaction
    │
COMMIT
    │
    ▼
Create import record (for rollback)
    │
    ▼
Send summary
    │
    ▼
Optionally notify users
```
