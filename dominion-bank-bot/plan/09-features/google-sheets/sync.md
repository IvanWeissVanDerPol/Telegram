# Google Sheets Sync

## Overview

Real-time sync with Google Sheets for live event tracking.

```
GOOGLE SHEET ◄──────► BOT
Staff edits     Sync    Auto-imports
live            every   new rows
                5 min
```

---

## Setup Commands

### /conectar_sheets [URL]

Link a Google Sheet.

```
/conectar_sheets https://docs.google.com/spreadsheets/d/xxx
```

**Response:**
```
✅ Google Sheet conectado

Nombre: Evento Enero
Filas detectadas: 15

Sync automático cada 5 minutos.
/sync_now para sincronizar ahora
```

### /desconectar_sheets

Remove link.

### /sync_status

Check sync status.

```
📊 Estado de Sync

Última sync: hace 2 min
Próxima sync: en 3 min
Modo: Normal (cada 5 min)
Filas procesadas hoy: 45
```

### /sync_now

Force immediate sync.

---

## Sheet Format

Same as Excel template, plus:

| username | tipo | cantidad | motivo | procesado |
|----------|------|----------|--------|-----------|
| @maria | add | 500 | Premio | ✓ |
| @juan | add | 200 | Juego | ✓ |
| @pedro | add | 100 | Nuevo | |

The `procesado` column is marked by bot after processing.

---

## Live Event Mode

During events, sync more frequently:

```
/evento_live ON   → Sync every 1 minute
/evento_live OFF  → Back to 5 minutes
```

---

## Sync Response

```
📊 Google Sheets Sync

Filas nuevas: 3

Procesado:
✅ @maria +500 (Premio)
✅ @juan +200 (Juego)
✅ @pedro +100 (Nuevo)

Próxima sync: en 5 min
```
