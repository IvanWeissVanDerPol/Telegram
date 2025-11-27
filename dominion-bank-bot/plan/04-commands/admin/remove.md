# Command: /quitar

## Purpose
Admin removes SadoCoins from a user (burning).

## Usage
```
/quitar @username cantidad
/quitar @username cantidad motivo
```

## Examples
```
/quitar @pedro 200
/quitar @juan 100 Penalización
```

## Who Can Use
**Admins only**

## Behavior
1. Verify sender is admin
2. Parse recipient and amount
3. Check recipient exists
4. Remove coins (can go negative = debt)
5. Record transaction
6. Notify user

## Response - Success
```
😈 SadoCoins quitados

⛓️ -200 SadoCoins ← @pedro
💰 Su nuevo saldo: 300 SadoCoins
```

## Response - Into Debt
```
😈 SadoCoins quitados

⛓️ -500 SadoCoins ← @pedro
💰 Su nuevo saldo: -200 SadoCoins

⚠️ @pedro ahora está en DEUDA
```

## Response - Notification (User DM)
```
😈 Te han quitado SadoCoins

⛓️ Un admin te quitó 200 SadoCoins
💰 Tu nuevo saldo: 300 SadoCoins
```

## Database Changes
- UPDATE user balance (subtract)
- INSERT transaction (type: 'admin_remove')
