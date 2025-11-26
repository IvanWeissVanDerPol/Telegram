# 03 - Commands Documentation

---

## Command Overview

| Command | Type | Description |
|---------|------|-------------|
| `/start` | User | Welcome message, register user |
| `/micollar` | User | Check your balance |
| `/servir` | User | Transfer {{CURRENCY_NAME}} to another user |
| `/calabozo` | User | See ranking of top users |
| `/marcas` | User | See your transaction history |
| `/recompensar` | Admin | Add {{CURRENCY_NAME}} to a user |
| `/castigar` | Admin | Remove {{CURRENCY_NAME}} from a user |
| `/versaldo` | Admin | Check any user's balance |

---

## Command: `/start`

### Purpose
Welcome new users and register them in the database.

### Usage
```
/start
```

### Who can use it
Everyone

### What it does
1. Check if user exists in database
2. If NOT exists → Create new user with 0 balance
3. If exists → Just show welcome message
4. Send welcome message with instructions

### Input
None

### Output
```
🖤 Bienvenido/a a {{BOT_NAME}}!

Tu wallet de {{CURRENCY_NAME}} para el grupo.

Comandos disponibles:
• /micollar - Ver tu saldo
• /servir @usuario cantidad - Transferir
• /calabozo - Ver ranking
• /marcas - Tu historial

Tu saldo actual: 0 {{CURRENCY_NAME}}
```

### Database changes
- INSERT new user if not exists
- No transaction recorded (not a coin movement)

---

## Command: `/micollar`

### Purpose
Show user their current balance.

### Usage
```
/micollar
```

### Who can use it
Everyone

### What it does
1. Get user from database (or create if not exists)
2. Return their balance

### Input
None

### Output - Success
```
🖤 Tu collar vale: 500 {{CURRENCY_NAME}}
```

### Output - New user
```
🖤 Tu collar vale: 0 {{CURRENCY_NAME}}

Aún no tienes {{CURRENCY_NAME}}. Un admin puede darte con /recompensar
```

### Database changes
- May INSERT new user if first interaction
- No balance changes

---

## Command: `/servir`

### Purpose
Transfer {{CURRENCY_NAME}} from your account to another user.

### Usage
```
/servir @username cantidad
/servir @maria 100
```

### Who can use it
Everyone

### What it does
1. Parse command arguments (recipient, amount)
2. Validate inputs
3. Check sender has enough balance
4. Check not sending to self
5. Subtract from sender
6. Add to recipient
7. Record transaction
8. Confirm to both users

### Input
| Parameter | Required | Type | Example |
|-----------|----------|------|---------|
| @recipient | Yes | @username or reply | `@maria` |
| amount | Yes | Positive integer | `100` |

### Alternative: Reply to message
```
(reply to someone's message)
/servir 100
```

### Validation Rules
| Rule | Error if violated |
|------|-------------------|
| Amount must be positive integer | "❌ La cantidad debe ser un número positivo" |
| Amount must be > 0 | "❌ La cantidad debe ser mayor a 0" |
| Sender must have enough balance | "❌ No tienes suficientes {{CURRENCY_NAME}}" |
| Can't send to yourself | "❌ No puedes enviarte {{CURRENCY_NAME}} a ti mismo" |
| Recipient must be valid user | "❌ Usuario no encontrado" |

### Output - Success
```
✅ Has servido 100 {{CURRENCY_NAME}} a @maria

Tu nuevo saldo: 400 {{CURRENCY_NAME}}
```

### Output - Insufficient funds
```
❌ No tienes suficientes {{CURRENCY_NAME}}

Tu saldo: 50 {{CURRENCY_NAME}}
Intentaste enviar: 100 {{CURRENCY_NAME}}
```

### Output - Invalid usage
```
❌ Uso correcto: /servir @usuario cantidad

Ejemplo: /servir @maria 100
```

### Database changes
- UPDATE sender balance (subtract)
- UPDATE recipient balance (add)
- INSERT transaction record (type: 'transfer')

### Notification to recipient
```
🎁 @franco te ha enviado 100 {{CURRENCY_NAME}}

Tu nuevo saldo: 200 {{CURRENCY_NAME}}
```

---

## Command: `/calabozo`

### Purpose
Show ranking of users with most {{CURRENCY_NAME}}.

### Usage
```
/calabozo
```

### Who can use it
Everyone

### What it does
1. Query database for top 10 users by balance
2. Format as leaderboard
3. Show user's own position if not in top 10

### Input
None

### Output
```
🏆 Calabozo de {{CURRENCY_NAME}}

1. 👑 @franco — 1,500
2. 🥈 @maria — 800
3. 🥉 @pedro — 650
4. @juan — 400
5. @ana — 350
6. @luis — 200
7. @carmen — 150
8. @diego — 100
9. @sofia — 50
10. @pablo — 25

Tu posición: #4 con 400 {{CURRENCY_NAME}}
```

### Database changes
None (read only)

---

## Command: `/marcas`

### Purpose
Show user's transaction history.

### Usage
```
/marcas
/marcas 20
```

### Who can use it
Everyone

### What it does
1. Get user's recent transactions (default: 10)
2. Format each transaction
3. Show summary

### Input
| Parameter | Required | Type | Default |
|-----------|----------|------|---------|
| limit | No | Integer 1-50 | 10 |

