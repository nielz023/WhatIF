# FACELESS YOUTUBE HQ

An isometric management sim: you are the CEO of a faceless YouTube automation agency staffed by AI agents.

```bash
npm install
npm run dev      # http://localhost:5173
npm run build
```

## What's in it
- **3D isometric office** (React Three Fiber): 8 clickable departments + War Room, animated employees (idle / working / meeting / training), glass walls, neon lighting, bloom.
- **Workflow & task engine** (`src/modules/tasks/engine.ts`): tasks with priority, status (Pending → Assigned → In Progress → Review → Approved/Rejected → Completed), deadlines, dependencies, comments, documents and results. Agents hand off work, request feedback and post on Threads.
- **11-stage pipeline** (`src/modules/workflows/pipeline.ts`): Research → Topic → Titles & Hooks → Script → Fact Check → Voice → Editing → Thumbnail → QC → CEO Approval → Publishing. Fact Check and QC can reject work back to Script / Editing.
- **24 agent roles**: hire, train, upgrade, edit instructions, assign to channels.
- CEO dashboard, channels, finances (filter by channel/month), internal Threads feed, War Room, achievements, daily missions and office upgrades.

## Honesty and safety
- Everything runs as a **local simulation**. Demo data is labelled in the UI.
- `src/services/adapters.ts` holds the adapters for Claude/OpenAI, the YouTube Data API, Threads, voice, image and video. Only the LLM adapters (and read-only YouTube stats) make real calls, and only once you enter your own key in Settings.
- Publishing never touches YouTube or Threads. It always asks for explicit confirmation and stays in the simulation.

## Persistence
- Autosaves to browser localStorage (`src/services/persistence/storage.ts`).
- Supabase-ready: run `supabase/schema.sql`, then enter the URL and anon key in Settings to save or load cloud saves.

## Controls
Space = pause/resume · Esc = close panels · 1×/3×/8× speed and "skip day" in the top bar. 1 tick = 1 game hour.

## Driftmark HQ (gekoppeld aan het project)
- Startpagina **Driftmark HQ** (`src/pages/DriftmarkPage.tsx`) toont de ECHTE stand: video 1-3, shorts, cast, sets, stats, regels, stemmen, tools en links naar de threads en documenten.
- Echte data staat in `src/data/driftmark.ts` (werk dat bestand bij) en `src/data/gallery.json` + `public/img/` (thumbnails uit /mnt/project-files).
- De game (3D-kantoor, Projects, Agents, Finances) speelt nu met Driftmark: kanaal Driftmark + Driftmark Shorts, video 3 in de pipeline, ideeën uit de ideeënlijst als onderwerpen, agent-instructies uit de werkwijze.
- Gepubliceerd als artifact: https://claude.ai/artifact/BenzViPNMtgbT6PpfeysPB (bouwen met `npm run build`, pagina = `dist/page.html`).
