# 10 - Commands Detail

## 🎭 The Phantom Bot - Complete Command List

---

## Command Summary

### User Commands (Everyone)

| Command | Description | Example |
|---------|-------------|---------|
| `/start` | Welcome + register | `/start` |
| `/help` | Show all commands | `/help` |
| `/ver` | Check your balance | `/ver` |
| `/dar` | Transfer SadoCoins | `/dar @maria 100` |
| `/ranking` | Top users leaderboard | `/ranking` |
| `/historial` | Your transaction history | `/historial` |

### Admin Commands (Admins Only)

| Command | Description | Example |
|---------|-------------|---------|
| `/dar_admin` | Give SadoCoins to user | `/dar_admin @juan 500` |
| `/quitar` | Remove SadoCoins from user | `/quitar @pedro 200` |
| `/saldo` | Check anyone's balance | `/saldo @maria` |
| `/reset` | Reset user to 0 | `/reset @juan` |
| `/broadcast` | Message all users | `/broadcast Hola a todos!` |

### Super Admin Commands (Owner Only)

| Command | Description | Example |
|---------|-------------|---------|
| `/addadmin` | Make user an admin | `/addadmin @maria` |
| `/removeadmin` | Remove admin role | `/removeadmin @pedro` |
| `/stats` | Bot statistics | `/stats` |
| `/backup` | Export database | `/backup` |

---

## Detailed Command Specifications

---

## `/start`

### Purpose
Welcome new users, register them in the database, show instructions.

### Usage
```
/start
```

### Who can use
Everyone

### Behavior
1. Check if user exists in database
2. If new → Create user with 0 SadoCoins
3. Send welcome message

### Response
```
🎭 Bienvenido/a a The Phantom!

Tu wallet secreta de SadoCoins ⛓️

📜 Comandos:
/ver - Tu saldo
/dar @user cantidad - Enviar SadoCoins
/ranking - Top usuarios
/historial - Tus movimientos
/help - Ayuda completa

⛓️ Tu saldo: 0 SadoCoins
```

---

## `/help`

### Purpose
Show complete command list with explanations.

### Usage
```
/help
/help dar
/help admin
```

### Who can use
Everyone (admin section only visible to admins)

### Response - General
```
🎭 The Phantom - Ayuda

👤 COMANDOS DE USUARIO:
/ver - Ver tu saldo actual
/dar @user 100 - Enviar SadoCoins
/ranking - Ver top 10 usuarios
/historial - Ver tus últimas transacciones

💡 Ejemplos:
• /dar @maria 50
• /dar 100 (respondiendo a un mensaje)

¿Necesitas más ayuda? Escribe /help [comando]
```

### Response - Specific Command
```
/help dar

📖 Comando: /dar

Envía SadoCoins a otro usuario.

✅ Formas de usar:
• /dar @usuario 100
• /dar 100 (respondiendo a un mensaje)

❌ No puedes:
• Enviarte a ti mismo
• Enviar más de lo que tienes
• Enviar cantidades negativas o 0

Ejemplo: /dar @maria 50
```

---

## `/ver`

### Purpose
Show user's current SadoCoin balance.

### Usage
```
/ver
```

### Who can use
Everyone

### Behavior
1. Get user from database (create if not exists)
2. Return formatted balance

### Response - Has Balance
```
⛓️ Tu saldo: 500 SadoCoins

📊 Ranking: #5 de 47 usuarios
```

### Response - Zero Balance
```
⛓️ Tu saldo: 0 SadoCoins

Aún no tienes SadoCoins.
Espera a que un admin te recompense o que alguien te envíe.
```

---

## `/dar`

### Purpose
Transfer SadoCoins from your account to another user.

### Usage
```
/dar @username cantidad
/dar cantidad                (replying to a message)
```

### Who can use
Everyone

### Examples
```
/dar @maria 100
/dar @juan 50
/dar 200                     (while replying to someone)
```

### Behavior
1. Parse recipient and amount
2. Validate amount (positive integer)
3. Check sender has enough balance
4. Check not sending to self
5. Check recipient is not a bot
6. Transfer coins
7. Record transaction
8. Notify both users

### Response - Success (to sender)
```
✅ Transferencia exitosa

⛓️ Enviaste 100 SadoCoins a @maria
💰 Tu nuevo saldo: 400 SadoCoins
```

### Response - Success (notification to recipient)
```
🎁 Has recibido SadoCoins!

⛓️ @juan te envió 100 SadoCoins
💰 Tu nuevo saldo: 150 SadoCoins
```

