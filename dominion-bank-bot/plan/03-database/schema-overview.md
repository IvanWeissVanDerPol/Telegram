# Database Schema Overview

## Database Choice

| Users | Recommended |
|-------|-------------|
| < 100 | SQLite |
| 100+ | PostgreSQL |

---

## Table Groups

### Core Tables
- `users` - User accounts & balances
- `transactions` - All coin movements
- `admins` - Admin permissions

### Profile Tables
- `profiles` - Extended profile info
- `user_kinks` - Kink preferences
- `user_limits` - Hard/soft limits
- `user_settings` - Privacy & notifications

### Relationship Tables
- `collars` - Ownership relationships
- `contracts` - Active agreements

### BDSM Feature Tables
- `punishments` - Active punishments
- `dungeon` - Users locked up
- `auctions` - Active auctions
- `bids` - Auction bids

### System Tables
- `imports` - Import history
- `audit_log` - Action logging
- `achievements` - Badge definitions
- `user_badges` - Earned badges

---

## See Individual Files

- [core-tables.md](core-tables.md) - Users, transactions
- [profile-tables.md](profile-tables.md) - Profiles, kinks
- [relationship-tables.md](relationship-tables.md) - Collars, contracts
- [bdsm-tables.md](bdsm-tables.md) - Punishments, auctions
- [system-tables.md](system-tables.md) - Imports, logging
