# Project Structure

## Folder Layout

```
dominion-bank-bot/
├── plan/                   # Planning docs (this folder)
├── config/                 # Configuration
│   ├── __init__.py
│   ├── settings.py         # Bot token, admin IDs
│   └── messages.py         # All bot messages
├── database/               # Database layer
│   ├── __init__.py
│   ├── connection.py       # DB connection
│   ├── models.py           # Table definitions
│   └── operations.py       # CRUD functions
├── handlers/               # Command handlers
│   ├── __init__.py
│   ├── core/               # Basic commands
│   ├── admin/              # Admin commands
│   └── bdsm/               # BDSM features
├── utils/                  # Utilities
│   ├── __init__.py
│   ├── validators.py       # Input validation
│   ├── decorators.py       # @admin_only etc
│   └── helpers.py          # Helper functions
├── bot.py                  # Main entry point
├── requirements.txt        # Dependencies
├── Procfile               # Railway config
├── runtime.txt            # Python version
├── .env.example           # Env template
└── .gitignore             # Git ignore
```

---

## File Purposes

### Root Files
| File | Purpose |
|------|---------|
| `bot.py` | Main entry - starts bot |
| `requirements.txt` | Python packages |
| `Procfile` | Railway startup command |
| `.env` | Secrets (not in git) |

### config/
| File | Purpose |
|------|---------|
| `settings.py` | BOT_TOKEN, ADMIN_IDS, constants |
| `messages.py` | All bot response text |

### database/
| File | Purpose |
|------|---------|
| `connection.py` | SQLite/PostgreSQL setup |
| `models.py` | Table schemas |
| `operations.py` | get_user(), transfer(), etc |

### handlers/
One file per command or feature group.

### utils/
| File | Purpose |
|------|---------|
| `validators.py` | Check amounts, users |
| `decorators.py` | @admin_only |
| `helpers.py` | Format numbers, dates |
