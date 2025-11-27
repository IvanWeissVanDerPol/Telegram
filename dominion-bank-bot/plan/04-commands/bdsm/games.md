# Game Commands

## /desafio @user [cantidad]

Challenge someone to a duel.

**Cost:** Both put up the amount

**Usage:**
```
/desafio @maria 100
```

**Response - Challenge:**
```
⚔️ ¡Desafío!

@juan desafía a @maria

💰 Apuesta: 100 SadoCoins cada uno
🏆 Ganador se lleva: 200 SadoCoins

@maria tiene 2 minutos:
/aceptar_desafio
/rechazar_desafio
```

**Response - Duel Result:**
```
⚔️ ¡Duelo!

@juan 🎲 vs 🎲 @maria

@juan sacó: 4
@maria sacó: 6

🏆 ¡@maria GANA!

💰 @maria recibe 200 SadoCoins
```

---

## /dados @user [cantidad]

Quick dice roll against someone.

**Usage:**
```
/dados @maria 50
```

**Response:**
```
🎲 Dados del Destino

@juan: 🎲 5
@maria: 🎲 3

🏆 @juan gana 50 SadoCoins de @maria
```

---

## /ruleta_castigo

Spin the punishment wheel.

**Cost:** 50 SadoCoins

**Usage:**
```
/ruleta_castigo
```

**Response:**
```
🎡 Ruleta del Castigo

*la rueda gira...*

🎯 ¡HUMILLACIÓN PÚBLICA!

Llevarás el título "Giró y Perdió" por 1 hora.

💰 -50 SadoCoins
```

**Possible Outcomes:**
- Humillación (título 1h)
- Calabozo (30 min)
- Pagar tributo random
- ¡Suerte! Ganas 100 SC
- Nalgada pública
- Penitencia asignada
