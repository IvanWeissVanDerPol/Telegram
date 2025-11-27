# Command: /ver

## Purpose
Show user's current SadoCoin balance.

## Usage
```
/ver
```

## Who Can Use
Everyone

## Behavior
1. Get user from database (create if not exists)
2. Return formatted balance

## Response - Has Balance
```
⛓️ Tu saldo: 500 SadoCoins

📊 Ranking: #5 de 47 usuarios
```

## Response - Zero Balance
```
⛓️ Tu saldo: 0 SadoCoins

Aún no tienes SadoCoins.
Espera a que un admin te recompense.
```

## Database Changes
- May create user if first interaction
- No balance changes
