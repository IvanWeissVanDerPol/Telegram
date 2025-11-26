# 📋 Project Plan - {{BOT_NAME}}

## Documentation Index

| # | File | Description | Read When |
|---|------|-------------|-----------|
| 00 | [OVERVIEW.md](00-OVERVIEW.md) | What we're building | **First** |
| 01 | [STRUCTURE.md](01-STRUCTURE.md) | Files and folders | Understanding code organization |
| 02 | [DATABASE.md](02-DATABASE.md) | Data storage | Working on database |
| 03 | [COMMANDS.md](03-COMMANDS.md) | All bot commands | Working on any command |
| 04 | [MESSAGES.md](04-MESSAGES.md) | Bot responses | Customizing messages |
| 05 | [LOGIC-FLOWS.md](05-LOGIC-FLOWS.md) | How each feature works | Understanding logic |
| 06 | [VALIDATIONS.md](06-VALIDATIONS.md) | Input checking | Adding validation |
| 07 | [SETUP.md](07-SETUP.md) | Initial setup | **Before coding** |
| 08 | [DEPLOYMENT.md](08-DEPLOYMENT.md) | Going live | After code works |
| 09 | [NAMING-OPTIONS.md](09-NAMING-OPTIONS.md) | Choose names | **Decide before coding** |

---

## Quick Start

### 1. First, decide on names
Open [09-NAMING-OPTIONS.md](09-NAMING-OPTIONS.md) and fill in your choices:
- Bot name
- Currency name
- Command names
- Message style

### 2. Understand the project
Read these in order:
1. [00-OVERVIEW.md](00-OVERVIEW.md)
2. [01-STRUCTURE.md](01-STRUCTURE.md)
3. [03-COMMANDS.md](03-COMMANDS.md)

### 3. Setup before coding
Follow [07-SETUP.md](07-SETUP.md) to:
- Create bot on Telegram
- Get admin IDs
- Set up Python environment

### 4. Code the bot
We'll work on each file based on:
- [02-DATABASE.md](02-DATABASE.md) - Database layer
- [05-LOGIC-FLOWS.md](05-LOGIC-FLOWS.md) - Command logic
- [06-VALIDATIONS.md](06-VALIDATIONS.md) - Input handling
- [04-MESSAGES.md](04-MESSAGES.md) - Bot responses

### 5. Deploy
Follow [08-DEPLOYMENT.md](08-DEPLOYMENT.md)

---

## Status

| Component | Status | Notes |
|-----------|--------|-------|
| Planning | ✅ Complete | All docs written |
| Naming decisions | ⏳ Pending | Fill out 09-NAMING-OPTIONS.md |
| Telegram bot created | ⏳ Pending | Follow 07-SETUP.md |
| Code written | ⏳ Pending | |
| Testing | ⏳ Pending | |
| Deployment | ⏳ Pending | |

---

## Pending Decisions

These need to be decided before coding:

1. **Currency name** - See [09-NAMING-OPTIONS.md](09-NAMING-OPTIONS.md)
2. **Bot name** - See [09-NAMING-OPTIONS.md](09-NAMING-OPTIONS.md)
3. **Command names** - Themed or simple?
4. **Castigar behavior** - Reject if not enough, or set to 0?
5. **Message style** - Formal, playful, or roleplay?

---

## Files to Create (Code)

When we start coding, we'll create:

```
dominion-bank-bot/
├── bot.py
├── requirements.txt
├── Procfile
├── runtime.txt
├── .env
├── .gitignore
├── config/
│   ├── __init__.py
│   ├── settings.py
│   └── messages.py
├── database/
│   ├── __init__.py
│   ├── connection.py
│   ├── models.py
│   └── operations.py
├── handlers/
│   ├── __init__.py
│   ├── start.py
│   ├── balance.py
│   ├── transfer.py
│   ├── admin_add.py
│   ├── admin_remove.py
│   ├── ranking.py
│   └── history.py
└── utils/
    ├── __init__.py
    ├── validators.py
    ├── decorators.py
    └── helpers.py
```

---

## Next Action

👉 **Open [09-NAMING-OPTIONS.md](09-NAMING-OPTIONS.md) and make your choices!**

Then let me know when you're ready to start coding.
