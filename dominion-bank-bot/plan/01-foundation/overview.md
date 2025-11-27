# Project Overview

## What Is This?

A Telegram bot that manages a virtual economy inside a BDSM group.

| Item | Value |
|------|-------|
| Bot Username | `@ThePhantomBot` |
| Display Name | The Phantom |
| Currency | SadoCoins |
| Currency Emoji | ⛓️ |

---

## Core Features

### For Regular Users
| Feature | Command | Description |
|---------|---------|-------------|
| Balance | `/ver` | Check your SadoCoins |
| Transfer | `/dar @user 100` | Send to another user |
| Ranking | `/ranking` | See leaderboard |
| History | `/historial` | Transaction history |

### For Admins
| Feature | Command | Description |
|---------|---------|-------------|
| Give coins | `/dar_admin @user 500` | Mint SadoCoins |
| Remove coins | `/quitar @user 200` | Burn SadoCoins |
| Check balance | `/saldo @user` | See any user's balance |

---

## How It Works

```
User types command → Telegram → Bot (Railway) → Database → Response
```

---

## Technology Stack

| Component | Technology |
|-----------|------------|
| Language | Python 3.11 |
| Bot Library | python-telegram-bot |
| Database | SQLite / PostgreSQL |
| Hosting | Railway.app |

---

## Design Decisions

| Decision | Choice | Reasoning |
|----------|--------|-----------|
| Currency unit | Integer | No decimals, simpler |
| Negative balance | Allowed (debt) | Part of roleplay |
| Self-transfer | NOT allowed | Prevents abuse |
| New user balance | 0 | Admins control economy |
