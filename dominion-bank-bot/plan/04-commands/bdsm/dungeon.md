# Dungeon Commands

## /calabozo @user

Lock someone in the dungeon.

**Cost:** 200 SadoCoins

**Duration:** 1 hour (max 4 hours)

**Usage:**
```
/calabozo @maria
/calabozo @maria 2h
```

**Response:**
```
🏰 ¡Al Calabozo!

@juan ha encerrado a @maria en el calabozo

🔒 @maria no puede:
- Enviar SadoCoins (/dar)
- Participar en subastas
- Aceptar collares

⏰ Duración: 1 hora
💰 -200 SadoCoins
```

**When prisoner tries actions:**
```
🔒 Estás en el calabozo

No puedes hacer eso hasta ser liberado/a.
Tiempo restante: 45 minutos
```

---

## /liberar_calabozo @user

Free from dungeon early.

**Cost:** 100 SC (50 if you locked them)

**Usage:**
```
/liberar_calabozo @maria
```

**Response:**
```
🏰 Liberación del Calabozo

@maria ha sido liberada por @juan
```

---

## /jaula @user

Stronger confinement - can't use ANY commands.

**Cost:** 400 SadoCoins

**Duration:** 2 hours

**Usage:**
```
/jaula @maria
```

**Response:**
```
🗝️ Enjaulamiento

@juan ha metido a @maria en la jaula

🔒 @maria no puede:
- Usar NINGÚN comando
- Solo puede observar

⏰ Duración: 2 horas
💰 -400 SadoCoins

Solo @juan puede liberar con /abrir_jaula
```

---

## /abrir_jaula @user

Release from cage.

**Cost:** Free (only owner can)

**Usage:**
```
/abrir_jaula @maria
```

---

## /encadenar @user

Chain someone to yourself.

**Cost:** 150 SadoCoins

**Duration:** 30 minutes

**Usage:**
```
/encadenar @maria
```

**Response:**
```
⛓️ Encadenamiento

@juan ha encadenado a @maria

@maria debe seguir a @juan:
- No puede interactuar con otros

⏰ Duración: 30 minutos
```
