# Command: /dar_admin

## Purpose
Admin gives SadoCoins to a user (minting).

## Usage
```
/dar_admin @username cantidad
/dar_admin @username cantidad motivo
```

## Examples
```
/dar_admin @maria 500
/dar_admin @juan 1000 Premio por evento
```

## Who Can Use
**Admins only**

## Behavior
1. Verify sender is admin
2. Parse recipient and amount
3. Create recipient if not exists
4. Add coins to recipient
5. Record transaction with admin ID
6. Notify recipient

## Response - Success (Admin)
```
✅ SadoCoins entregados

⛓️ +500 SadoCoins → @maria
💰 Su nuevo saldo: 800 SadoCoins
```

## Response - Notification (User DM)
```
🎁 Has recibido SadoCoins!

⛓️ Un admin te ha dado 500 SadoCoins
💰 Tu nuevo saldo: 800 SadoCoins
```

## Error - Not Admin
```
❌ No tienes permiso para usar este comando
```

## Database Changes
- UPDATE recipient balance (add)
- May INSERT recipient if new
- INSERT transaction (type: 'admin_add')
