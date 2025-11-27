# Command: /ranking

## Purpose
Show leaderboard of users with most SadoCoins.

## Usage
```
/ranking
/ranking 20        (show top 20)
```

## Who Can Use
Everyone

## Behavior
1. Query top N users by balance
2. Format with medals
3. Show user's own position

## Response
```
🏆 Ranking de SadoCoins

1. 👑 @carlos — 2,500 ⛓️
2. 🥈 @maria — 1,800 ⛓️
3. 🥉 @juan — 1,200 ⛓️
4. @ana — 950 ⛓️
5. @pedro — 800 ⛓️
6. @lucia — 650 ⛓️
7. @diego — 500 ⛓️
8. @sofia — 350 ⛓️
9. @pablo — 200 ⛓️
10. @elena — 100 ⛓️

━━━━━━━━━━━━━━━━
📍 Tu posición: #7 con 500 SadoCoins
```

## Response - Empty
```
🏆 Ranking de SadoCoins

Aún no hay usuarios con SadoCoins.
¡Sé el primero en recibirlos!
```

## Medal Assignment
| Position | Medal |
|----------|-------|
| 1 | 👑 |
| 2 | 🥈 |
| 3 | 🥉 |
| 4+ | (none) |

## Database Changes
None (read only)
