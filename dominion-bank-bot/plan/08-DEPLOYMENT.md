# 08 - Deployment Guide

How to put your bot online 24/7 for FREE.

---

## Hosting Options Comparison

| Platform | Free Tier | Always On | Ease | Best For |
|----------|-----------|-----------|------|----------|
| **Railway.app** | 500 hrs/month | ✅ Yes | ⭐⭐⭐⭐ Easy | ✅ Recommended |
| **Render.com** | 750 hrs/month | ❌ Sleeps | ⭐⭐⭐⭐ Easy | Backup option |
| **Fly.io** | 3 VMs free | ✅ Yes | ⭐⭐⭐ Medium | Alternative |
| **PythonAnywhere** | Limited | ❌ Limits | ⭐⭐⭐⭐⭐ Very Easy | Learning |
| **Oracle Cloud** | Always free VM | ✅ Yes | ⭐⭐ Hard | Advanced |
| **Your PC** | Free | ❌ Must stay on | ⭐⭐⭐⭐⭐ | Development |

**Recommendation:** Start with **Railway.app**

---

## Method 1: Railway.app (Recommended)

### Why Railway?
- ✅ 500 free hours/month (enough for 24/7)
- ✅ No credit card needed to start
- ✅ Auto-deploy from GitHub
- ✅ Easy environment variables
- ✅ Persistent storage for SQLite

### Step 1: Prepare Files for Deployment

Create these files in your project:

**requirements.txt**
```
python-telegram-bot>=20.0
python-dotenv>=1.0.0
```

**Procfile** (no extension)
```
worker: python bot.py
```

**runtime.txt**
```
python-3.11.0
```

### Step 2: Create GitHub Repository

1. Go to https://github.com
2. Create account (if needed)
3. Click "New Repository"
4. Name: `{{BOT_FOLDER_NAME}}`
5. Private: ✅ Yes (recommended)
6. Click "Create repository"

### Step 3: Push Code to GitHub

```bash
# In your project folder
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/{{BOT_FOLDER_NAME}}.git
git push -u origin main
```

### Step 4: Deploy on Railway

1. Go to https://railway.app
2. Click "Login" → "Login with GitHub"
3. Authorize Railway
4. Click "New Project"
5. Select "Deploy from GitHub repo"
6. Find and select your bot repository
7. Click "Deploy Now"

### Step 5: Add Environment Variables

1. In Railway, click on your project
2. Go to "Variables" tab
3. Click "New Variable"
4. Add each variable:

```
BOT_TOKEN = your-actual-token
ADMIN_IDS = 123456789,987654321
CURRENCY_NAME = latigazos
CURRENCY_EMOJI = 🖤
INITIAL_BALANCE = 0
```

### Step 6: Verify Deployment

1. Go to "Deployments" tab
2. Click on latest deployment
3. Check logs for:
```
✅ Bot iniciado! Escuchando mensajes...
```

### Step 7: Test Your Live Bot

1. Open Telegram
2. Find your bot
3. Send `/start`
4. Should respond immediately!

---

## Method 2: Render.com (Alternative)

### Limitations
- Free tier sleeps after 15 min of inactivity
- Wakes up when message received (30 sec delay)
- Good for low-traffic bots

### Steps

1. Go to https://render.com
2. Sign up with GitHub
3. Click "New +" → "Background Worker"
4. Connect your GitHub repo
5. Configure:
   - Name: `{{BOT_FOLDER_NAME}}`
   - Runtime: Python 3
   - Build: `pip install -r requirements.txt`
   - Start: `python bot.py`
6. Add environment variables
7. Click "Create Background Worker"

---

## Method 3: Fly.io (Alternative)

### Pros
- 3 shared VMs free forever
- Good reliability
- Global edge deployment

### Setup

1. Install flyctl:
```bash
# Windows (PowerShell)
iwr https://fly.io/install.ps1 -useb | iex
```

2. Login:
```bash
fly auth login
```

