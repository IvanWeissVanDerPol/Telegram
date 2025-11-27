# Add Bot to Group

## Step 1: Add Bot

1. Open your Telegram group
2. Click group name → "Edit"
3. "Add Members"
4. Search: `@ThePhantomBot`
5. Add it

---

## Step 2: Make Bot Admin

1. Group settings → "Administrators"
2. "Add Administrator"
3. Select your bot
4. Grant permissions:
   - ✅ Delete messages (optional)
   - ✅ Pin messages (optional)

---

## Step 3: Configure Privacy

### Option A: Bot sees all messages
1. Talk to @BotFather
2. `/setprivacy`
3. Select your bot
4. Choose "Disable"

### Option B: Bot only sees commands
- Default behavior
- More private
- Bot won't see regular chat

---

## Step 4: Test

Send in group:
```
/start
/ver
```

Bot should respond!

---

## Troubleshooting

### Bot doesn't respond
- Is it running? (Check Railway logs)
- Is it in the group?
- Is it admin?

### "User not found" for mentions
- User must have interacted with bot first
- Have them send `/start` to bot privately
