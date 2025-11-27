# Rate Limiting & Cooldowns

## Global Rate Limits

| Limit | Value |
|-------|-------|
| Commands per minute | 30 |
| Transfers per hour | 10 |
| Admin commands per minute | 5 |

---

## Per-Command Cooldowns

| Command | Cooldown | Scope |
|---------|----------|-------|
| `/azotar @user` | 5 min | Same target |
| `/nalgada @user` | 1 min | Same target |
| `/calabozo @user` | 30 min | Same target |
| `/tributo @user` | None | - |
| `/ofrenda @user` | 24 hours | Same target |
| `/desafio @user` | 10 min | Same target |

---

## Implementation

### Check Cooldown
```python
def check_cooldown(user_id, command, target_id=None):
    cooldown = get_cooldown(user_id, command, target_id)

    if cooldown and cooldown.expires_at > now():
        remaining = cooldown.expires_at - now()
        return Error(f"Espera {remaining} antes de usar esto de nuevo")

    return True
```

### Set Cooldown
```python
def set_cooldown(user_id, command, target_id, duration_seconds):
    expires = now() + timedelta(seconds=duration_seconds)

    upsert_cooldown(
        user_id=user_id,
        command=command,
        target_id=target_id,
        expires_at=expires
    )
```

### Cooldown Durations
```python
COOLDOWNS = {
    'azotar': 300,      # 5 min
    'nalgada': 60,      # 1 min
    'calabozo': 1800,   # 30 min
    'ofrenda': 86400,   # 24 hours
    'desafio': 600,     # 10 min
}
```

---

## Spam Protection

### Detect Spam
```python
def is_spamming(user_id):
    recent_commands = count_commands_last_minute(user_id)
    return recent_commands > 30
```

### Handle Spam
```python
if is_spamming(user_id):
    # Temporary block
    block_user_temporarily(user_id, duration=300)
    return Error("Demasiados comandos. Espera 5 minutos.")
```
