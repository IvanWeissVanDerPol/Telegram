# 13 - User Profiles, Tags & Kinks (Improved)

## Overview

Comprehensive profile system for BDSM community members.
Users fill profiles via Google Sheets initially, then edit via bot.

---

## Profile Sections

| Section | Content | Privacy |
|---------|---------|---------|
| 🎭 **Identity** | Name, pronouns, age, location | Configurable |
| 👤 **Role & Experience** | Dom/Sub, years, specializations | Public |
| 💜 **Kinks & Interests** | What they enjoy, give/receive | Configurable |
| 🚫 **Limits & Boundaries** | Hard/soft limits, safe words | Important |
| 🔍 **Looking For** | What they seek, availability | Public |
| ⛓️ **Dynamics** | Collars, contracts, relationships | Public |
| 📊 **Stats & Achievements** | SadoCoins, badges, activity | Public |
| ⚙️ **Preferences** | Contact, protocols, expectations | Configurable |

---

## Complete Profile Display

### `/perfil @user`

```
╔══════════════════════════════════════════╗
║  🎭 THE PHANTOM - PERFIL                 ║
╠══════════════════════════════════════════╣
║  @maria ✅                               ║
║  María | Ella/She | 28 | CDMX 🇲🇽        ║
╠══════════════════════════════════════════╣
║  👤 ROL & EXPERIENCIA                    ║
║  ─────────────────────────────────────   ║
║  Rol: Sumisa 🎀                          ║
║  Subroles: Brat, Rope Bunny, Little      ║
║  Experiencia: 📕 4 años                  ║
║  Especialidad: Shibari, Sensory play     ║
╠══════════════════════════════════════════╣
║  💜 KINKS                                ║
║  ─────────────────────────────────────   ║
║  Recibo ⬇️         │  Doy ⬆️             ║
║  Bondage ⭐⭐⭐     │  Service ⭐⭐       ║
║  Impact ⭐⭐       │  Massage ⭐⭐⭐     ║
║  Sensory ⭐⭐⭐    │                     ║
║  Wax ⭐⭐          │                     ║
║                                          ║
║  Curiosa en: Suspensión, Electro        ║
╠══════════════════════════════════════════╣
║  🚫 LÍMITES                              ║
║  ─────────────────────────────────────   ║
║  🔴 Hard: Sangre, Público, Marcas perm.  ║
║  🟡 Soft: Humillación verbal             ║
║  🛑 Safeword: "Rojo" / "Ámbar"          ║
╠══════════════════════════════════════════╣
║  🔍 BUSCO                                ║
║  ─────────────────────────────────────   ║
║  "Dom experimentado en bondage para      ║
║   sesiones regulares. Busco conexión     ║
║   real, no solo juego."                  ║
║                                          ║
║  📅 Disponibilidad: Fines de semana     ║
║  📍 Puede viajar: Sí, CDMX y alrededores║
╠══════════════════════════════════════════╣
║  ⛓️ DINÁMICAS ACTUALES                   ║
║  ─────────────────────────────────────   ║
║  👑 Collar: @juan (hace 45 días)        ║
║  📜 Contratos: 1 activo                  ║
║  👥 Mentor: @carlos                      ║
╠══════════════════════════════════════════╣
║  📊 ESTADÍSTICAS                         ║
║  ─────────────────────────────────────   ║
║  💰 SadoCoins: 1,250                     ║
║  🏆 Ranking: #8 de 67                    ║
║  🎪 Eventos: 12 asistidos                ║
║  📅 Miembro desde: Enero 2024            ║
║                                          ║
║  🏅 Badges:                              ║
║  ✅ Verificada  🎭 OG  💝 Generosa       ║
╠══════════════════════════════════════════╣
║  📝 BIO                                  ║
║  ─────────────────────────────────────   ║
║  "Bratty sub que necesita ser puesta     ║
║   en su lugar. Amante del shibari y      ║
║   las sensaciones. Seria para conocer,   ║
║   juguetona en sesión."                  ║
╠══════════════════════════════════════════╣
║  💭 Estado: 🔥 Disponible                ║
║  🕐 Última actividad: hace 2 horas       ║
╚══════════════════════════════════════════╝
```

---

## Section 1: Identity

### Fields

