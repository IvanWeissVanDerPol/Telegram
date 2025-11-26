# 14 - Initial Setup via Google Sheets

## Overview

Instead of users spamming the group with commands, they fill a Google Sheet with their info before joining. Admins import everything at once.

---

## Why This Approach?

| Problem | Solution |
|---------|----------|
| Users spam group with /start, /tags, /bio | Fill sheet once, import all |
| Hard to onboard many users | Bulk import from sheet |
| Users forget to set profile | Sheet is required to join |
| Inconsistent data | Validated columns |
| No overview of members | Sheet = member database |

---

## Setup Flow

```
┌─────────────────┐
│  NEW USER       │
│  wants to join  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Fill Google     │
│ Sheet with:     │
│ - Telegram @    │
│ - Rol           │
│ - Tags/Kinks    │
│ - Bio           │
│ - Limits        │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Admin reviews   │
│ and approves    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Bot imports     │
│ /importar_users │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ User added to   │
│ group + DB      │
│ Profile ready!  │
└─────────────────┘
```

---

## Master Google Sheet Structure

### Tab 1: "Usuarios" (Main User Data)

| username | telegram_id | nombre | rol | experiencia | verificado | saldo_inicial | fecha_registro |
|----------|-------------|--------|-----|-------------|------------|---------------|----------------|
| @maria | 123456789 | María García | Sumisa | Experimentada | SI | 100 | 2024-01-15 |
| @juan | 987654321 | Juan López | Dom | Veterano | SI | 100 | 2024-01-15 |
| @pedro | 555555555 | Pedro Ruiz | Switch | Principiante | NO | 50 | 2024-01-20 |

**Column Details:**

| Column | Required | Description |
|--------|----------|-------------|
| `username` | ✅ | Telegram @username |
| `telegram_id` | ❌ | Numeric ID (if known) |
| `nombre` | ✅ | Display name |
| `rol` | ✅ | Dom/Sub/Switch/etc |
| `experiencia` | ✅ | Level |
| `verificado` | ❌ | SI/NO - Admin verified |
| `saldo_inicial` | ❌ | Starting SadoCoins |
| `fecha_registro` | Auto | When added |

---

### Tab 2: "Perfiles" (Extended Profile)

| username | bio | busca | mood | ciudad | edad | genero | orientacion | disponibilidad |
|----------|-----|-------|------|--------|------|--------|-------------|----------------|
| @maria | 28 años, CDMX... | Dom para bondage | disponible | CDMX | 28 | F | Hetero | Fines de semana |
| @juan | Rigger con 10 años... | Sub para entrenar | disponible | Madrid | 35 | M | Hetero | Flexible |

---

### Tab 3: "Tags" (User Tags)

| username | tags |
|----------|------|
| @maria | #Sub, #Brat, #RopeBunny, #Sensual, #Latina |
| @juan | #Dom, #Rigger, #Daddy, #Mentor, #Shibari |
| @pedro | #Switch, #Primal, #Curioso |

---

### Tab 4: "Kinks" (Interests & Levels)

| username | bondage | impact | sensory | power | roleplay | limits |
|----------|---------|--------|---------|-------|----------|--------|
| @maria | 3 | 2 | 2 | 1 | 2 | Sin sangre, Sin público |
| @juan | 3 | 3 | 2 | 3 | 1 | Sin scat |
| @pedro | 1 | 1 | 2 | 0 | 3 | Muchos - nuevo |

**Scale:** 0 = No interest, 1 = Curious, 2 = Like, 3 = Love

---

### Tab 5: "Relaciones" (Ownership & Dynamics)

| dom | sub | tipo | desde | notas |
|-----|-----|------|-------|-------|
| @juan | @maria | collar | 2024-01-01 | Collar formal |
| @carlos | @ana | collar | 2024-02-15 | |
| @juan | @pedro | contrato | 2024-03-01 | Entrenamiento mensual |
| @luis | @sofia | collar | 2023-06-01 | Pareja estable |

**Relationship Types:**
- `collar` - Ownership/collar
- `contrato` - Active contract
- `pareja` - Romantic partners
- `mentor` - Mentorship

---

### Tab 6: "Transacciones" (Initial Balances & History)

| username | tipo | cantidad | motivo | fecha |
|----------|------|----------|--------|-------|
| @maria | add | 100 | Saldo inicial | 2024-01-15 |
| @juan | add | 100 | Saldo inicial | 2024-01-15 |
| @maria | add | 500 | Premio evento inaugural | 2024-01-20 |

---

### Tab 7: "Admins"

| username | nivel | desde |
|----------|-------|-------|
| @franco | super_admin | 2024-01-01 |
| @laura | admin | 2024-01-15 |
| @carlos | admin | 2024-02-01 |

---

## Import Commands

### `/importar_usuarios`

Import all users from sheet:

```
/importar_usuarios
```

Response:
```
📊 Importación de Usuarios

Conectando a Google Sheet...
✅ Conectado

Vista previa:
━━━━━━━━━━━━━━━━━━━━

Nuevos usuarios: 15
Actualizaciones: 3
Sin cambios: 42

Nuevos:
• @maria (Sumisa, 100 SC)
• @pedro (Switch, 50 SC)
• @ana (Dom, 100 SC)
...

¿Proceder? SI / CANCELAR
```

### `/importar_relaciones`

Import ownership/collars:

```
/importar_relaciones
```

Response:
```
⛓️ Importación de Relaciones

Collares: 8
Contratos: 3
Parejas: 5

Vista previa:
• @juan → @maria (collar)
• @carlos → @ana (collar)
• @juan → @pedro (contrato)
...

¿Proceder? SI / CANCELAR
```

