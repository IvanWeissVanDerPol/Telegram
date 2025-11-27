# Message Templates

## Variables

| Variable | Example |
|----------|---------|
| `{user}` | @maria |
| `{amount}` | 500 |
| `{balance}` | 1,200 |
| `{recipient}` | @juan |
| `{currency}` | SadoCoins |

---

## Welcome

```
🎭 Bienvenido/a a The Phantom!

Tu wallet de {currency} ⛓️

📜 Comandos:
/ver - Tu saldo
/dar @user cantidad - Enviar
/ranking - Top usuarios
/historial - Tus movimientos

💰 Tu saldo: {balance} {currency}
```

---

## Balance

```
⛓️ Tu saldo: {balance} {currency}
```

Zero balance:
```
⛓️ Tu saldo: 0 {currency}

Aún no tienes {currency}.
```

---

## Transfer Success

To sender:
```
✅ Transferencia exitosa

⛓️ Enviaste {amount} {currency} a {recipient}
💰 Tu nuevo saldo: {balance} {currency}
```

To recipient:
```
🎁 Has recibido {currency}!

⛓️ {sender} te envió {amount} {currency}
💰 Tu nuevo saldo: {balance} {currency}
```

---

## Ranking

```
🏆 Ranking de {currency}

1. 👑 @carlos — 2,500 ⛓️
2. 🥈 @maria — 1,800 ⛓️
3. 🥉 @juan — 1,200 ⛓️
...

━━━━━━━━━━━━━━━━
📍 Tu posición: {position} con {balance} {currency}
```

---

## History

```
📜 Tu historial

1. ➡️ -{amount} → {recipient} (hace 2h)
2. ⬅️ +{amount} ← {sender} (hace 5h)
3. 🎁 +{amount} Admin (hace 1d)

━━━━━━━━━━━━━━━━
💰 Saldo actual: {balance} {currency}
```

---

## Icons

| Icon | Meaning |
|------|---------|
| ⛓️ | Currency/brand |
| ✅ | Success |
| ❌ | Error |
| 💰 | Balance |
| 🎁 | Received |
| 😈 | Punishment |
| 🏆 | Ranking |
| 📜 | History |
| ➡️ | Sent |
| ⬅️ | Received |
| 👑 | First place |
| 🥈 | Second place |
| 🥉 | Third place |
