# Excel Template Format

## Simple Format

| username | tipo | cantidad | motivo |
|----------|------|----------|--------|
| @maria | add | 500 | Premio subasta |
| @juan | add | 200 | Participación |
| @pedro | remove | 100 | Compra tienda |

---

## Columns

| Column | Required | Values | Description |
|--------|----------|--------|-------------|
| `username` | ✅ | @user | Telegram username |
| `tipo` | ✅ | add/remove/set | Action type |
| `cantidad` | ✅ | Number | How much |
| `motivo` | ❌ | Text | Reason (for records) |

---

## Action Types

| Type | Effect |
|------|--------|
| `add` | Add to balance |
| `remove` | Subtract from balance |
| `set` | Set exact balance |

---

## Advanced Format

| username | tipo | cantidad | motivo | evento | fecha |
|----------|------|----------|--------|--------|-------|
| @maria | add | 500 | Premio | Fiesta | 2024-01-20 |

---

## Transfer Format

For IRL user-to-user transfers:

| from | to | cantidad | motivo |
|------|-----|----------|--------|
| @maria | @juan | 100 | Pago apuesta |

---

## Supported Formats

| Format | Extension |
|--------|-----------|
| Excel | `.xlsx` |
| Excel old | `.xls` |
| CSV | `.csv` (UTF-8) |
