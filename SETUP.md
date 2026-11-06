# Setup (5 minutes)

1. Create a **public** repo named exactly `devs901` (same as your username).
2. Upload everything in this folder: `README.md`, `assets/`, `.github/`, `scripts/`, `build.py`, `jarvis3d.py`, `jarvis_x.py`, `explainers.py`, and your CV saved as `Devendra_Rathod_CV.pdf` (the DOWNLOAD CV button links to it). (`themes/` and `SETUP.md` are optional.)
3. Your profile at github.com/devs901 now shows the README.

## Make the GitHub stats real
The stats panel shows dashes until it has synced once.
1. Repo > Settings > Actions > General > Workflow permissions > **Read and write permissions** > Save.
2. Repo > Actions > **Update GitHub stats** > Run workflow. It then refreshes itself every 6 hours and also redraws the live activity feed (`assets/feed.svg`).

## Optional contribution snake
Repo > Actions > **Generate contribution snake** > Run workflow. When it finishes, uncomment the snake block in `README.md`.

## What is in the Jarvis 3D design
Everything is a self-contained animated SVG (no JavaScript, no external files), so it runs live on your GitHub profile.
The 3D is real maths (rotation, perspective, depth) baked into the animation by `jarvis3d.py`.

| File | What you see |
|---|---|
| `header.svg` | Arc reactor swinging in 3D, extruded name, scrolling perspective grid floor |
| `hud.svg` | Rotating globe pinned on Pune, boot sequence, voice waveform, project radar |
| `journey.svg` | Experience as hanging 3D cards, plus a featured JioFiber Associate card with its service-flow pipeline |
| `p-*.svg` | Per-project 3D motif: rotating network, rising 3D bars, wireframe cube |
| `skills.svg` | 36 skills orbiting on a 3D globe, with the full skill manifest |
| `arc-reactor.svg` | Exploded-view arc reactor whose ten coils light in turn, one per skill |

## Change the colours
`jarvis` (default, cyan + orange on near-black navy) plus `cinematic`, `neon`, `royal` and `emerald`. Previews are in `themes/preview-*.png`.

**No Python:** copy the files from `themes/<name>/assets/` over `assets/` (keep `assets/stats.svg` once it has synced).
**With Python:** `python build.py --theme neon`, then commit `assets/`. If you use a non-default theme, also uncomment the `THEME:` line in `.github/workflows/stats.yml` so the stats card matches.
To invent your own palette, add an entry to `THEMES` at the top of `build.py`.

## Edit text
Experience, skills and the reactor coil labels are in `jarvis3d.py`. Project cards and headings are in `build.py`, and the three animated walkthroughs are in `explainers.py`.
Edit, run `python build.py`, commit `assets/`. Pin your three project repos on your profile so they match the project cards.