### Output
```
📜 Tus últimas marcas:

1. ➡️ Enviaste 100 a @maria (hace 2h)
2. ⬅️ Recibiste 50 de @pedro (hace 1d)
3. 🎁 Admin te dio 500 (hace 3d)
4. ➡️ Enviaste 200 a @juan (hace 5d)
5. 😈 Admin te quitó 50 (hace 1w)

Saldo actual: 400 {{CURRENCY_NAME}}
```

### Transaction display format
| Type | Icon | Format |
|------|------|--------|
| transfer (sent) | ➡️ | "Enviaste X a @user" |
| transfer (received) | ⬅️ | "Recibiste X de @user" |
| admin_add | 🎁 | "Admin te dio X" |
| admin_remove | 😈 | "Admin te quitó X" |

### Database changes
None (read only)

---

## Command: `/recompensar` (Admin)

### Purpose
Add {{CURRENCY_NAME}} to a user's balance. (Mint coins)

### Usage
```
/recompensar @username cantidad
/recompensar @maria 500
```

### Who can use it
**Admins only** (user_id in ADMIN_IDS list)

### What it does
1. Check if sender is admin
2. Parse arguments
3. Add coins to recipient
4. Record transaction
5. Confirm

### Input
| Parameter | Required | Type | Example |
|-----------|----------|------|---------|
| @recipient | Yes | @username or reply | `@maria` |
| amount | Yes | Positive integer | `500` |

### Validation Rules
| Rule | Error if violated |
|------|-------------------|
| Sender must be admin | "❌ No tienes permiso para usar este comando" |
| Amount must be positive | "❌ La cantidad debe ser un número positivo" |
| Recipient must exist or be valid | Creates user if not exists |

### Output - Success
```
✅ Has recompensado a @maria con 500 {{CURRENCY_NAME}}

Su nuevo saldo: 800 {{CURRENCY_NAME}}
```

### Output - Not admin
```
❌ No tienes permiso para usar este comando
```

### Database changes
- UPDATE recipient balance (add)
- May INSERT recipient if not exists
- INSERT transaction record (type: 'admin_add')

### Notification to recipient
```
🎁 Un admin te ha recompensado con 500 {{CURRENCY_NAME}}

Tu nuevo saldo: 800 {{CURRENCY_NAME}}
```

---

## Command: `/castigar` (Admin)

### Purpose
Remove {{CURRENCY_NAME}} from a user's balance. (Burn coins)

### Usage
```
/castigar @username cantidad
/castigar @pedro 200
```

### Who can use it
**Admins only**

### What it does
1. Check if sender is admin
2. Parse arguments
3. Check user has enough to remove (optional: allow going to 0)
4. Remove coins from user
5. Record transaction
6. Confirm

### Input
| Parameter | Required | Type | Example |
|-----------|----------|------|---------|
| @victim | Yes | @username or reply | `@pedro` |
| amount | Yes | Positive integer | `200` |

### Validation Rules
| Rule | Error if violated |
|------|-------------------|
| Sender must be admin | "❌ No tienes permiso" |
| Amount must be positive | "❌ Cantidad inválida" |
| User must exist | "❌ Usuario no encontrado" |

### Behavior: Insufficient balance
**Option A:** Reject if user doesn't have enough
```
❌ @pedro solo tiene 50 {{CURRENCY_NAME}}, no puedes quitar 200
```

**Option B:** Remove what they have (set to 0)
```
⚠️ @pedro solo tenía 50 {{CURRENCY_NAME}}, se le quitaron todos

Su nuevo saldo: 0 {{CURRENCY_NAME}}
```

**DECISION NEEDED:** Which behavior? ____________________

### Output - Success
```
😈 Has castigado a @pedro quitándole 200 {{CURRENCY_NAME}}

Su nuevo saldo: 150 {{CURRENCY_NAME}}
```

### Database changes
- UPDATE victim balance (subtract)
- INSERT transaction record (type: 'admin_remove')

### Notification to victim
```
😈 Un admin te ha castigado quitándote 200 {{CURRENCY_NAME}}

Tu nuevo saldo: 150 {{CURRENCY_NAME}}
```

---

## Command: `/versaldo` (Admin)

### Purpose
Check any user's balance (admin only).

### Usage
```
/versaldo @username
/versaldo @maria
```

### Who can use it
**Admins only**

### What it does
1. Check if sender is admin
2. Find user in database
3. Return their balance and stats

### Output
```
📊 Información de @maria:

Saldo: 800 {{CURRENCY_NAME}}
Posición: #2 de 45 usuarios
Registrado: hace 30 días
Última actividad: hace 2 horas
```

### Database changes
None (read only)

---

## Error Messages Summary

| Error | Message |
|-------|---------|
| Invalid amount | "❌ La cantidad debe ser un número positivo" |
| Insufficient balance | "❌ No tienes suficientes {{CURRENCY_NAME}}" |
| Self transfer | "❌ No puedes enviarte a ti mismo" |
| User not found | "❌ Usuario no encontrado" |
| Not admin | "❌ No tienes permiso para usar este comando" |
| Missing arguments | "❌ Uso: /comando @usuario cantidad" |
| Bot mentioned | "❌ No puedes enviar {{CURRENCY_NAME}} a un bot" |

---

## Next: [04-MESSAGES.md](04-MESSAGES.md)