| Field | Description | Example | Privacy |
|-------|-------------|---------|---------|
| `display_name` | Name to show | "María" | Public |
| `pronouns` | Pronouns | "Ella/She" | Public |
| `age` | Age (optional) | 28 | Configurable |
| `location` | City/Country | "CDMX 🇲🇽" | Configurable |
| `languages` | Languages spoken | "ES, EN" | Public |
| `timezone` | For scheduling | "GMT-6" | Hidden |

### Age Display Options
```
/edad mostrar    → Shows exact age
/edad rango      → Shows "25-30"
/edad ocultar    → Hidden
```

---

## Section 2: Role & Experience

### Main Role

| Role | Emoji | Description |
|------|-------|-------------|
| Dominante | 👑 | Primary dominant |
| Sumis@ | 🎀 | Primary submissive |
| Switch | 🔄 | Both roles |
| Explorador | 🌱 | Still discovering |

### Sub-Roles (Multiple allowed)

**Dominant Sub-Roles:**
| Sub-Role | Description |
|----------|-------------|
| Daddy/Mommy | Nurturing dominant |
| Master/Mistress | Protocol-focused |
| Owner | Pet play dominant |
| Rigger | Rope bondage top |
| Sadist | Enjoys giving pain |
| Brat Tamer | Handles bratty subs |
| Mentor | Teaches newcomers |
| Sir/Ma'am | Formal address |
| Primal Hunter | Primal play predator |

**Submissive Sub-Roles:**
| Sub-Role | Description |
|----------|-------------|
| Little | Age play, DDlg/MDlb |
| Pet | Pet play (puppy, kitten, etc) |
| Slave | Total power exchange |
| Rope Bunny | Loves being tied |
| Masochist | Enjoys receiving pain |
| Brat | Playfully disobedient |
| Service Sub | Service-oriented |
| Prey | Primal play prey |
| Baby Girl/Boy | DDlg/MDlb dynamic |

### Experience

| Level | Years | Description | Emoji |
|-------|-------|-------------|-------|
| Curioso | 0 | Just exploring | 🌱 |
| Principiante | <1 | Learning basics | 📗 |
| Intermedio | 1-3 | Has experience | 📘 |
| Experimentado | 3-5 | Skilled | 📕 |
| Veterano | 5-10 | Very experienced | ⭐ |
| Experto | 10+ | Master level | 👑 |

### Specializations (Up to 5)
```
Shibari, Impact Play, Sensory Deprivation, Protocol, Pet Training...
```

---

## Section 3: Kinks & Interests

### Kink Rating System

**Interest Level:**
| Stars | Meaning |
|-------|---------|
| ⭐ | Curious / Will try |
| ⭐⭐ | Enjoy / Like |
| ⭐⭐⭐ | Love / Expert |

**Give/Receive:**
| Symbol | Meaning |
|--------|---------|
| ⬆️ | Give / Top / Do to others |
| ⬇️ | Receive / Bottom / Done to me |
| ↕️ | Both |

### Kink Categories

**Bondage & Restraint**
| Kink | Description |
|------|-------------|
| Cuerdas/Rope | Rope bondage |
| Shibari | Japanese rope art |
| Esposas/Cuffs | Metal/leather cuffs |
| Cinta/Tape | Tape bondage |
| Suspensión | Suspension bondage |
| Momificación | Full body wrap |
| Predicament | Uncomfortable positions |

**Impact Play**
| Kink | Description |
|------|-------------|
| Nalgadas/Spanking | Hand spanking |
| Paddle | Paddle impact |
| Flogger | Multi-tail whip |
| Látigo/Whip | Single tail |
| Caning | Cane/rod impact |
| Belt | Belt spanking |
| Crop | Riding crop |

**Sensory**
| Kink | Description |
|------|-------------|
| Vendas/Blindfold | Sight deprivation |
| Cera/Wax | Wax play |
| Hielo/Ice | Temperature play cold |
| Fuego/Fire | Fire play |
| Electro | Electrical play |
| Pinwheels | Wartenberg wheel |
| Sensory dep | Full sensory removal |

**Power Exchange**
| Kink | Description |
|------|-------------|
| Humillación | Humiliation |
| Órdenes | Giving/receiving orders |
| Protocolo | Formal protocols |
| Servicio | Service submission |
| Control mental | Mind games |
| Orgasm control | Denial/forced |
| Chastity | Chastity devices |

