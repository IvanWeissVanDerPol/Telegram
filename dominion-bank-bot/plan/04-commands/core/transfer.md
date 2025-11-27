# Command: /dar

## Purpose
Transfer SadoCoins to another user.

## Usage
```
/dar @username cantidad
/dar cantidad            (replying to message)
```

## Examples
```
/dar @maria 100
/dar 200                 (reply to someone)
```

## Who Can Use
Everyone

## Behavior
1. Parse recipient and amount
2. Validate amount (positive integer)
3. Check sender has enough balance
4. Check not sending to self
5. Check recipient is not a bot
6. Transfer coins (atomic)
7. Record transaction
8. Notify both users

## Response - Success (Sender)
```
✅ Transferencia exitosa

⛓️ Enviaste 100 SadoCoins a @maria
💰 Tu nuevo saldo: 400 SadoCoins
```

## Response - Success (Recipient DM)
```
🎁 Has recibido SadoCoins!

⛓️ @juan te envió 100 SadoCoins
💰 Tu nuevo saldo: 150 SadoCoins
```

## Error Responses

### Not enough balance
```
❌ Saldo insuficiente

Tu saldo: 50 SadoCoins
Intentaste enviar: 100 SadoCoins
Te faltan: 50 SadoCoins
```

### Self transfer
```
❌ No puedes enviarte SadoCoins a ti mismo
```

### Invalid amount
```
❌ Cantidad inválida

La cantidad debe ser un número entero positivo.
Ejemplo: /dar @maria 100
```

### User not found
```
❌ Usuario no encontrado

Asegúrate de:
• Mencionar con @usuario
• Que haya usado el bot antes
• O responder a su mensaje
```

## Database Changes
- UPDATE sender balance (subtract)
- UPDATE recipient balance (add)
- INSERT transaction (type: 'transfer')
