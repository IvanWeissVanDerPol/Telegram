# Atomic Operations

## Why Atomic?

Prevents:
- Double spending
- Race conditions
- Data corruption

---

## Principle

All steps happen together, or none happen.

```
BEGIN TRANSACTION
    1. Check sender balance ─► if fail: ROLLBACK
    2. Subtract from sender ─► if fail: ROLLBACK
    3. Add to recipient ────► if fail: ROLLBACK
    4. Record transaction ──► if fail: ROLLBACK
COMMIT
```

---

## Transfer (Atomic)

```python
def transfer(sender_id, recipient_id, amount):
    with db.transaction():
        # Step 1: Check
        sender = get_user(sender_id)
        if sender.balance < amount:
            raise InsufficientBalance()

        # Step 2: Subtract
        update_balance(sender_id, sender.balance - amount)

        # Step 3: Add
        recipient = get_user(recipient_id)
        update_balance(recipient_id, recipient.balance + amount)

        # Step 4: Record
        create_transaction(
            type='transfer',
            from_id=sender_id,
            to_id=recipient_id,
            amount=amount
        )

    # Only reaches here if ALL steps succeeded
    return True
```

---

## Import (Atomic per batch)

```python
def import_transactions(rows):
    with db.transaction():
        import_id = create_import_record()

        for row in rows:
            user = get_or_create_user(row.username)

            if row.type == 'add':
                update_balance(user.id, user.balance + row.amount)
            elif row.type == 'remove':
                update_balance(user.id, user.balance - row.amount)
            elif row.type == 'set':
                update_balance(user.id, row.amount)

            create_transaction(
                type=f'import_{row.type}',
                to_id=user.id,
                amount=row.amount,
                import_id=import_id
            )

        return import_id
```

---

## Rollback Import

```python
def rollback_import(import_id):
    with db.transaction():
        transactions = get_transactions_by_import(import_id)

        for txn in transactions:
            # Reverse each transaction
            if txn.type == 'import_add':
                user = get_user(txn.to_id)
                update_balance(txn.to_id, user.balance - txn.amount)
            elif txn.type == 'import_remove':
                user = get_user(txn.from_id)
                update_balance(txn.from_id, user.balance + txn.amount)

        mark_import_rolled_back(import_id)
```

---

## Error Recovery

If something fails mid-operation:

| Scenario | Action |
|----------|--------|
| DB connection lost | Transaction auto-rollback |
| Code exception | Transaction auto-rollback |
| Bot crashes | Transaction not committed |
| Partial success | Full rollback |

SQLite and PostgreSQL both support this with proper transaction handling.