**Role Play**
| Kink | Description |
|------|-------------|
| Pet play | Animal role play |
| Age play | Age regression |
| Uniforms | Uniform fetish |
| Medical | Medical play |
| Captor/captive | Kidnapping scenes |
| Teacher/student | Authority scenes |

**Body**
| Kink | Description |
|------|-------------|
| Asfixia/Breath | Breath play |
| Mordazas/Gags | Gagging |
| Pies/Feet | Foot fetish |
| Latex | Latex clothing |
| Cuero/Leather | Leather fetish |
| Piercing play | Needle play |
| Marking | Temporary marks |

**Exhibition**
| Kink | Description |
|------|-------------|
| Exhibicionismo | Being watched |
| Voyeurismo | Watching others |
| Público | Public play |
| Fotos/Video | Being photographed |

### Kink Display Example

```
💜 MIS KINKS

BONDAGE ⬇️ Recibo
├── Cuerdas ⭐⭐⭐
├── Shibari ⭐⭐⭐
├── Suspensión ⭐ (curiosa)
└── Esposas ⭐⭐

IMPACT ⬇️ Recibo
├── Nalgadas ⭐⭐⭐
├── Flogger ⭐⭐
└── Paddle ⭐

SENSORY ↕️ Ambos
├── Vendas ⭐⭐⭐ ⬇️
├── Cera ⭐⭐ ⬇️
└── Masaje ⭐⭐⭐ ⬆️

POWER ⬇️ Recibo
├── Órdenes ⭐⭐
└── Servicio ⭐⭐ ⬆️
```

---

## Section 4: Limits & Boundaries

### Hard Limits (Absolute NO)
```
🔴 LÍMITES DUROS
• Sangre / Blood play
• Scat / Fluidos
• Público sin consentimiento
• Marcas permanentes
• Asfixia hasta inconsciencia
• Intoxicación
• Menores presentes
```

### Soft Limits (Negotiable)
```
🟡 LÍMITES SUAVES
• Humillación verbal fuerte
• Fotos de cara
• Más de 2 personas
```

### Safe Words
```
🛑 SAFE WORDS
• Parar todo: "ROJO" / "RED"
• Bajar intensidad: "ÁMBAR" / "YELLOW"
• Todo bien: "VERDE" / "GREEN"
• Gesto no verbal: 🤚 (3 palmadas)
```

### Health Considerations (Private)
```
⚕️ CONSIDERACIONES (Solo admins/pareja)
• Asma - evitar presión en pecho prolongada
• Rodilla derecha sensible
• Alergia al latex
```

---

## Section 5: Looking For

### Seeking Type

| Type | Description |
|------|-------------|
| 💑 Pareja dinámica | Long-term D/s relationship |
| 🎭 Compañero de juego | Play partner |
| 📚 Mentor/Aprendiz | Teaching/learning |
| 👥 Amigos kink | Kink-aware friends |
| 🎪 Eventos | Event companions |
| 💬 Chat | Just conversation |

### Availability

```
📅 DISPONIBILIDAD

Días: Viernes noche, Sábados, Domingos
Frecuencia: 2-3 veces al mes
Duración sesión: 2-4 horas preferido

📍 UBICACIÓN
Ciudad: CDMX, Zona Sur
Puede viajar: Sí, hasta 1 hora
Host: No (sin espacio privado)

⏰ RESPUESTA
Suelo responder: En 24 horas
Mejor contactar: Telegram DM
```

---

## Section 6: Dynamics & Relationships

### Current Dynamics

```
⛓️ DINÁMICAS ACTUALES

👑 COLLAR
└── Dueñ@: @juan
    ├── Desde: 15 Enero 2024 (45 días)
    ├── Tipo: Collar de consideración
    └── Público: ✅ Sí

📜 CONTRATOS ACTIVOS
└── Con: @juan
    ├── Tipo: Entrenamiento
    ├── Desde: 1 Feb 2024
    └── Hasta: 1 May 2024

👥 OTRAS CONEXIONES
├── Mentor: @carlos (aprendiendo shibari)
├── Pareja romántica: @juan
└── Rope partner: @ana (práctica)
```

### Past Dynamics (Optional)

```
📜 HISTORIAL (últimos 2 años)

• @pedro - Collar 6 meses (2023)
  Terminó: Mudanza

• @luis - Play partner 1 año (2022-2023)
  Terminó: Diferencias de estilo
```

