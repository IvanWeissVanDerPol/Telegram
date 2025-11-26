# 06 - Validations

All validation rules and error handling.

---

## Input Validation Summary

| Input | Valid | Invalid |
|-------|-------|---------|
| Amount | `100`, `1`, `999999` | `0`, `-5`, `abc`, `10.5`, `` |
| Username | `@user`, reply to message | `user`, `@`, empty |
| User ID | Exists in DB or can resolve | Non-existent, bot |

---

## Amount Validation

### Rules
1. Must be a number
2. Must be an integer (no decimals)
3. Must be positive (> 0)
4. Must not exceed maximum (optional)

### Valid Examples
```
100       ✅
1         ✅
999999    ✅
1000000   ✅
```

### Invalid Examples
```
0         ❌  "Debe ser mayor a 0"
-50       ❌  "Debe ser positivo"
10.5      ❌  "Debe ser número entero"
abc       ❌  "Debe ser un número"
10,5      ❌  "Formato inválido"
""        ❌  "Cantidad requerida"
```

### Validation Function Logic
```
function validate_amount(input):

    1. Check if empty
       if input is empty → ERROR "Cantidad requerida"

    2. Try to convert to number
       if fails → ERROR "Debe ser un número"

    3. Check if integer
       if has decimals → ERROR "Debe ser número entero"

    4. Check if positive
       if <= 0 → ERROR "Debe ser mayor a 0"

    5. (Optional) Check maximum
       if > MAX_AMOUNT → ERROR "Cantidad muy alta"

    6. Return valid amount as integer
```

---

## User/Recipient Validation

### Ways to Specify a User

| Method | Example | How to Resolve |
|--------|---------|----------------|
| @mention | `@maria` | Look up by username |
| Reply | (reply to message) | Get user_id from replied message |
| User ID | `123456789` | Direct lookup |

### Validation Rules
1. User must be resolvable (found in DB or valid Telegram user)
2. User must not be a bot
3. User must not be the sender (for transfers)
4. User must exist or be creatable

### Resolution Flow
```
function resolve_user(input, message):

    1. Check if replying to a message
       if message.reply_to_message exists:
           return reply_to_message.from_user

    2. Check for @mention in message entities
       for entity in message.entities:
           if entity.type == "mention":
               username = extract @username
               return lookup_by_username(username)
           if entity.type == "text_mention":
               return entity.user

    3. Check if input is numeric (user_id)
       if input.is_numeric():
           return lookup_by_id(input)

    4. Nothing found
       return ERROR "Usuario no encontrado"
```

### Validation Function
```
function validate_recipient(user, sender_id):

    1. Check if user was found
       if user is None → ERROR "Usuario no encontrado"

    2. Check if user is a bot
       if user.is_bot → ERROR "No puedes enviar a un bot"

    3. Check if same as sender
       if user.id == sender_id → ERROR "No puedes enviarte a ti mismo"

    4. Return valid user
```

---

## Balance Validation

### For Transfers (sender must have enough)
```
function validate_sufficient_balance(user_id, amount):

    1. Get current balance
       balance = get_balance(user_id)

    2. Check if enough
       if balance < amount:
           ERROR "No tienes suficientes {{CURRENCY_NAME}}"
           + show current balance
           + show attempted amount
           + show difference needed

    3. Return OK
```

### For Admin Remove (optional: allow setting to 0)
```
function validate_removable_amount(user_id, amount, allow_overdraft):

    balance = get_balance(user_id)

    if allow_overdraft:
        # Just remove whatever they have
        actual_amount = min(balance, amount)
        return actual_amount
    else:
        # Strict: must have enough
        if balance < amount:
            ERROR "Usuario solo tiene X"
        return amount
```

---

## Admin Validation

### How Admins Are Defined
```
# In config/settings.py or .env
ADMIN_IDS = [123456789, 987654321, ...]
```

### Validation Function
```
function is_admin(user_id):
    return user_id in ADMIN_IDS
```