### Error Responses

**Not enough balance:**
```
❌ Saldo insuficiente

Tu saldo: 50 SadoCoins
Intentaste enviar: 100 SadoCoins
Te faltan: 50 SadoCoins
```

**Self transfer:**
```
❌ No puedes enviarte SadoCoins a ti mismo
```

**Invalid amount:**
```
❌ Cantidad inválida

La cantidad debe ser un número entero positivo.
Ejemplo: /dar @maria 100
```

**User not found:**
```
❌ Usuario no encontrado

Asegúrate de:
• Mencionar con @usuario
• Que haya usado el bot antes
• O responder a su mensaje
```

**Missing arguments:**
```
❌ Formato incorrecto

Uso: /dar @usuario cantidad
Ejemplo: /dar @maria 100

O responde a un mensaje con: /dar 100
```

---

## `/ranking`

### Purpose
Show leaderboard of users with most SadoCoins.

### Usage
```
/ranking
/ranking 20        (show top 20)
```

### Who can use
Everyone

### Response
```
🏆 Ranking de SadoCoins

1. 👑 @carlos — 2,500 ⛓️
2. 🥈 @maria — 1,800 ⛓️
3. 🥉 @juan — 1,200 ⛓️
4. @ana — 950 ⛓️
5. @pedro — 800 ⛓️
6. @lucia — 650 ⛓️
7. @diego — 500 ⛓️
8. @sofia — 350 ⛓️
9. @pablo — 200 ⛓️
10. @elena — 100 ⛓️

━━━━━━━━━━━━━━━━━━━━
📍 Tu posición: #7 con 500 SadoCoins
```

### Response - Empty
```
🏆 Ranking de SadoCoins

Aún no hay usuarios con SadoCoins.
¡Sé el primero en recibirlos!
```

---

## `/historial`

### Purpose
Show user's recent transaction history.

### Usage
```
/historial
/historial 20      (show last 20)
```

### Who can use
Everyone

### Response
```
📜 Tu historial de SadoCoins

1. ➡️ -100 → @maria (hace 2h)
2. ⬅️ +50 ← @pedro (hace 5h)
3. 🎁 +500 Admin (hace 1d)
4. ➡️ -200 → @juan (hace 2d)
5. 😈 -100 Admin (hace 3d)

━━━━━━━━━━━━━━━━━━━━
💰 Saldo actual: 650 SadoCoins
```

### Transaction Icons
| Icon | Meaning |
|------|---------|
| ➡️ | You sent |
| ⬅️ | You received |
| 🎁 | Admin gave you |
| 😈 | Admin took from you |

### Response - Empty
```
📜 Tu historial de SadoCoins

No tienes transacciones aún.
```

---

# ADMIN COMMANDS

---

## `/dar_admin`

### Purpose
Admin gives SadoCoins to a user (minting).

### Usage
```
/dar_admin @username cantidad
/dar_admin @username cantidad motivo
```

### Who can use
**Admins only**

### Examples
```
/dar_admin @maria 500
/dar_admin @juan 1000 Premio por evento
```

### Behavior
1. Verify sender is admin
2. Parse recipient and amount
3. Create recipient if not exists
4. Add coins to recipient
5. Record transaction with admin ID
6. Notify recipient

### Response - Success (to admin)
```
✅ SadoCoins entregados

⛓️ +500 SadoCoins → @maria
💰 Su nuevo saldo: 800 SadoCoins
```

### Response - Notification to user
```
🎁 Has recibido SadoCoins!

⛓️ Un admin te ha dado 500 SadoCoins
💰 Tu nuevo saldo: 800 SadoCoins
```

### Error - Not admin
```
❌ No tienes permiso para usar este comando
```

---

## `/quitar`

### Purpose
Admin removes SadoCoins from a user (burning).

### Usage
```
/quitar @username cantidad
/quitar @username cantidad motivo
```

### Who can use
**Admins only**

### Examples
```
/quitar @pedro 200
/quitar @juan 100 Penalización
```

### Behavior
1. Verify sender is admin
2. Parse recipient and amount
3. Check recipient exists
4. Check recipient has enough (or set to 0)
5. Remove coins
6. Record transaction
7. Notify user

### Response - Success
```
😈 SadoCoins quitados

⛓️ -200 SadoCoins ← @pedro
💰 Su nuevo saldo: 300 SadoCoins
```

