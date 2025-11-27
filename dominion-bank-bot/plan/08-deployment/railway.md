# Deploy to Railway

## Why Railway?

- 500 free hours/month (enough for 24/7)
- No credit card needed
- Auto-deploy from GitHub
- Easy environment variables
- Persistent storage

---

## Prepare Files

### requirements.txt
```
python-telegram-bot>=20.0
python-dotenv>=1.0.0
openpyxl>=3.1.0
```

### Procfile
```
worker: python bot.py
```

### runtime.txt
```
python-3.11.0
```

---

## Push to GitHub

```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/YOU/dominion-bank-bot.git
git push -u origin main
```

---

## Deploy on Railway

1. Go to https://railway.app
2. Login with GitHub
3. "New Project" → "Deploy from GitHub"
4. Select your repo
5. "Deploy Now"

---

## Set Environment Variables

In Railway dashboard → Variables:

```
BOT_TOKEN = your-actual-token
ADMIN_IDS = 123456789,987654321
CURRENCY_NAME = SadoCoins
CURRENCY_EMOJI = ⛓️
```

---

## Add Volume (Database Persistence)

1. In Railway, add Volume
2. Mount path: `/data`
3. Update code:
```python
import os
if os.environ.get('RAILWAY_ENVIRONMENT'):
    DB_PATH = '/data/wallets.db'
else:
    DB_PATH = 'wallets.db'
```

---

## Verify

1. Deployments tab → check logs
2. Should see: "Bot started!"
3. Test in Telegram: `/start`