### Decorator Pattern (for handlers)
```
@admin_only
def admin_add_command(update, context):
    # This code only runs if user is admin
    # Otherwise, error message is sent automatically
```

### Decorator Implementation Logic
```
function admin_only(handler_function):

    function wrapper(update, context):
        user_id = update.effective_user.id

        if user_id not in ADMIN_IDS:
            send_message("❌ No tienes permiso")
            return  # Stop here

        # User is admin, continue
        return handler_function(update, context)

    return wrapper
```

---

## Command Parsing

### Expected Formats
```
/servir @user 100
/servir 100           (when replying)
/recompensar @user 500
/castigar @user 200
```

### Parsing Logic
```
function parse_transfer_command(message):

    text = message.text
    parts = text.split()

    # /servir @user 100
    # parts[0] = "/servir"
    # parts[1] = "@user" (maybe)
    # parts[2] = "100" (maybe)

    # Case 1: Replying to message
    if message.reply_to_message:
        recipient = message.reply_to_message.from_user
        amount = parts[1] if len(parts) > 1 else None
        return (recipient, amount)

    # Case 2: @mention
    if len(parts) >= 3:
        recipient = resolve_mention(parts[1])
        amount = parts[2]
        return (recipient, amount)

    # Case 3: Not enough arguments
    return ERROR "Uso: /servir @usuario cantidad"
```

---

## Error Handling Strategy

### Levels of Errors

| Level | Example | Response |
|-------|---------|----------|
| User error | Invalid amount | Friendly message + how to fix |
| Not found | User doesn't exist | Helpful message |
| Permission | Non-admin uses admin cmd | Clear denial |
| System error | Database down | Apologize + suggest retry |

### Error Response Format
```
❌ [Error title]

[Explanation]

[How to fix / Example]
```

### Example Error Responses

**Invalid Amount:**
```
❌ Cantidad inválida

La cantidad debe ser un número entero positivo.

✅ Ejemplo: /servir @maria 100
```

**Insufficient Balance:**
```
❌ No tienes suficientes {{CURRENCY_NAME}}

Tu saldo: 50 {{CURRENCY_NAME}}
Intentaste enviar: 100 {{CURRENCY_NAME}}
Te faltan: 50 {{CURRENCY_NAME}}
```

**User Not Found:**
```
❌ Usuario no encontrado

Asegúrate de:
• Usar @ antes del nombre (@maria)
• Que el usuario haya interactuado con el bot
• O responder a uno de sus mensajes
```

---

## Edge Cases

| Case | How to Handle |
|------|---------------|
| User sends `/servir` with no args | Show usage |
| User sends `/servir @user` (no amount) | Show usage |
| User mentions themselves | "No puedes enviarte a ti mismo" |
| User mentions the bot | "No puedes enviar a un bot" |
| Amount is `0` | "Cantidad debe ser mayor a 0" |
| Amount is negative | "Cantidad debe ser positiva" |
| Amount has decimals | "Cantidad debe ser entera" |
| Amount is extremely large | Accept (or set max limit) |
| User doesn't exist in DB | Create on first mention |
| @username changed | Store user_id, update username |
| User has no username | Use first_name for display |

---

## Validation Checklist by Command

### /servir
- [ ] Amount is valid integer > 0
- [ ] Recipient is specified (@ or reply)
- [ ] Recipient is found
- [ ] Recipient is not sender
- [ ] Recipient is not a bot
- [ ] Sender has sufficient balance

### /recompensar
- [ ] Sender is admin
- [ ] Amount is valid integer > 0
- [ ] Recipient is specified
- [ ] Recipient is found/creatable

### /castigar
- [ ] Sender is admin
- [ ] Amount is valid integer > 0
- [ ] Recipient is specified
- [ ] Recipient is found
- [ ] Recipient has balance (or handle gracefully)

---

## Next: [07-SETUP.md](07-SETUP.md)