### Response - User doesn't have enough
```
⚠️ @pedro solo tiene 50 SadoCoins

¿Quitar todo? Usa: /quitar @pedro 50
O usa: /reset @pedro
```

### Response - Notification to user
```
😈 Te han quitado SadoCoins

⛓️ Un admin te quitó 200 SadoCoins
💰 Tu nuevo saldo: 300 SadoCoins
```

---

## `/saldo`

### Purpose
Admin checks any user's balance and info.

### Usage
```
/saldo @username
```

### Who can use
**Admins only**

### Response
```
📊 Info de @maria

💰 Saldo: 800 SadoCoins
📍 Ranking: #3 de 47
📅 Registro: hace 30 días
🕐 Última actividad: hace 2 horas
📈 Total recibido: 1,500 SadoCoins
📉 Total enviado: 700 SadoCoins
```

---

## `/reset`

### Purpose
Reset a user's balance to 0.

### Usage
```
/reset @username
```

### Who can use
**Admins only**

### Response
```
🔄 Usuario reseteado

@pedro ahora tiene 0 SadoCoins
(Tenía 500 SadoCoins)
```

---

## `/broadcast`

### Purpose
Send a message to all users who have used the bot.

### Usage
```
/broadcast Tu mensaje aquí
```

### Who can use
**Admins only**

### Response
```
📢 Broadcast enviado

Mensaje enviado a 47 usuarios.
```

---

# SUPER ADMIN COMMANDS

---

## `/addadmin`

### Purpose
Grant admin privileges to a user.

### Usage
```
/addadmin @username
```

### Who can use
**Super Admin only** (configured in .env)

### Response
```
✅ Admin agregado

@maria ahora es administrador
```

---

## `/removeadmin`

### Purpose
Revoke admin privileges from a user.

### Usage
```
/removeadmin @username
```

### Who can use
**Super Admin only**

### Response
```
✅ Admin removido

@pedro ya no es administrador
```

---

## `/stats`

### Purpose
Show bot statistics.

### Usage
```
/stats
```

### Who can use
**Super Admin only**

### Response
```
📊 Estadísticas de The Phantom

👥 Usuarios totales: 47
💰 SadoCoins en circulación: 25,000
📈 Transacciones hoy: 15
📅 Transacciones total: 342
🏆 Usuario más rico: @carlos (2,500)
📊 Promedio por usuario: 531 SadoCoins
```

---

## `/backup`

### Purpose
Export database to file.

### Usage
```
/backup
```

### Who can use
**Super Admin only**

### Response
Bot sends a file: `phantom_backup_2024-01-20.db`

---

## Command Access Summary

| Command | Users | Admins | Super Admin |
|---------|:-----:|:------:|:-----------:|
| `/start` | ✅ | ✅ | ✅ |
| `/help` | ✅ | ✅ | ✅ |
| `/ver` | ✅ | ✅ | ✅ |
| `/dar` | ✅ | ✅ | ✅ |
| `/ranking` | ✅ | ✅ | ✅ |
| `/historial` | ✅ | ✅ | ✅ |
| `/dar_admin` | ❌ | ✅ | ✅ |
| `/quitar` | ❌ | ✅ | ✅ |
| `/saldo` | ❌ | ✅ | ✅ |
| `/reset` | ❌ | ✅ | ✅ |
| `/broadcast` | ❌ | ✅ | ✅ |
| `/addadmin` | ❌ | ❌ | ✅ |
| `/removeadmin` | ❌ | ❌ | ✅ |
| `/stats` | ❌ | ❌ | ✅ |
| `/backup` | ❌ | ❌ | ✅ |

---

## Ideas for Future Commands

| Command | Description | Priority |
|---------|-------------|----------|
| `/apostar` | Bet SadoCoins (gambling) | Optional |
| `/tienda` | Buy items with SadoCoins | Optional |
| `/daily` | Daily reward | Optional |
| `/gift` | Anonymous transfer | Optional |
| `/loan` | Request loan from admin | Optional |
| `/convert` | Convert to other currency | Optional |

---

## Pending Decisions

1. **Notification preference**: Should users receive DM notifications for transfers?
2. **Broadcast limit**: How often can admins broadcast?
3. **Reset confirmation**: Require confirmation before reset?
4. **Negative balance**: Allow admin to set negative? (debt)
5. **Transfer limits**: Max transfer per day?

---

## Next Steps

Review this command list and let me know:
1. Any commands to **add**?
2. Any commands to **remove**?
3. Any commands to **rename**?
4. Any behavior to **change**?