### References

```
✅ REFERENCIAS

Pueden dar referencias sobre mí:
• @carlos (Mentor) - "Respetuosa y dedicada"
• @ana (Amiga) - "Confiable, buena comunicación"
• @admin (Verificador) - "Verificada en evento"
```

---

## Section 7: Stats & Achievements

### Statistics

```
📊 ESTADÍSTICAS

💰 Economía
├── SadoCoins: 1,250
├── Ranking: #8 de 67
├── Total ganado: 3,500 SC
└── Total gastado: 2,250 SC

🎪 Actividad
├── Eventos asistidos: 12
├── Contratos completados: 3
├── Tiempo en comunidad: 8 meses
└── Última actividad: hace 2h

⛓️ Dinámicas
├── Collares recibidos: 2
├── Collares dados: 0
└── Contratos totales: 5
```

### Badges & Achievements

**Status Badges:**
| Badge | Name | How to earn |
|-------|------|-------------|
| ✅ | Verificad@ | Admin verification |
| 🎭 | Phantom OG | First 50 members |
| 💎 | Élite | Top 3 ranking |
| 👑 | Legendario | 1 year + active |

**Activity Badges:**
| Badge | Name | How to earn |
|-------|------|-------------|
| 🎪 | Eventero | 10+ events |
| 📜 | Contractor | 5+ contracts completed |
| 💝 | Generoso | Gave 5,000+ SC |
| ⛓️ | Collector | Collared 5+ people |
| 🔥 | Popular | 10+ people sought them |

**Skill Badges:**
| Badge | Name | How to earn |
|-------|------|-------------|
| 🪢 | Rigger | Recognized rope skills |
| 🎯 | Impact Master | Recognized impact skills |
| 📚 | Mentor | Mentored 3+ people |
| 🌟 | Rising Star | Fast progression |

---

## Section 8: Preferences & Settings

### Contact Preferences

```
📬 PREFERENCIAS DE CONTACTO

Primer contacto:
✅ DM abiertos
❌ No mensajes de voz iniciales
✅ Preséntate primero

Respondo mejor a:
• Mensajes claros sobre intención
• Preguntas específicas
• Respeto a mis límites

NO me contactes si:
• Sin foto de perfil
• Primer mensaje sexual
• No has leído mi perfil
```

### Protocol Preferences

```
📋 PROTOCOLOS

En sesión:
• Trato: "Señor/Sir" a mi Dom
• Posición: Rodillas al saludar
• Permisos: Pedir antes de hablar

Fuera de sesión:
• Trato normal/casual
• Seguimos siendo D/s pero relajado

En público (eventos):
• Collar visible
• Cerca de mi Dom
• Comportamiento discreto
```

### Notification Preferences

```
🔔 NOTIFICACIONES

Recibir DM cuando:
☑️ Me envían SadoCoins
☑️ Me mencionan en ranking
☑️ Alguien ve mi perfil
☐ Match de compatibilidad
☑️ Nuevo mensaje de collar
☑️ Recordatorios de eventos
```

---

## Commands Summary

### View Commands
| Command | Description |
|---------|-------------|
| `/perfil` | View your profile |
| `/perfil @user` | View someone's profile |
| `/perfil completo` | Full detailed view |
| `/perfil resumen` | Short summary |

### Edit Commands
| Command | Description |
|---------|-------------|
| `/editarperfil` | Interactive menu |
| `/bio [texto]` | Set bio |
| `/rol [rol]` | Set main role |
| `/subroles [roles]` | Set sub-roles |
| `/experiencia [nivel]` | Set experience |
| `/especialidad [lista]` | Set specializations |

### Kinks & Limits
| Command | Description |
|---------|-------------|
| `/kinks` | Interactive kink editor |
| `/kink add [kink] [nivel] [dar/recibir]` | Add kink |
| `/kink remove [kink]` | Remove kink |
| `/limites` | Edit limits |
| `/safeword [palabra]` | Set safe words |

### Looking For
| Command | Description |
|---------|-------------|
| `/busco [texto]` | Set what you seek |
| `/disponibilidad` | Set schedule |
| `/ubicacion [ciudad]` | Set location |

### Privacy
| Command | Description |
|---------|-------------|
| `/privacidad` | Privacy settings menu |
| `/ocultar [seccion]` | Hide a section |
| `/mostrar [seccion]` | Show a section |