3. Create fly.toml:
```toml
app = "{{BOT_FOLDER_NAME}}"
primary_region = "mia"

[build]
  builder = "paketobuildpacks/builder:base"

[env]
  CURRENCY_NAME = "latigazos"

[processes]
  worker = "python bot.py"
```

4. Set secrets:
```bash
fly secrets set BOT_TOKEN=your-token
fly secrets set ADMIN_IDS=123,456
```

5. Deploy:
```bash
fly launch
fly deploy
```

---

## Database Persistence

### The Problem
- Railway/Render reset file system on deploy
- SQLite database (`wallets.db`) would be lost!

### Solutions

**Option A: Railway Volume (Recommended)**
1. In Railway, add a Volume
2. Mount path: `/data`
3. Update code to use `/data/wallets.db`

**Option B: Use PostgreSQL**
- Railway offers free PostgreSQL
- More robust, but requires code changes
- Better for larger bots

**Option C: External Database**
- Use free tier of:
  - Supabase (PostgreSQL)
  - PlanetScale (MySQL)
  - MongoDB Atlas

### For SQLite with Railway Volume

Update your database connection:
```python
import os

# Use /data for Railway, local folder for development
if os.environ.get('RAILWAY_ENVIRONMENT'):
    DB_PATH = '/data/wallets.db'
else:
    DB_PATH = 'wallets.db'
```

---

## Adding Bot to Your Group

### Step 1: Add Bot to Group
1. Open your Telegram group
2. Click group name → "Edit"
3. Click "Add Members"
4. Search for your bot: `@{{BOT_USERNAME}}`
5. Add it

### Step 2: Make Bot Admin (Important!)
1. Group settings → "Administrators"
2. Click "Add Administrator"
3. Select your bot
4. Grant permissions:
   - ✅ Delete messages (optional)
   - ✅ Pin messages (optional)
   - Other permissions as needed

### Step 3: Configure Bot Privacy

**Option A: Bot sees all messages**
1. Talk to @BotFather
2. Send `/setprivacy`
3. Select your bot
4. Choose "Disable"

**Option B: Bot only sees commands**
- Default behavior
- More private
- Bot won't see regular chat

### Step 4: Test in Group
Send in the group:
```
/start
/micollar
```

Bot should respond!

---

## Monitoring & Maintenance

### Check Bot Status

**Railway:**
- Dashboard → Your project → Deployments
- Check logs for errors

**Telegram:**
- Send `/micollar` - if it responds, bot is alive

### Automatic Restarts

Railway automatically restarts crashed bots.

### Updating the Bot

1. Make changes locally
2. Test locally
3. Commit and push:
```bash
git add .
git commit -m "Update: description"
git push
```
4. Railway auto-deploys!

---

## Troubleshooting Deployment

### "Build failed"
- Check `requirements.txt` is correct
- Check `runtime.txt` Python version

### "Bot not responding"
- Check environment variables are set
- Check logs for errors
- Verify BOT_TOKEN is correct

### "Database empty after deploy"
- Set up Volume/persistent storage
- Or migrate to PostgreSQL

### "Error: Unauthorized"
- BOT_TOKEN is wrong
- Generate new token with BotFather

---

## Cost Summary

| Service | Monthly Cost |
|---------|--------------|
| Railway.app | $0 (500 hrs) |
| GitHub | $0 |
| Telegram API | $0 |
| Domain | Not needed |
| **Total** | **$0** |

---

## Deployment Checklist

- [ ] requirements.txt created
- [ ] Procfile created
- [ ] runtime.txt created
- [ ] .gitignore includes .env
- [ ] Code pushed to GitHub
- [ ] Railway project created
- [ ] Environment variables set
- [ ] Deployment successful (check logs)
- [ ] Bot responds to /start
- [ ] Volume/persistence configured
- [ ] Bot added to group
- [ ] Bot is admin in group
- [ ] All commands work in group

---

## You're Done! 🎉

Your bot is now:
- ✅ Running 24/7
- ✅ Auto-deploying on updates
- ✅ Free forever
- ✅ Ready for your group!
