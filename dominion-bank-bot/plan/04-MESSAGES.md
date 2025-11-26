# 04 - Message Templates

All bot messages in one place. Easy to customize!

---

## Variables Available

These variables get replaced with real values:

| Variable | Description | Example |
|----------|-------------|---------|
| `{user}` | Username or first name | `@franco` or `Franco` |
| `{amount}` | Number of coins | `500` |
| `{balance}` | Current balance | `1,200` |
| `{recipient}` | Who received | `@maria` |
| `{sender}` | Who sent | `@pedro` |
| `{position}` | Ranking position | `#3` |
| `{total_users}` | Total users count | `45` |
| `{currency}` | Currency name | `{{CURRENCY_NAME}}` |

---

## Welcome Messages

### MSG_WELCOME (on /start)
```
🖤 Bienvenido/a a {{BOT_NAME}}!

Tu wallet de {currency} para el grupo.

📜 Comandos disponibles:
• /micollar - Ver tu saldo
• /servir @usuario cantidad - Transferir
• /calabozo - Ver ranking
• /marcas - Tu historial

💰 Tu saldo actual: {balance} {currency}
```

### MSG_WELCOME_RETURNING (existing user)
```
🖤 Hola de nuevo, {user}!

💰 Tu saldo: {balance} {currency}

Escribe /micollar para ver tu saldo completo.
```

---

## Balance Messages

### MSG_BALANCE
```
🖤 Tu collar vale: {balance} {currency}
```

### MSG_BALANCE_ZERO
```
🖤 Tu collar vale: 0 {currency}

Aún no tienes {currency}.
Pide a un admin que te recompense o que otro usuario te envíe.
```

### MSG_BALANCE_ADMIN_CHECK
```
📊 Saldo de {user}: {balance} {currency}

Posición: {position} de {total_users}
```

---

## Transfer Messages

### MSG_TRANSFER_SUCCESS (to sender)
```
✅ Has servido {amount} {currency} a {recipient}

💰 Tu nuevo saldo: {balance} {currency}
```

### MSG_TRANSFER_RECEIVED (to recipient)
```
🎁 {sender} te ha enviado {amount} {currency}

💰 Tu nuevo saldo: {balance} {currency}
```

### MSG_TRANSFER_INSUFFICIENT
```
❌ No tienes suficientes {currency}

Tu saldo: {balance} {currency}
Intentaste enviar: {amount} {currency}
Te faltan: {missing} {currency}
```

### MSG_TRANSFER_SELF
```
❌ No puedes enviarte {currency} a ti mismo

¿Intentabas enviar a alguien más?
```

### MSG_TRANSFER_USAGE
```
❌ Formato incorrecto

✅ Uso: /servir @usuario cantidad
📝 Ejemplo: /servir @maria 100

También puedes responder a un mensaje:
↩️ (responde a alguien) /servir 100
```

---

## Admin Messages

### MSG_ADMIN_ADD_SUCCESS
```
✅ Has recompensado a {recipient} con {amount} {currency}

💰 Su nuevo saldo: {balance} {currency}
```

### MSG_ADMIN_ADD_RECEIVED (notification to user)
```
🎁 ¡Has sido recompensado/a!

Un admin te ha dado {amount} {currency}

💰 Tu nuevo saldo: {balance} {currency}
```

### MSG_ADMIN_REMOVE_SUCCESS
```
😈 Has castigado a {recipient} quitándole {amount} {currency}

💰 Su nuevo saldo: {balance} {currency}
```

### MSG_ADMIN_REMOVE_RECEIVED (notification to user)
```
😈 Has sido castigado/a

Un admin te ha quitado {amount} {currency}

💰 Tu nuevo saldo: {balance} {currency}
```

### MSG_ADMIN_NOT_ENOUGH (if user doesn't have enough to remove)
```
⚠️ {user} solo tiene {balance} {currency}

¿Quitar todo su saldo?
Usa: /castigar {user} {balance}
```

---

## Ranking Messages

### MSG_RANKING_HEADER
```
🏆 Calabozo de {currency}
━━━━━━━━━━━━━━━━━━━━
```

### MSG_RANKING_ROW (for each user)
```
{position}. {medal} {user} — {balance}
```

### MSG_RANKING_MEDALS
| Position | Medal |
|----------|-------|
| 1 | 👑 |
| 2 | 🥈 |
| 3 | 🥉 |
| 4-10 | (none) |

### MSG_RANKING_FOOTER
```
━━━━━━━━━━━━━━━━━━━━
Tu posición: {position} con {balance} {currency}
```

### MSG_RANKING_EMPTY
```
🏆 Calabozo de {currency}

Aún no hay usuarios con {currency}.
¡Sé el primero!
```

---

## History Messages

### MSG_HISTORY_HEADER
```
📜 Tus últimas marcas:
━━━━━━━━━━━━━━━━━━━━
```

### MSG_HISTORY_SENT
```
➡️ Enviaste {amount} a {recipient} ({time_ago})
```

### MSG_HISTORY_RECEIVED
```
⬅️ Recibiste {amount} de {sender} ({time_ago})
```

### MSG_HISTORY_ADMIN_ADD
```
🎁 Admin te dio {amount} ({time_ago})
```

### MSG_HISTORY_ADMIN_REMOVE
```
😈 Admin te quitó {amount} ({time_ago})
```

### MSG_HISTORY_FOOTER
```
━━━━━━━━━━━━━━━━━━━━
💰 Saldo actual: {balance} {currency}
```

### MSG_HISTORY_EMPTY
```
📜 Tu historial está vacío

Aún no tienes transacciones.
```

---

## Error Messages

### MSG_ERROR_NOT_ADMIN
```
❌ No tienes permiso para usar este comando

Este comando es solo para administradores.
```

### MSG_ERROR_INVALID_AMOUNT
```
❌ Cantidad inválida

La cantidad debe ser un número positivo.
Ejemplo: 100
```

### MSG_ERROR_USER_NOT_FOUND
```
❌ Usuario no encontrado

Asegúrate de:
• Mencionar al usuario con @
• Que el usuario haya usado el bot antes
• O responder a uno de sus mensajes
```

### MSG_ERROR_INVALID_USER
```
❌ No puedes hacer eso

No puedes enviar {currency} a:
• Ti mismo
• Bots
• Usuarios que no existen
```

### MSG_ERROR_GENERIC
```
❌ Algo salió mal

Intenta de nuevo. Si el problema persiste, contacta a un admin.
```

---

## Time Formatting

| Time | Display |
|------|---------|
| < 1 minute | "ahora" |
| < 1 hour | "hace X min" |
| < 24 hours | "hace X h" |
| < 7 days | "hace X días" |
| < 30 days | "hace X semanas" |
| >= 30 days | "hace X meses" |

---

## Number Formatting

| Number | Display |
|--------|---------|
| 1000 | 1,000 |
| 1000000 | 1,000,000 |

Use thousand separators for readability.

---

## Emoji Reference

| Emoji | Meaning |
|-------|---------|
| 🖤 | Main currency/brand |
| ✅ | Success |
| ❌ | Error |
| 💰 | Balance |
| 🎁 | Received coins |
| 😈 | Punishment |
| 🏆 | Ranking |
| 📜 | History |
| ⬅️ | Received |
| ➡️ | Sent |
| 👑 | First place |
| 🥈 | Second place |
| 🥉 | Third place |
| ⚠️ | Warning |

---

## Next: [05-LOGIC-FLOWS.md](05-LOGIC-FLOWS.md)