### Search & Match
| Command | Description |
|---------|-------------|
| `/buscar [criterios]` | Search profiles |
| `/compatibles` | Find matches |
| `/kinksmatch @user` | Compare kinks |
| `/quienmevio` | Who viewed my profile |

---

## Profile Completeness

Encourage complete profiles:

```
📊 Tu perfil está al 73%

Falta completar:
☐ Agregar límites suaves
☐ Definir safe words
☐ Agregar 2+ kinks
☐ Escribir qué buscas

Perfiles completos aparecen primero en búsquedas
y tienen acceso a /compatibles
```

### Completeness Rewards

| Level | Percentage | Reward |
|-------|------------|--------|
| Básico | 50% | Can use bot |
| Completo | 75% | Appear in searches |
| Detallado | 90% | Priority in matches |
| Perfecto | 100% | Special badge 🌟 |

---

## Privacy Levels

| Level | Who sees | What they see |
|-------|----------|---------------|
| **Público** | Everyone | Basic info, role, tags |
| **Miembros** | Group members | + kinks, limits, busco |
| **Verificados** | Verified users | + contact, availability |
| **Dinámicas** | Collar/contract | + health, private notes |
| **Admins** | Admins only | Everything |

### Per-Section Privacy

```
/privacidad secciones

🔒 Privacidad por Sección:

👤 Identidad
├── Nombre: 🌍 Público
├── Edad: 👥 Solo miembros
├── Ubicación: 👥 Solo miembros
└── Idiomas: 🌍 Público

💜 Kinks
├── Lista: 👥 Solo miembros
└── Niveles: ✅ Solo verificados

🚫 Límites
├── Hard limits: 👥 Solo miembros
├── Soft limits: ✅ Solo verificados
└── Health: 🔒 Solo dinámicas

/privacidad [seccion] [nivel]
```

---

## Database Schema

```sql
-- Main profile table
CREATE TABLE profiles (
    user_id INTEGER PRIMARY KEY,
    display_name TEXT,
    pronouns TEXT,
    age INTEGER,
    show_age TEXT DEFAULT 'exact', -- exact, range, hidden
    location TEXT,
    timezone TEXT,
    languages TEXT, -- JSON array

    main_role TEXT,
    sub_roles TEXT, -- JSON array
    experience_level TEXT,
    experience_years INTEGER,
    specializations TEXT, -- JSON array

    looking_for_type TEXT, -- JSON array
    looking_for_text TEXT,
    availability TEXT, -- JSON object
    can_travel BOOLEAN,
    can_host BOOLEAN,

    bio TEXT,
    protocols TEXT,
    contact_preferences TEXT, -- JSON object

    hard_limits TEXT, -- JSON array
    soft_limits TEXT, -- JSON array
    safe_words TEXT, -- JSON object
    health_notes TEXT, -- encrypted

    privacy_settings TEXT, -- JSON object
    notification_settings TEXT, -- JSON object

    verified BOOLEAN DEFAULT FALSE,
    verified_by INTEGER,
    verified_at TIMESTAMP,

    profile_completeness INTEGER DEFAULT 0,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
);

-- Kinks table (many-to-many)
CREATE TABLE user_kinks (
    user_id INTEGER,
    kink_id INTEGER,
    level INTEGER, -- 1-3 stars
    direction TEXT, -- give, receive, both
    curious BOOLEAN DEFAULT FALSE,
    PRIMARY KEY (user_id, kink_id)
);

-- Predefined kinks
CREATE TABLE kinks (
    id INTEGER PRIMARY KEY,
    name TEXT,
    category TEXT,
    description TEXT,
    emoji TEXT
);

-- Profile views tracking
CREATE TABLE profile_views (
    viewer_id INTEGER,
    viewed_id INTEGER,
    viewed_at TIMESTAMP,
    PRIMARY KEY (viewer_id, viewed_id, viewed_at)
);

-- References
CREATE TABLE references (
    id INTEGER PRIMARY KEY,
    from_user_id INTEGER,
    to_user_id INTEGER,
    reference_text TEXT,
    approved BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP
);
```

---

## Next Steps

1. Review this improved structure
2. Decide which sections are mandatory vs optional
3. Update Google Sheets template to match
4. Create the kink/limit predefined lists
