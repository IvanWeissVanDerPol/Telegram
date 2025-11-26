# 11 - Excel Data Input System

## Overview

Import coin transactions from IRL events via Excel/CSV files.

---

## Use Cases

| Scenario | Example |
|----------|---------|
| **IRL Event earnings** | User earned 500 SC at party for activity |
| **IRL Event spending** | User spent 200 SC at auction |
| **Bulk rewards** | Give 100 SC to all event attendees |
| **Corrections** | Fix wrong transactions |
| **Migration** | Import from old system |

---

## How It Works

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   IRL EVENT     │     │     EXCEL       │     │   TELEGRAM      │
│                 │     │                 │     │     BOT         │
│  Record on      │────▶│  Fill template  │────▶│  /importar      │
│  paper/phone    │     │  with data      │     │  processes      │
│                 │     │                 │     │  file           │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                                                        │
                                                        ▼
                                               ┌─────────────────┐
                                               │   DATABASE      │
                                               │                 │
                                               │  Balances       │
                                               │  updated        │
                                               └─────────────────┘
```

---

## Excel Template Format

### Simple Format (Recommended)

| username | tipo | cantidad | motivo |
|----------|------|----------|--------|
| @maria | add | 500 | Premio subasta |
| @juan | add | 200 | Participación evento |
| @pedro | remove | 100 | Compra en tienda |
| @ana | add | 300 | Ganó desafío |
| @luis | remove | 50 | Penalización |

### Columns Explained

| Column | Required | Values | Description |
|--------|----------|--------|-------------|
| `username` | ✅ | @user or telegram_id | Who |
| `tipo` | ✅ | `add` / `remove` / `set` | What action |
| `cantidad` | ✅ | Positive number | How much |
| `motivo` | ❌ | Text | Why (for records) |

### Action Types

| Type | Description | Example |
|------|-------------|---------|
| `add` | Add to balance | Earned at event |
| `remove` | Subtract from balance | Spent at event |
| `set` | Set exact balance | Override/correction |

---

## Advanced Format (With More Data)

| username | tipo | cantidad | motivo | evento | fecha | admin |
|----------|------|----------|--------|--------|-------|-------|
| @maria | add | 500 | Premio subasta | Fiesta Enero | 2024-01-20 | @franco |
| @juan | add | 200 | Participación | Fiesta Enero | 2024-01-20 | @franco |

### Additional Columns

| Column | Required | Description |
|--------|----------|-------------|
| `evento` | ❌ | Event name for grouping |
| `fecha` | ❌ | Date of transaction |
| `admin` | ❌ | Who recorded it |

---

## Transfer Format (User to User)

For recording IRL transfers between users:

| from | to | cantidad | motivo |
|------|-----|----------|--------|
| @maria | @juan | 100 | Pago apuesta |
| @pedro | @ana | 50 | Regalo |

---

## Bot Commands for Import

### `/importar`

Upload and process Excel/CSV file.

**Usage:**
1. Send `/importar` command
2. Attach Excel (.xlsx) or CSV file
3. Bot processes and confirms

**Response - Preview:**
```
📊 Archivo recibido: evento_enero.xlsx

Vista previa:
1. @maria +500 (Premio subasta)
2. @juan +200 (Participación)
3. @pedro -100 (Compra tienda)
4. @ana +300 (Ganó desafío)

Total: 4 transacciones
Agregar: 1,000 SadoCoins
Quitar: 100 SadoCoins

¿Confirmar? Responde "SI" o "CANCELAR"
```

**Response - Confirmed:**
```
✅ Importación completada

4 transacciones procesadas
3 usuarios recibieron SadoCoins
1 usuario gastó SadoCoins

Evento: Fiesta Enero
Admin: @franco
```

---

### `/exportar`

Export transactions to Excel for records.

**Usage:**
```
/exportar                    (all transactions)
/exportar 30                 (last 30 days)
/exportar evento "Fiesta"    (specific event)
```

**Response:**
Bot sends file: `phantom_export_2024-01-20.xlsx`

---

### `/plantilla`

Get blank Excel template.

**Response:**
Bot sends file: `phantom_template.xlsx`

---

## File Formats Supported

| Format | Extension | Notes |
|--------|-----------|-------|
| Excel | `.xlsx` | Recommended |
| Excel old | `.xls` | Supported |
| CSV | `.csv` | Use UTF-8 encoding |
| Google Sheets | Export as xlsx | Download first |

---

## Validation Rules

Before processing, bot checks:

| Check | Error if fails |
|-------|----------------|
| File format valid | "Formato no soportado" |
| Required columns exist | "Falta columna: username" |
| Usernames valid | "Usuario no encontrado: @xxx" |
| Amounts are numbers | "Cantidad inválida en fila 3" |
| Amounts positive | "Cantidad debe ser positiva" |
| No duplicates | "Fila duplicada: 5 y 8" |

---

## Error Handling

### Partial Success Option

If some rows fail:
```
⚠️ Importación parcial

