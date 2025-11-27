# Import Flow

## How Files Connect

```
bot.py (main)
    │
    ├── config/
    │   ├── settings.py (BOT_TOKEN, ADMIN_IDS)
    │   └── messages.py (all messages)
    │
    ├── database/
    │   └── connection.py (init_database)
    │
    └── handlers/
        ├── core/*.py
        ├── admin/*.py
        └── bdsm/*.py
            │
            └── Each handler imports:
                ├── database/operations.py
                ├── config/messages.py
                └── utils/*.py
```

---

## Which File to Edit

| I want to... | Edit |
|--------------|------|
| Change bot token | `.env` |
| Add/remove admins | `.env` |
| Change currency name | `config/settings.py` |
| Change bot messages | `config/messages.py` |
| Change balance logic | `handlers/core/balance.py` |
| Change transfer logic | `handlers/core/transfer.py` |
| Add new command | New file in `handlers/` |
| Change validation | `utils/validators.py` |
