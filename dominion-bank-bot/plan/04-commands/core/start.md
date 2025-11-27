# Command: /start

## Purpose
Welcome new users and register them.

## Usage
```
/start
```

## Who Can Use
Everyone

## Behavior
1. Check if user exists in database
2. If new: Create user with 0 SadoCoins
3. Send welcome message

## Response
```
🎭 Bienvenido/a a The Phantom!

Tu wallet secreta de SadoCoins ⛓️

📜 Comandos:
/ver - Tu saldo
/dar @user cantidad - Enviar
/ranking - Top usuarios
/historial - Tus movimientos
/help - Ayuda completa

⛓️ Tu saldo: 0 SadoCoins
```

## Database Changes
- INSERT user if not exists
- No transaction recorded