✅ 8 transacciones exitosas
❌ 2 transacciones fallidas:

Fila 4: @usuario_inexistente - Usuario no encontrado
Fila 7: @maria - Saldo insuficiente para quitar 1000

¿Procesar las exitosas? SI / CANCELAR
```

### Rollback Option

If something goes wrong:
```
❌ Error en importación

Se procesaron 5 de 10 transacciones antes del error.

¿Deshacer todo? SI / NO
```

---

## IRL Event Workflow

### Before Event
1. Download `/plantilla`
2. Prepare Excel with expected rewards
3. Share with event staff

### During Event
1. Record earnings/spending on paper or phone
2. Fill Excel in real-time or after

### After Event
1. Complete Excel file
2. Send to bot with `/importar`
3. Review preview
4. Confirm
5. Users receive notifications

---

## Example: Full Event Flow

### Event: "Noche de Máscaras"

**Activities with SadoCoins:**
| Activity | Earn/Spend | Amount |
|----------|------------|--------|
| Attendance | Earn | 100 |
| Win game | Earn | 200 |
| Auction bid | Spend | Variable |
| Buy drink | Spend | 50 |
| Best costume | Earn | 500 |

**Excel after event:**
| username | tipo | cantidad | motivo |
|----------|------|----------|--------|
| @maria | add | 100 | Asistencia |
| @maria | add | 500 | Mejor disfraz |
| @maria | remove | 300 | Ganó subasta |
| @juan | add | 100 | Asistencia |
| @juan | add | 200 | Ganó juego |
| @pedro | add | 100 | Asistencia |
| @pedro | remove | 50 | Compró bebida |

**Import result:**
```
✅ Evento "Noche de Máscaras" importado

7 transacciones procesadas
3 usuarios afectados

Resumen:
@maria: +300 (tenía 500, ahora 800)
@juan: +300 (tenía 200, ahora 500)
@pedro: +50 (tenía 100, ahora 150)
```

---

## Notifications to Users

After import, users receive DM:

```
🎭 The Phantom

📥 Actualización de SadoCoins

Evento: Noche de Máscaras

+100 Asistencia
+500 Mejor disfraz
-300 Ganó subasta
━━━━━━━━━━━━━━
Neto: +300 SadoCoins

💰 Nuevo saldo: 800 SadoCoins
```

---

## Security

| Measure | Description |
|---------|-------------|
| Admin only | Only admins can import |
| Preview required | Must confirm before processing |
| Audit log | All imports recorded with admin ID |
| Max file size | 1MB limit |
| Max rows | 500 per file |
| Rate limit | 1 import per 5 minutes |

---

## Database Records

Each import creates:
- Transaction records for each row
- Import log entry with:
  - Admin who imported
  - Filename
  - Timestamp
  - Row count
  - Event name (if provided)

---

## Admin Commands Summary

| Command | Description |
|---------|-------------|
| `/importar` | Upload and process file |
| `/exportar` | Download transactions |
| `/plantilla` | Get blank template |
| `/imports` | View import history |
| `/deshacer_import [id]` | Rollback an import |

---

## Technical Notes

### Libraries Needed
- `openpyxl` - Read/write Excel
- `pandas` - Data processing (optional)
- `csv` - CSV handling (built-in)

### File Handling
1. User sends file to bot
2. Bot downloads to temp folder
3. Parse and validate
4. Show preview
5. On confirm: process
6. Delete temp file

---

## Decisions Made

| Question | Decision |
|----------|----------|
| Auto-create users? | ✅ Yes - Create with 0 balance if not exists |
| Negative balance? | ✅ Yes - User marked as "in debt" |
| Notifications? | ⚙️ Optional - Admin can toggle |
| Import approval? | ❌ No - Single admin can import |
| Google Sheets? | ✅ Yes - Real-time sync |

---

## 🔴 Debt System (Negative Balance)

When a user goes negative, they enter "debt" status.

### How It Works

```
User has: 50 SadoCoins
Remove:   200 SadoCoins
Result:   -150 SadoCoins (IN DEBT)
```

### Debt Status Effects

| Restriction | Description |
|-------------|-------------|
| 🚫 Can't transfer | Can't use `/dar` until positive |
| 🚫 Can't bid | Can't participate in auctions |
| 🚫 Can't buy | Can't purchase titles/items |
| 🔴 Marked in profile | Shows "EN DEUDA" badge |
| 🔴 Shown in ranking | Appears at bottom with negative |
| ⚠️ Admin notified | Admins see list of debtors |

### Profile with Debt
```
🎭 Perfil de @pedro

