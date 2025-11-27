# Development Environment Setup

## Install Python

### Windows
1. Go to https://python.org/downloads/
2. Download Python 3.11+
3. Run installer
4. **Check "Add Python to PATH"**
5. Install

### Verify
```bash
python --version
# Should show: Python 3.11.x
```

---

## Create Project

```bash
# Create folder
mkdir dominion-bank-bot
cd dominion-bank-bot

# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Mac/Linux)
source venv/bin/activate
```

You should see `(venv)` in your prompt.

---

## Install Dependencies

```bash
pip install python-telegram-bot python-dotenv openpyxl
```

### Verify
```bash
pip list
```
Should show:
```
python-telegram-bot   20.x
python-dotenv         1.x
openpyxl             3.x
```

---

## Create Configuration Files

### .env
```env
BOT_TOKEN=your-bot-token-here
ADMIN_IDS=123456789,987654321
CURRENCY_NAME=SadoCoins
CURRENCY_EMOJI=⛓️
INITIAL_BALANCE=0
```

### .env.example (safe to share)
```env
BOT_TOKEN=your-bot-token-here
ADMIN_IDS=123456789,987654321
CURRENCY_NAME=SadoCoins
CURRENCY_EMOJI=⛓️
INITIAL_BALANCE=0
```

### .gitignore
```
.env
*.db
__pycache__/
*.pyc
venv/
.vscode/
.idea/
```

---

## Test Locally

```bash
python bot.py
```

Should show:
```
INFO - Starting The Phantom...
INFO - Database initialized
INFO - Bot started! Listening...
```

Test in Telegram:
```
/start
/ver
```
