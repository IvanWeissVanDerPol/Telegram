# 12 - BDSM Themed Commands

## 🎭 The Phantom - Roleplay Commands

All themed commands for the BDSM community.

---

## Command Categories

| Category | Commands | Theme |
|----------|----------|-------|
| ⛓️ Collars & Ownership | 6 | Dom/Sub dynamics |
| 🔥 Punishment & Discipline | 7 | Pain/pleasure play |
| 📜 Contracts & Agreements | 5 | Negotiation |
| 🏰 Dungeon & Confinement | 5 | Restraint |
| 💎 Tribute & Worship | 5 | Service/devotion |
| 🎭 Auctions & Bidding | 4 | Objectification |
| 🎲 Games & Challenges | 5 | Competition |
| 👤 Profile & Roles | 5 | Identity |

---

# ⛓️ COLLARS & OWNERSHIP

---

## `/collar @user`

Put your collar on someone, claiming them as yours.

### Usage
```
/collar @maria
```

### Cost
300 SadoCoins

### Requirements
- Target must not already be collared
- Target can refuse within 5 minutes
- You pay only if accepted

### Response - Request Sent
```
⛓️ Solicitud de Collar

@juan quiere ponerte su collar, @maria

Esto significa que serás suyo/a públicamente.

Responde en 5 minutos:
/aceptar_collar - Aceptar
/rechazar_collar - Rechazar
```

### Response - Accepted
```
⛓️ Collar Aceptado

@maria ahora lleva el collar de @juan

💰 -300 SadoCoins (@juan)

/liberar para quitar el collar
/exhibir para ver tus sumis@s
```

### Response - Rejected
```
⛓️ Collar Rechazado

@maria ha rechazado el collar de @juan

No se cobraron SadoCoins.
```

### Effects
- Shows in both profiles
- Listed in `/exhibir`
- Can't be collared by another

---

## `/liberar @user`

Remove your collar from someone.

### Usage
```
/liberar @maria
```

### Cost
Free

### Requirements
- Must be YOUR collar
- Immediate effect

### Response
```
⛓️ Collar Removido

@juan ha liberado a @maria

@maria ya no está bajo su control.
```

---

## `/aceptar_collar`

Accept a pending collar request.

### Usage
```
/aceptar_collar
```

---

## `/rechazar_collar`

Reject a pending collar request.

### Usage
```
/rechazar_collar
```

---

## `/exhibir`

Show everyone who wears your collar.

### Usage
```
/exhibir
```

### Response
```
⛓️ Propiedad de @juan

1. @maria (desde hace 30 días)
2. @ana (desde hace 15 días)
3. @lucia (desde hace 3 días)

Total: 3 sumis@s
```

### Response - Empty
```
⛓️ Propiedad de @juan

No tienes a nadie bajo tu collar.

Usa /collar @user para reclamar a alguien.
```

---

## `/amo`

Show who owns you (who collared you).

### Usage
```
/amo
```

### Response - Collared
```
⛓️ Tu Dueño/a

Llevas el collar de @juan desde hace 15 días.

/suplicar_libertad para pedir ser liberado/a
```

### Response - Free
```
⛓️ Estás libre

No llevas el collar de nadie.
```

---

## `/suplicar_libertad`

Request to be freed from a collar.

### Usage
```
/suplicar_libertad
```

### Response
```
⛓️ Súplica de Libertad

@maria suplica a @juan que la libere.

@juan puede usar /liberar @maria
o ignorar esta súplica.
```

---

# 🔥 PUNISHMENT & DISCIPLINE

---

## `/azotar @user`

Whip someone publicly.

### Usage
```
/azotar @maria
/azotar @maria 10        (specific number)
```

### Cost
20 SadoCoins base + 5 per lash

### Response
```
🔥 Castigo Público

@juan le dio 7 latigazos a @maria

*El sonido del látigo resuena*
*@maria cuenta cada uno*

💰 -55 SadoCoins (20 + 7×5)
```

### Random Lash Count
If not specified: random 1-10

---

## `/nalgada @user`

Playful spank.

### Usage
```
/nalgada @maria
```

### Cost
10 SadoCoins

### Response
```
👋 ¡Nalgada!

@juan le dio una nalgada a @maria

*¡SLAP!* 🍑

💰 -10 SadoCoins
```

---

## `/castigar @user [motivo]`

Formal punishment with reason.

### Usage
```
/castigar @maria Por desobediente
/castigar @pedro
```

### Cost
100 SadoCoins

### Response
```
😈 Castigo Formal

@juan ha castigado a @maria
Motivo: "Por desobediente"

*@maria recibe su merecido*

💰 -100 SadoCoins
```

---

## `/humillar @user`

Public humiliation - gives them a shame title.

### Usage
```
/humillar @maria
```

