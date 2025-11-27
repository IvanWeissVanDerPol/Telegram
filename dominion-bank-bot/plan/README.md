# The Phantom Bot - Plan Documentation

## Quick Start

1. Read [01-foundation/overview.md](01-foundation/overview.md)
2. Review [01-foundation/naming.md](01-foundation/naming.md)
3. Follow [07-setup/](07-setup/) guides
4. Deploy with [08-deployment/](08-deployment/)

---

## Documentation Structure

```
plan/
├── 01-foundation/          # Project basics
│   ├── overview.md         # What we're building
│   └── naming.md           # Bot & currency names
│
├── 02-architecture/        # Code structure
│   ├── project-structure.md
│   └── import-flow.md
│
├── 03-database/            # Database design
│   ├── schema-overview.md
│   ├── core-tables.md      # users, transactions
│   ├── profile-tables.md   # profiles, kinks
│   ├── relationship-tables.md
│   ├── bdsm-tables.md
│   └── system-tables.md
│
├── 04-commands/            # All bot commands
│   ├── overview.md
│   ├── core/               # /ver, /dar, /ranking
│   ├── admin/              # /dar_admin, /quitar
│   └── bdsm/               # /collar, /azotar, etc
│
├── 05-logic/               # Flow diagrams
│   ├── overview.md
│   ├── core-flows.md
│   ├── admin-flows.md
│   └── atomic-operations.md
│
├── 06-validation/          # Input validation
│   ├── input-validation.md
│   ├── rate-limiting.md
│   └── error-messages.md
│
├── 07-setup/               # Development setup
│   ├── telegram-bot.md     # Create bot
│   └── development-env.md  # Python setup
│
├── 08-deployment/          # Go live
│   ├── railway.md          # Deploy to Railway
│   └── add-to-group.md     # Add bot to group
│
├── 09-features/            # Feature details
│   ├── profiles/           # User profiles
│   ├── excel-import/       # Excel import
│   └── google-sheets/      # Sheets sync
│
└── 10-reference/           # Reference docs
    ├── analysis.md         # Decisions & priorities
    └── messages.md         # Message templates
```

---

## Implementation Order

### Phase 1: Core
- [ ] Database setup
- [ ] /start, /ver
- [ ] /dar (transfer)
- [ ] /dar_admin, /quitar
- [ ] /ranking, /historial

### Phase 2: Import
- [ ] Excel import
- [ ] Google Sheets sync

### Phase 3: BDSM
- [ ] Collars
- [ ] Punishments
- [ ] Dungeon

### Phase 4: Advanced
- [ ] Auctions
- [ ] Contracts
- [ ] Full profiles

---

## Key Decisions

| Item | Decision |
|------|----------|
| Bot Name | The Phantom |
| Currency | SadoCoins |
| Commands | Simple Spanish |
| Database | SQLite → PostgreSQL |
| Hosting | Railway.app |

---

## Status

| Component | Status |
|-----------|--------|
| Planning | Complete |
| Documentation | Organized |
| Implementation | Ready to start |