🔴 ESTADO: EN DEUDA

💰 SadoCoins: -150
⚠️ Debe pagar su deuda antes de participar

📜 Debe ser castigado por un admin
```

### Admin Commands for Debt

| Command | Description |
|---------|-------------|
| `/deudores` | List all users in debt |
| `/perdonar_deuda @user` | Clear debt (set to 0) |
| `/cobrar_deuda @user` | Mark debt as "paid" via punishment |

### Debt Notification
```
🔴 ¡ALERTA DE DEUDA!

@pedro ha entrado en deuda: -150 SadoCoins

Motivo: Compras en evento "Noche de Máscaras"

Debe ser castigado o pagar su deuda.

/deudores para ver todos los deudores
```

### Ways to Clear Debt
1. Receive SadoCoins from admin (`/dar_admin`)
2. Receive transfer from another user
3. Admin forgives debt (`/perdonar_deuda`)
4. Admin marks as punished (`/cobrar_deuda`)
5. Earn at next IRL event

---

## 📊 Google Sheets Integration

Real-time sync with Google Sheets for live event tracking.

### How It Works

```
┌─────────────────┐         ┌─────────────────┐
│  GOOGLE SHEET   │◄───────►│   TELEGRAM      │
│                 │  Sync   │     BOT         │
│  Staff edits    │ every   │  Auto-imports   │
│  live during    │ 5 min   │  new rows       │
│  event          │         │                 │
└─────────────────┘         └─────────────────┘
```

### Setup Commands

| Command | Description |
|---------|-------------|
| `/conectar_sheets [URL]` | Link a Google Sheet |
| `/desconectar_sheets` | Remove link |
| `/sync_status` | Check sync status |
| `/sync_now` | Force immediate sync |

### Setup Process

1. Create Google Sheet with template format
2. Share sheet with bot's service account email
3. Use `/conectar_sheets [sheet_url]`
4. Bot validates format
5. Sync begins automatically

### Sheet Format Required

Same as Excel template:

| username | tipo | cantidad | motivo | procesado |
|----------|------|----------|--------|-----------|
| @maria | add | 500 | Premio | |
| @juan | add | 200 | Juego | |

**New column: `procesado`**
- Bot marks rows as "✓" after processing
- Prevents duplicate imports

### Sync Behavior

| Setting | Default | Description |
|---------|---------|-------------|
| Sync interval | 5 minutes | How often to check |
| Auto-notify | OFF | DM users on sync |
| Live mode | OFF | Sync every 1 min during events |

### Commands During Event

```
/evento_live ON     → Sync every 1 minute
/evento_live OFF    → Back to 5 minutes
```

### Sync Response
```
📊 Google Sheets Sync

Última sincronización: hace 2 min
Filas nuevas encontradas: 3

Procesado:
✅ @maria +500 (Premio)
✅ @juan +200 (Juego)
✅ @pedro -100 (Compra)

Próxima sync: en 3 min
```

### Error Handling
```
⚠️ Error de Sync

No se pudo acceder al Google Sheet.

Posibles causas:
- Sheet no compartido con el bot
- URL incorrecta
- Formato de columnas incorrecto

/sync_status para más detalles
```

### Security for Google Sheets

| Measure | Description |
|---------|-------------|
| Read-only option | Bot can only read, not edit |
| Specific sheet | Only syncs from specific tab |
| Admin approval | New connections need admin |
| Audit log | All syncs logged |

---

## Notification Settings

Admins can configure notification preferences:

### Command: `/config_notificaciones`

```
⚙️ Configuración de Notificaciones

Importaciones:
[ON/OFF] Notificar a usuarios al importar

Google Sheets:
[ON/OFF] Notificar en cada sync

Deudas:
[ON/OFF] Notificar cuando alguien entra en deuda

Actualmente: Solo deudas activas
```

### Per-Import Option

When importing:
```
📊 Vista previa de importación...

¿Notificar a los usuarios?
1. SI - Enviar DM a cada usuario
2. NO - Importar silenciosamente

Responde 1 o 2, luego "CONFIRMAR"
```
