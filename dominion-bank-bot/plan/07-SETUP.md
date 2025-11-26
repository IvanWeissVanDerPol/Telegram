# 07 - Setup Guide

Step-by-step guide to set everything up.

---

## Overview

| Step | What | Time |
|------|------|------|
| 1 | Create bot on Telegram | 5 min |
| 2 | Get your admin user IDs | 5 min |
| 3 | Set up development environment | 10 min |
| 4 | Configure the bot | 5 min |
| 5 | Test locally | 10 min |

---

## Step 1: Create Bot on Telegram

### 1.1 Open BotFather
1. Open Telegram
2. Search for `@BotFather`
3. Start a chat with it

### 1.2 Create New Bot
Send these messages to BotFather:

```
/newbot
```

BotFather asks: "What name do you want for your bot?"
```
{{BOT_NAME}}
```

BotFather asks: "Choose a username for your bot"
```
{{BOT_USERNAME}}
```
(Must end in `bot`, like `DominionBankBot`)

### 1.3 Save Your Token
BotFather will respond with something like:
```
Done! Congratulations on your new bot.
You will find it at t.me/DominionBankBot

Use this token to access the HTTP API:
123456789:ABCdefGHIjklMNOpqrsTUVwxyz
```

**⚠️ SAVE THIS TOKEN! Keep it secret!**

### 1.4 Set Bot Description (Optional)
```
/setdescription
```
Select your bot, then send:
```
🖤 Bot de economía virtual para grupos BDSM.
Gana, envía y recibe {{CURRENCY_NAME}}.
```

### 1.5 Set Bot Commands (Optional)
```
/setcommands
```
Select your bot, then send:
```
micollar - Ver tu saldo
servir - Transferir a otro usuario
calabozo - Ver ranking
marcas - Ver tu historial
```

---

## Step 2: Get Admin User IDs

### What is a User ID?
- Every Telegram user has a unique numeric ID
- Example: `123456789`
- This never changes (unlike @username)

### How to Get Your User ID

**Method 1: Use @userinfobot**
1. Open Telegram
2. Search for `@userinfobot`
3. Send `/start`
4. Bot replies with your ID

**Method 2: Use @getmyid_bot**
1. Search for `@getmyid_bot`
2. Send `/start`
3. Copy the ID shown

### Record All Admin IDs
Write down the user ID for each person who should be admin:

```
Admin 1 (name): _______________
Admin 2 (name): _______________
Admin 3 (name): _______________
```

---

## Step 3: Set Up Development Environment

### 3.1 Install Python

**Windows:**
1. Go to https://www.python.org/downloads/
2. Download Python 3.11 or newer
3. Run installer
4. ✅ Check "Add Python to PATH"
5. Click Install

**Verify installation:**
```bash
python --version
# Should show: Python 3.11.x
```

### 3.2 Create Project Folder
```bash
# Navigate to where you want the project
cd Documents

# Create folder
mkdir {{BOT_FOLDER_NAME}}
cd {{BOT_FOLDER_NAME}}
```

### 3.3 Create Virtual Environment
```bash
# Create virtual environment
python -m venv venv

# Activate it
# On Windows:
venv\Scripts\activate

# On Mac/Linux:
source venv/bin/activate
```

You should see `(venv)` in your terminal prompt.

### 3.4 Install Dependencies
```bash
pip install python-telegram-bot python-dotenv
```

### 3.5 Verify Installation
```bash
pip list
```
Should show:
```
python-telegram-bot   20.x
python-dotenv         1.x
```

---

## Step 4: Configure the Bot

### 4.1 Create .env File
Create a file named `.env` (no extension) in your project folder:

```env
# Bot Configuration
BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz

# Admin User IDs (comma-separated)
ADMIN_IDS=123456789,987654321

# Currency Settings
CURRENCY_NAME=latigazos
CURRENCY_EMOJI=🖤

# Initial balance for new users
INITIAL_BALANCE=0
```

### 4.2 Create .env.example
Create a safe-to-share template:

```env
# Bot Configuration
BOT_TOKEN=your-bot-token-here

# Admin User IDs (comma-separated)
ADMIN_IDS=123456789,987654321

# Currency Settings
CURRENCY_NAME=latigazos
CURRENCY_EMOJI=🖤

# Initial balance for new users
INITIAL_BALANCE=0
```

### 4.3 Create .gitignore
```
# Secrets
.env

# Database
*.db

# Python
__pycache__/
*.pyc
venv/

# IDE
.vscode/
.idea/
```

---

## Step 5: Test Locally

### 5.1 Run the Bot
```bash
python bot.py
```

You should see:
```
INFO - 🖤 Iniciando {{BOT_NAME}}...
INFO - 📦 Inicializando base de datos...
INFO - 🤖 Creando aplicación del bot...
INFO - 📝 Registrando comandos...
INFO - ✅ Bot iniciado! Escuchando mensajes...
```

### 5.2 Test in Telegram
1. Open Telegram
2. Search for your bot: `@{{BOT_USERNAME}}`
3. Send `/start`
4. You should get a welcome message

### 5.3 Test Commands
```
/start          → Should show welcome
/micollar       → Should show balance (0)
/calabozo       → Should show empty ranking
```

### 5.4 Test Admin Commands
As an admin:
```
/recompensar @yourself 100    → Should add coins
/micollar                     → Should show 100
```

### 5.5 Stop the Bot
Press `Ctrl+C` in the terminal.

---

## Troubleshooting

### "ModuleNotFoundError: No module named 'telegram'"
```bash
pip install python-telegram-bot
```

### "Invalid token"
- Check your `.env` file
- Make sure BOT_TOKEN is correct
- No extra spaces or quotes

### Bot doesn't respond
- Is the bot running? (Check terminal)
- Did you start a chat with the bot first?
- Check for errors in terminal

### "User not found" errors
- Make sure the user has interacted with the bot at least once
- Try having them send `/start` first

---

## Next Steps

Once testing works locally:
1. See [08-DEPLOYMENT.md](08-DEPLOYMENT.md) to put it online 24/7
2. Add bot to your group
3. Configure group settings

---

## Checklist

Before moving to deployment:

- [ ] Bot token saved securely
- [ ] All admin IDs collected
- [ ] Python installed
- [ ] Virtual environment created
- [ ] Dependencies installed
- [ ] .env configured
- [ ] Bot runs locally
- [ ] /start command works
- [ ] /micollar command works
- [ ] /recompensar command works (as admin)
- [ ] .gitignore includes .env

---

## Next: [08-DEPLOYMENT.md](08-DEPLOYMENT.md)
