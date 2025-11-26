# 00 - Project Overview
# Dominion Bank Bot 🖤⛓️

---

## What Is This?

A Telegram bot that manages a virtual economy inside a BDSM group.

- **Currency Name:** Latigazos (whip lashes)
- **Bot Name:** @DominionBankBot
- **Display Name:** Dominion Bank 🖤⛓️

---

## Core Features

### For Regular Users
| Feature | Command | What it does |
|---------|---------|--------------|
| See balance | `/micollar` | Shows how many latigazos you have |
| Transfer | `/servir @user 100` | Give your latigazos to another user |
| Ranking | `/calabozo` | See who has the most latigazos |
| History | `/marcas` | See your transaction history |

### For Admins Only
| Feature | Command | What it does |
|---------|---------|--------------|
| Add coins | `/recompensar @user 500` | Give latigazos to a user (mint) |
| Remove coins | `/castigar @user 200` | Take latigazos from a user (burn) |
| Check anyone | `/versaldo @user` | See any user's balance |

---

## How It Works (Simple Explanation)

```
┌─────────────────────────────────────────────────────────┐
│                    TELEGRAM GROUP                        │
│                                                          │
│   User types: /micollar                                 │
│                    │                                     │
│                    ▼                                     │
│   ┌─────────────────────────────────┐                   │
│   │     Telegram Servers            │                   │
│   │   (receives the message)        │                   │
│   └─────────────────────────────────┘                   │
│                    │                                     │
│                    ▼                                     │
│   ┌─────────────────────────────────┐                   │
│   │    OUR BOT (on Railway.app)     │                   │
│   │                                 │                   │
│   │  1. Receives /micollar          │                   │
│   │  2. Checks database             │                   │
│   │  3. Finds user has 500          │                   │
│   │  4. Sends response back         │                   │
│   └─────────────────────────────────┘                   │
│                    │                                     │
│                    ▼                                     │
│   Bot replies: "🖤 Tu collar vale: 500 latigazos"       │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

---

## Technology Stack

| Component | Technology | Why |
|-----------|------------|-----|
| Language | Python 3.11 | Easy, great Telegram libraries |
| Bot Library | python-telegram-bot | Most popular, well documented |
| Database | SQLite | Free, simple, no server needed |
| Hosting | Railway.app | Free tier, easy deploy |

---

## Key Concepts

### 1. Polling vs Webhooks
We'll use **polling** (simpler):
- Bot constantly asks Telegram: "Any new messages?"
- Telegram responds with new messages
- Easier to set up, works everywhere

### 2. User Identification
- Each Telegram user has a unique `user_id` (number)
- We store this in our database
- We can also store their `@username` for display

### 3. Admin System
- Admin user IDs are stored in configuration
- Before admin commands execute, we check if user is admin
- Regular users get an error if they try admin commands

### 4. Transactions
- Every coin movement is recorded
- This allows us to show history
- Also useful for debugging issues

---

## Design Decisions

| Decision | Choice | Reasoning |
|----------|--------|-----------|
| Currency unit | Integer (whole numbers) | No decimals, simpler math |
| Negative balance | NOT allowed | Users can't go into debt |
| Self-transfer | NOT allowed | Prevents mistakes |
| New user balance | 0 latigazos | Admins control the economy |
| Transaction history | Store all | Transparency, debugging |

---

## Files We'll Create

See [01-STRUCTURE.md](01-STRUCTURE.md) for the complete file structure.

---

## Next Steps

1. Review [01-STRUCTURE.md](01-STRUCTURE.md) - Understand the files
2. Review [02-DATABASE.md](02-DATABASE.md) - Understand data storage
3. Review [03-COMMANDS.md](03-COMMANDS.md) - Understand each command
4. Review [04-MESSAGES.md](04-MESSAGES.md) - Customize bot messages
5. Review [05-LOGIC-FLOWS.md](05-LOGIC-FLOWS.md) - Understand the logic
6. Follow [07-SETUP.md](07-SETUP.md) - Create the bot on Telegram
7. Follow [08-DEPLOYMENT.md](08-DEPLOYMENT.md) - Deploy to Railway
