# Excel Import Overview

## Purpose

Import coin transactions from IRL events via Excel/CSV files.

---

## Use Cases

| Scenario | Example |
|----------|---------|
| IRL Event earnings | User earned 500 SC at party |
| IRL Event spending | User spent 200 SC at auction |
| Bulk rewards | Give 100 SC to all attendees |
| Corrections | Fix wrong transactions |
| Migration | Import from old system |

---

## Workflow

```
IRL EVENT → Paper/Phone notes
    ↓
EXCEL → Fill template
    ↓
BOT → /importar + file
    ↓
DATABASE → Balances updated
```

---

## Files

- [template.md](template.md) - Excel format
- [commands.md](commands.md) - Import commands
- [validation.md](validation.md) - Data validation
