# Contract Commands

## /contrato @user [términos]

Propose a formal contract.

**Cost:** 50 SadoCoins (to create)

**Usage:**
```
/contrato @maria Serás mi sumis@ por 7 días
/contrato @juan 500 SC semanales de tributo
```

**Response:**
```
📜 Contrato Propuesto

De: @juan
Para: @maria

Términos:
"Serás mi sumis@ por 7 días"

@maria tiene 24h para responder:
/firmar - Aceptar contrato
/rechazar_contrato - Rechazar
```

---

## /firmar

Sign/accept a pending contract.

**Cost:** 50 SadoCoins (both parties pay)

**Usage:**
```
/firmar
```

**Response:**
```
📜 Contrato Firmado

@juan ⛓️ @maria

Términos: "Serás mi sumis@ por 7 días"
Inicio: Ahora
Fin: En 7 días

💰 -50 SadoCoins (cada uno)
```

---

## /rechazar_contrato

Decline a contract proposal.

**Usage:**
```
/rechazar_contrato
```

**Response:**
```
📜 Contrato Rechazado

@maria ha rechazado el contrato de @juan.
```

---

## /romper

Break an active contract (with penalty).

**Cost:** 200 SadoCoins penalty

**Usage:**
```
/romper
```

**Response:**
```
💔 Contrato Roto

@maria ha roto el contrato con @juan

⚠️ Penalización: -200 SadoCoins
```

---

## /contratos

View your active contracts.

**Usage:**
```
/contratos
```

**Response:**
```
📜 Tus Contratos

Como Dom:
1. @maria - "7 días de servicio" (quedan 3 días)

Como Sub:
1. @carlos - "Tributo semanal" (permanente)

/contrato @user para crear nuevo
```
