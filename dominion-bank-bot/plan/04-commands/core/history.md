# Command: /historial

## Purpose
Show user's transaction history.

## Usage
```
/historial
/historial 20      (show last 20)
```

## Who Can Use
Everyone

## Behavior
1. Query user's recent transactions
2. Format each with icon and time
3. Show current balance

## Response
```
📜 Tu historial de SadoCoins

1. ➡️ -100 → @maria (hace 2h)
2. ⬅️ +50 ← @pedro (hace 5h)
3. 🎁 +500 Admin (hace 1d)
4. ➡️ -200 → @juan (hace 2d)
5. 😈 -100 Admin (hace 3d)

━━━━━━━━━━━━━━━━
💰 Saldo actual: 650 SadoCoins
```

## Transaction Icons
| Icon | Meaning |
|------|---------|
| ➡️ | You sent |
| ⬅️ | You received |
| 🎁 | Admin gave you |
| 😈 | Admin took from you |
| ⛓️ | Tribute/BDSM |

## Response - Empty
```
📜 Tu historial de SadoCoins

No tienes transacciones aún.
```

## Time Formatting
| Time | Display |
|------|---------|
| < 1 min | "ahora" |
| < 1 hour | "hace X min" |
| < 24 hours | "hace X h" |
| < 7 days | "hace X días" |

## Database Changes
None (read only)