### Cost
150 SadoCoins

### Response
```
😈 Humillación Pública

@juan ha humillado a @maria

@maria llevará el título:
🔴 "Sumis@ Castigad@" por 2 horas

💰 -150 SadoCoins

/perdonar @maria para quitar el título
```

### Humiliation Titles (Random)
- 🔴 "Sumis@ Castigad@"
- 🔴 "En Penitencia"
- 🔴 "Desobediente"
- 🔴 "En la Esquina"
- 🔴 "Necesita Disciplina"

---

## `/perdonar @user`

Remove humiliation title, show mercy.

### Usage
```
/perdonar @maria
```

### Cost
Free (or 50 SC if not the one who humiliated)

### Response
```
💝 Perdón Otorgado

@juan ha perdonado a @maria

El título de vergüenza ha sido removido.
```

---

## `/penitencia @user [tarea]`

Assign a task/penance.

### Usage
```
/penitencia @maria Escribir 100 veces "obedeceré"
```

### Cost
50 SadoCoins

### Response
```
📜 Penitencia Asignada

@juan le asignó una penitencia a @maria:

"Escribir 100 veces 'obedeceré'"

@maria debe completarla o enfrentar más castigo.

/completar_penitencia cuando termine
```

---

## `/absolver @user`

Forgive all pending punishments.

### Usage
```
/absolver @maria
```

### Cost
200 SadoCoins

### Response
```
✨ Absolución

@juan ha absuelto a @maria de todos sus castigos.

Títulos removidos: 1
Penitencias canceladas: 2
```

---

# 📜 CONTRACTS & AGREEMENTS

---

## `/contrato @user [términos]`

Propose a formal contract.

### Usage
```
/contrato @maria Serás mi sumis@ por 7 días
/contrato @juan 500 SC semanales de tributo
```

### Cost
50 SadoCoins (to create)

### Response
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

## `/firmar`

Sign/accept a pending contract.

### Usage
```
/firmar
```

### Cost
50 SadoCoins (both parties pay)

### Response
```
📜 Contrato Firmado

@juan ⛓️ @maria

Términos: "Serás mi sumis@ por 7 días"
Inicio: Ahora
Fin: En 7 días

💰 -50 SadoCoins (cada uno)

/romper para terminar anticipadamente
```

---

## `/rechazar_contrato`

Decline a contract proposal.

### Usage
```
/rechazar_contrato
```

### Response
```
📜 Contrato Rechazado

@maria ha rechazado el contrato de @juan.
```

---

## `/romper`

Break an active contract (with penalty).

### Usage
```
/romper
```

### Cost
Penalty: 200 SadoCoins

### Response
```
💔 Contrato Roto

@maria ha roto el contrato con @juan

⚠️ Penalización: -200 SadoCoins
```

---

## `/contratos`

View your active contracts.

### Usage
```
/contratos
```

### Response
```
📜 Tus Contratos

Como Dom:
1. @maria - "7 días de servicio" (quedan 3 días)

Como Sub:
1. @carlos - "Tributo semanal" (permanente)

/contrato @user para crear nuevo
/romper para terminar uno
```

---

# 🏰 DUNGEON & CONFINEMENT

---

## `/calabozo @user`

Lock someone in the dungeon.

### Usage
```
/calabozo @maria
/calabozo @maria 2h       (specific time)
```

### Cost
200 SadoCoins

### Duration
Default: 1 hora (max: 4 horas)

### Response
```
🏰 ¡Al Calabozo!

@juan ha encerrado a @maria en el calabozo

🔒 @maria no puede:
- Enviar SadoCoins (/dar)
- Participar en subastas
- Aceptar collares

⏰ Duración: 1 hora
💰 -200 SadoCoins

/liberar_calabozo @maria para liberar antes
```

### Effects on Prisoner
When they try restricted actions:
```
🔒 Estás en el calabozo

No puedes hacer eso hasta que seas liberado/a.
Tiempo restante: 45 minutos

Suplica con /suplicar_libertad
```

---

## `/liberar_calabozo @user`

Free someone from dungeon early.

### Usage
```
/liberar_calabozo @maria
```

