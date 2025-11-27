# Import Commands

## /importar

Upload and process Excel/CSV file.

**Usage:**
1. Send `/importar`
2. Attach file

**Response - Preview:**
```
📊 Archivo recibido: evento_enero.xlsx

Vista previa:
1. @maria +500 (Premio subasta)
2. @juan +200 (Participación)
3. @pedro -100 (Compra tienda)

Total: 3 transacciones
Agregar: 700 SadoCoins
Quitar: 100 SadoCoins

¿Confirmar? SI / CANCELAR
```

**Response - Confirmed:**
```
✅ Importación completada

3 transacciones procesadas
```

---

## /exportar

Export transactions to Excel.

**Usage:**
```
/exportar              (all)
/exportar 30           (last 30 days)
```

**Response:**
Bot sends: `phantom_export_2024-01-20.xlsx`

---

## /plantilla

Get blank Excel template.

**Response:**
Bot sends: `phantom_template.xlsx`

---

## /imports

View import history.

**Response:**
```
📦 Historial de Importaciones

1. evento_enero.xlsx (hace 2d)
   60 transacciones por @admin

2. ajustes.csv (hace 1w)
   5 transacciones por @admin

/deshacer_import [id] para revertir
```

---

## /deshacer_import [id]

Rollback an import.

**Response:**
```
🔄 Revirtiendo importación #1...

60 transacciones revertidas
Saldos restaurados

✅ Rollback completado
```
