# Auction Commands

## /subasta [precio_inicial]

Put yourself up for auction.

**Cost:** Free to start

**Duration:** 10 minutes

**Usage:**
```
/subasta 100
/subasta 500 Una noche de servicio
```

**Response:**
```
🎭 ¡SUBASTA!

@maria se pone en subasta

📜 "Una noche de servicio"

💰 Precio inicial: 100 SadoCoins
⏰ Tiempo: 10 minutos

/pujar [cantidad] para ofertar
```

---

## /pujar [cantidad]

Bid on active auction.

**Requirements:**
- Higher than current bid
- Must have the SadoCoins
- Coins held until outbid or win

**Usage:**
```
/pujar 150
```

**Response - New High Bid:**
```
🎭 ¡Nueva Oferta!

@juan ofrece 150 SadoCoins por @maria

⏰ Quedan 8 minutos

Supera con /pujar [+150]
```

**Response - Outbid:**
```
⚠️ ¡Superado!

@pedro ofreció 200 SadoCoins

Tus 150 SC han sido devueltos.
¿Contraoferta? /pujar [+200]
```

---

## /subastas

View active auctions.

**Usage:**
```
/subastas
```

**Response:**
```
🎭 Subastas Activas

1. @maria - "Noche de servicio"
   💰 Actual: 500 SC (@juan)
   ⏰ 3 minutos

2. @pedro - "Sesión de masajes"
   💰 Actual: 200 SC (@ana)
   ⏰ 7 minutos

/pujar [cantidad] para ofertar
```

---

## /cancelar_subasta

Cancel your auction (before any bids).

**Usage:**
```
/cancelar_subasta
```

**Response:**
```
🎭 Subasta Cancelada

Tu subasta ha sido cancelada.
(Solo posible si no hay ofertas)
```

---

## Auction End

When time runs out:

```
🎭 ¡SUBASTA TERMINADA!

@maria fue ganada por @juan

💰 500 SadoCoins transferidos a @maria

¡Que disfruten! 😈
```
