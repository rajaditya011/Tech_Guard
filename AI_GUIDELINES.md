# AI Handoff Protocol & Rules for Workers

This file contains the internal protocols and rules for AI assistants working on the HomeGuardian AI project. 

---

## 1. AI Handoff Protocol

### Session Start (Every AI Must Do This)

1. **Read** `CHANGELOG.md` — find the last entry, understand current state.
2. **Read** `README.md` — understand the project overview.
3. **Read** the relevant `build/chunk_XX_*.md` file for the next incomplete chunk.
4. **Run diagnostics** (see Diagnostics section) to confirm the current environment state.
5. **Begin work** on the next incomplete chunk only.

### Session End (Every AI Must Do This)

1. **Update** `CHANGELOG.md` — add a new entry using the template at the bottom.
2. **Update** the Build Status Table in `README.md` — mark chunks as complete/in-progress.
3. **Run diagnostics** to verify everything still passes.
4. **Note** any blockers, known issues, or decisions made for the next AI session.

---

## 2. Build Order — Dependency Graph

```
Chunk 00: Manifest + Diagnostics
    |
Chunk 01: Project Setup (folders, deps, env)
    |
Chunk 02: Backend Core (FastAPI, DB, auth, MQTT, WS)
    |
    +-------+-------+
    |               |
Chunk 03:       Chunk 06:
Sensor Pipeline  Frontend Shell
    |               |
Chunk 04:       Chunk 07:
ML + Anomaly     Old Device Portal
    |               |
Chunk 05:       Chunk 08:
Intelligence     New Device Dashboard
    |               |
    +-------+-------+
            |
        Chunk 09:
        Secret Weapon + Security + Deploy
```

---

## 3. Rules for All AI Workers

1. **Follow chunk files exactly.** Each chunk in `build/` contains complete, copy-paste-ready code. Do not improvise when a chunk provides exact code.
2. **Use design tokens.** All colors, spacing, typography, and animation values MUST use CSS custom properties defined in `design/UI_DESIGN_PROMPTS.md`. Never hardcode visual values.
3. **Demo mode is required.** Every feature MUST work with `DEMO_MODE=true` and zero API keys. Pre-loaded demo data for all four scenarios (Normal Routine, Late Night Anomaly, Casing Simulation, Full Intrusion Prediction).
4. **Log to CHANGELOG.md.** Every AI session must add a timestamped entry documenting what was built, modified, and any decisions made.
5. **Both portals always present.** Never remove or disable either the Old Device Portal or the New Device Dashboard. They are separate authenticated experiences.
6. **Theme always works.** Every UI component must render correctly in both light and dark themes. Test both before marking a frontend chunk complete.
7. **Security from day one.** Input sanitization, parameterized SQL, CORS, rate limiting, MQTT access control. Follow `security/SECURITY_CHECKLIST.md`.
8. **Verify each chunk.** Run the verification commands at the end of each chunk file before moving to the next.
9. **No emojis.** Use professional text markers, numbered lists, and colored badges throughout all files and UI.
10. **Production quality.** This is production-grade work. Clean code, proper error handling, meaningful variable names, documented functions.
11. **Respect dependency order.** Follow the build order graph. Do not skip ahead.
12. **Preserve existing work.** When building a new chunk, verify that all previously completed chunks still function correctly.

---

## 4. Quick Start for New AI Sessions

```
1. Read CHANGELOG.md          -- What has been done?
2. Read README.md             -- What is the plan?
3. Read the next chunk file    -- What exactly to build?
4. Build it                    -- Follow the chunk exactly
5. Verify it                   -- Run chunk verification commands
6. Update CHANGELOG.md         -- Log your work
```
