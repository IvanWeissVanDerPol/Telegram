# Error Messages

## Standard Format

```
❌ [Error Title]

[Explanation]

[How to fix / Example]
```

---

## Error Catalog

### Invalid Amount
```
❌ Cantidad inválida

La cantidad debe ser un número entero positivo.

✅ Ejemplo: /dar @maria 100
```

### Insufficient Balance
```
❌ Saldo insuficiente

Tu saldo: 50 SadoCoins
Intentaste enviar: 100 SadoCoins
Te faltan: 50 SadoCoins
```

### Self Transfer
```
❌ No puedes enviarte SadoCoins a ti mismo

¿Intentabas enviar a alguien más?
```

### User Not Found
```
❌ Usuario no encontrado

Asegúrate de:
• Mencionar con @usuario
• Que haya usado el bot antes
• O responder a su mensaje
```

### Not Admin
```
❌ No tienes permiso para usar este comando

Este comando es solo para administradores.
```

### Missing Arguments
```
❌ Formato incorrecto

✅ Uso: /dar @usuario cantidad
📝 Ejemplo: /dar @maria 100
```

### Bot Mentioned
```
❌ No puedes enviar SadoCoins a un bot
```

### In Dungeon
```
🔒 Estás en el calabozo

No puedes hacer eso hasta ser liberado/a.
Tiempo restante: 45 minutos

Suplica con /suplicar_libertad
```

### In Debt
```
🔴 Estás en deuda

No puedes enviar SadoCoins mientras debas.
Tu deuda: -150 SadoCoins

Paga tu deuda primero.
```

### Already Collared
```
⛓️ Ya llevas un collar

No puedes aceptar otro collar.
Primero pide ser liberado/a de @juan.
```

### Cooldown Active
```
⏰ Demasiado pronto

Debes esperar 4 minutos antes de usar /azotar con @maria de nuevo.
```

### Generic Error
```
❌ Algo salió mal

Intenta de nuevo. Si el problema persiste, contacta a un admin.
```