### Cost
100 SadoCoins (50 if you're the one who locked them)

### Response
```
🏰 Liberación del Calabozo

@maria ha sido liberada por @juan

Ya puede volver a participar normalmente.
```

---

## `/encadenar @user`

Chain someone to yourself.

### Usage
```
/encadenar @maria
```

### Cost
150 SadoCoins

### Duration
30 minutos

### Response
```
⛓️ Encadenamiento

@juan ha encadenado a @maria

@maria debe seguir a @juan:
- Recibirá copia de mensajes relevantes
- No puede interactuar con otros hasta liberación

⏰ Duración: 30 minutos
```

---

## `/jaula @user`

Put someone in a cage (stronger confinement).

### Usage
```
/jaula @maria
```

### Cost
400 SadoCoins

### Duration
2 horas

### Response
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

## `/abrir_jaula @user`

Release from cage.

### Usage
```
/abrir_jaula @maria
```

### Cost
Free (only cage owner can)

---

# 💎 TRIBUTE & WORSHIP

---

## `/tributo @user [cantidad]`

Pay tribute to someone.

### Usage
```
/tributo @maria 100
/tributo @juan 50 Gracias por enseñarme
```

### Cost
The amount you specify (min: 10 SC)

### Response
```
💎 Tributo Pagado

@pedro le pagó tributo a @maria

⛓️ 100 SadoCoins entregados

"Gracias por enseñarme"

💰 @pedro: -100 SC
💰 @maria: +100 SC
```

---

## `/adorar @user`

Worship someone publicly.

### Usage
```
/adorar @maria
```

### Cost
50 SadoCoins (goes to them)

### Response
```
🙇 Adoración

@pedro se arrodilla ante @maria

*muestra total devoción y respeto*

💰 50 SadoCoins transferidos a @maria
```

---

## `/reverencia @user`

Bow to someone.

### Usage
```
/reverencia @maria
```

### Cost
20 SadoCoins (goes to them)

### Response
```
🎩 Reverencia

@pedro hace una reverencia ante @maria

*inclina la cabeza con respeto*

💰 20 SadoCoins transferidos
```

---

## `/ofrenda @user`

Daily offering (once per day per person).

### Usage
```
/ofrenda @maria
```

### Cost
30 SadoCoins

### Limit
Once per day to each person

### Response
```
🕯️ Ofrenda Diaria

@pedro ofrece su tributo diario a @maria

💎 30 SadoCoins entregados

Próxima ofrenda disponible: mañana
```

---

## `/altar @user`

Create an altar (passive income for them).

### Usage
```
/altar @maria
```

### Cost
1000 SadoCoins

### Effect
Target receives 10 SC daily from "worshippers"

### Response
```
⛩️ Altar Creado

@juan ha construido un altar para @maria

@maria recibirá 10 SadoCoins diarios
mientras el altar exista.

💰 -1000 SadoCoins

/destruir_altar para eliminarlo
```

---

# 🎭 AUCTIONS & BIDDING

---

## `/subasta [precio_inicial]`

Put yourself up for auction.

### Usage
```
/subasta 100
/subasta 500 Una noche de servicio
```

### Cost
Free to start

### Duration
10 minutos

### Response
```
🎭 ¡SUBASTA!

@maria se pone en subasta

📜 "Una noche de servicio"

💰 Precio inicial: 100 SadoCoins
⏰ Tiempo: 10 minutos

/pujar [cantidad] para ofertar
Mínimo: 100 SC
```

---

## `/pujar [cantidad]`

Bid on active auction.

### Usage
```
/pujar 150
/pujar 500
```

### Requirements
- Must be higher than current bid
- Must have the SadoCoins
- Coins are held until outbid or win

### Response - New High Bid
```
🎭 ¡Nueva Oferta!

@juan ofrece 150 SadoCoins por @maria

⏰ Quedan 8 minutos

Supera con /pujar [+150]
```

### Response - Outbid
```
⚠️ ¡Superado!

@pedro ofreció 200 SadoCoins

Tus 150 SC han sido devueltos.
¿Contraoferta? /pujar [+200]
```

---

## `/subastas`

View active auctions.

### Usage
```
/subastas
```

### Response
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

## `/cancelar_subasta`

Cancel your own auction (before any bids).

### Usage
```
/cancelar_subasta
```

### Response
```
🎭 Subasta Cancelada

Tu subasta ha sido cancelada.
(Solo posible si no hay ofertas)
```

---

# 🎲 GAMES & CHALLENGES

---

## `/desafio @user [cantidad]`

Challenge someone to a duel.

### Usage
```
/desafio @maria 100
```

### Cost
Both put up the amount (held)

### Response - Challenge Sent
```
⚔️ ¡Desafío!

@juan desafía a @maria

💰 Apuesta: 100 SadoCoins cada uno
🏆 Ganador se lleva: 200 SadoCoins

@maria tiene 2 minutos:
/aceptar_desafio
/rechazar_desafio
```

### Response - Duel Result
```
⚔️ ¡Duelo!

@juan 🎲 vs 🎲 @maria

@juan sacó: 4
@maria sacó: 6

🏆 ¡@maria GANA!

💰 @maria recibe 200 SadoCoins
```

---

## `/aceptar_desafio`

Accept a pending challenge.

---

## `/rechazar_desafio`

Decline a challenge.

---

## `/ruleta_castigo`

Spin the punishment wheel.

### Usage
```
/ruleta_castigo
```

### Cost
50 SadoCoins

### Response
```
🎡 Ruleta del Castigo

*la rueda gira...*

🎯 ¡HUMILLACIÓN PÚBLICA!

Llevarás el título "Giró y Perdió" por 1 hora.

💰 -50 SadoCoins
```

### Possible Outcomes
- Humillación (título 1h)
- Calabozo (30 min)
- Pagar tributo random
- ¡Suerte! Ganas 100 SC
- Nalgada pública
- Penitencia asignada

---

## `/dados @user [cantidad]`

Dice roll against someone.

### Usage
```
/dados @maria 50
```

### Response
```
🎲 Dados del Destino

@juan: 🎲 5
@maria: 🎲 3

🏆 @juan gana 50 SadoCoins de @maria
```

---

# 👤 PROFILE & ROLES

---

## `/perfil`

View your full profile.

### Usage
```
/perfil
/perfil @maria       (view someone else)
```

### Response
```
🎭 Perfil de @maria

👤 Rol: Sumisa
⛓️ Collar: @juan (hace 15 días)
💰 SadoCoins: 850
📊 Ranking: #5

📜 Títulos:
• 💎 "Devota"
• ⭐ "Primera Subasta"

📈 Estadísticas:
• Transacciones: 47
• Tributos pagados: 12
• Castigos recibidos: 3
• Días activa: 45

🎭 Contratos activos: 1
```

---

## `/rol [rol]`

Set your role/identity.

### Usage
```
/rol Dom
/rol Sub
/rol Switch
/rol Brat
```

### Available Roles
- Dom / Dominante
- Sub / Sumis@
- Switch
- Brat
- Master / Mistress
- Slave / Esclav@
- Daddy / Mommy
- Little
- Pet
- Observador

### Response
```
👤 Rol Actualizado

Tu rol ahora es: Dominante

Esto se mostrará en tu /perfil
```

---

## `/titulo [titulo]`

Buy a custom title.

### Usage
```
/titulo El Implacable
```

### Cost
200 SadoCoins

### Response
```
🏷️ Título Adquirido

Tu nuevo título: "El Implacable"

💰 -200 SadoCoins
```

---

## `/titulos`

View available and owned titles.

### Usage
```
/titulos
```

### Response
```
🏷️ Títulos

Tus títulos:
• 💎 "El Implacable" (comprado)
• ⭐ "Primera Sangre" (logro)

Disponibles para comprar:
• "Señor/a del Dolor" - 300 SC
• "Amo/a de las Cadenas" - 500 SC
• "Phantom Elite" - 1000 SC
```

---

## `/mood [estado]`

Set your current mood/status.

### Usage
```
/mood 🔥
/mood disponible
/mood ocupad@
```

### Moods
- 🔥 Caliente
- 😈 Travieso
- 🥺 Sumis@
- 👑 Dominante
- 💤 Descansando
- ⛔ No molestar

### Response
```
💭 Mood Actualizado

Tu estado: 🔥 Caliente

Otros verán esto en tu perfil.
```

---

## Command Summary Table

| Command | Cost | Category |
|---------|------|----------|
| `/collar @user` | 300 SC | Ownership |
| `/liberar @user` | Free | Ownership |
| `/exhibir` | Free | Ownership |
| `/amo` | Free | Ownership |
| `/azotar @user` | 20+ SC | Punishment |
| `/nalgada @user` | 10 SC | Punishment |
| `/castigar @user` | 100 SC | Punishment |
| `/humillar @user` | 150 SC | Punishment |
| `/perdonar @user` | Free/50 | Punishment |
| `/contrato @user` | 50 SC | Contracts |
| `/firmar` | 50 SC | Contracts |
| `/romper` | 200 SC | Contracts |
| `/calabozo @user` | 200 SC | Dungeon |
| `/jaula @user` | 400 SC | Dungeon |
| `/tributo @user` | Variable | Worship |
| `/adorar @user` | 50 SC | Worship |
| `/reverencia @user` | 20 SC | Worship |
| `/ofrenda @user` | 30 SC | Worship |
| `/altar @user` | 1000 SC | Worship |
| `/subasta` | Free | Auction |
| `/pujar` | Variable | Auction |
| `/desafio @user` | Variable | Games |
| `/ruleta_castigo` | 50 SC | Games |
| `/perfil` | Free | Profile |
| `/rol` | Free | Profile |
| `/titulo` | 200 SC | Profile |
| `/mood` | Free | Profile |

---

## Pending Decisions

1. **Consent system?** Require acceptance for punishments?
2. **Cooldowns?** Limit how often you can punish same person?
3. **Revenge protection?** Can a sub punish their Dom?
4. **Escape options?** Can prisoners do anything?
5. **Title duration?** Permanent or temporary?
6. **Role restrictions?** Only Doms can collar?
