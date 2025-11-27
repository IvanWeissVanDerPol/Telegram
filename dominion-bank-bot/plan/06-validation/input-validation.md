# Input Validation

## Amount Validation

### Rules
1. Must be a number
2. Must be integer (no decimals)
3. Must be positive (> 0)
4. Optional: max limit

### Valid
```
100  ✅
1    ✅
999999 ✅
```

### Invalid
```
0     ❌ "Debe ser mayor a 0"
-50   ❌ "Debe ser positivo"
10.5  ❌ "Debe ser entero"
abc   ❌ "Debe ser un número"
```

### Logic
```python
def validate_amount(input):
    if not input:
        return Error("Cantidad requerida")

    try:
        amount = int(input)
    except:
        return Error("Debe ser un número")

    if amount <= 0:
        return Error("Debe ser mayor a 0")

    return amount
```

---

## User Validation

### Ways to Specify User

| Method | Example | Resolution |
|--------|---------|------------|
| @mention | `@maria` | Lookup by username |
| Reply | (reply to message) | Get from replied message |
| User ID | `123456789` | Direct lookup |

### Resolution Logic
```python
def resolve_user(message):
    # Check reply
    if message.reply_to_message:
        return message.reply_to_message.from_user

    # Check @mention
    for entity in message.entities:
        if entity.type == "mention":
            username = extract_username(entity)
            return lookup_by_username(username)
        if entity.type == "text_mention":
            return entity.user

    return None
```

### Validation
```python
def validate_recipient(user, sender_id):
    if user is None:
        return Error("Usuario no encontrado")

    if user.is_bot:
        return Error("No puedes enviar a un bot")

    if user.id == sender_id:
        return Error("No puedes enviarte a ti mismo")

    return user
```

---

## Balance Validation

### For Transfers
```python
def validate_balance(user_id, amount):
    balance = get_balance(user_id)

    if balance < amount:
        return Error(
            f"Saldo insuficiente\n"
            f"Tu saldo: {balance}\n"
            f"Intentaste: {amount}\n"
            f"Te faltan: {amount - balance}"
        )

    return True
```

---

## Admin Validation

```python
ADMIN_IDS = [123456789, 987654321]

def is_admin(user_id):
    return user_id in ADMIN_IDS

# Decorator
def admin_only(handler):
    def wrapper(update, context):
        if not is_admin(update.effective_user.id):
            send_message("❌ No tienes permiso")
            return
        return handler(update, context)
    return wrapper
```