### `/importar_perfiles`

Import extended profiles:

```
/importar_perfiles
```

### `/importar_todo`

Import everything at once:

```
/importar_todo
```

Response:
```
📦 Importación Completa

Procesando todas las pestañas...

✅ Usuarios: 60 importados
✅ Perfiles: 58 importados
✅ Tags: 60 importados
✅ Kinks: 55 importados
✅ Relaciones: 16 importadas
✅ Transacciones: 120 importadas
✅ Admins: 3 configurados

¡Sistema listo! 🎭
```

---

## User Registration Form

### Option A: Direct Sheet Access

1. Share Google Sheet link with new users
2. They fill their row
3. Admin reviews and approves
4. Import when ready

### Option B: Google Form → Sheet

Create a Google Form that feeds into the sheet:

**Form Fields:**
1. Telegram Username* (@...)
2. Nombre para mostrar*
3. Rol* (dropdown: Dom/Sub/Switch/Brat/etc)
4. Nivel de experiencia* (dropdown)
5. Tags (checkboxes)
6. Kinks - Bondage (scale 0-3)
7. Kinks - Impact (scale 0-3)
8. ... more kinks
9. Límites duros*
10. Bio (text area)
11. ¿Qué buscas?
12. Ciudad
13. Disponibilidad
14. ¿Cómo conociste al grupo?

**Form Response → Sheet → Bot Import**

---

## Validation on Import

### User Validation
| Check | Action |
|-------|--------|
| Username format | Must start with @ |
| Duplicate username | Skip or update |
| Required fields empty | Error + skip |
| Invalid rol | Use default |
| Invalid experience | Use default |

### Relationship Validation
| Check | Action |
|-------|--------|
| Both users exist | Create if not |
| Circular ownership | Error |
| Already collared | Error or update |
| Self-relationship | Error |

---

## Sync Modes

### One-Time Import
```
/importar_todo
```
Import once, then manage via bot commands.

### Continuous Sync
```
/conectar_sheets [URL]
/sync_modo maestro ON
```
Sheet is always the "master" - changes in sheet override bot data.

### Bot Master Mode
```
/sync_modo bot ON
```
Bot is master - export to sheet for backup only.

---

## Sheet Templates

### Command: `/plantilla_usuarios`

Bot sends Google Sheet template with:
- All tabs pre-created
- Column headers
- Data validation dropdowns
- Example rows
- Instructions tab

### Template Includes:
- Dropdown for Rol (Dom/Sub/Switch/etc)
- Dropdown for Experience levels
- Checkbox lists for Tags
- Scale 0-3 for Kinks
- Date pickers
- Conditional formatting

---

## Privacy in Sheet

### Sensitive Data Handling

| Data | In Sheet? | Notes |
|------|-----------|-------|
| Username | ✅ | Required |
| Real name | ⚠️ | Optional, admin only |
| Telegram ID | ✅ | For matching |
| Kinks | ✅ | For matching |
| Limits | ✅ | Important |
| Contact info | ❌ | Never in sheet |
| Photos | ❌ | Never in sheet |

### Sheet Access Levels

| Level | Can See | Can Edit |
|-------|---------|----------|
| New user | Own row only | Own row |
| Member | Public columns | Own row |
| Admin | All columns | All rows |
| Super Admin | Everything | Everything + structure |

---

## Notifications After Import

### To New Users (DM)
```
🎭 ¡Bienvenid@ a The Phantom!

Tu perfil ha sido importado:

👤 Rol: Sumisa
🏷️ Tags: #Brat #RopeBunny
⛓️ Saldo: 100 SadoCoins

Usa /perfil para ver tu perfil completo.
Usa /editarperfil para hacer cambios.

¡Diviértete! 😈
```

### To Users with Relationships (DM)
```
⛓️ Relación Importada

Llevas el collar de @juan

Esta relación fue registrada por un admin.
Si esto es incorrecto, contacta a un admin.

/amo para ver detalles
```

---

## Export Commands

### `/exportar_usuarios`

Export all users back to sheet format:
```
Bot sends: phantom_users_export.xlsx
```

### `/exportar_todo`

Full database export:
```
Bot sends: phantom_full_backup.xlsx
```

With all tabs matching the import format.

---

## Example: Full Setup Workflow

### Day 0: Preparation
1. Admin creates Google Sheet from template
2. Admin creates Google Form (optional)
3. Share form/sheet link with community

### Days 1-7: Registration
1. Users fill the form/sheet
2. Admin reviews entries
3. Admin verifies known members

### Day 8: Import
```
/conectar_sheets [URL]
/importar_todo
```

### Go Live
1. Add bot to group
2. Announce bot is ready
3. Users can use /perfil to see their data
4. Start using all features!

---

## Ongoing Management

| Task | Method |
|------|--------|
| Add new user | Sheet + /importar_usuarios |
| Edit profile | User: bot commands / Admin: sheet |
| Add relationship | Sheet + /importar_relaciones |
| Bulk changes | Edit sheet + /sync_now |
| Backup | /exportar_todo weekly |

---

## Admin Dashboard Sheet

Optional tab for admin overview:

| Metric | Value |
|--------|-------|
| Total users | 60 |
| Active (30d) | 45 |
| Total SadoCoins | 25,000 |
| Active collars | 12 |
| Active contracts | 5 |
| Pending verifications | 3 |
| In debt | 2 |

Auto-updated via bot → sheet sync.
