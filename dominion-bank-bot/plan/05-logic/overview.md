# Logic Flows Overview

Step-by-step logic for each operation.

## Flow Categories

| Category | Files | Description |
|----------|-------|-------------|
| Core | `core-flows.md` | Balance, transfer |
| Admin | `admin-flows.md` | Give, remove coins |
| Validation | `validation-flows.md` | Input checking |
| Atomic | `atomic-operations.md` | Transaction safety |

---

## General Pattern

Every command follows:

```
1. Parse input
2. Validate input
3. Check permissions
4. Check business rules
5. Execute operation (atomic)
6. Send response
7. Send notifications
```

---

## See Individual Files

- [core-flows.md](core-flows.md) - Balance, transfer, ranking
- [admin-flows.md](admin-flows.md) - Admin operations
- [validation-flows.md](validation-flows.md) - Input validation
- [atomic-operations.md](atomic-operations.md) - Database transactions
