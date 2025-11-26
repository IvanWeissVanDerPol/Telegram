# 01 - Project Structure

---

## Complete Folder Structure

```
dominion-bank-bot/
│
├── plan/                       # 📋 THIS FOLDER - Planning docs
│   ├── 00-OVERVIEW.md
│   ├── 01-STRUCTURE.md         # (you are here)
│   ├── 02-DATABASE.md
│   ├── 03-COMMANDS.md
│   ├── 04-MESSAGES.md
│   ├── 05-LOGIC-FLOWS.md
│   ├── 06-VALIDATIONS.md
│   ├── 07-SETUP.md
│   └── 08-DEPLOYMENT.md
│
├── config/                     # ⚙️ Configuration files
│   ├── __init__.py
│   ├── settings.py             # Bot token, admin IDs, constants
│   └── messages.py             # All bot response messages
│
├── database/                   # 💾 Database layer
│   ├── __init__.py
│   ├── connection.py           # SQLite connection setup
│   ├── models.py               # User and Transaction table definitions
│   └── operations.py           # CRUD functions (create, read, update, delete)
│
├── handlers/                   # 🎮 Command handlers
│   ├── __init__.py
│   ├── start.py                # /start command
│   ├── balance.py              # /micollar command
│   ├── transfer.py             # /servir command
│   ├── admin_add.py            # /recompensar command
│   ├── admin_remove.py         # /castigar command
│   ├── ranking.py              # /calabozo command
│   └── history.py              # /marcas command
│
├── utils/                      # 🔧 Utility functions
│   ├── __init__.py
│   ├── validators.py           # Input validation functions
│   ├── decorators.py           # @admin_only decorator
│   └── helpers.py              # Misc helper functions
│
├── bot.py                      # 🚀 MAIN ENTRY POINT
├── requirements.txt            # 📦 Python dependencies
├── Procfile                    # 🚂 Railway deployment config
├── runtime.txt                 # 🐍 Python version
├── .env.example                # 🔐 Example environment variables
├── .env                        # 🔐 YOUR actual secrets (not in git)
├── .gitignore                  # 🚫 Files to ignore in git
└── wallets.db                  # 💾 SQLite database (auto-created)
```

---

## File Descriptions

### Root Files

| File | Purpose |
|------|---------|
| `bot.py` | **Main file** - Run this to start the bot. Loads config, initializes DB, registers handlers, starts polling |
| `requirements.txt` | Lists Python packages needed (python-telegram-bot, python-dotenv) |
| `Procfile` | Tells Railway how to run the bot: `worker: python bot.py` |
| `runtime.txt` | Specifies Python version: `python-3.11.0` |
| `.env.example` | Template for environment variables (safe to share) |
| `.env` | **YOUR secrets** - Bot token, admin IDs (NEVER share/commit) |
| `.gitignore` | Tells git to ignore `.env`, `wallets.db`, `__pycache__` |
| `wallets.db` | SQLite database file (created automatically on first run) |

---

### config/ Folder

| File | Purpose | Contains |
|------|---------|----------|
| `settings.py` | All configuration | BOT_TOKEN, ADMIN_IDS, CURRENCY_NAME, INITIAL_BALANCE |
| `messages.py` | All bot messages | Welcome text, error messages, success messages (all themed) |

**Why separate?**
- Easy to change messages without touching logic
- Easy to translate to another language
- All configuration in one place

---

### database/ Folder

| File | Purpose | Contains |
|------|---------|----------|
| `connection.py` | Database setup | Connect to SQLite, create tables if not exist |
| `models.py` | Data structures | User table, Transaction table definitions |
| `operations.py` | Database actions | get_user(), update_balance(), create_transaction(), etc. |

**Why separate?**
- `models.py` = WHAT data looks like
- `operations.py` = HOW to manipulate data
- `connection.py` = WHERE data is stored

---

### handlers/ Folder

Each file handles ONE command:

| File | Command | User Type |
|------|---------|-----------|
| `start.py` | `/start` | Everyone |
| `balance.py` | `/micollar` | Everyone |
| `transfer.py` | `/servir` | Everyone |
| `ranking.py` | `/calabozo` | Everyone |
| `history.py` | `/marcas` | Everyone |
| `admin_add.py` | `/recompensar` | Admin only |
| `admin_remove.py` | `/castigar` | Admin only |

**Why separate?**
- Easy to find code for specific command
- Easy to modify one command without affecting others
- Clean and organized

---

### utils/ Folder

| File | Purpose | Contains |
|------|---------|----------|
| `validators.py` | Check inputs | is_valid_amount(), is_valid_user(), parse_command_args() |
| `decorators.py` | Access control | @admin_only decorator to protect admin commands |
| `helpers.py` | Misc utilities | format_balance(), get_username_display(), etc. |

**Why separate?**
- Reusable across multiple handlers
- Keeps handlers clean and focused
- Easy to test individually

---

## Import Flow Diagram

```
bot.py (main)
    │
    ├── imports from config/
    │   ├── settings.py (BOT_TOKEN)
    │   └── messages.py (all messages)
    │
    ├── imports from database/
    │   └── connection.py (init_database)
    │
    └── imports from handlers/
        ├── start.py
        ├── balance.py ──────┐
        ├── transfer.py ─────┤
        ├── admin_add.py ────┤── each handler imports from:
        ├── admin_remove.py ─┤       ├── database/operations.py
        ├── ranking.py ──────┤       ├── config/messages.py
        └── history.py ──────┘       └── utils/*.py
```

---

## Which Files to Edit for What

| I want to... | Edit this file |
|--------------|----------------|
| Change bot token | `.env` |
| Add/remove admins | `.env` |
| Change currency name | `config/settings.py` |
| Change bot messages | `config/messages.py` |
| Change how balance works | `handlers/balance.py` |
| Change transfer logic | `handlers/transfer.py` |
| Change database structure | `database/models.py` |
| Add a new command | Create new file in `handlers/`, register in `bot.py` |
| Change validation rules | `utils/validators.py` |

---

## Next: [02-DATABASE.md](02-DATABASE.md)
