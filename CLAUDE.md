# Good Answer — Project Reference

## Project Overview
Family Feud-inspired game with original features and styling. Working title: **Good Answer**. Stack: vanilla HTML/CSS/JS, no frameworks.
- Main game file: `feud.html`
- Question bank: `master_question_bank.json` (active file, includes variants — see below)
- Pre-variants backup: `question_bank_pre-variants.json`
- Award definitions: `awards.json` (name, id, compute key — see "Victory Awards" section)
- Tooltip definitions: `tooltips.csv` (id, class, flavor, description — see "Tooltip System" section)
- Sound files alongside feud.html: `ding.mp3` (correct answer reveal), `newstrike.wav` (incorrect answer), `goodanswer.mp3` (top answer reveal, 300ms delayed, baseVolume 0.35), `negativebeep.wav` (failed steal attempt), `opentheme.mp3`, `endtheme.mp3`, `analogbuttonclick.mp3`, `flick.wav` (tick SFX + board-wrapper slide), `phonetype.wav` (typewriter keystroke SFX + tile-cover hover), `balbg.mp3` (background music, looping), `roundend.wav` (round winner determined), `decreaseblip.mp3` (streak/mult decrease), `neutralbeep.wav` (duplicate answer rejection), `chime.wav` (badge bounce SFX), `zoop.wav` (speed stepper SFX), `slit.wav` (fly-in/out whoosh — cat-row entry/exit, dialog open/close), `tap1.wav` (button click — setup nav, menu, confirm), `tap2.wav` (element landing — input area fly in/out), `tvon.wav` (CRT power-on), `powerdown.wav` (CRT power-off)

### Branch structure
- **`main`** — **active development branch.** Source of truth for the current state of the game. Includes: Firebase/Firestore multiplayer foundation, Secret Scribble module, module orchestration layer (round type picker), input-area "home base" refactor (`setInputAreaMode` API), and the renaming of feud rounds to "ranked questions" (High Five + Survey). Previously named `multi-scribble`; renamed to `main` on 2026-04-19 when branch structure was cleaned up.
- **`offline`** — pre-Firebase local-only snapshot. Kept as a rollback reference; not under active development. Was the original `main` before the 2026-04-19 rename.
- **`multi`** — multiplayer foundation snapshot (Firebase/Firestore integration, pre-scribble). Kept as a rollback reference; not under active development.
- **`coyne-feud-classic`** — the original Coyne Feud family game night tool. Finished product, not under active development. Do not merge between branches — it's effectively a different game.

Because the game is still in rapid structural flux, the snapshot branches (`offline`, `multi`) are not intended to be merged into `main`. They exist as "how we got here" reference points. Future module branches will likely use the pattern `main-<modulename>` (e.g. `main-commonthread`) — short-lived branches that either merge back into `main` or supersede it entirely depending on how drastic the in-progress changes are.

### Firebase project
- Project: `good-answer-game` (Firestore in `us-east1`, test-mode rules expire 2026-05-13)
- Services enabled: Firestore, Anonymous Auth, Google Auth
- Currently on **Spark (free) plan** with client-authoritative architecture. Mike is willing to upgrade to **Blaze (pay-as-you-go)** if Cloud Functions (server-authoritative) proves to be the better path for the prototype. Migration from client-authoritative to Cloud Functions is straightforward — same Firestore schema, game logic just moves from the active player's browser to a server function.

### Hosting & Deployment
- **GitHub Pages** serves the game at **https://mikec52.github.io/good-answer/feud.html**
- Source repo: `mikec52/good-answer` (public). Pages is configured to serve from **`main`** (active dev branch). `offline` and `multi` are held as rollback snapshots.
- **Deploy workflow**: `git push origin main` = live in ~60 seconds. No build step, no config files. To change which branch Pages serves from: `gh api --method PUT repos/mikec52/good-answer/pages -f "source[branch]=<branch>" -f "source[path]=/"`.
- GitHub CLI (`gh`) is installed and authenticated for Mike's account (`mikec52`). Git credentials are wired through `gh auth setup-git`.
- This is a temporary static hosting solution for playtesting. When Phase 2A (Firebase shared state) arrives, the hosting may migrate to Netlify/Vercel/Cloudflare Pages for serverless function support — or Firebase Hosting itself. The migration is trivial since all these platforms point at the same GitHub repo.

### File organization
- **`drafts/`** — design mockups, PSD source files, Excel layouts (git-ignored)
- **`outdated/`** — deprecated questions and assets (git-ignored)
- **`.gitignore`** excludes: `drafts/`, `outdated/`, `*.psd`, `*.xlsx`, `*.rtfd`, `.DS_Store`, `.variants_batch_id`
- Audio and image files used by the game **are tracked** in git — include them in commits

### Filename conventions
- **All lowercase** — macOS is case-insensitive but Linux servers (GitHub Pages) are case-sensitive. Mismatched casing works locally but breaks in production.
- **No spaces** — use hyphens or underscores. Spaces require URL-encoding (`%20`) and quoting in shell commands.
- **No special characters** beyond hyphens, underscores, and dots.

### Web font rules
- **Never reference local font names** (e.g. `"Futura"`, `"Dazzle Unicase"`). macOS has fonts installed locally that mask loading failures on other platforms.
- **Always use the Typekit/Google Fonts identifier** — check the hosted CSS for the exact `font-family` string. Current Typekit kit: `lps4irc`.
- Key mappings: `"futura-100"` (not `"Futura"`), `"dazzle-unicase"` (not `"Dazzle Unicase"`), `"embarcadero-mvb-pro-condense"`, `"video"`.

---

## Long-Term Development Strategy

The goal is a polished, distributable game app without migrating away from the current HTML/JS stack. Three additive phases:

1. **HTML/JS game (current)** — continue developing `feud.html` as a single-file vanilla build. Same-room play (one device, one host, players submit guesses at the keyboard) is largely functional. Balatro-inspired contained viewport, zone-based layout, animation-rich transitions (see "Viewport Redesign" section below). This phase is "done" when the game is feature-complete and visually polished for single-session use.

2. **Server layer — Remote Play (ACTIVE)** — add a real-time backend so multiple devices share game state. Implementation: Firebase/Firestore with client-authoritative architecture. **Phase 2A (shared state) and Phase 2B (authenticated players) are live on `main`.** See "Multiplayer Implementation" section below for current status and architecture details.

3. **Electron / Capacitor shell (stretch goal)** — wrap the finished game in a native app shell for distribution. Platform priority: Mac → iOS → Windows → Android → Steam. Note: Electron covers Mac/Windows/Linux (desktop only); iOS and Android require Capacitor instead. Game code inside is unchanged either way.

**Distribution phases:**
- **Phase 1 (current goal)**: Owner-hosted. Mike is always the session host; others join as players at a shared URL.
- **Phase 2 (future)**: Self-serve hosting. Other users can independently spin up and host their own game sessions.

**Character mascots (exploratory):** A host character and his dog that react to game moments (correct answers, strikes, steals, etc.), adding personality. Early asset experiments use frame-swap animation (JS `setInterval` cycling preloaded PNGs). The long-term asset pipeline uses Replicate models trained on reference images for consistent, animation-ready sprite frames. Not a confirmed feature — experimental and low priority.

**What this avoids:** No migration to Unity or Phaser. The current stack is the final stack. Phaser would only be reconsidered if animation/visual polish becomes a hard blocker — not anticipated.

---

## Pre-Blaze Cleanup Refactor — Strategy

**Status:** Blaze/Cloud Functions migration is on hold. The client-side architecture needs cleanup first. A large share of the "non-host visual bug" class we've been hitting is not actually caused by host-authoritative sync — it's caused by cross-module DOM coupling that migration wouldn't fix. This section is the plan for addressing that before any server work.

Goal: stabilize the client-side architecture so (a) new features don't risk regressions in old features, (b) visual bugs get cheaper to diagnose and fix, and (c) the eventual Blaze migration is a contained change to game logic rather than a refactor-and-migrate bundle. Ordered by dependency — each step assumes the previous is done. Dive into each step via a proper plan-mode session when picking it up.

### 1. Reclassify all UI regions as **evergreen** or **module-scoped**

The root cause of most cross-module visual bugs is that some DOM containers mix elements with different lifetimes. Evergreen elements (persist across all modules and phases) share containers with module-scoped elements (only exist during one module). Mutations to the module-scoped child leave collateral state on the shared parent, which the next module inherits.

**Canonical classification:**

- **Evergreen regions:** `#phase-indicator`, `#input-area`, `#scoreboard`. Always present, never touched by module code. Only orchestrator public APIs (`setPhase`, `setInputAreaMode`, score-update helpers) mutate them.
- **Module-scoped regions:** everything else in the main gameplay area — category pills, content-tv + question + cat-label, board-wrapper, scribble container, faceoff container. All destined to be swappable children of a single module canvas.

This is the lens driving steps 2–4.

### 2. Sidebar becomes evergreen-only

Currently the sidebar houses both evergreen (`#input-area`) and module-scoped (`#content-tv`, `#sidebar-category-select` → `#category-pills-area`) content. Refactor so the sidebar contains only `#phase-indicator` + `#input-area`. No module code ever reaches into the sidebar; only the orchestrator APIs.

### 3. Introduce a single `#module-canvas` in the main zone

Inside `#zone-board-main`, below the evergreen `#scoreboard`, add one `#module-canvas` slot. Every module owns this slot completely while active:

- Ranked questions render their category pills first (replacing the current sidebar-hosted selection), then their content-tv + question + board-wrapper inside it.
- Scribble renders its drawers/guessers/summary inside it.
- Faceoff renders its two-battle layout inside it.

Existing DOM reparents: `#content-tv`, `#category-pills-area` (and its wrapper), `#board-wrapper`, `#scribble-container`, `#faceoff-container` all move from their current homes into `#module-canvas`.

Ranked-question entry becomes a two-step sequence within the canvas: category pills first, then content-tv + board-wrapper slide/fade in once a category is picked.

### 4. Formalize a `boardClean` (or `resetModuleCanvas`) step between modules

With the module canvas in place, teardown collapses to clearing the canvas between modules. Introduce an explicit phase in the orchestration flow:

```
roundEnd → boardClean → roundStart (or selectRound)
```

`boardClean` runs after Ready Up resolves, during or just after the existing exit animations — while the visible area is already empty/animating out, so the user never sees the wipe. It resets the module-canvas to its canonical empty state and strips any module-specific classes from shared elements.

Each module's entry function can then assume a clean slate. All current defensive cleanup code at the top of module entry points (`initRoundState`'s cat-label removal, `setupFaceoffUI`'s hides, `enterScribbleRound`'s clears, etc.) goes away.

**Observed symptoms (regression cases for when `boardClean` lands):**

- **Scribble scoreboard/summary retained on faceoff screen** (non-host view). After a scribble round ends and faceoff begins, the scribble UI (session summary, per-team boxes) stays visible behind/around the faceoff layout. Root cause: `setupFaceoffUI` (feud.html:~10533) hides `board-wrapper` and `content-tv` but does not hide `scribble-container` or its scoreboard children. Each module's entry has its own hand-maintained cross-module cleanup matrix, and the matrix is incomplete. `boardClean` replaces all of these with one call.
- **Input-area drift on non-host clients.** Something pushes `#input-area` progressively further down the sidebar until it's the non-host's turn to guess, at which point it re-settles. Symptom of mixed-lifetime sidebar/module-canvas layout mutations that aren't reset between phases — module transitions leave residual spacer/margin/offset state on shared ancestors. Should verify this goes away once `boardClean` normalizes the canvas and sidebar geometry between modules.
- **Evergreen regions clipped above canvas on new-game start after faceoff.** On play-again after a faceoff-completed game, the phase indicator and scoreboard both render pushed up past the canvas top edge (only their bottom slivers visible). Simultaneously the round-type picker renders with duplicated/ghosted pill text and the old "PICKING A ROUND TYPE" phase span overlaps the input-area. Suggests faceoff→victory→play-again leaves residual `transform`, `margin`, or position state on shared ancestors that the new game's entry animations layer on top of instead of starting from baseline. Step 4's `boardClean` (plus an evergreen reset for sidebar + scoreboard transforms) is the right hammer — any inline fix now would just re-check boxes that the refactor removes entirely.

### 5. Dead-code audit, module by module

With the architecture clarified, pass through each module's entry/exit to remove code that was only there to defend against the old mixed-lifetime containers:

- Scribble's `sq-zone-content` visibility manipulations
- `showInputArea`'s defensive `sq-zone-content` handling
- Faceoff's `#board-wrapper` and `#content-tv` hides
- `setInputAreaMode` gymnastics that exist because sidebar layout was fragile
- **Single-writer contract for `#turn-subtext`.** Currently ~8 call sites write to it; only `updateTurn()` and `animateTurnSwap()` call `fitByCharCount` afterward. The rest (`setInputAreaMode`, faceoff reset, `resetGame`'s 2rem `--fit-base` reset, the raw HTML default) leave `--fit-scale` stale. Observed symptom: during ranked-question gameplay, host sees `#turn-subtext` at 27.4px while non-host sees 32px — host passed through `updateTurn()` with a 14-char name (scale 0.857 baked in), non-host's mirror path went through `setInputAreaMode` and never fitted. Fix shape: route every text update through `setInputAreaMode` (matching the `#phase-indicator` / `setPhase` single-writer model), and have `setInputAreaMode` call `fitByCharCount` internally. Also clear `--fit-scale` wherever `--fit-base` is reset.

Net LOC goes down; N×N coupling between modules goes away.

### 6. Screen-by-screen polish pass

General UI polish across the game, walked through in play order rather than by concern. Not an isolated animation pass — no single animation is broken enough to need its own dedicated pass. Instead: go screen by screen (start screen → setup → lobby → category select → gameplay → steal → round result → round type picker → scribble flow → faceoff → victory → play-again) and tweak whatever needs it at that screen — layout, copy, spacing, colors, animation timing, transitions — all together in one pass per screen.

Animation-specific things to keep an eye out for during this pass (carried over from what was going to be Step 6):

- Entrance/exit animations that assume specific DOM adjacency or sidebar geometry after the Steps 2–4 reparenting: content-tv's tv-on, the typewriter, cat-label marquee, sq-zone-input slide-up, board-wrapper slide-in from above. Keyframe origins and clipping parents may need small adjustments.
- `#content-tv` and `#board-wrapper` sizing inside the new `#module-canvas` (follow-up from Step 2+3) — dimensions were tuned for the sidebar and may need retuning for the main zone.

### 7. Phase reconcile robustness (spotty-network recovery)

Firestore's `onSnapshot` only delivers the **latest** document state, not every intermediate transition. A client whose write aborts or whose tab is momentarily starved of CPU can miss a snapshot and arrive at the next phase mid-flow. Most of our reconcile handlers assume linear progression (`phase N-1 → N`) and gate on local state — so when a client catches up from phase N-2 to phase N, the handler for N silently no-ops because the guard fails, and the client gets stuck.

**Canonical symptom (2026-04-17, scribble):** Player 3's Firestore write aborted during `scribbleStartWordSelection`'s auto-pick, they missed `scribble-drawing-start`, and the subsequent `scribble-session-end` handler rejected because `scribbleState.phase !== "drawing"`. Their local scribble flow never completed — `scribbleFinishRound → handleModuleComplete` never ran — so no Ready Up button ever appeared. Input-area was stuck on the word-select "disabled" text. A targeted safety net was added in the `round-result` handler to force the Ready Up UI when `lastResult.outcome === 'module-complete'` and input-area isn't already in action mode. That's a patch, not a cure.

**The real fix is design-level.** Every reconcile `case '<phase>':` handler should treat itself as "bring the client to this phase's canonical state" — idempotent, no assumption about prior local state. Replace the current pattern of:

```js
case 'scribble-session-end':
  if (scribbleState.phase === "drawing" || scribbleState.phase === "countdown") {
    scribbleApplyEndDrawingSession(...);
  }
```

…with handlers that either (a) fast-forward through skipped intermediate steps using fields the snapshot still carries (e.g. `scribbleSessionWords` persists across phases), or (b) render the target phase's UI directly regardless of local state.

**Dirtiest offenders (audit targets):**

- **Scribble:** every handler gates on `scribbleState.phase`. Biggest desync surface. Word-select, drawing-start, session-end, summary all need review.
- **Faceoff:** entry/exit gates on `faceoffState.active` transitions. Missing `faceoff` snapshot leaves non-host on ranked-round UI with stale scoreboard; missing `round-result` after face-off end leaves non-host with face-off container still showing.
- **Steal-chance:** handler assumes client saw `gameplay` first. Probably fine (gameplay state is idempotent) but worth verifying.
- **Ready-up countdown:** `readyCountdown` start is a timestamp, but the countdown display is driven by a local interval started in reconcile. A client that joins mid-countdown starts counting from the wrong point.
- **Category-select re-entry on play-again:** already has specific handling; check it still holds up under missed snapshots.

**Non-goals:**
- Don't try to replay missed animations. Recovery is about consistent state, not visual continuity.
- Don't add a polling fallback. Snapshot delivery is reliable once the connection re-stabilizes; the gap is handler tolerance, not delivery.

**Workload:** medium — mechanical, but needs a careful pass per handler. Scribble is the biggest chunk. Faceoff is next. The others are mostly verification.

**Why this matters:** distinguishes "game that can crash on you at any moment" from "game that feels stable." The bugs this prevents are the worst kind for users — no obvious cause, can't reproduce on demand, makes the game feel broken.

### Execution order and scope

- **Step 1:** ✅ Done — thinking/documentation only, captured above.
- **Steps 2+3:** ✅ Done (2026-04-17). Sidebar is evergreen-only (`#phase-indicator` + `#sq-zone-input`). `#module-canvas` introduced in `#zone-board-main` holding `#category-pills-area`, `#content-tv`, `#round-type-picker-container`, `#board-wrapper`, `#faceoff-container`, `#scribble-container`. `#category-pills-area` is `position: absolute` inside the canvas so it doesn't displace sibling module children. Verified: all modules complete end-to-end, faceoff runs, play-again + return-to-lobby flows are clean. Known follow-up: `#content-tv` and `#board-wrapper` need a sizing pass for High Five/Survey inside the new canvas — they currently overlap/overflow because their dimensions were tuned for the sidebar, not the main zone.
- **Step 4:** ✅ Done (2026-04-17). `resetModuleCanvas()` added near `advanceRound`; wired into `advanceRound` between exit animations and `updateTurn`, and into non-host `category-select` reconcile path. Verified flows 1–4 (ranked×3, ranked→scribble→ranked, scribble→scribble, any→faceoff non-host). Flow 5 (input-area drift) deferred to Step 5 — currently masked by a `margin-top: 0` workaround on `#sq-zone-input`; the real verification happens when that workaround is removed.
- **Step 4b:** ✅ Done (2026-04-17). `resetEvergreenRegions()` added next to `resetModuleCanvas`; called at the tail of `resetGameUI()` (play-again, return-to-lobby, lobby→game) and near the top of `resetGame()` (exit-to-menu). Clears inline `transform` / `margin` / `background` + stale animation classes on `#phase-indicator`, `#sq-zone-input`, `#input-area`, and `#scoreboard` so game-boundary entry animations start from a clean baseline. Defensive — no visible regressions on flows that already worked, but removes the accumulation class of bugs (e.g. "evergreens clipped above canvas on play-again after faceoff").
- **Step 5:** ✅ Done (2026-04-17). Dead-code pass landed with several tied-in home-base improvements:
  - `#turn-header` / `#turn-subtext` roles swapped so the semantic names match the layout (header = big primary line, subtext = small secondary line). Wrapped both in a new `#turn-message` parent; `#input-area` bumped 250 → 300px.
  - `#input-area` now anchors to the bottom-left of the sidebar via `margin-top: auto` on `#sq-zone-input`. The old `margin-top: 0` workaround is gone. No drift observed.
  - Dead `#message` div removed (CSS rule, HTML, and all 4 JS references). `#input-area` now bleeds off the canvas bottom (square bottom corners, `margin-bottom: -2px`, `padding-bottom: 5px`).
  - Disabled `#guess` background changed to `#c5c5c5` for a clearer disabled affordance.
  - `.team-name` span wrapper scopes team color to the player-name token inside turn-message instead of coloring the whole line. All subtext/header writers updated (`updateRoleUI`, `showRoundTypePicker`, `showCategorySelection`, `updateTurn`, plus `animateTurnSwap` now uses `innerHTML` to preserve the span on restore).
  - "Chance to steal" header renders during steal phase via `showHeader: !!stealPhase` path (now moot since turn-header is always visible, but the call remains).
  - `#player-inventory` now shows a "PRIZES" label (0.8rem futura-100, top-center) as a placeholder for the items system.
  - `#sq-zone-input` is intentionally **retained**, not removed. It's reserved as a placeholder for future content above the input-area — the margin-top-auto anchor already positions it correctly whether empty or populated.
- **Step 6:** ⏭ Next. Screen-by-screen polish pass — see Step 6 body above.
- **Step 7:** medium. Independent of 4–6 — can be done any time after steps 2+3 landed. Scribble handlers are the highest-value target. No rush — safety precaution rather than blocker.

### Guiding principle — phase-indicator as reference design

`#phase-indicator` is the model for how evergreen regions should be built. Its container is persistent; all possible text spans exist in the DOM simultaneously; a single attribute (`data-phase`) selects which is visible; one function (`setPhase`) mutates that attribute. No accumulation, no defensive resets, no cross-module leakage. After this refactor, every evergreen region should follow that same pattern, and every module-scoped region should live inside `#module-canvas` where it can be freely torn down.

---

## Feature Roadmap

Planned features grouped by rough workload tier. Each entry has tags for feasibility (✅ clean fit / ⚠️ feasible with friction / ❌ not feasible) and workload (🟢 quick win / 🟡 moderate / 🔴 heavy lift). Update this list as items ship or new features are added.

### Quick Wins 🟢

- **Category multiplier round-end animation** ✅ 🟢 — The category multiplier currently applies silently during round-end scoring. Needs dramatic reveal: badge flies to round total, pulses, count-up applies the multiplier visibly. CSS + `anim.sequence`, no system touches.
- **Randomize turn order at game start** ✅ 🟢 — Currently `transitionFromLobbyToGame` sorts team arrays by UID for determinism. Replace with host-generated random permutation synced to Firestore. Keeps determinism across clients.
- **Separate turn order for category selection** ✅ 🟢 — Add `categoryPlayerIndex` parallel to `playerIndex`, advanced independently. Small touch to `pickCategory()` and `advanceRound()`. Bonus: unlocks minigame-specific turn orders later.
- **Pixel art for awards (lower priority)** ✅ 🟢 — Content addition only. Wire `<img>` tags into victory dialog award list items after assets exist.

### Moderate 🟡

- ~~**Rebrand Fast Money → Lightning Round**~~ → shipped as **Face-off Round** (see CLAUDE.md "Face-off Round" section). Two 1v1 battles with simultaneous input from random player pairs, 60s timer each, 2x multiplier on totals, always runs at the end of every game. Follow-up work: styling pass, voting-based player selection, polished transitions, Cloud Functions migration for fair same-answer race ordering.
- **Turn timer** ✅ 🟡 — Per-turn countdown with visual indicator. Host-authoritative: host writes expiry timestamp, all clients display. On expiry, auto-strike or auto-submit. Touches `submitGuess` flow.
- **Quests** ✅ 🟡 — Randomized per-round goals with small progress overlay (e.g. "First to 3 top-3 answers → 300pts bonus"). Needs: quest definition JSON (like `awards.json`), progress hooks in `submitGuess`, overlay UI, completion rewards. Moderate because it touches the gameplay loop.
- **Minigame: Number is Correct** ✅ 🟡 — Price-is-Right style numeric question. Closest without going over wins. Simpler than Circle of Prizes: single question screen, one guess per player/team, reveal animation. Open question: numeric question bank source (new pool or tagged subset of existing).
- **4-player mode** ⚠️ 🟡 — Each player is their own "team." Strikes pass control to next player, scoring becomes per-player. Current team-based structures (`teamScores[2]`, `teamTurn`, `teamPlayerUids[2][]`) need to generalize. Tradeoff: generalize the data model (cleaner, bigger upfront lift) or branch on a `mode` flag (faster, accumulates debt). Lean toward generalize.
- **Prizes (items system)** ⚠️ 🟡 — **Captains shipped (unblocked)** (first-player-to-join = captain, per agreement). Then: prize pool JSON, end-of-round award flow (winner picks first, loser gets leftover), 3-slot team inventory, use/discard actions gated to captain, steal-a-prize right on steal-round wins. Effect types (bonus points, clear strikes, streak/mult boosts) each need a gameplay hook. Inventory system is contained; effects are the spread.
- **Animated host + dog characters** ⚠️ 🟡 — Asset pipeline is the unknown. Start screen already has placeholder dog frame-swap. Need: reaction triggers (correct, strike, steal, round end, victory), frame sets per reaction, positioning. Friction: asset generation via Replicate-trained models for consistent sprite frames. Workload is mostly asset creation + hook wiring.

### Heavy 🔴

- **Minigame: Circle of Prizes** ✅ 🔴 — Wheel-of-Fortune final round clone. Pre-revealed letters, turn-based letter guessing, word guess to win. Brand new game mode: custom UI, letter-bank state, keyboard input, scoring rules. Mid-game event slot is fine architecturally; the game itself is a significant build.
- **Real-time buzz-in round opener** ⚠️ 🔴 — Current Firestore sync has 200–500ms latency, so buzz races can't be decided by true network timing. **Agreed path: build host-authoritative first** (host picks winner by Firestore write receipt order — "good enough"), upgrade to Cloud Functions (server-authoritative, requires Blaze plan) once the game proves out. Needs new UI (buzzer state, simultaneous question reveal, buzz animation) and a new turn-start flow. Underlying buzz system is reusable for other minigame modes — builds compound value.
- **Round timer (experimental)** ⚠️ 🔴 — Fundamentally restructures the round loop. Currently: one question per round, N rounds. Proposed: one 5-min round with boards cycling as they complete. Needs: round-level vs board-level state separation, question cycling logic, cross-board score aggregation, timer-driven round end. Big rewrite of the core loop. Keep experimental for now.
- **Stat tracking for Google-authed accounts** ⚠️ 🔴 — Dependency: Google Sign-In must be actually enabled (currently wired but deferred). Then: per-user profile docs in Firestore, post-game stat aggregation, profile/history UI, privacy review. Gated to Google-authed users only; guests excluded. Heavy because it adds a whole new surface area (profiles) on top of enabling auth for real.

### Needs to Land First (dependencies)

- ~~**Captains feature**~~ — ✅ shipped. Prizes is now unblocked.

### Suggested Working Order

1. Quick wins (category multiplier animation, randomize turn order, separate category turn order) — immediate polish, near-zero risk
2. ~~Lightning Round~~ → ✅ shipped as Face-off Round; styling iteration next
3. ~~Captains feature~~ → ✅ shipped. Prizes now unblocked.
4. Prizes — first major gameplay expansion (unblocked)
5. Minigames (Number is Correct before Circle of Prizes — smaller build, lower risk)
6. Everything else as appetite dictates

---

## Multiplayer Implementation

Firebase/Firestore powers real-time state sync. The full implementation plan is at `.claude/plans/buzzing-toasting-feather.md`.

### Architecture — Host-Authoritative

- **Host-authoritative**: The host's browser is the sole authority for all game logic. The host generates categories, pre-selects questions, evaluates guesses, advances turns, computes scores/stats/awards, and determines round/game end. Non-host clients submit raw inputs (`pendingAction`) and render synced results. This mirrors the eventual Cloud Functions migration — swap "host's browser" for "server function."
- **`pendingAction` pattern**: Non-host players write `{ pendingAction: { type, data, uid } }` to Firestore. The host's snapshot listener intercepts these before `reconcileLocalState`, processes them, syncs the result, and clears the action. Two action types: `selectCategory` and `guess`.
- **Auth**: Firebase Anonymous Auth (display name on join). Google Sign-In enabled but deferred to commercialization.
- **Local mode preserved**: `isMultiplayer` flag gates all sync behavior. The game works identically offline.
- **Single-file philosophy maintained**: Firebase SDK via CDN `<script type="module">`, config in `firebase-config.js`, all sync logic inline in `feud.html`.

### Key Multiplayer Functions

- **`syncState(updates)`** — writes game state to Firestore with `_writerUid` and `_writeId` metadata. Includes a `clean()` sanitizer that converts `undefined` to `null` (Firestore rejects `undefined`) and handles sparse arrays. Preserves non-plain objects (Firebase FieldValue sentinels) by only recursing into plain `{}` objects.
- **`startGameListener()` / `stopGameListener()`** — manages `onSnapshot` subscription on the game document. The host's listener has a `pendingAction` processor at the top that intercepts non-host inputs before reconciliation.
- **`reconcileLocalState(data, prev)`** — processes incoming Firestore snapshots on all non-writing clients. Split into two phases: Phase 1 updates all state variables (playerIndex, teamTurn, stealPhase, scores, strikes, streak, etc.), Phase 2 triggers UI updates (updateScores, updateStrikes, flipTile, updateTurn, etc.) after state is consistent.
- **`handlePhaseTransition(data)`** — handles `category-select`, `gameplay`, `steal`, and `round-result` phase changes for non-host clients.
- **`setupQuestionScreenForSpectator()`** — builds the full question/gameplay screen when a non-host client receives a category pick. Mirrors `pickCategory()`'s animation sequence: content-tv CRT power-on → typewriter question text → input area slide-up.
- **`animateSpectatorCategoryExit()`** — staggers category pills out left before the question screen builds, matching the controller's `animateCategoryTransition` Path A.
- **`syncAfterGuess(result, roundEnd)`** — called by the host after evaluating a guess. Writes the full game state snapshot to Firestore. Optional `roundEnd` parameter adds `roundResultMsg`, `roundWinner`, `roundPhaseText` and sets phase to `round-result`.
- **`onCategoryClick(category)`** — router: host/local runs `pickCategory()` directly, non-host writes `pendingAction: { type: 'selectCategory' }`.
- **`hostProcessCategorySelect(category)` / `hostProcessGuess(guess, uid)`** — host-side handlers for non-host actions.
- **`getActivePlayerUid()` / `amIActivePlayer()`** — determines who has control based on `teamTurn`, `playerIndex`, and `teamPlayerUids`.
- **`updateRoleUI(activeUid)`** — enables/disables controls based on whether this client is the active player. Called from `updateTurn()`. Skips button hiding during `round-result` phase so all players can interact with Ready Up.

### Self-Echo Detection

The `onSnapshot` listener skips all snapshots where `data._writerUid === myUid`. The writing client already applied changes locally, so echoes are ignored. This replaced an earlier per-writeId check that broke when stale echoes arrived after `_lastWriteId` had advanced.

### Deterministic Team Ordering

Firestore map key iteration order (`Object.entries(players)`) is not guaranteed across clients. All player iteration now sorts by UID (`localeCompare`) for deterministic ordering. The host writes canonical `teamPlayers` arrays (sorted `[{uid, name}, ...]`) to Firestore at game start. `transitionFromLobbyToGame` reads from `data.teamPlayers` (not `data.players`) so all clients get identical `teamPlayers` and `teamPlayerUids` arrays. This prevents `playerIndex[N]` from referencing different players on different clients.

### Ready-Up Consensus

Between rounds, all players see a "Ready Up" button. First click starts a 10-second countdown (server timestamp). Auto-advances when all players ready or countdown expires. The host (`teamPlayerUids[0][0]`) is the designated advancer — calls `advanceRound()`. Other clients receive the `category-select` phase via snapshot. State: `readyPlayers` map, `readyCountdown` timestamp, `_readyCountdownInterval` local timer.

### Game Flow

1. **Start screen** → Mode Select (Local / Online)
2. **Local**: existing setup flow unchanged
3. **Online → Create Game**: generates 5-char alphanumeric code, writes game doc to Firestore, shows lobby
4. **Online → Join Game**: enter code + display name, Firebase Anonymous Auth, join lobby
5. **Lobby**: real-time player list, team assignment (Join Red/Join Blue). Host sees interactive settings (round count cycles 2→4→6, speed stepper). Non-host sees read-only settings. Start Game enabled when both teams have players.
6. **Game start**: host determines `startingTeam` and canonical team arrays (sorted by UID), writes to Firestore. All clients transition to gameplay via `transitionFromLobbyToGame()` → `startGameFromLobby()`.
7. **Category selection**: host generates random picks, pre-selects a question per category, rolls multipliers, syncs `categoryPicks` (including embedded questions) to Firestore. All non-host clients render from synced data. Active player can click; others are disabled via `updateRoleUI`.
8. **Category pick**: active player clicks a category. If host, runs `pickCategory()` directly using the pre-selected question. If non-host, writes `pendingAction: { type: 'selectCategory' }` → host processes → syncs question + `phase: 'gameplay'`.
9. **Gameplay**: active player submits guesses. If host, evaluates locally. If non-host, writes `pendingAction: { type: 'guess' }` → host evaluates → syncs result. All clients animate from synced state (tile reveals, strikes, streak/mult updates). Scoring sync fires before animation so spectators see results within ~200-500ms.
10. **Steal phase**: on 3 strikes, `stealPhase` flips, `teamTurn` switches. Steal counts as a turn (`playerIndex` advances). Phase indicator shows stealing player's name.
11. **Round end**: auto-triggers `endGameByRounds()` on final round. Non-final rounds show Ready Up button for all players.
12. **Round advancement**: ready-up consensus → host calls `advanceRound()` → generates next round's categories → syncs.

### What Works (tested with 2-3 browser windows)

- Full lobby flow (create, join, team assignment, settings, start)
- Host-authoritative category generation with pre-selected questions
- Category selection via pendingAction (non-host → host → sync)
- Guess evaluation via pendingAction (non-host → host → sync)
- Immediate scoring sync (spectator sees tile reveals within ~500ms)
- Spectator animations: category exit fly-out, content-tv CRT power-on, typewriter question text, input area slide-in, staggered strike → streak → mult reset
- Ready-up consensus with countdown timer
- Victory/end-game sync (auto-victory on final round, all clients see dialog)
- Host-controlled game speed (broadcast to all clients in real-time)
- Deterministic team ordering across clients
- Turn rotation synced via playerIndex
- SFX on all clients (correct ding + good answer splash, wrong strike sound)
- Phase indicator shows active player's name (category select, steal chance)

### What's Left (priority order)

1. **Return-to-lobby turn desync (intermittent)** — one test showed host thinking it was player 4's turn while non-hosts showed player 1. Could not reproduce on subsequent tests. Debug logging added to `category-select` and `play-again` phase transitions to capture state if it recurs. Monitoring.
2. **Safari visual polish** — content-tv clipping issues. Deferred until feature development stabilizes — the content-tv aesthetic may change before a Safari pass is worthwhile.
3. **Lobby UX (future)** — team name editing in lobby, team color selection.
4. **No disconnect handling** — host leaving mid-game strands all players. Lobby back button handles pre-game disconnect, but mid-game disconnects are unhandled.
5. **Debug logging cleanup** — diagnostic `console.log` statements in `category-select` transition, `play-again` transition, and `host syncing category-select` should be removed once multiplayer flows are stable.
6. **Face-off UI polish** — cover plate clipping, countdown animation timing on non-host, turn-header/turn-subtext styling consistency, neutral color refinements. Functional but needs visual iteration.

### What Was Fixed (April 18 session)

- **Scribble session 2 rendering below session 1 (crossfade broken).** `scribbleRenderSessions` was setting `host.style.display = "block"` on `.scribble-summary-sessions`, overriding the CSS `display: grid` rule that the grid-overlay crossfade relies on (all session blocks at `grid-area: 1 / 1`, stacked via opacity). Fix: `host.style.display = ""` lets the class rule win. Session 2 now properly replaces session 1 in the same div with the automatic cycler behavior.
- **Unified scribble summary panel styling.** Title + sessions + totals now share one `#1a1a1a` surface: moved `background: #1a1a1a` up from `.scribble-session-block` onto parent `.scribble-summary-sessions`; added `background: #1a1a1a` + `border-radius: 10px 10px 0 0` on `.scribble-summary-title`; zero gap between children (`gap: 0`); `margin-top: -8px` on `#scribble-summary` eliminates the scribble-container padding gap under the scoreboard.
- **Scribble summary entry/exit as slide-from-scoreboard.** Entry keyframe simplified from scale/opacity/translateY(28px) to pure `translateY(-100%) → translateY(0)` so the summary descends from behind the scoreboard. New `ss-fly-out` keyframe + class added for the reverse. Wired into `advanceRound` via `Promise.all` with the existing `anim.sequence` exit steps — the 0.45s slide-up completes in parallel with (and is explicitly awaited alongside) the input + content-tv exits before `resetModuleCanvas` wipes the canvas.
- **"WAITING FOR YOUR BATTLE" rendering at ~8px in face-off.** The non-participant's `setInputAreaMode` call passed `subtextFitBase: '1rem'` (which is misleadingly applied to `turnHeader --fit-base`, not the subtext), combined with the 23-char message hitting the non-wrap `maxChars: 12, power: 1` path → `scale = 12/23 ≈ 0.52` × `1rem = 8.3px`. Fix: swap for `headerWrap: true` so the message wraps across 2 lines at ~27px. Future cleanup: `subtextFitBase` is a misnomer — it controls the header, not the subtext.
- **Face-off splash scoped to `#module-canvas`.** Was mounting to `#game-root` at `z-index: 9500`, covering the entire canvas. Now mounts to `#module-canvas` at `z-index: 50`, leaving sidebar (phase-indicator, input-area) and scoreboard visible during the "FACE"/"OFF" slam. Typography scaled down to match the narrower canvas width: title `6.5rem → 5.5rem`, vs `2.6rem → 2.1rem`, name max-width `360px → 260px`, padding `22px → 18px`.
- **Round-type picker cards blinking out on exit (amethyst/topaz only).** `.rt-card.rt-has-gem.rt-gem-revealed.rt-tier-amethyst` (4-class specificity) applies `animation: rt-card-glow-pulse infinite`. `.rt-card.rt-sliding-out` (2-class specificity) tried to apply `animation: rt-card-slide-up` on exit — but the higher-specificity pulse won the cascade, so the exit animation never ran. Card kept pulsing in place until `innerHTML = ""` wiped it at the stagger timeout, appearing to "blink out." Fix: scope the pulse with `:not(.rt-sliding-out)` so it stops matching during exit, letting `rt-sliding-out` win the cascade. Only amethyst and topaz were affected (sapphire/emerald don't trigger the pulse rule).
- **Round-type picker cards blinking out on gem reveal (amethyst/topaz only).** Same specificity war, different trigger. When a card's gem reveals, the card gains `.rt-gem-revealed`, matching the 5-class pulse rule (`.rt-card.rt-has-gem.rt-gem-revealed.rt-tier-{amethyst,topaz}`). That rule replaced the slide-in animation — but `anim.stagger` had set an inline `animationDelay` longhand on the card during entry, and CSS inline longhands override class-defined shorthand defaults. The pulse animation inherited the stale 300–600ms delay, did nothing during that window, and the card's base `transform: translateY(-110%)` state showed through for that frame → blink. Fix: clear `card.style.animationDelay = ""` in the per-card gem-reveal timer callback before adding `.rt-gem-revealed`. Same class of bug (+ same fix) as `animateCategoryTransition`'s defensive `animationDelay = ""` clear.
- **Non-host scribble session-end timing lag.** Each client ran a fresh 2.2s session-end hold starting from when *their own* `scribbleApplyEndDrawingSession` fired. Non-host's fire was delayed by Firestore RTT (200–500ms), so summary / advance lagged host visibly. Fix: host stamps `scribbleEndTs = Date.now()` at the host caller, syncs it, and both caller and non-host reconcile handler pass it as an `anchorTs` param. `scribbleApplyEndDrawingSession` shrinks its `holdMs` by `Date.now() - anchorTs` (floored at 200ms). All clients now cross into the next step in near-lockstep.
- **Non-host scribble round "hang then jump" exit.** Symptom: non-host sees scribble drawing UI persist past round-end, then everything snaps to round-type-select. Two compounding causes: (1) `scribble-session-end` reconcile handler was guarded on `scribbleState.phase === "drawing" || "countdown"` — if the non-host missed an intermediate snapshot (e.g. their `scribble-drawing-start` handler aborted), this handler silently no-op'd, leaving the drawing UI mounted; (2) `round-result` safety net only force-showed Ready Up, never hid stale scribble DOM — so the Ready Up button stacked *on top of* the frozen drawing canvas. Fix: (a) loosen the phase guard to accept any live-scribble phase with defensive `scribbleInitSessionScoring()` init; the underlying `scribbleApplyEndDrawingSession` already early-returns on session-end/summary so re-entry is safe. (b) Extend the round-result safety net with a stale-scribble-container sweep: when `lastResult.outcome === 'module-complete'` and `#scribble-container` is still visible, either call `scribbleShowSummary()` (if `sessions.length > 0`) or hide `#scribble-game`, `#scribble-word-select`, `#scribble-summary`, and the container outright. Idempotent — safe even when the normal path already ran. Follows Step 7's "bring the client to this phase's canonical state regardless of prior local state" philosophy.

### What Was Fixed (April 18 session, part 2)

- **Face-off non-host snap-cut → proper exit choreography.** Non-host entry into face-off (reconcile block at `data.faceoffState.active && !wasActive`) was a snap-cut with a comment acknowledging that "async exit animations caused the setup to hang." Replaced with the round-type-select transition pattern: content-tv `tv-off`, board-wrapper `offscreen` (with tick SFX via `anim.timer`), scribble-summary `ss-fly-out` if present — all awaited via `Promise.all` with gated conditionals (`_ssExiting ? anim.done(_ss) : Promise.resolve()`) so non-existent elements don't hang the await. Captures `_foEntryBattle` locally to avoid state drift during the async gap.
- **Face-off non-host 2-second delay (caused timer desync).** Initial version of the above also added `await anim.wait(2000 / gameSpeed)` to match `advanceRound`'s between-round buffer. This was wrong: host's `advanceRound` pays that 2s BEFORE writing the faceoff snapshot, so by the time non-host receives the snapshot, host is already ~2s ahead on wall-clock. Face-off battle timer uses host-written `battleExpiry` (wall-clock timestamp), so the extra wait just ate live battle seconds. Removed the wait. Non-host now only pays ~400ms for exit animations, which is acceptable given the timer is wall-clock-bound.
- **Round-type picker gem reveal: empty card slots no longer consume 650ms.** Previous code used `cards.forEach((card, i) => ...)` with `gemOffset = allCardsLandedMs + i * gemHopMs`, so a lone gem on card index 2 waited 1300ms for two empty slots to "reveal" (nothing). Replaced positional index with a `gemSlot` counter that only increments for gem-bearing cards. Single-gem setups now reveal the gem immediately after cards land.
- **Mode-select CSS tweaks.** `#mode-select` gap 5px, margin-top 60px. `#mode-select h1` margin-bottom 0. Visual tightening only.

### Version tag + "Ship it" convention

- **`#version-tag` element** in `#game-root` (top-left of canvas, subtle `rgba(255,255,255,0.35)` Bitcount Mono Single text, `pointer-events: none`). Currently `v0.13`. Single source of truth for the version string — a deploy script or GitHub Action can sed-replace this line.
- **Auto-increment scheme:** hundredths bump (v0.10 → v0.11) on each push to `main`. Manual tenths bump (v0.11 → v0.20) for major feature milestones, decided case-by-case.
- **"Ship it" trigger phrase:** user says "Ship it" to mean bump hundredths + commit + push to `main` (which auto-deploys to GitHub Pages). Variations: "Ship it at v0.20" for a manual tenths bump; "Commit but don't ship" to commit without pushing.
- **Dev mode button removed from start screen** but underlying `activateDevMode()` / `_dismissStartScreen()` JS retained so it can be re-enabled quickly if needed. The button was irrelevant during most recent development.

### Host/non-host UI drift at round-result (spawned as separate task)

Observed end of scribble round with visible divergences between host and non-host:
- **Input-area header copy:** host shows "RED TEAM WON WITH 2250 PTS!" (short form, `handleModuleComplete` feud.html:10319 builds from local variables). Non-host shows "RED TEAM WON THE ROUND WITH 2250 POINTS!" (long form, round-result safety-net feud.html:8607-8619 reads `data.roundResultMsg` which host synced from the phase-indicator text).
- **Button label:** host "Ready Up" vs non-host "Ready for Face-off" — non-host's face-off-pending logic overrides the label.
- **Phase indicator team color:** host's `handleModuleComplete` calls `setPhaseText` + `setPhase` but NOT `setPhaseTeamColor(scoringTeam)`, so the phase indicator keeps the last-set team color (typically the scribble turn's active team, not the scoring team). Non-host's reconcile path reads `data.roundWinner` and sets the color correctly.

**Root cause (bug class, not instance):** dual-writer architecture. Host writes UI locally (fast path) AND syncs to Firestore. Non-host only reads Firestore. Every phase with a custom host-side local render path is a potential drift site because the two paths independently construct UI from different inputs.

**Spawned task:** extract shared `renderXxx(data)` functions that both host and non-host call with identical Firestore-shaped data objects. Audit all divergence points (round-result most visible; also category-select entry, gameplay updates, steal phase, face-off transitions, victory, play-again). Land in pieces, not one giant PR. See task chip for full brief.

### What Was Fixed (April 17 session)

- **Scribble word-select short-circuit on host-last-to-pick** — host's own `syncState({scribbleWordPicks.${myUid}: pick})` is skipped by the snapshot listener (self-echo), so `scribbleState._wordPicks[hostUid]` was never populated. When host was the LAST drawer to pick, `scribbleHostMaybeStartEarly` never saw both picks and the 10s timer ran full duration. Fixed by mirroring the host's own pick into `_wordPicks` locally at the drawer click handler + the auto-pick countdown path. Also added session-start reset: `_wordPicks = {}` at the top of `scribbleStartWordSelection` so stale picks from a prior session don't false-positive.
- **Scribble phase indicator stuck on "pick a round type"** — `enterScribbleRound` now calls `setPhaseText("gameplay", "LET'S SCRIBBLE!")` + `setPhase("gameplay")` to override the leftover round-type-select text for the duration of the round.
- **Scribble word bank CSV wired up** — `SCRIBBLE_WORD_BANK` now loads from `scribblewords.csv` at page load (50 easy / 50 medium / 50 hard). Uses the existing `parseCSVLine` helper. Hardcoded seed arrays remain as offline fallback.
- **Input-area active during round-type-select** — `updateRoleUI` was clobbering `setInputAreaMode({mode:'disabled'})`'s state by re-enabling the guess input based on whose turn it was. Added a `moduleOwnsInput` guard: when `#input-area` has `data-ia-mode` of `'disabled'` or `'action'`, `updateRoleUI` no longer touches the input/submit button. Matches the existing subtext-skip pattern.
- **Module-complete Ready Up safety net** — in the `round-result` reconcile handler, if `lastResult.outcome === 'module-complete'` and `#input-area` isn't already in `'action'` mode, force-apply `setInputAreaMode('action', {Ready Up})` using the synced `roundResultMsg`. Recovery path for clients that missed intermediate scribble phase snapshots (e.g. via transient Firestore write failures) — without this, the module's own completion path never runs locally and the player is stuck on the mid-module input-area text. Idempotent; safe when the module's path also ran.
- **Pre-Blaze Cleanup Refactor Step 4 landed** — `resetModuleCanvas()` added (feud.html). See "Pre-Blaze Cleanup Refactor" section above for details.
- **Pre-Blaze Cleanup Refactor Step 4b landed** — `resetEvergreenRegions()` added (feud.html). Defensive baseline for game-boundary transitions. See same section.
- **Active diagnostic log** — `console.log('[endRound]', {...})` at `endRound`'s entry. Temporary; logs `_lastRoundWasModule`, `iaMode`, `isHost`, `roundNumber`, etc. Planted to diagnose the "Ready for Face-off button only shown to host after module×3→feud sequence" bug (on radar). Remove once confirmed + fixed.

### Round-Type Picker Polish (April 17 session, part 2)

Visual + UX pass on the round-type picker (`showRoundTypePicker`):

- **Sequential gem reveal** — all 3 cards slide in first (staggered), then gems hop in left-to-right with 650ms gap (matches `rt-gem-hop` duration). Each gem reveal plays a glint SFX.
- **Exit slide-up on selection** — new `rt-card-slide-up` keyframe + `.rt-sliding-out` class; `hideRoundTypePicker` staggers cards out at 70ms intervals before clearing the container. Cards retreat behind the scoreboard.
- **Gem color palette swap** — `--rt-gem-color` CSS variable per tier: emerald `#00a90d`, sapphire `#4c8cff`, amethyst `#d803ff`, topaz `#fe5815`. `.rt-gem-value` text colors match.
- **Gem + value lift together on hover** — identical `transform` + `rt-gem-lift-nudge` animation applied to both `.rt-gem img` and `.rt-gem .rt-gem-value`.
- **Amethyst + topaz pulse glow** — `rt-card-glow-pulse` keyframe uses `color-mix(in srgb, var(--rt-gem-color) N%, transparent)` for a gem-tinted box-shadow aura on the two highest tiers.
- **Gem tooltips** — added 4 entries to `tooltips.csv` (`gem-emerald`, `gem-sapphire`, `gem-amethyst`, `gem-topaz`) describing each tier's multiplier. Category-row tooltip (`data-tip="cat-pill"`) removed — redundant with gem tooltip coverage.
- **`rt-picker-grid` bleed** — `margin-top: -5px` so cards tuck up under the scoreboard for a cleaner seam.
- **Phase indicator centering** — `.ph-span` now `position: absolute; inset: 0` with flex centering so every phase's text sits visually centered in the 140px band, not left-anchored.

### Scribble Polish (April 17 session, part 2)

- **Scribble panel labels team-colored** — `.scribble-panel-label.team-red` / `.team-blue` CSS rules added. `setupScribbleDrawingSession` (guesser branch) assigns the class so teammate label uses viewer's team color, opponent label uses the other team's color. Gap between the label strip and its canvas panel reduced to 0 for a flush look.
- **Word-pick time 10s → 15s** — `wordSelectTime` constant bumped. Gives drawers more breathing room when weighing three difficulty options.

### Music Polish (April 17 session, part 2)

- **Per-track volume -20% across the board** — `MUSIC_TRACKS` (`maintheme`, `roundselect`, `draw`) and `PLAYLIST_TRACKS` (`bossa`, `ranked`) all at `vol: 0.32–0.4` (from 0.4–0.5). Each track's `vol` multiplies with `volumeMaster × volumeMusic` in the crossfade gain math.
- **`volumeMusic` default restored to 1.0** — was `0.6` as a temporary reduction; mix balance now lives in per-track `vol` instead.

### Crashes Fixed (April 17 session, part 2)

- **`myTeam is not defined` in `scribbleStartDrawingSession`** — the guesser-branch label-coloring block referenced a bare `myTeam` that wasn't in that function's scope (caller `scribbleEnterDrawingForMyTeam` derives it locally, but the function itself doesn't receive it). Crashed on every non-host client's drawing-start reconcile, preventing canvases + tile grid from rendering. Fixed by re-deriving `_myTeam` inside the guesser branch via the standard `(isMultiplayer && myUid && teamPlayerUids[1]?.includes(myUid)) ? 1 : 0` pattern.

### What Was Fixed (April 14 session)

- **`amDesignatedAdvancer()`** — was using `teamPlayerUids[0][0]` (alphabetical first UID) instead of `isHost`. Caused wrong client to call `advanceRound()`. Simplified to `return isHost`.
- **Streak/mult decrease SFX on round exit** — `decreaseblip.mp3` fired during round transitions via stale `updateStreakDisplay` callbacks. Fixed with `_streakDisplayGeneration` counter (incremented in `initRoundState`) and `_prevStreak`/`_prevMultiplier` pre-sync in reconcile when `currentStreak` drops to 0.
- **3D prism buttons replaced** — `.input-btn` (4-face rotating prism) replaced with flat `.btn .action-btn` for all action buttons (Submit, Ready Up, Next Round, etc.). Category pills keep `.btn-3d`. Eliminated the `filter: brightness()` flattening bug on disabled buttons and removed `setup3dBtns()` calls for non-category elements.
- **Spectator round-end effects** — failed steal wiggle + `negativebeep.wav` + strikes glow fade now synced via `lastResult.outcome === 'steal_fail'` in reconcile. Phase indicator `round-glow` + `sfxRoundEnd` + blob color reset now fire in `handlePhaseTransition` directly (bypassing `setPhase` early-return caused by synchronous `data-phase` attribute set).
- **Spectator category exit animation** — non-host now uses `animateCategoryTransition()` (same as host) instead of the simplified `animateSpectatorCategoryExit()`. Selected category gets the full glow → CRT power-off sequence on all clients.
- **Spectator round-advance exit animation** — non-host `category-select` phase handler now mirrors host's `advanceRound` exit sequence (input slides down → content-tv slides out left → board slides out) before `initRoundState()`.
- **Category pills opacity flicker** — removed `blend-multiply` from `#category-pills-area`. Replaced with simple `background: rgba(17,17,17,0.35)`. Added `pills-slide-in` animation (slides from left). Eliminated the `opacity: 0` → rAF → `opacity: 1` race condition workaround.
- **Blob background simplified** — fixed SMPTE-inspired colors per blob (green/yellow left, magenta/cyan right). `--bg-blob-base` now only controls `#game-root` background gradient. Neutral color changed from purple (`#513f6d`) to black (`#111`). All inline fill override code removed.
- **Reveal All automatic** — `revealAll()` now auto-triggers 3 seconds after round winner is determined (both mid-game and final round). Reveal All button removed from UI. Works on all clients locally (no Firestore sync needed).
- **Non-host input focus** — `updateRoleUI` now focuses guess input when it's the player's turn, but only after `sq-zone-input` has finished its slide-in (prevents browser forcing offscreen element visible). `setupQuestionScreenForSpectator` focuses input at end of `anim.sequence`.
- **Spectator tooltip access** — `pointer-events: none` moved from `.cat-row` to child `.btn-3d`/`.action-btn` elements via `.spectator-disabled` class, preserving hover for tooltips.

### What Was Fixed (April 15 session, part 2)

- **Host submit button during teammate's turn** — confirmed fixed. `updateRoleUI` correctly disables the submit button after host's scoring animation completes.
- **Speed boost non-host persistence** — `deactivateSpeedBoost()` was only called inside `submitGuess()` (host-only code path). Non-host clients go through `reconcileLocalState` → `flipTile().then()`, which cleared `_scoringInProgress` but never deactivated speed boost. Added `deactivateSpeedBoost()` to the non-host's `flipTile().then()` callback in reconcile.
- **Victory dialog height** — increased from 60% to 72% of canvas height (+~80px) to better fit action buttons and vote status notices.
- **Awards host-synced** — `computeAwards()` used `Math.random()` shuffle independently on each client, causing tied awards to resolve differently per device. Fix: host computes awards in `endGame()` and syncs the result array to Firestore (`data.awards`). Non-host reads `_syncedAwards` from reconcile instead of computing locally. `playVictoryAnimation(winnerIdx, awards)` now receives pre-computed awards. Local/single-player mode unchanged (computes locally as before).
- **Awards tie-breaking simplified** — replaced two-pass system (which spread tied awards across players by preferring unawarded ones) with single-pass logic. On ties, candidates are filtered to the subset with the fewest existing awards this game, then randomized within that subset. A player who legitimately earns multiple awards outright can sweep.
- **Captains feature (lobby + scoreboard)** — added first-player-to-join = captain per team, displayed in lobby with a gold "C" badge. Captain or host can reassign via per-teammate "↑C" button (only visible to same-team, same-authorized viewer). Captaincy locked at `lobbyStartGame` via new `teamCaptainUids` field in Firestore, read into local `teamCaptainUids` + `hostUid` at `transitionFromLobbyToGame`. In-game scoreboard shows C (gold) and H (gray) badges before player names in `updatePlayerPanels`. `getCurrentCaptainUid(team)` helper returns locked captain if still in `teamPlayerUids[team]`, else falls back to first remaining player — disconnect-proof even though disconnect detection itself isn't wired up yet. Tooltips added for all 4 badge types + the make-captain button.

### What Was Fixed (April 15 session, part 1)

#### Victory Dialog & Post-Game Flow
- **Victory dialog redesigned** — "Dismiss" button replaced with toggle arrow (▼/▲) in header corner. Three action buttons in a CSS grid row: "Play Again" (consensus), "Return to Lobby" (timer), "Exit to Menu" (individual). Vote status text below buttons.
- **Play Again vote system** — multiplayer: all players must vote unanimously. Votes synced via `playAgainVotes` map in Firestore. Host triggers `phase: 'play-again'` on consensus. Non-host receives via `handlePhaseTransition` — resets state, slides out victory panel, waits for `category-select` phase (no `executePlayAgain` call to avoid async race conditions).
- **Return to Lobby vote system** — 25-second countdown starts on first vote. Unanimous vote triggers immediately. Players can switch votes. Host writes `status: 'lobby'` to Firestore. Vote state: `lobbyVotes`, `lobbyCountdownStart`.
- **Exit to Menu** — individual action. Removes player from Firestore `players` map. Remaining players' consensus thresholds auto-adjust via `teamPlayerUids` filtering in `reconcileLocalState`.
- **Victory panel slide-out animation** — `slideOutVictoryPanel()` stops particles/canvases immediately but lets panel exit via CSS transition. Runs in parallel with exit animations on Play Again, sequentially on Return to Lobby.
- **`stopVictoryAnimation` race fix** — `VICTORY._stopped` guard prevents deferred `requestAnimationFrame` from re-adding `active` class after stop. Backdrop `display: none` set explicitly.

#### Game Reset & UI Cleanup
- **`resetGameUI()` function** — comprehensive DOM cleanup: resets scores, round counter, board wrapper, content-tv, input area, category pills, phase indicator, sidebar panels, scoreboard animation classes. Called by `executePlayAgain`, `executeReturnToLobby`, and `startGameFromLobby`.
- **Stale category pills flash** — `resetGameUI` now clears `#category-pills-area` innerHTML, preventing old pills from flashing on non-host during game restart.
- **Return-to-lobby exit animations** — added board/input/content-tv exit sequence (was missing). Guard flag `_returningToLobby` prevents double-execution from concurrent snapshots.
- **Game listener stopped before animations** — both `executePlayAgain` (host only) and `executeReturnToLobby` stop the game listener before async animations to prevent snapshot interference.
- **Play-again infinite loop fix** — non-host no longer stops/restarts game listener during play-again. The restarted listener was seeing the same `phase: 'play-again'` and re-triggering `executePlayAgain` infinitely. Non-host now keeps listener running and waits for `category-select`.
- **Play-again round counter race fix** — non-host `play-again` handler no longer calls `executePlayAgain()`. Instead it just resets state and dismisses victory panel. The `category-select` handler sets `roundCounter` correctly without competing async functions.
- **Exit to Menu setup bleedthrough** — `exitToMainMenu` now hides setup and ribbon-scroller after `resetGame()` before showing mode select.

#### Scoring Guard (concurrent answer prevention)
- **`_scoringInProgress` flag** — set `true` before `flipTile()`, cleared after. Blocks `submitGuess()` at the top via early return.
- **`updateRoleUI` respects scoring guard** — `guessInput.disabled` and `submitBtn.disabled` now check `_scoringInProgress` before enabling, preventing the role UI from re-enabling controls during animations.
- **Non-host scoring guard** — `reconcileLocalState` sets `_scoringInProgress = true` and disables input/button when a tile reveal snapshot arrives. `flipTile().then()` clears the flag and calls `updateRoleUI` to restore correct state.
- **Host post-scoring role UI** — after `flipTile` completes, host calls `updateRoleUI(getActivePlayerUid())` instead of blindly re-enabling controls, so the button is correctly disabled when it's the teammate's turn.
- **Enter key guard** — inline `onkeydown` handler checks `!_scoringInProgress` before calling `submitGuess()`.
- **Submit button selector fix** — all references changed from `getElementById("turn-submit-btn")` (which returned `null` — button never had that ID) to `querySelector('#turn-body .action-btn')`.

### Lobby Redesign (April 14 session)

- **Host name input** — `showCreateGame()` now shows a name input form. Blank defaults to "Player 1". Host auto-assigned to Red team with `joinedAt` timestamp.
- **Auto team assignment** — `submitJoinGame()` counts red vs blue players and assigns to the smaller team (red if tied). `joinedAt: Date.now()` added to all player entries.
- **3-column layout** — Red Team | Unassigned | Blue Team. "Undecided" button lets players move to unassigned. Join buttons fixed above player lists (never pushed down).
- **Chronological ordering** — player lists sorted by `joinedAt` instead of UID. First joiner appears at top.
- **Start validation** — requires all players on teams AND both teams have ≥1 player. Dynamic button text explains why Start is disabled.
- **Back button** — `leaveLobby()` function: host leaving deletes game doc (kicks all players via `onSnapshot` `!snap.exists()` handler), non-host leaving removes self via `deleteField()`. `deleteField` added to Firestore imports.
- **Settings doubled** — lobby settings display at 1.8rem font, 48px gap.
- **Click to copy label** — visible label next to game code, updates to "Copied!" on click.
- **Game code length** — currently set to 1 character for dev testing convenience. Change loop bound in `generateGameCode()` to restore (4-5 chars for production).

### Parallel Data Structures (multiplayer-specific)

- **`teamPlayerUids = [[], []]`** — parallel to `teamPlayers`, stores Firebase UIDs. Set by `transitionFromLobbyToGame()` from host-written `data.teamPlayers` arrays (sorted by UID for determinism).
- **`teamCaptainUids = [null, null]`** — locked captain UID per team at `transitionFromLobbyToGame`. Host writes `teamCaptainUids` to Firestore alongside `teamPlayers`. Used by `getCurrentCaptainUid(team)` helper which falls back to `teamPlayerUids[team][0]` if the locked captain is no longer in the roster (disconnect fallback).
- **`hostUid`** — synced from Firestore game doc at game start so all clients can render the H badge. Independent of the local `isHost` boolean.
- **`_lobbyStartingTeam`** — host-determined starting team, passed through Firestore so all clients agree.
- **`_syncedCategoryPicks`** — `{ picks, hasSurvey, multipliers, questions }` object synced by the host. Includes pre-selected questions per category.
- **`_preSelectedQuestions`** — `{ category: { question, answers, _poolIdx } }` local cache. Host generates at category time; non-host clients receive via synced `categoryPicks.questions`.
- **`_prevSnapshot`** — last Firestore snapshot data, used by `reconcileLocalState` for diffing.
- **`_readyPlayersMap`** — `{ uid: true }` map tracking ready-up clicks. `_readyCountdownEnd` / `_readyCountdownInterval` for the 10-second timer.
- **`_syncedAwards`** — host-computed awards array synced in `endGame()`. Non-host reads this in reconcile and renders via `renderVictoryAwards()` — arrives as a separate snapshot after the round-result sync, so non-host's victory dialog shows empty awards briefly then populates.

### Captains Feature

First player to join each team is captain by default. Players have `isCaptain: boolean` in the Firestore `players` map. Rules:

- **Create game** — creator gets `isCaptain: true`
- **Join game** — new player gets captain if their auto-assigned team has no current captain
- **`joinTeam(teamIdx)`** — on team change, transfers captaincy: if leaver was captain, next earliest `joinedAt` on old team inherits; if new team has no captain, mover becomes captain
- **`leaveLobby()`** — if leaver is captain, next earliest teammate inherits before the player entry is deleted
- **`reassignCaptain(newCaptainUid)`** — lobby-only, callable by current team captain or host. Batched `updateDoc` flips `isCaptain` on old/new captains
- **`lobbyStartGame()`** — locks captain UIDs into Firestore `teamCaptainUids: [red, blue]` alongside `teamPlayers`
- **`transitionFromLobbyToGame()`** — reads `teamCaptainUids` and `hostUid` from synced data into locals
- **`getCurrentCaptainUid(team)`** — returns locked captain if still in `teamPlayerUids[team]`, else `teamPlayerUids[team][0]` (disconnect fallback; dormant until disconnect detection is wired up)

UI: gold "C" badge in lobby next to captain name; small "↑C" button for non-captain teammates visible only to captain/host. In-game scoreboard shows C (gold) and H (gray) badges inline before the player name in `updatePlayerPanels`'s `itemHtml` closure. Tooltips for all badges + make-captain button in `tooltips.csv`. Captains are prerequisite for the Prizes system.

### Face-off Round

A fixed additional round that runs at the end of every game before the victory dialog. Replaces the old Fast Money concept as the primary endgame feature. Two parallel 1v1 battles, each 60s, with simultaneous input from the two selected players. Scores get a flat 2x multiplier and fold into `teamScores[]` before the winner is determined.

**Flow**:
1. Final normal round ends → `endRound()` detects `isLastRound && !faceoffState.completed` and schedules `enterFaceoffRound()` after a 5s pause (scaled by gameSpeed)
2. Host picks two unused Survey questions and two random player pairs (one per battle per team)
3. Host syncs `faceoffState` + `phase: 'faceoff'`; all clients call `setupFaceoffUI()` + `startBattle(0)`
4. Battle 1 plays out on the left; Battle 2 plays out on the right afterwards
5. On all-revealed or timer expiry, `endBattle()` reveals remaining tiles as missed, advances to next battle or calls `endFaceoffRound()`
6. `endFaceoffRound()` applies 2x, folds into teamScores, triggers normal `endGameByRounds()` flow for victory dialog + awards

**State**: `faceoffState` object near the multiplayer state block. Reset by `resetFaceoffState()` called from `startGame`, `startGameFromLobby`, `resetGame`, and `resetGameUI`. Includes `active`, `completed`, `currentBattle`, `questions[2]`, `playerUids[2][2]`, `playerNames[2][2]`, `revealed[2][]`, `revealedData[2][]`, `battleScores[2][2]`, `battleExpiry[2]`, `battleGuesses[2][]`, `timerInterval`.

**Round counter**: `setupFaceoffUI()` swaps `#round-label` text from "Round" to "FACEOFF" and hides `#round-info`. Both are restored in `resetGame` and `resetGameUI`.

**DOM**: `#faceoff-container` is a flex row with two `#faceoff-battle-{0,1}` children, each containing `.faceoff-question`, `.faceoff-timer`, `.faceoff-board`, `.faceoff-battle-total`. Hidden by default (`display: none`), shown via `setupFaceoffUI()` which also hides `#board-wrapper` and `#content-tv`.

**Styling**: face-off boards reuse ranked board DOM classes (`.answer`, `.tile-cover`, `.tile-inner`, `.tile-front`, `.tile-back`, `.tile-num`, `.tile-text`, `.tile-pts`) inside `.faceoff-board`. Team color applied via scoped `.faceoff-board .tile-back.faceoff-{red,blue,missed}` overrides. Cover-slide reveal, tile marquee, and hover lift inherit automatically. `renderFaceoffBoard(battleIdx)` builds tile DOM once per question and does incremental reveals from `faceoffState.revealed`/`revealedData`.

**Input routing**: `submitGuess()` has an early branch — if `faceoffState.active`, routes to `submitFaceoffGuess()` which forks by client:
- Local / host: calls `evaluateFaceoffGuess(guess, myUid)` directly
- Non-host multiplayer: writes `pendingFaceoffActions.${myUid} = { guess, clientTs, battleIdx }` — a map (not single field) so simultaneous submissions don't overwrite each other. Host picks them up in `reconcileLocalState`, sorts by `clientTs`, processes each and clears via `deleteField`.

**Latency caveat**: host has a ~300ms advantage on same-answer races because its submissions don't round-trip. Known and accepted. The `clientTs` field is already captured so the eventual Cloud Functions migration can use it for fair server-authoritative ordering.

**Timer**: host writes `battleExpiry[currentBattle]` as a wall-clock ms timestamp. All clients run a local 250ms-tick countdown reading the synced expiry. On expiry, only the host calls `endBattle()` (authoritative). Warning class `.warning` applies at ≤10s remaining.

**Player selection**: random each time. `enterFaceoffRound()` shuffles `teamPlayerUids[team]` (or `teamPlayers[team]` in local mode) and picks the first two. 1-player teams use the same player for both battles; 3+ player teams leave positions 2+ out of the face-off. For voting-based selection later, swap the shuffle logic at one call site.

**Local mode attribution**: local mode has only one input field, so `evaluateFaceoffGuess` uses a `_localTurnToggle` to alternate which team gets credit. This is imperfect and explicitly acknowledged as a placeholder — multiplayer is the primary test path.

**Fast Money legacy**: the old Fast Money code (`fm` state object, `startFastMoney`, `fastmoney_questions.json`, `#fast-money` DOM) is still on disk but orphaned. The "Fast Money Round" button has been removed from `endGame()`. Nothing calls `startFastMoney` anymore. Safe to delete entirely in a future cleanup pass.

### Firestore State Cleanup Across Games

When the same Firestore document is reused across games (play-again or return-to-lobby → new game), `updateDoc` merges fields rather than replacing, so stale game state from the previous game persists unless explicitly cleared. Two code paths handle this:

- **`executePlayAgain`** — syncs `faceoffState: null, pendingFaceoffActions: null, awards: null` alongside the play-again payload (scores, round number, etc.)
- **`lobbyStartGame`** — when starting a new game from lobby, comprehensively clears ALL game-state fields: `faceoffState`, `pendingFaceoffActions`, `awards`, `gameEnded`, `readyPlayers`, `readyCountdown`, `categoryPicks`, `pendingAction`, `currentQuestion`, `revealed`, `revealedData`, `matchLog`, `guessHistory`, `lastResult`, `roundResultMsg`, `roundWinner`, `roundPhaseText`, `phase`, `roundNumber`, `teamScores`, `strikes`, `currentStreak`, `answerMultiplier`, `roundScore`, `stealPhase`, `categoryMultiplier`, `playerIndex`, `usedQuestions`

This prevents stale fields from a previous game (especially `faceoffState.completed` and `categoryPicks`) from bleeding into the new game's reconcile snapshots.

### Lobby UI Updates (April 15–16 sessions)

- **Player name alignment**: names left-justified (`.lobby-player-name` with `flex: 1; text-align: left`), badges right-anchored via flex layout
- **Name truncation**: `.lobby-player-name` uses `text-overflow: ellipsis; overflow: hidden; white-space: nowrap` — badges stay full-size while long names truncate
- **Badges**: HOST (gray), CAPTAIN (gold), MAKE CAPTAIN (gold border button) — all with `data-tip-placement="below"` and full-word labels
- **Game code**: limited to characters `1`, `2`, `3` for dev testing (restore full charset before shipping). 1-character length (restore to 4-5 for production).
- **Default rounds**: online games default to 2 rounds (`maxRounds: 2` in `submitCreateGame`)

### Tooltip Positioning Improvements

The tooltip arrow now tracks the true target center instead of always pointing at `left: 50%` of the tooltip body:

- **CSS variables**: `--tip-arrow-x` (for above/below placements) and `--tip-arrow-y` (for left/right) replace the hardcoded `left: 50%` / `top: 50%` in `#tooltip::after` rules
- **JS calculation**: after viewport-edge clamping, `showTooltip` computes the arrow's position as `targetCenterX - tooltipLeft` (or Y equivalent), clamped to 12px padding from tooltip edges
- **Auto-flip**: forced `data-tip-placement="below"` auto-flips to `above` if the target is in the bottom 20% of the canvas; `above` flips to `below` if in the top 20%

### Dev Mode Question Pool

`computeDevModeQuestions()` limits the available question pool per category. Increased from 3 to **10** per category to support multiple consecutive games with face-off (each game uses 2 normal questions + 2 face-off Survey questions from the pool). `usedQuestions` persists across play-again to prevent repeats within a session.

---

## Module Orchestration Layer

Major architectural shift: the game is no longer a fixed sequence of feud rounds. Each round, the active player picks a **round type** (module) from a picker UI, and that module runs independently and returns scores. This replaced the old flow where every round started with category selection.

### Vocabulary

- **Ranked questions** — the umbrella term for feud-style modules (High Five for trivia, Survey for survey questions). Called this because there's a single winner and ranked answer list, distinct from modules like Scribble where both teams can score.
- **Module** — a self-contained round type with its own entry point, internal turn management, scoring, and UI.
- **Orchestrator** — the `advanceRound` → `showRoundTypePicker` → module dispatch layer.

### `ROUND_MODULES` registry

Defined near the top of the script block. Each module entry:

```js
ROUND_MODULES = {
  'high-five':       { label, colorClass, minPlayersPerTeam, enter(onComplete), reset() },
  'poll-position':   { label, colorClass, minPlayersPerTeam, enter(onComplete), reset() },
  'secret-scribble': { label, colorClass, minPlayersPerTeam: 2, enter(onComplete), reset() },
  'common-thread':   { label, colorClass, minPlayersPerTeam: 2, enter(onComplete), reset() },
};
```

`minPlayersPerTeam` gates the pill in the picker — Secret Scribble and Common Thread grey out in 1v1 games. Add new modules by extending this registry.

**Current module roster (all shipped, complete):**
- **High Five** — trivia ranked question (formerly the default feud round).
- **Poll Position** — survey ranked question (the now-deprecated "Survey" round type spun off into its own module). Shares H5's summary classes since the format is identical (ranked answer list, one winning team).
- **Secret Scribble** — Pictionary-style drawing minigame. See "Secret Scribble — Module Overview".
- **Common Thread** — Codenames-style clue/guess round. See "Common Thread — Module Overview".

**Next on the roadmap:** **Number is Correct** (NIC) — Price-is-Right-style numeric guessing. Not yet built.

### Module Visual Identity — Animated Logos

Each module has two logo/animation deliverables that share the same SVG asset:

1. **Cinematic intro** — full-screen overlay on `#module-canvas` that plays before the round begins (via `mod.cinematic()` in `ROUND_MODULES`). Sequenced CSS keyframe animations reveal the logo dramatically, then fade out and resolve a Promise so the module entry function can proceed. Common Thread's cinematic (`_playCtCinematic`) is the reference implementation — it animates text trace + fill, draws the thread line, slides the logo up, and fades in role assignments for multiplayer.

2. **Animated logo on the round-type picker card** — a compact looping animation displayed inside the `.rt-card` while the player is choosing a round. Loops indefinitely via CSS `animation: ... infinite`. Common Thread uses a boomerang `stroke-dashoffset` loop on the thread path (`.rt-ct-logo-line`).

**Status by module:**
- **Common Thread** — ✅ Both done. SVG: inline in `feud.html` (viewBox `0 0 500 210`, Futura Bold text + cubic-bezier thread path). Cinematic: `_playCtCinematic()`. Picker logo: `.rt-ct-logo-line` boomerang animation.
- **High Five** — ✅ Both done. Picker logo: `_buildH5PickerArtHtml` — "HIGH" word + numeric "5" in rounded pill + hand SVG (nested at `translate(560 0) scale(0.20)`, viewBox `0 0 826 260`). Cinematic: `_playH5Cinematic()` — 999→5 odometer countdown + high-five slap + 1.8s hold, then **docks in place** (shrinks to 66.5% + `translateY(-190px)` via `.h5ci-docked` class) instead of fading out. While docked, an "SELECT A CATEGORY" subhead (`.h5ci-subhead`) fades in with delay timed to land after pills finish entering. See "High Five round flow" below.
- **Secret Scribble** — ❌ Not started.
- **Poll Position** — ✅ Both done. Prototype: `poll-position-logo.html`. Picker logo: `_buildPpPickerArtHtml` — two stacked 3D spinning prisms ("POLL" cyan-on-white, "POSITION" white-on-cyan) at 0.5× scale, each slot with its own `perspective: 1200px`. Cinematic: `_playPpCinematic()` — POLL + POSITION buttons fly in L/R (0.65s each, staggered), face-cycle rotateX animation (4.5s each), then shared CRT power-off on `.ppci-buttons` wrapper at 6.10s. Known cosmetic limitation: the CRT collapse renders as two closely-stacked lines rather than one, because each slot's `perspective` establishes an independent 3D rendering context that the wrapper's `filter` layer can't fully flatten. Tested a `filter: brightness(1)` + `will-change` baseline on the wrapper in proto — marginal improvement, not worth the diff. Accepted as-is.

**High Five round flow (dock + pills-from-below pattern):**
- H5 is the only module where the cinematic does not exit before the module starts — it docks above and the category pills slide up from below into the vacated space.
- `#h5-cinematic.h5ci-docked` gets `pointer-events: none` so clicks pass through to the pills beneath it.
- `#category-pills-area.pills-from-below` swaps the container's entry animation from `translateX` (slide from left) to `translateY` (rise from below), bottom-anchors the pills (`bottom: 20px`), and overrides each `.cat-row`'s `animation-name` to `cat-slide-in-below`. Must override BOTH the container and the child rows — cat-rows have their own independent `animation: cat-slide-in` (translateX) that the container class alone doesn't affect.
- Host path: `hostProcessRoundTypePick_highFive()` adds `pills-from-below` then calls `showCategorySelection(null, { excludeSurvey: true })`.
- Non-host path: the `case 'category-select':` handler in `reconcileLocalState` adds `pills-from-below` when `data.selectedRoundType === 'high-five'`, mirroring the host.
- `resetModuleCanvas()` is **H5-aware**: it preserves both `#h5-cinematic` AND `pills-from-below` while the cinematic is docked. Without this, the non-host path would wipe both between `round-type-selected` and `category-select` phases, since resetModuleCanvas runs after the cinematic resolves but before `showCategorySelection`.
- Exit gate in `animateCategoryTransition`: all three exit streams must `Promise.all` before the function returns — (1) `#h5-cinematic` fade-out (`.h5ci-fade-out`, 450ms), (2) unselected cat-rows fade-out (`cat-fade-out` keyframe, staggered), (3) selected cat-row glow → CRT power-off. Only after all resolve does `pickCategory` begin content-tv tv-on and board-wrapper slide-in, so no entry animation overlaps with an unfinished exit.

**Animation change (2026-04-21):** Unselected pills' exit animation changed from `cat-slide-out-left` (translateX slide) to `cat-fade-out` (opacity only). Path A items now fade in place instead of sliding off-canvas. The `cat-slide-out-left` keyframe is retained — still used by the non-host spectator exit path in the gameplay handler.

**Implementation pattern for new module cinematics:**
- Mount to `#module-canvas` (≈930px wide) via `document.getElementById('module-canvas') || document.getElementById('game-root')`
- `position: absolute; inset: 0` on the overlay div so it fills the canvas
- SVG width tuned to `~78%` of canvas width for breathing room
- Resolve the Promise after fade-out so the module entry function chains correctly
- Register as `cinematic: () => _playModuleCinematic()` in `ROUND_MODULES`

### Round flow (host-authoritative)

1. `advanceRound()` — flips `teamTurn`, increments `roundNumber`, runs exit animations, clears ready state (`_readyPlayersMap`, `_readyCountdownInterval`, `_readyCountdownEnd`), resets input-area to neutral state, hides any lingering scribble container.
2. **Face-off branch** unchanged — if `faceoffPending`, calls `hostStartFaceoffRound()` directly.
3. Otherwise calls `showRoundTypePicker()`.
4. `showRoundTypePicker()` — renders module pills (reusing `#category-pills-area` with the same stagger animations), sets phase indicator "Pick a round type", wires `onRoundTypePick(moduleKey)` onclick. Non-host see disabled/dimmed pills via `amIActivePlayer()` check.
5. Active player clicks → `onRoundTypePick` (host: direct; non-host: `pendingAction: { type: 'selectRoundType', moduleKey }`).
6. `hostProcessRoundTypePick(moduleKey)` syncs `phase: 'round-type-selected'` + `selectedRoundType`, then dispatches:
   - `'high-five'` → `showCategorySelection(null, { excludeSurvey: true })` (existing feud flow, trivia categories only)
   - `'survey'` → `showCategorySelection(null, { surveyOnly: true })` (skips category UI, auto-picks Survey)
   - `'secret-scribble'` → `enterScribbleRound(handleModuleComplete)`
7. Non-feud modules call `onComplete({ redScore, blueScore })` when they finish.
8. `handleModuleComplete` folds scores into `teamScores[]` (host-only; non-hosts rely on synced values), calls `restoreMainGameUI()`, calls `mod.reset()`, sets phase `round-result`, shows Ready Up via `setInputAreaMode('action')`, host syncs via `syncAfterGuess(..., true)`.
9. Ready Up consensus → `advanceRound()` → next round.

### Module contract

Every non-feud module must:
- Store `onComplete` callback on its state object at entry
- Manage its own internal turn structure (randomized on entry — no reliance on `playerIndex`/`teamTurn`)
- Clean up its UI when done (hide its container when `advanceRound` fires — the orchestrator does this via `restoreMainGameUI`, but module-specific element cleanup goes in the module's `reset()`)
- Call `onComplete({ redScore, blueScore })` when finished

### Turn order philosophy

- **Round-type selection turn order** is strict (uses existing `playerIndex` / `teamTurn` rotation).
- **Within-module turn order** is randomized on module entry (Face-off shuffles drawers, Scribble shuffles session drawers). Modules do not respect or preserve the global `playerIndex` / `teamTurn` / `stealPhase` / `currentStreak` state — those are feud-specific globals.

### New Firestore phases

- `'round-type-select'` — host syncs available module keys, active player UID
- `'round-type-selected'` — host syncs chosen module key
- `'scribble-word-select'`, `'scribble-drawing-start'`, `'scribble-session-end'` — scribble internal phases (see Secret Scribble section)

### `pendingAction` types

- Existing: `selectCategory`, `guess`
- New: `selectRoundType`, `scribbleGuess`

---

## Input-Area Home Base

The `#input-area` in the sidebar is now the player's persistent "home base" — always visible, content changes per game phase instead of sliding in/out with each transition. Analogous to how `#phase-indicator` stays present and swaps text spans.

### `setInputAreaMode(opts)` API

Single function all modules use to update input-area content. Creates canonical `.turn-input-row` and `.turn-action-row` children on first call, then toggles between them instead of replacing `innerHTML`:

```js
setInputAreaMode({
  mode: 'guess' | 'disabled' | 'action',
  header,           // innerHTML — can include team-colored spans
  subtext,          // textContent for turn-subtext
  inputPlaceholder, // placeholder for #guess
  buttonText,       // action mode — label on the button
  onButtonClick,    // action mode — callback (readyUp or advanceRound recognized by reference)
  teamColor,        // 0 = red, 1 = blue — applies team class to #turn-input-box
});
```

**Modes:**
- `'guess'` — input enabled, ready for typing guesses (feud gameplay, scribble guessers)
- `'disabled'` — input visible but greyed with a contextual placeholder (scribble drawers seeing "Drawing — no guessing", anyone waiting, etc.)
- `'action'` — input row hidden, action row shown with a `make3dBtn` Ready Up / Next Round button. Includes `#ready-status` div for countdown/count. Recognized callbacks (`readyUp`, `advanceRound`) get converted to string form for `make3dBtn`'s inline `onclick` attribute; other callbacks fall back to a flat button with `.onclick` property.

### `showInputArea()` helper

Guarantees the sidebar input region is visible and slid-in:
- Shows `#sidebar-question-answer` as flex
- Hides `#sq-zone-content` via `visibility: hidden` (preserving its flex:1 space so input stays bottom-anchored)
- Removes `offscreen-below` / `input-exit` classes on `#sq-zone-input`, adds `input-enter`
- Removes `.hidden` class on `#input-area`

**Critical detail:** don't use `display: none` on `#sq-zone-content` during scribble — its `flex: 1` collapse pushes `#sq-zone-input` to the top of the sidebar, sliding up from the wrong position. `visibility: hidden` preserves the layout.

### Where it's used

- `handleModuleComplete` — sets action mode with Ready Up when a module finishes
- `advanceRound` — sets neutral disabled mode before the next module takes over
- `showRoundTypePicker` — sets "PICK A ROUND TYPE" context (active player) or "Waiting on X..." (non-picker)
- Scribble `scribbleStartWordSelection` — drawer/guesser specific context
- Scribble `scribbleStartDrawingSession` — "YOUR TURN TO DRAW!" for drawer, "GUESS THE DRAWINGS" for guesser
- Scribble `scribbleApplyEndDrawingSession` — "Session complete" disabled state
- Scribble `updateScribbleRoleUI` — replaces the feud-specific role gating with scribble-aware modes

### Feud flow coexistence

The feud `endRound` function still uses direct `turn-body.innerHTML = ...` for its Ready Up. When a non-feud module completes, `handleModuleComplete` sets `window._lastRoundWasModule = true`; feud's `endRound` checks this flag and skips the innerHTML replacement, letting the module's `setInputAreaMode('action')` be the sole Ready Up UI. The flag is cleared after the check. This keeps feud's existing behavior intact while letting modules use the new API.

### Migration note

Feud rounds (High Five, Survey) still use the legacy `turn-body.innerHTML` swap pattern. Future cleanup: migrate them to `setInputAreaMode` for consistency. Both patterns coexist safely because `setInputAreaMode` rebuilds canonical rows if they're missing.

---

## Secret Scribble — Module Overview

Pictionary-style drawing minigame. Requires 4+ players (2 per team minimum). See `secret-scribble.html` for the standalone prototype that preceded integration.

### Round structure

One scribble round = 2 drawing sessions. Each session has 2 drawers (one per team) drawing simultaneously while the other players guess. Drawer/guesser assignment rotates between sessions (session 0 uses `teamPlayerUids[team][0]`, session 1 uses `teamPlayerUids[team][1]`).

### Phase flow

1. **Word selection** (`scribble-word-select`, 10s) — each drawer picks from 3 options (easy/medium/hard, 50/75/100 points). Guessers see "Drawers are selecting words". Drawers who pick early see "Pick locked in. Waiting for other drawer..." First drawer's early pick doesn't start the session — all clients wait for timer expiry so drawing starts simultaneously. Missing picks auto-fill to medium difficulty.
2. **Drawing** (`scribble-drawing-start`, 60s) — Ready/Set/Draw countdown overlay, then drawers draw while guessers type guesses into the main input-area. Opponent canvas shows tile grid (4x4, 16 tiles) revealing one tile every 4s. Canvas snapshots sync via JPEG data URLs (`scribbleCanvases.{team}` field) on stroke-end, bucket fill, and clear — not continuously during drawing, so guessers see updates after each stroke completes.
3. **Session end** (`scribble-session-end`) — host-authoritative. When host's timer expires or all drawings solved, host writes this phase; non-hosts mirror via `handlePhaseTransition` → `scribbleApplyEndDrawingSession`. Shows status message for 2s, then advances (next session or summary).
4. **Summary** — `scribbleShowSummary` is orchestrated inside the shared Round Summary Framework (see "Round Summary Framework" section). Flow: `showRoundCompleteCard` (with team-colored subtitle or tied message) → hide word-select/game → `ss-fly-in` on `#scribble-summary` → populate team names with 0 scores → `scribbleRenderSessions()` fills per-session events into the left/right columns → 700ms beat → parallel raw-score countups (red + blue) → if the round multiplier > 1, parallel per-team `runTeamMult` gem slam + pulse + multiplier countup → `hidePhaseGem()` → 1500ms hold → `scribbleFinishRound()` → `handleModuleComplete`. Summary container stays visible through Ready Up; `advanceRound` hides it when the next round starts.

### Scoring

Time-based multipliers (scored at moment of guess):
- First 15s elapsed (46+ remaining): 3x
- 16–30s elapsed (31–45 remaining): 2x
- 31–45s elapsed (16–30 remaining): 1.5x
- 46–60s elapsed (0–15 remaining): 1x

Bonuses (reset per drawing session):
- **First correct guess:** +50 to the guesser (one per session)
- **Steal** (opponent canvas guessed): +50 to the guesser
- **First drawing guessed:** +50 to the **drawer's team** (even if stolen — rewards drawing prowess)
- **Word points:** 50 / 75 / 100 by difficulty

Scoring is host-authoritative: non-host guesses route through `pendingAction: { type: 'scribbleGuess' }`. Host's `scribbleEvaluateGuess` uses **absolute team indices** (not viewer-relative), looks up words via `scribbleState._team0Word` / `_team1Word`, computes score, syncs `scribbleScoring` and `scribbleLastSolve` back to all clients. Non-hosts receive via reconcile and call `scribbleApplySolve` to show the overlay + status message locally.

Status messages are perspective-aware (`scribbleApplySolve`):
- Guesser's team, teammate word: `✓ Correct! WORD — +X pts`
- Guesser's team, steal: `🎯 Steal! WORD — +X pts`
- Drawer's team (stolen from): `💔 They stole "WORD"!` (red)
- Neutral observer: `The other team guessed "WORD"`

### Canvas sync architecture

- Drawer broadcasts via `scribbleBroadcastCanvas()` — `canvas.toDataURL("image/jpeg", 0.5)` written to `scribbleCanvases.${myTeam}` in Firestore on pointerup / bucket fill / clear. ~50–100 writes per drawing session.
- All clients receive snapshots via reconcile's `scribbleApplyCanvasSnapshot(teamIdx, dataUrl)` — renders onto either `#scribble-teammate-canvas` (my team's drawing) or `#scribble-opp-canvas` (other team's drawing) based on viewer's team.
- Drawer view (single canvas, `#scribble-draw-canvas`): only drawer can interact, input-area in 'disabled' mode.
- Guesser view (two canvases side-by-side): teammate canvas clear, opponent canvas covered by tile grid with CSS flip reveal animations.

**Stroke-level continuous sync NOT implemented** — guessers see updates per stroke completion, not live stroke-by-stroke. Good enough for playtesting; upgrade path is either high-frequency Firestore writes (expensive on Spark quota) or Realtime Database / Cloud Functions post-Blaze migration.

### Critical state reset points

Many session 2 bugs came from stale state leaking. Places that must reset:
- **New scribble round** (`enterScribbleRound`): clears status text, waiting msg, solved overlays, `sessions` array, `usedWords` set
- **New session within a round** (`scribbleStartWordSelection`): clears `_wsCountdown`, `sessionInterval`, `revealTimer`, `_teammateSolved`, `_opponentSolved`, `_myWordPick`; syncs `phase: 'scribble-word-select'` + `scribbleWordPicks: null` + `scribbleCanvases: null` to clear Firestore
- **Drawing-start sync** (host in `scribbleHostStartDrawing`): syncs FRESH `scribbleScoring` object (`firstGuessClaimed: false, drawingFirstClaimed: [false, false], events: [], teamScores: [0, 0]`) — otherwise stale session 1 scoring would override the fresh local init during reconcile
- **Session end** (`scribbleApplyEndDrawingSession`): clears `sessionInterval`, `revealTimer`, reveals all tiles, pushes session results into `sessions` array, schedules next session or summary

### Firestore fields added

- `scribbleWordPicks: { [uid]: { word, difficulty, points } }` — drawers' word picks, cleared at drawing-start
- `scribbleSessionWords: { team0, team1 }` — synced by host at drawing-start so all clients use same words
- `scribbleScoring` — synced host-side scoring object
- `scribbleLastSolve: { solvedTeam, word, guesserUid, total, mult, ts }` — triggers solve animations on clients
- `scribbleCanvases: { "0": dataUrl, "1": dataUrl }` — compressed canvas snapshots per team
- `scribbleEndReason`, `scribbleEndSessionData`, `scribbleEndTs` — session-end sync payload
- `selectedRoundType`, `scribbleSession` — misc phase state
- All cleared in `lobbyStartGame`'s Firestore reset block (alongside existing `faceoffState`, `pendingFaceoffActions`, etc.)

### Ready countdown leak (CRITICAL historical bug, fixed)

Pre-fix symptom: on round 2 with fewer than maxRounds remaining, game would jump to face-off unexpectedly. Root cause: `_readyCountdownEnd` timestamp wasn't cleared when `advanceRound` ran, so later `checkReadyAdvance` calls (fired from reconcile when readyPlayers changed) still saw `timedOut=true` and called `advanceRound()` **again**, double-incrementing `roundNumber` past `maxRounds`, triggering faceoff.

Fix:
- `advanceRound` explicitly clears `_readyCountdownInterval`, `_readyCountdownEnd`, `_readyPlayersMap`
- `checkReadyAdvance` guards: only advances if `#phase-indicator [data-phase]` is `round-result`. Otherwise cleans up state and returns.
- Non-host's `round-type-select` phase handler also clears these locally (same cleanup as host's advanceRound)

### `_advancingRound` reentry guard (2026-04-17)

A cousin of the ready-countdown-leak bug, same shape, different trigger window. Symptom: on the final round of a play-again game ending in a scribble round, faceoff would silently not run — the round-type picker appeared instead, the user picked High Five, and the winner was announced mid-question. Log showed two back-to-back `checkReadyAdvance → ADVANCING` entries and two `advanceRound gate` entries firing in the same event-loop tick, with `phase=faceoff` (writeId=73) immediately overwritten by `phase=round-type-select` (writeId=74).

Root cause: two non-host clients wrote identical `round-result` snapshots with the full ready map back-to-back. The host's listener re-ran `checkReadyAdvance` on both, and the existing DOM-phase guard (`phase-indicator.dataset.phase === 'round-result'`) doesn't catch same-tick reentry because `advanceRound` is async — the DOM attribute doesn't flip until after the ~900ms exit-animation await sequence.

Fix: synchronous `_advancingRound` boolean flag (declared next to `_readyCountdownInterval`), set at the top of `advanceRound` before any `await`, cleared in a `try { ... } finally` wrapper covering all exit paths. `checkReadyAdvance` early-returns when the flag is set. Mirrors the `_scoringInProgress` and `_returningToLobby` patterns — idiomatic for async state-mutating critical sections in this codebase.

Only the synchronous flag catches this race; DOM checks and Firestore atomicity can't, because both racing handlers run before any async work completes.

### Known outstanding bugs (as of session end on multi-scribble)

These were in flight at the branch's current head; resume here next session:

1. **Ready Up button occasionally disabled on session 2 drawers (inconsistent).** Users observed this but not deterministically — likely a race between the reconcile's `readyPlayers` handler disabling the button (based on `_readyPlayersMap[myUid]`) and `handleModuleComplete` creating a fresh Ready Up button. Next step: get a timestamped log from the user showing exactly when it reproduces, then add explicit "enable" step after `setInputAreaMode('action')` or stricter guard in the reconcile handler. May also be fixable by clearing `_readyPlayersMap` at the start of `handleModuleComplete` (before showing Ready Up) rather than waiting for round-type-select.

2. **Ranked question (High Five / Survey) turn-order bugs under new orchestration.** Not fully investigated — user reported "bugs within it when it comes to turn order" after the orchestration refactor. The feud flow still uses `turn-body.innerHTML` swaps and its legacy `updateRoleUI` logic; interactions with the new input-area home base may have introduced regressions. Triage with a fresh ranked-question-only test session.

3. **Face-off duplicate-answer wiggle bug (pre-existing, from before scribble work).** Host input area wiggles when a non-host submits a duplicate answer in face-off; some non-host clients see no wiggle when they should. Spawned as a separate task chip during an earlier session. Check `submitFaceoffGuess` duplicate detection logic and reconcile routing of the wiggle effect.

4. **Input-area flash during round-select on some non-host clients.** Mostly addressed by removing the `input-exit` animation from the `round-type-select` phase handler, but user reported one lingering flash on "player 2's screen" in an early test. Recheck after the session 2 reset fixes stabilize.

5. **Stroke-level canvas sync (design choice, not a bug).** Guessers see canvas snapshots at stroke-end, not live. Mentioned for awareness — no current fix needed, revisit post-Blaze migration when continuous sync via Cloud Functions or Realtime Database becomes viable.

### Scribble summary — known polish-pass items

Picked up during the Round Summary Framework unification. Scribble's summary adopts the shared `.round-summary-*` classes (frosted glass background, negative margin-top, shared title/totals styling), but three visual/wording inconsistencies vs. H5 and Common Thread remain for the next polish pass:

1. **Header margins** on `#scribble-summary`'s title don't match the margins other modules use — slight vertical rhythm difference.
2. **Totals row** — red and blue team scores cluster toward the center instead of spreading to opposite edges of the panel like H5/CT do.
3. **Round-end message wording** — scribble's `handleModuleComplete` says "[team] won X points!" instead of the standard "[team] won the round with X points!" used by other modules. Fix by updating the `resultMsg`/`phaseMsg` template in the scribble branch of `handleModuleComplete`.

All cosmetic; no functional impact on the round result or scoring.

### Dev flag: removed

`DEV_SKIP_TO_SCRIBBLE` existed during early integration to jump straight from lobby → scribble for rapid testing. Removed once scribble was reachable through the normal round-type picker. No longer exists in the codebase.

---

## Round Summary Framework

Shared end-of-round summary + recap system used by every module (High Five, Poll Position, Secret Scribble, Common Thread, and anything new). Unifies the visual framing and the orchestration of the post-round score reveal so the moment lands the same way across modules.

### Shared CSS classes

All summary panels apply `.round-summary` as a base class on the outermost container. The `.round-summary-*` family covers the structural sub-parts:

- `.round-summary` — base frosted-glass panel: `rgba(26,26,26,0.75)` background, `backdrop-filter: blur(20px)`, `border-radius: 10px`, `padding: 14px 14px 12px`, `margin-top: -5px` (tucks up under the scoreboard).
- `.round-summary-title` — the "ROUND SUMMARY" header bar (gold dazzle-unicase).
- `.round-summary-board-recap` — slot for the answer-board recap (used by H5/Poll Position; scribble uses its own per-session column layout inside this area instead).
- `.round-summary-scoring-recap` — slot for the per-event scoring recap rows.
- `.round-summary-totals` — bottom band showing both teams' final scores side-by-side.
- `.round-summary-team` / `.round-summary-team-name` / `.round-summary-team-red` / `.round-summary-team-blue` / `.round-summary-team-score` — team name + score cells inside `.round-summary-totals`.
- `.round-summary-mult-gem` — the multiplier gem that slams onto a team's score during the round-multiplier reveal.
- `.round-summary-score-pulse` — pulse highlight class applied briefly to the team-score number during the post-multiplier countup.

Any module-specific container (e.g. `#scribble-summary`) keeps its layout-only rules and adds `.round-summary` to inherit the frosted background, border-radius, negative margin, and typography.

### `showRoundCompleteCard({title, subtitle, holdMs, extraClass})`

Helper that flies in a "ROUND COMPLETE" card over the module canvas, holds, then flies out. Mounted into `#module-canvas`. Used by every module as the opening beat of the round-end sequence.

- `title` — typically `"ROUND COMPLETE"`.
- `subtitle` — short outcome line (e.g. `"RED TEAM WINS THE ROUND"`, `"TIED ROUND"`). Accepts inline HTML so team-color spans can be embedded.
- `holdMs` — milliseconds to hold fully-visible before flying out.
- `extraClass` — optional extra class on the card (e.g. `rcc-scribble`, `rcc-ct`) for per-module styling tweaks.
- **Plays `roundbell.wav`** internally via `playRoundBell()` immediately after adding `.rcc-entering`. Fires automatically for every module that uses this helper.

### Standard round-end orchestration

All modules follow the same sequence so the feel is consistent:

1. `showRoundCompleteCard({...})` — round bell SFX, card flies in, holds, flies out.
2. Module's summary container slides in (each module has its own entry animation — `ss-fly-in` for scribble, analogous classes for H5/CT).
3. Module populates its summary with events/rows showing **raw** (pre-multiplier) points, team score cells showing 0.
4. Short beat (~700ms) for the panel to settle.
5. Parallel raw-score countups — both teams' `.round-summary-team-score` count up from 0 to their raw totals via `animateCountUp(..., {tick: true})`.
6. If `currentRoundMultiplier > 1`: parallel per-team multiplier reveal (`runTeamMult`):
   - Gem slam — a `.round-summary-mult-gem` (pulled by `getRoundMultiplierGem(mult)`) flies onto the score, plays the gem-slam glint SFX via `playGlint(tier)`.
   - `.round-summary-score-pulse` flashes the score.
   - Second `animateCountUp` runs from the raw total to `raw × multiplier`.
7. `hidePhaseGem()` — tucks the phase-indicator gem away (it's now redundant with the slammed gem).
8. Brief post-countup hold.
9. `onComplete({ redScore, blueScore })` fires — `handleModuleComplete` folds the final (post-multiplier) scores into `teamScores[]`, sets round-result phase, shows Ready Up, and syncs.

### Deferred point-announcement (true across all modules)

Module round-result messaging is split into two stages so the point total lands *after* the summary countup instead of spoiling it up front:

- **Pre-summary message** — `roundResultMsg` / `roundPhaseText` say something like `"[team] wins the round!"` or `"[team] clears the board!"` or `"[team] steals!"` — no points mentioned. This is what the phase indicator and input-area show during the summary animation.
- **Post-summary message** — `postRoundResultMsg` / `postRoundPhaseText` say `"[team] won the round with X points!"` (standard wording). Swapped in at the end of the summary sequence, after the final countup has landed, so the number the player just watched tick up is the number the message references.

Different modules stash this post-message in slightly different ways:
- **H5 / Poll Position** — stash via `_h5PostSummary` at the start of the summary, swap in at the end of `showH5Summary`.
- **Common Thread** — natural `await ctShowSummary` ordering: the next line after the await writes the point-including message.
- **Secret Scribble** — `handleModuleComplete` runs after the scribble summary's own countup finishes, so the single result message written there is already post-countup. (See scribble polish-pass note about the current wording deviation.)

This deferred-announcement pattern is a shared contract — any new module should follow the same two-stage messaging.

### Adding a new module to the framework

1. Apply `.round-summary` to your module's outermost summary container; use the `.round-summary-*` sub-classes for title/totals/gem so styling is inherited automatically.
2. Call `showRoundCompleteCard({...})` as the first step of your round-end sequence (you get `roundbell.wav` for free).
3. Sequence: card → summary fly-in → populate at raw values → beat → parallel 0→raw countups → if `currentRoundMultiplier > 1` do the parallel `runTeamMult` gem-slam + pulse + post-mult countup → `hidePhaseGem()` → hold → `onComplete`.
4. Stash the point-including message in a post-summary field and swap it in when countup completes, so the deferred point announcement works.

---

## Common Thread — Module Overview

Codenames-style minigame. Requires 4+ players (2 per team minimum). `minPlayersPerTeam: 2` in `ROUND_MODULES['common-thread']`. Originally prototyped at [common-thread.html](common-thread.html); now integrated into `feud.html` as a complete module.

### Premise

4×4 grid of word cards. Each board randomly assigns:
- 6 red-team cards (+base points on reveal)
- 6 blue-team cards (+base points on reveal)
- 2 penalty cards worth −100
- 2 penalty cards worth −200

One player per team is the **clue giver** (randomized at module entry, locked for the whole Common Thread round). All other players on each team are **guessers**. Clue giver sees each card's value (light-tinted team backgrounds on their view; gray bg + visible value for penalties). Guessers see cream fronts only.

Clue giver submits a one-word clue + quantity. Guessers pick cards up to that quantity. Picking your own team's card scores points and keeps the turn; picking the opponent's card awards those points to the opponent and ends the turn; picking a penalty subtracts the penalty from the guessing team and ends the turn.

### Round end

First team to have all 6 of their cards revealed wins the round (regardless of who revealed them). No timer.

### Scoring

- On clue submit, **base points = quantity × 100**.
- Own-team card correct: `earned = round(base × multiplier[team])`, then `streak++`, `multiplier = 1 + streak × 0.2`. Mirrors the ranked-question streak formula.
- Opposing-team card: flat `base` points to the opposing team (no multiplier — they didn't earn it via clue). Guessing team's streak/mult reset.
- Penalty: flat card value (−100 or −200) subtracted from the guessing team. Streak/mult reset.
- Revealed card back displays `+N` at mult 1.0, or `+N x 1.2` etc. when mult > 1.

### Module scoreboard

Inside the module canvas: a single module-scoped scoreboard row showing each team's streak, multiplier, and current round score. Separate from the main `#scoreboard` — the module's own scoreboard folds into the main scoreboard via `handleModuleComplete` at round end.

### Clue validation

Strict substring check: reject the clue if it is a substring or superstring of any board word (case-insensitive, normalized — lowercase + strip non-alphanumerics). Catches plurals and compound words algorithmically. Semantic variants (e.g. "MACINTOSH" for APPLE) are not caught; out of scope for v1.

### Word bank

Pulls 16 random words from `SCRIBBLE_WORD_BANK` (flattened across easy/medium/hard). A dedicated Common Thread word bank is a future polish item.

### Compose-clue input mode

`setInputAreaMode` supports a `'compose-clue'` mode: `#turn-input-row` renders a text input (clue word) with a number stepper (◀ N ▶) for the quantity, plus a Submit button. Clue giver sees this mode; everyone else sees `'disabled'` with a "Waiting for [name]..." status. After submit, everyone switches to a `'guess'` mode showing the active clue prominently (word + count). Guessers don't type — their input is clicking the cards. Clue giver sees disabled during the guess phase.

### Host-authoritative sync

- Non-host clue giver writes `pendingAction: { type: 'commonThreadClue', word, count, uid }`.
- Non-host guesser writes `pendingAction: { type: 'commonThreadGuess', cardIdx, uid }`.
- Host processes both, updates `commonThreadState`, syncs the snapshot. Mirrors the scribble `pendingAction` pattern.
- Card reveal sync: host writes `cards[i].revealed = true` + `revealedInfo`. Non-host reconcile toggles the `.flipped` class on the existing card element for the Y-axis flip (don't rebuild the DOM or the transition is lost).

### Round-end orchestration

Follows the shared Round Summary Framework. `ctFinishRound` awaits `ctShowSummary`, which runs the standard card → summary-in → countup → gem-slam → post-mult sequence. After a 1500ms hold, `onComplete({redScore, blueScore})` fires `handleModuleComplete`, which writes the post-summary point-including message (`"[team] won the round with X points!"`).

### Firestore schema

```js
commonThreadState: {
  phase: 'clue' | 'guess',
  cards: [{ word, type, points, team, revealed, revealedInfo }],  // 16 entries
  scores: [redRoundScore, blueRoundScore],   // module-local, folded on complete
  streaks: [0, 0],
  multipliers: [1.0, 1.0],
  currentTeam: 0 | 1,
  activeClue: { word, count, team } | null,
  picksRemaining: 0,
  basePoints: 100,
  clueGiverUids: [redUid, blueUid],
}
```

`pendingAction` types: `commonThreadClue` (word, count), `commonThreadGuess` (cardIdx). All `commonThreadState` fields and pendingActions are cleared in `lobbyStartGame`'s Firestore reset block alongside `scribbleState` / `faceoffState` / etc.

### Future polish items (deferred)

- Clue composition and/or guess timers (currently no timer).
- Victory award compute functions specific to CT: "best clue giver" (most correct per clue), "best guesser" (most cards flipped for own team), etc. Match log entry types for CT-specific outcomes.
- Dedicated clueable-word bank (scribble words like "DANCE" can be awkward for Codenames play).
- Round-type picker card art pass (gem tier / color treatment).
- Step 7 (phase reconcile robustness) from the Pre-Blaze Cleanup Refactor applies to Common Thread handlers too — idempotent phase transitions, no assumptions about prior local state.

---

## Question Bank — JSON Schema

Each question object has this shape:

```json
{
  "question": "Name a...",
  "category": "Sports",
  "subCategory": "NBA",
  "answers": [
    { "text": "Answer", "display": "Answer (context)", "points": 40, "variants": ["Alt phrasing", "Shorthand"] },
    ...
  ],
  "factCheck": "Brief flag if uncertain — one line max",
  "removeQuestion": true
}
```

**Field notes:**
- `category`: parent category shown to players (e.g. "Sports", "Movies")
- `subCategory`: child category for filtering/grouping (e.g. "NBA", "NFL", "MLB")
- `display`: optional — shown on the revealed tile when stat or year context adds value (e.g. `"LeBron James (2012)"`, `"Chicago Bulls (72-10)"`). If omitted, `text` is shown instead.
- `points`: integer, descending order — highest-ranked answer has the most points
- `variants`: optional array of alternate phrasings a player might type that should earn credit for this answer. Omit if not needed. See variant rules below.
- `factCheck`: a short flag for human review, not a full explanation. E.g. `"verify Mureșan height"`. Omit if confident.
- `removeQuestion`: set to `true` to flag for removal. Omit otherwise.

**Variant rules:**
- A valid variant IS the answer — a synonym, shorthand, or specific instance that unambiguously belongs to it. E.g. "Wine" and "Beer" are valid variants of "Alcohol"; "Philly" is a valid variant of "Philadelphia".
- A variant is NOT valid if it is a separate answer to the survey question that happens to be in the same category. E.g. on a question about things that can be spoiled, "A movie" is not a variant of "A Surprise" — it is a different answer entirely.
- Do not add variants for numeric answers — players will type the number exactly.
- `feud.html` matching: `answerMatches(guess, ans)` checks `ans.text` first, then each entry in `ans.variants`. Uses proportional Levenshtein (1 error per 4 chars, min 0) on normalized strings (strips leading articles, trailing s).

**Answers must be in strict descending point order.** When two answers are tied in value, rank alphabetically by **first name** — lower letter = higher rank = more points. Example: "Bill Russell" ranks above "Michael Jordan" at tied 5 MVP awards because "Bill" < "Michael".

---

## Variant Generation — Batch Process

Variants for all 4,144 questions were generated using the Anthropic Message Batches API with `claude-haiku-4-5`. The script is `add_variants.py`. To add variants to new questions in bulk:

1. Set `ANTHROPIC_API_KEY` in your environment
2. Place new questions in `master_question_bank.json`
3. Update `FAILED_INDICES` in the script if rerunning retries, or use `--submit` for a fresh full run
4. Run: `python3 add_variants.py --submit --wait`
5. Output goes to `master_question_bank_variants.json` — review, then rename to replace the active file

For spot-checking output quality: `python3 sample_variants.py --with-variants-only --seed <N>`

Cost reference: ~$0.001 per question with Haiku via Batches API (50% batch discount applied).

---

## Viewport Redesign

Active UI overhaul inspired by **Balatro's** contained, zone-based, animation-rich design. The goal is a game that feels like a native app, not a browser page — no scrollbars, everything always visible, all transitions animated.

### Canvas Architecture — Option B (transform: scale)

The game canvas is a fixed **1280×720** reference resolution (`#game-root`). A JS function scales the entire container to fit the window via `transform: scale()`. All internal sizing uses `rem`, `px`, or `%` — the transform handles responsiveness uniformly.

**Critical rule: no `vw`/`vh` units inside `#game-root`.** These track the viewport, not the canvas, causing double-scaling interference with the transform approach. If you see `vw` inside game elements, it's a bug.

- **Body** is a flex container centering `#game-root` with dark `#0a0a0a` bars (letterbox)
- **Reference resolution** is a design coordinate space, not a max size — scales up and down freely
- **16:9 target** — at non-16:9 windows, letterbox bars appear (acceptable graceful degradation)
- **Electron future** — will set default window to 1280×720 with a minimum size floor; bars disappear on 16:9 screens

### Layout Zones

Evolved from a simple 3-zone vertical stack to a **sidebar + main column** model:

```
#game-root
  #zone-board (flex row, fills canvas)
    #sidebar-zone (25%)
      #phase-indicator  ← persistent header, contains all phase spans
        .ph-category-select, .ph-gameplay, .ph-steal-chance, .ph-round-result
      #sidebar-category-select  ← during category selection
        #category-pills-area (.trivia-categories, .pills-divider, .survey-categories)
      #sidebar-question-answer  ← during gameplay
        #sq-zone-content → #content-tv (cat-label + question-box + vignette)
        #sq-zone-input → #input-area, #message
    #zone-board-main (75%)
      #header-zone
        #scoreboard (5-col CSS grid: player panels + score boxes + round display)
      #game-board-zone
        #game-area
          #board-wrapper (game board + stats + strikes)
```

- **Sidebar** always visible — JS swaps which panel is shown (category select vs. question/answer)
- **Scoreboard** is a flat 5-column grid row — bleeds off the top of the canvas (no top border-radius). Round display shows "ROUND X OF Y". `#targetDisplay` was removed.
- **Board wrapper** contains the game board, round total, and stats (streak, multiplier, strikes). Anchored to the bottom of `#game-board-zone` via `justify-content: flex-end`. Bleeds off the bottom of the canvas (no bottom border-radius). Hidden during category selection; slides in from below when a category is picked.
- **Answer history** is a collapsible tray at the bottom of the sidebar

### Screen Flow

1. **Start screen** — `.crt-start-screen` class applies composite CRT effects (animated noise via `::before`, scanlines + glare via `::after`, vignette via inset box-shadow). SVG blobs use distinct per-blob colors on start screen only (set via inline `fill`, restored to `--bg-blob-base` on dismiss). On click: blob colors crossfade to default (1.5s), then logo does `logo-tv-off` animation, then screen fades out + setup slides in.
2. **Setup step 1** — rounds selection only (target score mode removed). 3D isometric SVG buttons for 2/4/6 rounds with raised/depressed states. "Proceed to Team Setup" button.
3. **Setup step 2** — team/player name entry. Flies in from left after step 1 flies right. `#selected-rounds` (absolutely positioned left side) shows the chosen round count with a rewind-icon back button. The back button returns to step 1 with reverse fly animations. See "Setup Step Transitions" below for full timing.
4. **Game start exit** — two parallel tracks: 3-beat sequence (Start button slides down → player columns slide right → title slides up) runs alongside `#selected-rounds` fade-out (1s). `startGame()` fires after the slower track completes.
5. **Category selection** — sidebar shows team prompt + 3D rotating category pills
6. **Gameplay** — sidebar shows question + input; main zone shows scoreboard + board

### Animation Principles

- **Nothing appears/disappears instantly** — every screen change has a transition (fly-in/out, fade, slide)
- **CSS owns the "what", JS owns the "when".** Keyframes and state classes (`.offscreen`, `.slide-in`, `.ph-exiting`, etc.) live in CSS. Orchestration — sequencing, staggering, delayed starts — lives in JS via the `anim` helper. See "Animation Framework" for the helper API.
- **Single source of timing truth.** Durations that JS cares about live in the `TIMING` constants object at the top of the `<script>` block. Never hardcode magic numbers in call sites.
- **3D rotating category buttons** — 4-face prism with slow tilt animation (±50° over 25s), stops on hover, staggered with negative `animation-delay`
- **SVG blob background** — four rotating blobs using `color-mix()` from a single `--bg-blob-base` CSS variable; opacity varies per blob for shade depth. A CSS-only replacement exists (pseudo-elements on `#game-root` with animated radial gradients) gated behind `.css-bg-active` class — currently **not active**; SVG version is in use.
- **CRT overlay** — start-screen-only effect, opacity-based transitions (not display toggle)

### Category Color Palette

CSS variables in `:root` — **single source of truth** for all category colors. The 3D buttons derive `--cat-face` (0.9 alpha) and `--cat-solid` (1.0) via `color-mix()`:

```css
--cat-science:    #0000c0;   /* blue */
--cat-geography:  #00c000;   /* green */
--cat-popculture: #c000c0;   /* pink */
--cat-survey:     #fb8c00;   /* orange */
--cat-sports:     #fdd835;   /* yellow — uses black text */
```

Button color derivation (no hardcoded rgba duplicates):
```css
.cat-science { --cat-face: color-mix(in srgb, var(--cat-science) 90%, transparent); --cat-solid: var(--cat-science); }
```

`getCategoryClass()` in JS maps category strings to CSS classes via lowercase matching.

### Width/Sizing Conventions

- **No hardcoded pixel `max-width` values** — use percentages of the canvas (e.g. `width: 88%`, `max-width: 92%`)
- **Font sizes in `rem`** — the transform handles all scaling; no `clamp()` needed
- **Padding/margins** can use `px` or `%` — both scale uniformly with the transform

---

## Animation Framework — `anim` helper + `TIMING` constants

All animation orchestration in the game runs through a small in-file helper called `anim` (~100 lines) at the top of the main `<script>` block, paired with a `TIMING` constants object for tunable values. This is not a third-party library — it's an internal utility that wraps the patterns we were hand-rolling (animationend listeners, reflow hacks, setTimeout chains) into a consistent Promise-based API.

**Why this exists:** as the game grew, orchestration code became hard to read and tune — nested `animationend` listeners, copy-pasted `void offsetWidth` replay hacks, scattered setTimeout delays, and magic-number durations duplicated between CSS and JS. Introducing a third-party library (GSAP, Motion One, Tailwind) was considered and rejected — the single-file vanilla philosophy is a feature, and the helper captures 80% of the value at zero dependency cost.

### The `anim` API

All times in **milliseconds** (the helper converts to seconds internally when writing CSS `animation-delay`).

```js
// Add a class, await the animation it triggers
await anim.play(el, "slide-in");

// Force a keyframe restart (replaces the `void el.offsetWidth` dance)
await anim.replay(el, "slide-in");

// Await the next animation on an element (doesn't add a class)
await anim.done(el);

// Set inline `animation-delay` on one element (ms in, seconds out)
anim.setDelay(el, 400);

// Stagger `animation-delay` across a list of elements.
// Elements must already have a CSS `animation` property (via their base
// class, or via the optional `className` arg). Resolves when the LAST
// element's animation finishes.
await anim.stagger(rows, { gap: 150, baseDelay: 0, className: "cat-slide-in" });

// Run async functions one after another (each returns a Promise)
await anim.sequence([
  () => anim.play(btn, "exit-down"),
  () => anim.wait(50),
  () => anim.play(columns, "exit-right"),
  () => anim.wait(50),
  () => anim.play(title, "exit-up"),
  () => startGame(),
]);

// Run async functions concurrently
await anim.parallel([
  () => anim.play(a, "fade-in"),
  () => anim.play(b, "slide-up"),
]);

// Promise-wrapped setTimeout — use inside sequences for pure time waits
await anim.wait(200);

// Schedule a callback on the animation timeline (not wall-clock).
// Uses a throwaway WAAPI animation so DevTools animation speed
// control affects timing. At 100% speed, identical to setTimeout.
anim.timer(el, 350, () => playSfx());
```

### `TIMING` constants

All JS-driven delays live in one object so tuning the "feel" of the game doesn't require hunting through function bodies. Current keys:

```js
const TIMING = {
  // Phase indicator (sidebar header)
  phaseTextEnterDelay:  400,  // delay before phase text drops in at game start
  phaseKnockOverlap:    120,  // overlap window before phase swap during steal knock

  // Category pills
  catRowStagger:        150,  // ms between successive cat-row slide-ins
  catRowSlideDuration:  400,  // must match cat-slide-in duration in CSS
  catRowExitStagger:    100,  // ms between successive cat-row exits
  pillsDividerBuffer:    50,  // extra ms after last cat-row settles before divider fades in

  // Setup → game transition
  setupExitBeatGap:      50,  // pause between the 3 setup exit beats

  // Scoring sequence (correct answer)
  scoringStepGap:        150,  // ms pause between scoring animation steps
};
```

**Rules when adding new animations:**
1. If a duration needs to be known by JS (for sequencing or delay math), add it to `TIMING`.
2. If JS only triggers the animation and doesn't care when it ends, leave the duration in CSS.
3. When a `TIMING` value must match a CSS duration exactly, comment both sides so they stay in sync.
4. Prefer `anim.play`/`anim.replay` over raw `classList.add` + `animationend` listeners.
5. Prefer `anim.sequence` over nested `setTimeout` chains or nested `animationend` callbacks.
6. Prefer `anim.stagger` over manual `forEach` loops that compute `animationDelay`.
7. **Prefer `anim.done(el)` over `anim.wait(ms)` when sequencing two animations on the same element.** `anim.wait` is wall-clock; `anim.done` is animation-clock. See the next section for why this matters.
8. **Never use raw `animationend` listeners on elements with animated descendants.** `animationend` bubbles — a child's animation finishing will trigger a parent's `{ once: true }` listener prematurely. `anim.done` uses WAAPI's `getAnimations({ subtree: false })` which only tracks the element's own animations, avoiding this entirely. This was the root cause of the setup flow bugs where `backToRoundSelect` listeners were consumed by the `.rw-arrow` rewind glyph animations.
9. **Present a timing table when proposing new animation sequences.** Before implementing, lay out a table showing parallel tracks, per-step durations, and cumulative timing. This catches conflicts (e.g. a 520ms sequence gating a 1s fade-out) before code is written.

### `anim.done` is WAAPI-only (and why)

`anim.done` is implemented purely with the Web Animations API's `Animation.finished` promise. It does NOT listen for `animationend` events. The previous implementation used both as a belt-and-suspenders approach but ran into a class of bugs that the WAAPI-only path avoids:

**Why no `animationend` listener:** When a CSS animation finishes, the browser **queues** an `animationend` event for the next event-loop tick. If JS code in between cancels or replaces that animation (e.g. via a class swap to start a new animation on the same element), the queued event still dispatches afterwards. A subsequent `anim.done()` call adds a fresh `animationend` listener, which then catches the **stale event from the previous animation** and resolves prematurely. This bit us hard during the category exit work — `anim.done` for the CRT power-off was resolving in ~1ms because it caught the queued `animationend` from the just-finished glow ramp.

`Animation.finished` doesn't have this problem because each promise is bound to a specific Animation object. There's no cross-animation event-queue confusion.

**What `anim.done` is robust against:**
- **Empty animation list** — resolves immediately if there's nothing to wait for, instead of hanging.
- **Canceled animations** — `.finished` rejects on cancel, the helper's `.catch(() => {})` turns that into a clean resolve.
- **Two consecutive `done()` calls on the same element** — each call snapshots the current animations on its own `requestAnimationFrame`, so they don't interfere.
- **DevTools playback-rate slowdown** — `Animation.finished` is driven by the animation's *internal* timeline, which DevTools' speed control correctly affects. So at 10% speed, `anim.done` waits 7000ms wall-clock for a 700ms animation, keeping JS in sync with the visible animation.

**`anim.wait(ms)` is wall-clock:** `setTimeout` is NOT affected by DevTools animation slowdown. If you sequence two animations using `anim.wait(700)` between them and then test at 10% speed, the JS will race 10x ahead of the visible animations. The first animation will be cut off mid-flight. Use `anim.wait` only for genuine time-based waits (like a leading pause before an animation starts), never as a substitute for "wait for animation N to finish."

### Inline `animation-delay` longhand vs. class-based shorthand — important gotcha

`anim.stagger` sets `animationDelay` as an **inline longhand** on each element. This persists across class changes and **inline longhands override class-defined shorthand defaults**. So if a row has inline `animationDelay: 0.45s` from entry, then later gets a class with `animation: cat-glow-ramp 700ms ease-in both` (which has implicit delay 0s), the computed delay is **0.45s**, not 0s. The new animation silently inherits the old stagger delay.

There are two ways to avoid this:
1. **Set the new animation as an inline shorthand** — `el.style.animation = "..."` resets all longhands, including the inline `animationDelay`. Path A's exit code does this and was unaffected by the bug.
2. **Explicitly clear the longhand** before class-based animations — `el.style.animationDelay = ""`. Path B's selected row needed this fix because it only added a class, never an inline shorthand.

`animateCategoryTransition` clears the inline `animationDelay` on every cat-row + the divider at the start of the function as a defensive measure. Any new code that does `classList.add(...)` to trigger a CSS animation on an element that was previously touched by `anim.stagger` should do the same.

### `forwards` fill-mode + missing 100% keyframe properties — gotcha

When a keyframe animation uses `animation-fill-mode: forwards`, only properties **explicitly listed at the 100% keyframe** persist after the animation ends. Any property that's animated at intermediate keyframes but omitted at 100% reverts to whatever the element's base rule specifies.

Fix: add the intended final value to the 100% keyframe explicitly (e.g. `100% { transform: scale(1); opacity: 1; ... }`). When writing a new keyframed animation with `forwards` fill, audit the 100% step against every property you animated earlier *and* every property you set in the base rule — if the base rule would mask the desired final value, pin it at 100%.

**Additional gotcha with animation replacement**: when a new CSS animation class replaces a previous one (e.g. `.marquee-scroll` replacing `.tv-on`), the `forwards` fill from the first animation is lost and base-rule values reassert. The `cat-label-marquee` keyframes include `scale(1)` in both `from` and `to` to prevent the base `transform: scale(0)` from snapping back. Inline `opacity: 1` is set in JS before the class swap.

### Testing limitation: hidden preview tab

The Claude Preview runs as a backgrounded browser tab. Chrome **pauses** CSS animations in hidden tabs. Timing-only paths (`anim.wait`, `anim.setDelay`, `anim.stagger` delay math) verify fine in preview, but full visible exit/entry sequences need in-browser spot-checks. Computed style queries can sometimes show interpolated values mid-animation in the hidden tab, but don't trust that — always validate in a visible browser.

### What the helper does NOT do

- It does not replace `@keyframes` — those still live in CSS.
- It does not replace CSS state classes (`.offscreen`, `.slide-in`, etc.) — those are still the right tool for declarative state transitions the browser manages automatically.
- It is not a physics library — no springs, no scroll triggers, no SVG morphing. If those are ever needed, Motion One (~5kb) is the recommended drop-in upgrade because its mental model (Promise-based, sequence/parallel/stagger) matches the helper's API closely.

---

## Team Colors — CSS Variables

Defined in `:root`. Use these variables everywhere team color appears — do not hardcode hex values for team UI elements.

```css
--red-bg:   #990b0b;
--red-text: #ff5555;
--blue-bg:  #053977;
--blue-text: #4c8cff;
```

**Board tile colors** (`#board` and its `.correct`, `.missed` tiles) are intentionally independent of team colors. Do not apply team color variables to board elements.

---

## Board & Scoreboard Design System

Both `#board-wrapper` and `#scoreboard` follow a consistent frame/field pattern:

- **Scoreboard frame** — industrial noise texture (SVG turbulence grain over vertical gradient, `inset` bevel highlights). All labels sit directly on this frame.
- **`#111` value fields** — data cells (player lists, round info, stat values, answer tiles) have `background: #111` with `border-radius: 6px`.
- **Team-colored exception** — `.team-points` fields use `var(--red-bg)` / `var(--blue-bg)` instead of `#111`. These have CRT overlay effects: `::before` (combined white noise + scanlines at opacity 0.3, z-index 1), `box-shadow: inset` vignette, and `overflow: hidden` to contain effects within border-radius. Active-team arrow `::after` has `z-index: 2` to render above the CRT layer.
- **`6px` gutters** — consistent `gap: 6px` between all cells. No padding on individual cells for spacing; the gap property handles all gutters. Wrappers retain outer padding for the border inset.
- **Answer rows** are fixed at `40px` height. Each row has a `.tile-cover` (glossy black with pixelated 8-bit circle) that slides right to reveal the answer. Correct = green (`#1b5e20`), missed = red (`#7b0000`). The old flip animation was removed; cover-slide is the only reveal mechanism.
- **Board wrapper** slides in from below the canvas when a category is picked (`board-slide-in` animation), hidden during category selection (`.offscreen` class).
- **Scoreboard** bleeds off the top edge; board wrapper bleeds off the bottom edge.
- **Scoreboard grid** uses `grid-template-columns: minmax(0, 1fr) × 5` (not bare `1fr`) so cells can't expand to fit long team names — the fit-shrink helper needs the cells to stay pinned. See "Shrink-to-Fit Text" for the full explanation.
- **Scoreboard columns are bottom-aligned** via `align-items: end`. Player panels vary in height (marquee + header) while score boxes and round display are shorter; bottom-alignment keeps the data rows flush and lets the "Turn Order" headers float above each column at their natural position.

---

## Blend-Multiply Utility

A reusable `.blend-multiply` CSS class enables Adobe-style multiply blending on any container's background without affecting child elements:

```html
<div class="blend-multiply" style="--blend-bg: #d4a373;">
  <button>Children render normally</button>
</div>
```

- Set `--blend-bg` to the desired color. Opaque, saturated colors work best — white multiplied is invisible, black multiplied is black.
- Internally uses a `::before` pseudo-element with `mix-blend-mode: multiply`; children sit above it via `position: relative; z-index: 1`.
- **Stacking context requirement**: `mix-blend-mode` blends against the nearest stacking context's backdrop. Avoid `z-index` on ancestor elements between the blended element and `#game-root` — it creates isolation boundaries that block the blend from reaching the SVG blobs. The `z-index` was intentionally removed from `#game`, `#setup`, and `#fast-money` for this reason.

---

## Shrink-to-Fit Text

For elements that take unpredictable-length text (team names, questions, etc.), we use a **character-count-based** shrink helper rather than measuring layout. The reasoning matters: we previously tried the obvious approach — measure `offsetWidth` / `scrollWidth`, loop and decrement font-size until it fits — and hit a cascade of failures (hidden elements reporting 0 width, layout shifts after the measurement ran, `ResizeObserver` timing quirks, flex-center `scrollWidth` not counting left overflow). The char-count approach sidesteps all of this because it runs synchronously at text-set time and never reads layout.

### CSS pattern

```css
.my-fit-el {
  --fit-base: 1.8rem;
  font-size: calc(var(--fit-base) * var(--fit-scale, 1));
}
```

The base size is the "comfortable" size. `--fit-scale` defaults to 1 (no shrinking). The JS helper sets it to a value between 0 and 1 when text exceeds the threshold.

### JS helper

```js
function fitByCharCount(el, maxChars, text, power = 1) {
  if (!el) return;
  const len = (text ?? el.textContent).trim().length;
  const scale = len <= maxChars ? 1 : Math.pow(maxChars / len, power);
  el.style.setProperty("--fit-scale", scale);
}
```

Call it immediately after assigning `textContent` — no deferral, no rAF, no observers.

The optional `power` parameter controls the shrink curve shape:
- **`power = 1`** (default) — linear shrink. Good for single-line elements where overflow is the hard constraint.
- **`power < 1`** (e.g. 0.5 = square root) — concave curve, shrinks less aggressively. Better for multi-line wrapping text where moderate shrinking suffices and the char-count proxy is noisier.
- **`power > 1`** — convex curve, shrinks more aggressively (not currently used).

Tuning process: collect 5–7 real strings with their ideal font sizes, compute `base × (maxChars / len)^power` across candidate values, pick the combination that minimizes max error. Non-monotonic outliers are expected with proportional fonts — the formula can't predict which strings wrap efficiently.

### Where it's currently applied

- **Team labels** (`.team-score-box .team-label h4`) — `--fit-base: 1.5rem`, `maxChars: 10`, called in `startGame()` at the `textContent` assignment.
- **Question text** (`#question`) — `--fit-base: 1.8rem`, `maxChars: 48`, `power: 0.5` (square root curve), called in the question-render block. `#question-box` has `max-height: 180px; overflow: hidden` as a safety net.
- **Turn subtext** (`#turn-subtext`) — `--fit-base: 2rem`, `maxChars: 12`, `power: 1` (linear), called in `updateTurn()` and the mid-animation swap in `animateTurnSwap()`.
- **NOT the players list** — char-count wasn't the right tool there (see marquee below).

### Caveats and tuning

- Char count is a width *proxy*. Works cleanly for monospace-ish fonts (Bitcount Single). For proportional fonts it's "close enough for a fallback" — `maxChars` is tuned by eye.
- **Not for multi-line wrapping text.** Char count doesn't know about line breaks. If the container can grow taller (wrapping), use a different approach.
- **Tune `maxChars` by watching real content.** Questions that still look cramped at scale 1 → lower `maxChars`. Too many things shrinking unnecessarily → raise it.
- **Grid cells must have `minmax(0, 1fr)`**, not bare `1fr`. Bare `1fr` tracks expand to fit content, so an overflowing child can blow out the whole layout *before* the fit helper sees any overflow. The scoreboard and any similar grid layout using fit-shrink children need explicit `minmax(0, 1fr)`.

### Bitcount Centering Nudge

The Bitcount Single typeface has asymmetric horizontal bearings — characters sit slightly left of center in their em box. For elements where a number should appear visually centered (tile numbers, stat values, round buttons), a `padding-left: 0.1em` nudge corrects this. The `em` unit scales proportionally with font size so the correction works at any scale.

Currently applied to:
- **`.tile-num`** — board answer tile numbers. The `padding: 0` that was on `.tile-cover-circle .tile-num` was removed so it doesn't override.
- **`.board-stat-value`** — streak, multiplier, and strikes displays
- **`.btn-number`** (SVG `<text>`) — round select buttons, using `dx="0.1em"` (the SVG equivalent)

---

## Players List Marquee

The player list (turn order panels in the scoreboard) uses a **vertical marquee** instead of shrink-to-fit because shrinking to fit 4–5 players made text unreadably small. Structure:

```
<div class="players-list">        ← outer clip container, fixed height 80px, overflow hidden
  <ul class="players-list-track">  ← inner flex-column track
    <li>...</li>                   ← player items
    <!-- duplicated when ≥4 players for seamless loop -->
  </ul>
</div>
```

- **≤3 players**: single copy of items, no animation class. Static display, identical to original behavior.
- **≥4 players**: items are rendered twice in the track, `.marquee` class added, CSS `@keyframes players-marquee-scroll` animates `translateY(0 → var(--marquee-distance))` on infinite loop.
- **Loop distance** is measured *once* after render as `items[playerCount].offsetTop - items[0].offsetTop` — the exact pixel gap between the start of copy 1 and the start of copy 2. Using `offsetTop` auto-accounts for padding + gap math, giving a seamless loop. Because the initial measurement may be off if web fonts haven't loaded, the measurement is re-run on `document.fonts.ready`.
- **Duration** scales with player count: `playerCount * MARQUEE_MS_PER_ITEM / 1000` seconds. Default `MARQUEE_MS_PER_ITEM = 1500` (each player gets ~1.5s of screen time per cycle).
- **Tuning knobs** live at the top of `updatePlayerPanels()`: `MARQUEE_MIN_PLAYERS` (threshold) and `MARQUEE_MS_PER_ITEM` (speed).

The element was changed from `<ul>` to `<div>` at the outer level so we could nest a proper `<ul>` track inside without invalid HTML. `.players-list li` selectors still match because `li` is a descendant.

---

## UI / Behavior Decisions

- **Answer history format:** `[PlayerName] guessed "[guess]" — [result]`
  - Player name rendered in their team color
  - Correct results shown in green (`✓`), wrong results in red (`✗`)
  - Use plain text symbols `✓` / `✗`, not emoji variants — emoji variation selectors break CSS color
- **Steal attempts** log the **team name**, not an individual player name
- **Board renders only the number of rows needed** for the current question's answers (no blank padding rows).
- **"Advanced question options"** — opens a content dialog (`showQuestionOptions()`) with option rows for: get new question, flag for removal, flag for fact check, copy answers for judge. "Get new question" opens a confirm dialog stacked on top without dismissing the options dialog.
- **End-of-round state** repurposes the turn-input-box: header shows the round result message, body shows Reveal All / Next Round buttons.
- **Score edits** — a "Score edits needed?" link opens a content dialog (`showScoreEdits()` / `showFmScoreEdits()`) with +/−/input/Apply controls per team. Apply triggers a confirm dialog stacked on top.
- **Answer history** — "Answer History" link in `#questionActions` (right-aligned, alongside "Advanced question options") opens a content dialog (`showAnswerHistory()`) that reads from `guessHistory` on demand. Empty state shows italicized "No answers have been submitted yet this round".
- **Player/team name limit** — 18 characters max (`maxlength="18"` on all setup inputs). No explicit error message; the input shakes (CSS `input-shake` animation, 0.3s) when a keystroke is rejected at the limit. Backspace, arrows, and modifier shortcuts pass through normally.
- **Duplicate answer** — if a guess matches a previously submitted guess (normalized), the input field shakes (`input-shake`), placeholder text changes to "Answer already submitted" for 2s, and `neutralbeep.wav` plays. No message element used.
- **Export CSV** — removed. Was a Coyne Feud feature, not relevant for Good Answer.

---

## Scoring Mechanics

Two multiplier systems layer on top of the base point values:

### Answer Multiplier (Streaks)

- **State**: `currentStreak` (int, starts 0), `answerMultiplier` (float, starts 1.0)
- On correct answer: `answerTotal = Math.round(ans.points * answerMultiplier)`, then `currentStreak++`, `answerMultiplier = 1 + (currentStreak * 0.2)`
- On strike: `currentStreak = 0`, `answerMultiplier = 1.0` — previously earned points are locked in
- **Applies during steals** — streak belongs to the round, not the team. In normal flow the multiplier will be 1.0 at steal time (3 strikes reset it), but future items may preserve a streak into a steal
- Tile display: Mult column shows the multiplier used (e.g. "1.4x"), Total column shows `answerTotal`. Missed tiles show "—" for both
- **Reset** per round in `initRoundState()`

### Category Multiplier

- Rolled per question in `showCategorySelection()` via `rollCategoryMultiplier()`: 20% chance 1.5x, 5% chance 2x, 2% chance 3x
- Each of the 3-4 displayed categories gets an independent roll stored in `categoryMultipliers` map
- **Coin badges** on category pills: bronze (1.5x), silver (2x), gold (3x) — circular tokens positioned to the right of the button, staggered slide-in with Y-axis spin and bounce (1/2/3 bounces per tier)
- On category pick: `categoryMultiplier` set from the map
- **Applied at round end** via `awardRoundScore(team, callback)`: multiplies `roundScore` before adding to `teamScores`. If multiplier > 1, plays a count-up interstitial animation before showing the end-of-round message
- Coin badge relocates to the board footer (below `#board-round-total`) during the question screen, replacing the old `#cat-mult-indicator`

### Items (planned, not yet implemented)

- Teams can attain items that impact gameplay (e.g. activate a category multiplier, reveal an answer to preserve a streak)
- Max 2 items per team inventory, carry over between rounds until used/discarded
- Awarded at end of every round: 2 items presented, trailing team picks first, leading team can accept or pass the remaining item
- Items can only be used on your team's turn

---

## Phase Indicator — Persistent Sidebar Header

The top of `#sidebar-zone` contains a single persistent element, `#phase-indicator`, that drives the contextual header text across every game phase. The container stays put once it slides in at game start; only the text content inside swaps. This replaced an earlier "two identical divs" approach (`#category-prompt` + `#board-control`) that had to fake continuity by matching shapes during a panel swap.

### Structure

```html
<div id="phase-indicator" class="team-red">
  <span class="ph-span ph-category-select"></span>
  <span class="ph-span ph-gameplay"></span>
  <span class="ph-span ph-steal-chance"></span>
  <span class="ph-span ph-round-result"></span>
</div>
```

- Fixed **140px** height, flush top (no top border-radius), bottom border-radius 30px
- Background driven by team color (`team-red` / `team-blue` classes) with `transition: background 0.3s ease` for smooth cross-fades when the active team changes
- Only one phase span is visible at a time, selected via a `data-phase="..."` attribute on the container and matching CSS selectors
- Each span is absolutely positioned inside the container so two spans can briefly coexist during the "knock" collision (steal chance pushes gameplay span out)

### JS API (in feud.html, near `startGame`)

```js
setPhaseText("category-select", "Red Team, select a category:");
setPhaseTeamColor(0);          // 0 = red, 1 = blue
await setPhase("category-select");              // normal swap
await setPhase("steal-chance", { knock: true }); // collision mode
showPhaseIndicator();          // slide container in from above (game start)
hidePhaseIndicator();          // slide container out (resetGame)
```

- `setPhase()` handles the outgoing span's exit animation and the incoming span's entry animation. In **normal mode** it `await`s the outgoing exit animation fully before flipping `data-phase`, so the incoming span never crosses paths with the outgoing one. In **`knock` mode** the exit is fire-and-forget and only `TIMING.phaseKnockOverlap` (~120ms) elapses before the swap, so both spans render simultaneously and visually collide. Callers generally do not `await` the returned promise — the phase swap runs alongside whatever other sequence follows.
- All span entry/exit animations live in CSS (`ph-text-slide-in`, `ph-text-slide-out`, `ph-text-knock-out`). The JS only adds `.ph-exiting` or `.ph-knocked` to the outgoing span and awaits the animationend.

### Phase flow

1. **`category-select`** — "[Team], select a category:" during category pick
2. **`gameplay`** — "[Team] has the board" during a normal round
3. **`steal-chance`** — "[Team] can steal!" after a third strike (triggered with `knock: true`)
4. **`round-result`** — dynamic text for round outcomes:
   - Normal win: "[Team] won the round with [N] points!"
   - Steal success: "[Team] stole [N] points!"
   - Steal fail: "[Team] wins the round and keeps [N] points!"

`round-result` is a single reusable span whose text is rewritten per outcome (not three separate spans).

---

## Question Screen Layout

The sidebar during gameplay is split between the persistent `#phase-indicator` at the top (see previous section) and `#sidebar-question-answer` below it, which is a flex column stack with two zones:

### Zone 1: Content (`#sq-zone-content`)

Contains a single child: `#content-tv`, a 300×300px "TV screen" container with CRT overlay.

- **`#content-tv`** — fixed 300×300, `border-radius: 50px`, `overflow: hidden`, centered via `margin: 30px auto 10px auto`. Flex column layout. `perspective: 500px` + `transform-style: preserve-3d` for subtle 3D CRT bulge. Three overlay layers above children:
  - `::before` (z-index 10) — animated white noise (SVG turbulence + `tv-static` keyframes, `soft-light` blend, opacity 0.5)
  - `::after` (z-index 11) — CRT scanlines (repeating-linear-gradient, opacity 0.2)
  - `#content-tv-vignette` (z-index 12) — dedicated div for `box-shadow: inset` vignette (separate from scanlines so opacity is independent)
  Starts hidden with `.ct-hidden` class (opacity 0, scale 0). TV-on animation (`.tv-on` class) reveals it with CRT power-on effect.
- **`#cat-label`** — category ticker band inside content-tv. 50px tall, 1.8rem Bitcount font, `border-radius: 0`, no border, `z-index: 5` (above question-box, below CRT overlays). Background uses `var(--cat-face)` with category color classes. Marquee is pre-configured at creation — text repeats enough times to fill the 300px container (computed from char-count estimate), already scrolling when content-tv reveals. Created dynamically by `pickCategory()` and inserted into `#content-tv` before `#question-box`.
- **`#question-box`** — `position: absolute; inset: 0` fills the full 300×300 of content-tv, behind cat-label (`z-index: 1`). `padding-top: 60px` pushes content below the 50px cat-label. `display: grid; grid-template-rows: 85% 15%`: row 1 = `#question` (centered text), row 2 = `#questionActions` (flex row with `justify-content: space-between` — "Advanced question options" left, "Answer History" right). `transform: translateZ(20px)` pushes content forward within the 3D perspective. `#category` element has been removed.

### Zone 2: Input (`#sq-zone-input`)
- `#input-area` — full width, locked height (`min-height: 250px; max-height: 250px`), flex column. `#turn-header` is hidden (redundant with phase indicator). `#turn-input-box` fills parent height (`flex: 1`), `#turn-body` uses `justify-content: space-between` to pin the input row at the bottom. `#turn-subtext` has a fixed `height: 2.5rem` with `flex-shrink: 0` so font-size changes from `fitByCharCount` don't shift the input field. Buttons use `.input-btn` 3D prism class (see "3D Input-Area Buttons").

### Board Wrapper
- 70% width, centered via `margin: 0 auto`
- Attached directly under scoreboard (border-radius on bottom corners only)
- Slides in from above the canvas (behind the scoreboard) via `board-slide-in-top` animation
- `#game-board-zone` uses `justify-content: flex-start` + `overflow: hidden` to position board at top and clip the slide-in
- **Initial state**: has `class="offscreen"` in HTML so it starts above the canvas. Without this the wrapper briefly flashes on-screen at game start before sliding up to its hidden position.

### Canvas clipping lives at `#game-root`

`#game-root` has `overflow: hidden` and is the primary clipping boundary. Overflow settings down the sidebar chain:

- **`#sidebar-zone`** — `overflow: visible`, `min-width: 0`. Visible overflow is needed for category multiplier badges that hang off `.cat-row` edges. `min-width: 0` prevents flex expansion from nowrap marquee content.
- **`#sidebar-question-answer`** — `overflow: hidden`. Clips content-tv's fly-in and sq-zone-input's off-canvas slide.
- **`#sq-zone-content`** — `overflow: hidden`. Additional clipping layer.
- **`#content-tv`** — `overflow: hidden`. Clips cat-label marquee and question content.

---

## Question Phase — Entry Animations

The full sequence from "category picked → ready-to-play" state. Orchestrated in `pickCategory()` via `anim.sequence`.

### Order — strictly serial

1. **`#content-tv`** plays tv-on CRT effect (`.ct-hidden` → `.tv-on`, `tv-on` keyframes, 700ms — dot → line → full screen). Cat-label and question-box are already loaded inside — the screen reveals fully populated content.
2. **`#question`** text streams in via `typewriter()` (default 30ms per char; cursor blinks during `.typing`, steady during `.typed`)
3. **`#sq-zone-input`** slides up from below the canvas (`.offscreen-below` → `.input-enter`, `input-slide-up` keyframes, 500ms)

After step 3, `#guess` is focused. The board wrapper's `slide-in` from above starts in parallel at the very beginning of this sequence (separate from `anim.sequence`) so the main game area fills in while the sidebar steps play out.

### `typewriter()` helper

`typewriter(el, text, charMs = 30)` streams characters into `el` one at a time via `setTimeout`, returns a promise that resolves when done. Sequence:
- Clears `el.textContent`, removes `.typed`, adds `.typing` (opacity 1 + blinking `::after` cursor)
- Appends one char per `charMs` via `el.textContent = text.slice(0, i)`
- On completion, swaps `.typing` → `.typed` (opacity 1, no cursor)

**Call `fitByCharCount(el, max, finalText)` BEFORE clearing and streaming** — the fit scale needs to be computed against the full final text, not each intermediate substring, so the layout is stable while chars stream in.

Hidden-tab caveat: Chrome throttles `setTimeout` in background tabs, so the typewriter runs at ~1s/char in the Claude Preview hidden tab. Full visible runs need an in-browser check.

### Cleanup between rounds

`initRoundState()` resets all elements to their pre-animation states so the sequence replays cleanly:
- `#content-tv`: remove `.slide-out-left`, `.tv-on`, add `.ct-hidden`
- `#sq-zone-input`: remove `.input-enter`, add `.offscreen-below`
- `#question`: remove `.typing`, `.typed`
- `#cat-label`: the entire element is removed (the next round recreates it in `pickCategory()`)

---

## Stat Change Chevrons

`#board-streak` and `#board-mult` (`.board-stat-value` elements) show directional chevron indicators when their values change:

- **`flashChevron(el, dir)`** — creates a `<span class="stat-chevron up|down">` with `▲` or `▼`, appends to the stat element, self-removes on `animationend`. Plays `decreaseblip.mp3` when direction is `"down"`.
- **Up** (value increased): green `#4caf50`, starts at `bottom: 6px`, animates upward 45px.
- **Down** (value decreased): red `var(--red-text)`, starts at `top: 10px`, animates downward 45px. Plays `decreaseblip.mp3` once per field.
- Both animations: 0.75s, 3 keyframe stops, opacity stays 1 until 99.9% then snaps to 0 (abrupt disappear, no fade).
- **`_prevStreak` / `_prevMultiplier`** track previous values for direction detection. Reset in `initRoundState()`.
- **`updateStreakValue()`** and **`updateMultValue()`** are separate async functions that each handle their own count-up + chevron and return a Promise. `updateStreakDisplay(opts)` calls both — with `{ afterStrike: true }`, it waits 1400ms (strike animation duration), then sequences streak → 500ms gap → mult. See "Strike → Decrease Sequencing" section.
- On the first correct answer (transitioning from "—"), streak counts up from 0 and multiplier counts up from 1.0 (not instant).

---

## Correct Answer Scoring Sequence

When a correct answer is submitted, `flipTile` orchestrates a serialized animation sequence so each number change has individual visual impact. The sequence is `async` and `await`ed by `submitGuess`. Input is disabled during the sequence.

### Sequence steps

| Step | Element | Action |
|------|---------|--------|
| 1 | `.tile-cover` | Slide right (400ms CSS anim). Tile-back is revealed showing tile-num + tile-text only. |
| 2a | `.tile-pts` | Fade in (`.tile-stat-visible`) + count up 0 → points |
| gap | | `TIMING.scoringStepGap` (150ms) |
| 2b | `.tile-mult` | Fade in + count up 1.0 → mult (if > 1), or instant "—" with single tick |
| gap | | 150ms |
| 2c | `.tile-total` | Fade in + count up 0 → earnedTotal |
| gap | | 150ms |
| 3 | `#board-round-total` | Count up oldVal → roundScore |
| gap | | 150ms |
| 4a | `#board-streak` | Count up (or set "—") + chevron |
| gap | | 150ms |
| 4b | `#board-mult` | Count up (or set "—") + chevron |

After step 4b, `animateTurnSwap()` fires — unless all answers are now revealed (round ending), in which case the turn swap is skipped.

### CSS: hidden stat cells on reveal

`.tile-back.correct .tile-pts/.tile-mult/.tile-total` start with `color: transparent` (green background visible, text hidden). The `.tile-stat-visible` class sets `color: #fff` (or `#a5d6a7` for pts). Already-revealed tiles rebuilt by `updateBoard()` get `.tile-stat-visible` immediately.

### Tile scoring data persistence

`revealedData[]` stores `{ mult, earnedTotal }` per tile at reveal time. When `updateBoard()` rebuilds the DOM (e.g. after a strike), it passes `revealedData[i]` to `buildTileBack()` so tile-mult and tile-total retain their original values instead of showing current (reset) multiplier state.

### Skip streak/mult on final answer

When `revealed.every(r => r)` after a correct answer, steps 4a/4b are skipped entirely — streak and multiplier don't carry over to the next round.

---

## Count-Up Animation — `animateCountUp`

`animateCountUp(el, from, to, opts)` animates a number in an element using `setInterval`. Returns a Promise that resolves when the animation completes.

### Duration model (Balatro-inspired)

Duration auto-scales with the number of increments, keeping small changes leisurely and large changes faster per-tick:

```
duration = minDur + (maxDur - minDur) × min(increments / diffCeiling, 1)
```

Current values: `minDur = 1000ms`, `maxDur = 3000ms`, `diffCeiling = 100`.

| Increments | Duration |
|-----------|----------|
| 1–20 | 1000–1400ms |
| 50 | 2000ms |
| 100+ | 3000ms (capped) |

- **Steps** capped at 100 (`Math.min(increments, 100)`)
- **stepTime** capped at 500ms max (prevents single-increment changes from stalling)
- **Decimal handling**: when `decimals > 0`, increments are computed as `diff × 10^decimals` (so 1.2→1.4 = 2 increments at 0.1 steps)
- Sets `el.textContent` to the `from` value before the interval starts (prevents flash of final value)

### Options

- `suffix` (string, default `""`) — appended to displayed value (e.g. `"x"`)
- `decimals` (int, default `0`) — decimal places in display
- `tick` (bool, default `true`) — play tick SFX on each step

### Future: game speed multiplier

A global speed setting (Balatro-style 1×/2×/3×/4×) could scale `minDur`/`maxDur` and `TIMING.scoringStepGap` uniformly.

---

## Tick SFX — Web Audio API

Rapid-fire tick sounds during count-up animations use the Web Audio API (not `new Audio()`) for performance. A single `AudioBuffer` is decoded once from `flick.wav`; each tick creates a disposable `AudioBufferSourceNode`.

### Pitch scaling

`playTick(progress, opts)` plays a tick with pitch that rises over the count-up:

- `baseRate` (default 0.6) — starting playback rate
- `pitchRange` (default 1.2) — added to baseRate at progress=1
- Range: 0.6× → 1.8× (≈1.5 octave sweep)
- `volume` (default 0.3) — per-tick volume, multiplied by master × SFX gain

### Where ticks play

- **Scoring sequence** (inside `flipTile`): all count-ups have ticks by default
- **"—" reveal** for tile-mult: single tick at `playTick(0)` (low pitch)
- **Team scores** (`updateScores`): `tick: false` — these fire during round-end transitions
- **Round total** (`updateBoardRoundTotal`): `tick: false` — called from non-sequenced paths

### Sound file guidance

Ideal tick sound: short (<100ms), dry, percussive. Marimba hit, digital pip, or coin ting. Avoid reverb tails — they blur at high tick rates.

---

## Keystroke SFX — Typewriter Sound

The `typewriter()` helper plays a keystroke sound (`phonetype.wav`) on every character (including spaces). Uses the same Web Audio API pattern as the tick system — a single `AudioBuffer` decoded once, disposable `AudioBufferSourceNode` per play.

- **`playKeystroke()`** — no pitch variation, no random sample selection. Single identical sound per character. This mirrors phone keyboard SFX behavior (iOS/Android use one repeated click) and sounds natural in a digital context.
- **Volume**: `1.0 × master × SFX` gain — intentionally louder than tick SFX (0.3) because the typewriter runs at ~30ms intervals vs. tick's rapid-fire scoring bursts.
- **Reuses `tickAudioCtx`** — no second AudioContext. `initKeystrokeSfx()` creates the context if the tick system hasn't already.

---

## Tile Text Marquee

When a revealed answer's display text overflows `.tile-text`, a horizontal bounce marquee scrolls to show the full text.

### Trigger

`applyTileMarquee(txtEl)` checks `scrollWidth - clientWidth > 3` (3px threshold prevents near-miss jitter). Called from `flipTile()` on reveal and `updateBoard()` on rebuild.

### Structure

Text is wrapped in a `.tile-marquee-track` span inside the `.tile-text` element (which gets `.tile-marquee` class). CSS `@keyframes tile-marquee-scroll` bounces: hold at start (0–10%) → scroll to end (10–45%) → hold at end (45–55%) → scroll back (55–90%) → hold at start (90–100%).

### Duration

`4 + overflow / 48` seconds — proportional to overflow distance. Longer text gets more time but moves slightly faster per pixel. Minimum ~4s for short overflows.

---

## Background Music

Single looping track (`balbg.mp3`) via `<audio>` element with `loop = true`. No crossfade, no intro skip.

- `startBgMusic()` / `stopBgMusic()` — play/pause controls
- Volume: `volumeMaster × volumeMusic`, applied via `applyVolumes()`

---

## SFX System — Web Audio Buffers

All rapid-fire and animation-synced SFX use the Web Audio API (not `new Audio()`). A shared `AudioContext` (`tickAudioCtx`) is created once; each sound file is decoded into an `AudioBuffer` on load. Per-play: a disposable `AudioBufferSourceNode` is created, connected through a `GainNode` (volume = per-call × master × SFX gain), and started.

### Sound files and their buffers

| Buffer | File | Player function | Used for |
|--------|------|----------------|----------|
| `tickBuffer` | `flick.wav` | `playTick(progress, opts)` | Scoring count-ups, board-wrapper slide |
| `keystrokeBuffer` | `phonetype.wav` | `playKeystroke(volume)` | Typewriter chars, player row add/remove, tile-cover hover |
| `chimeBuffer` | `chime.wav` | `playChime(rate, volume)` | Badge bounce apex |
| `zoopBuffer` | `zoop.wav` | `playZoop(notchIndex)` | Speed stepper |
| `slitBuffer` | `slit.wav` | `playSlit(rate, volume)` | Cat-row entry/exit stagger, dialog open/close |
| `tap1Buffer` | `tap1.wav` | `playTap(1, volume)` | Setup nav buttons, menu toggle, confirm dialog |
| `tap2Buffer` | `tap2.wav` | `playTap(2, volume)` | Input area fly in/out |
| `tvonBuffer` | `tvon.wav` | `playTvOn(volume)` | Content-TV CRT power-on |
| `powerdownBuffer` | `powerdown.wav` | `playPowerdown(volume)` | CRT power-off (category select + start screen) |

### Audio offset and fade

- **`slit.wav`**: `source.start(0, 0.24)` — skips 240ms of silence + harsh beep transient at the start
- **`powerdown.wav`**: `source.start(0, 0.18)` — skips initial thump + quiet gap, starts at the rising drone
- **`tvon.wav`**: `linearRampToValueAtTime` fades gain to 0 over the final 900ms (sound is 1.6s, animation is 0.7s)
- **`powerdown.wav` timing**: sound starts 75ms before the CRT animation (`anim.wait(75)` between `playPowerdown()` and `.crt-off` class add) so the crescendo aligns with the visual collapse

### `anim.timer` — animation-synced SFX scheduling

SFX timed to land at a specific point in an animation (e.g. 70% through a slide-in) use `anim.timer(el, ms, fn)` instead of `setTimeout`. This creates a throwaway WAAPI animation with empty keyframes (`[{}, {}]`) so Chrome DevTools' animation speed control affects the timer's duration — at 10% speed, a 350ms timer takes 3500ms, keeping SFX in sync with slowed-down CSS animations.

**Critical: empty keyframes required.** The timer animation MUST use `[{}, {}]` (no properties). If any CSS property is specified (e.g. `{ opacity: 1 }`), the WAAPI animation overrides CSS animation values on the same element. This caused a major bug where `opacity: 1` in the timer overrode the `backwards` fill `opacity: 0` on cat-row slide-in animations, making buttons visible before their stagger delay.

### `<audio>` element SFX (non-Web Audio)

These use `new Audio()` and `playSound()`: `sfxCorrect` (`ding.mp3`), `sfxWrong` (`newstrike.wav`), `sfxGoodAnswer` (`goodanswer.mp3`, 300ms delayed after ding, baseVolume 0.35), `sfxNegativeBeep` (`negativebeep.wav`, failed steal only), `sfxSurveySays`, `sfxRoundEnd`, `sfxDecreaseBlip`, `sfxNeutralBeep`, `sfxButtonClick`. Volume: `volumeMaster × volumeSfx × baseVolume`. `baseVolume` is 0.6 for correct/wrong/surveysays, 0.35 for goodanswer, 1.0 (default) for others.

---

## Liftable Hover Effect

A reusable pick-up-and-set-down hover interaction for game elements. Currently applied to tile covers; designed to be extended to items, rewards, and other interactive elements.

### CSS classes

- **`.liftable`** — base class: `transition: transform 0.3s ease, box-shadow 0.3s ease`
- **`.lift-hover`** (applied by JS) — `transform: perspective(600px) rotateX(-4deg) translateY(-2px)`, dark drop shadow, `lift-nudge` wiggle animation (subtle ±0.5° rotation oscillation over 0.3s, staying in the lifted state throughout — no snap to flat)
- **`.lift-area`** — stable hit-zone parent. The `.liftable` element's transform shifts its edges, which can cause hover flicker at boundaries. Wrapping it in a `.lift-area` parent means hover is tracked on the non-moving parent.

### JS delegation

A single `mouseover` listener on `document` finds `.liftable` elements, tracks hover state on the nearest `.lift-area` (or the element itself if none), adds `.lift-hover`, plays `phonetype.wav`, and cleans up on `mouseleave`. Tile covers are gated on `.board-ready` to prevent interaction during the board slide-in animation.

### Hover flicker prevention — lessons learned

- **`lift-nudge` keyframes must stay in the lifted state throughout.** An earlier version started from `transform: none` at 0%, which snapped the element back to its original position mid-animation. This shifted the hit area, causing the cursor to leave and re-enter, triggering a hover feedback loop.
- **Hit area must be stable.** For tile covers, hover is tracked on the `.answer` row (40px, never transforms) rather than the `.tile-cover` itself. The `_liftHover` flag on the area element prevents re-triggering while already hovered.

---

## Board-Wrapper Category Badge

When a category has a multiplier, a coin badge (`.cat-mult-badge.board-badge`) is placed in `.board-footer` (which has `position: relative` inline). Positioned with `right: -50px; top: 115%; transform: translateY(-50%)` to sit just right of the round total value. Starts with `opacity: 0`, fades in via `.badge-visible` class after `anim.done(bwEl)` (board slide-in complete).

Cleanup: `document.querySelectorAll(".board-footer > .cat-mult-badge").forEach(el => el.remove())` in `initRoundState()`.

---

## `transitionend` Bubbling — Gotcha

`transitionend` events bubble. A `{ once: true }` listener on a parent that guards with `e.target !== parent` will silently consume the listener when a child's transition ends first — the guard returns early but `{ once: true }` already removed the listener. The parent's own transition then has no listener.

Fix: use a named function listener without `{ once: true }`, and manually `removeEventListener` inside the guard's success branch. See `beginStartGameExit()` for the canonical example.

---

## Turn Swap Animation

`animateTurnSwap()` provides visual feedback when the active player changes after a guess:

- Captures old text, calls `updateTurn()` (which sets new text + all game state), then if text changed: restores old text, plays `turn-swap` animation (0.45s), swaps to new text at 160ms (peak of the jump).
- `@keyframes turn-swap`: pop up 14px → slam down 2px past center with 1.12× scale → small bounce → settle.
- **Not used** when 3 strikes trigger steal phase — plain `updateTurn()` runs instead to avoid the 160ms setTimeout racing with the steal-phase UI update.
- **Not used** when the correct answer reveals the final tile — round is ending, no next turn.
- `#turn-subtext` uses `fitByCharCount` with `maxChars: 12`.

---

## 3D Isometric Round-Select Buttons

Setup step 1 uses inline SVG buttons (`.rounds-svg`) for round count selection (2/4/6):

- **Structure**: isometric projected rhombus (top face `#fba300`, sides `#b87800`) with `<text>` numbers sharing the same isometric `transform="matrix(0.866025 -0.5 0.866025 0.5 ...)"` as the face so they appear on the 3D surface. Size: 150×150px, font 3.125rem.
- **Height states**: `setButtonDepressed(svg, bool)` modifies SVG attributes directly (transform matrix Y offset, side strip y/height, clip-path) — CSS transforms can't be used because clip-paths need to stay in sync. Raised = y=43, height=16. Depressed = y=51, height=8.
- **Glow**: CSS `filter: drop-shadow()` on `.btn-number` for hover/selected states. Dormant LED look (`fill: rgba(255,255,255,0.3)`) for non-active state.
- **Sound**: `analogbuttonclick.mp3` plays on selection via `playSound(sfxButtonClick)`.
- **Unique SVG IDs**: each button uses suffixed IDs (`clip-r2`/`clip-r4`/`clip-r6`) to avoid conflicts in shared DOM.
- **`selectRounds(n, el)`** uses `el.closest('.rounds-svg')` to handle clicks on child SVG elements.

---

## 3D Input-Area Buttons (`.input-btn`)

Buttons inside `#input-area` (Submit, Reveal All, Next Round, game-over actions) use a 4-face rotating prism matching the category select `.btn-3d` pattern but with `#111` faces.

- **`make3dBtn(text, onclick, extraClass)`** — JS helper that returns button HTML with 4 `<span>` children. Optional `extraClass` for size variants.
- **Structure**: same `btn3d-tilt` keyframes as `.btn-3d`. Height: 38px, `translateZ(19px)` (half height). Width: 98%. Faces: `rgba(17,17,17,0.9)`, border `#333`, opacity 0.95.
- **Hover**: `setup3dBtns()` targets both `.btn-3d` and `.input-btn` with a `_has3dHover` guard to prevent duplicate listeners. Must be called after any innerHTML update that creates `.input-btn` elements.
- **Size variants**: `.input-btn-sm` (1rem font, white background — used for Reveal All), `.input-btn-xs` (0.9rem — Conclude Final Round), `.input-btn-fm` (1.2rem — Fast Money Round).
- **Stagger**: sibling `.input-btn` elements get staggered `animation-delay` (0s / -1.6s / -3.2s).
- **Not applied to**: score edit +/- buttons, fast money buttons, setup buttons — these remain flat `.btn` class.

---

## Round-End Sequence

When a round winner is determined (`setPhase("round-result")`), three simultaneous effects fire:

1. **Phase indicator glow** — `.round-glow` class adds `box-shadow: 0 0 30px rgba(255,255,255,0.6), 0 0 60px rgba(255,255,255,0.3)`. Uses CSS `transition: box-shadow 0.4s ease` (not keyframe animation) to avoid conflicting with the slide-in/slide-out `animation` property. Removed when phase transitions away from `round-result`.
2. **Round-end SFX** — `roundend.wav` plays via `playSound()`.
3. **Purple blob crossfade** — `--bg-blob-base` set to `#513f6d` (default purple, neutral between red/blue team colors). Restored to team color by `updateBlobColor()` via `updateTurn()` at the start of `advanceRound()`.

---

## Round Exit Animations (`advanceRound`)

`advanceRound()` is `async`. Before resetting state, it animates sidebar elements out:

1. **`#sq-zone-input`** slides down (`input-exit`, 0.4s)
2. **`#content-tv`** slides out left (`slide-out-left`, 0.4s) — takes cat-label + question-box with it as a unit
3. **`#board-wrapper`** slides out in parallel (CSS transition via `.offscreen` class, 0.5s)

**Color change is deferred**: `updateTurn()` (which sets team colors on input-area, blobs, phase indicator) runs *after* all exit animations complete, not before. This prevents jarring color snaps during the exit sequence.

---

## Per-Track Base Volume

Individual SFX tracks can have a `baseVolume` property (0–1) that multiplies with master × SFX gain in `applyVolumes()`. Default is 1 if unset. Currently reduced to 0.6: `sfxCorrect`, `sfxWrong`, `sfxSurveySays`. `sfxGoodAnswer` is 0.35.

---

## Strike → Decrease Sequencing

When a wrong answer triggers a strike, the streak and multiplier decrease animations are delayed until the strike-x-slam overlay completes (1.4s). `updateStreakDisplay({ afterStrike: true })` sequences: wait 1400ms → streak update + chevron + decrease blip → 500ms gap → multiplier update + chevron + decrease blip. Without `afterStrike`, both fire immediately (used by `initRoundState` resets).

---

## Setup Step Transitions

Two-step setup flow with ticker-style slide transitions. All use `async`/`await` with `anim.play`/`anim.done`. Both `#setup-step-1` and `#setup-step-2` have `flex: 1` to fill the remaining height below the title, with `justify-content: center` for vertical centering.

### Step 1: Game settings

- **Round count**: 3D isometric SVG buttons (2/4/6) — same pattern as before
- **Game speed stepper**: `◀ [value] ▶` arrow stepper. Futura 700, 3rem. Arrows have subtle CSS nudge animations (`speed-arrow-nudge-left/right`, 1.2s cycle). Arrows disable (no animation, dimmed color) at min/max bounds. Value label slides in/out on change with 125px fixed-width container and `overflow: hidden` clipping.
- **Next button** (`#setup-next-btn`): absolutely positioned right side, vertically centered (`right: 0%; top: 50%; transform: translateY(-50%)`). Uses `transport-btn` style with 5.8rem glyphs.

### Step 2: Team configuration

- **Back button** (`#setup-back-btn`): absolutely positioned left side, same size as Next/Start Game buttons
- **Player columns** (`#player-columns`): two team cards with dynamic player rows (see "Dynamic Player Rows" below)
- **`#selected-rounds`**: simple text line below player columns — "[X] Round Game" in Futura 700, 1.2rem, `#fba300`
- **Start Game button** (`#start-game-container`): absolutely positioned right side, always visible (no fade-in/out)

### Forward: Step 1 → Step 2 (`proceedToTeamSetup`)

Ticker-style: content slides **left** (user is navigating right).

| Step | Action | Duration |
|------|--------|----------|
| 1 | Step 1 flies out left (`setup-fly-out`, translateX → -120%) | 0.28s |
| 2 | Step 1 hidden, step 2 shown, flies in from right (`setup-fly-in`, translateX 120% → 0) | 0.30s |

### Back: Step 2 → Step 1 (`backToRoundSelect`)

Reverse ticker: content slides **right**.

| Step | Action | Duration |
|------|--------|----------|
| 1 | Step 2 flies out right (`setup-fly-out-left`, translateX → 120%) | 0.28s |
| 2 | Step 2 hidden, step 1 shown, flies in from left (`setup-fly-in-right`, translateX -120% → 0) | 0.30s |

**No opacity transitions** on any fly animations — pure slide for consistent ticker aesthetic.

Team names, player rows, and speed/round selections are preserved across back/forward navigation.

### Game start: Step 2 → Game (`beginStartGameExit`)

Simple fade of the entire `#setup` container (opacity 1 → 0, 0.5s ease). `startGame()` fires on `transitionend`.

### Dev mode dismiss

`activateDevMode()` calls `_dismissStartScreen()` — the same animated sequence as a normal start screen click (text fade → logo TV-off → screen fade). Pre-fills 2 players per team by programmatically calling `addPlayerRow()`.

---

## Game Speed System

Global speed multiplier that scales all gameplay animations uniformly. Two coordinated mechanisms:

### CSS: `--speed` custom property

Set on `:root` via `setGameSpeed()`. All gameplay animations use `calc(duration / var(--speed))` in their `animation-duration`. Ambient animations (blobs, button tilt, scanlines, cursor blink, marquees) are **not** scaled.

### JS: `gameSpeed` divisor

`anim.wait(ms)` and `anim.setDelay(el, ms)` divide by `gameSpeed` internally. `animateCountUp` divides its computed duration by `gameSpeed`. `typewriter()` divides `charMs` by `gameSpeed`. This means callers pass base timing values and scaling is automatic.

### Speed notch table

```js
const SPEED_NOTCHES = [
  { value: 0.5, label: "0.5" },
  { value: 1,   label: "1" },
  { value: 2,   label: "2" },
  { value: 3,   label: "3" },
];
```

To add a new speed tier, append an entry. The setup stepper, settings slider, and all notch labels auto-adjust.

### Two UIs, synced

- **Setup screen stepper** (`stepSpeed(dir)`): arrow-based ◀/▶ with sliding number label. Plays `zoop.wav` with pitch modulated by notch index (0.7× at 0.5 speed → 1.4× at 3 speed).
- **Settings tray slider** (`applySpeedFromSlider(index)`): range input with clickable notch labels. Applies speed changes immediately (live mid-game). `syncSpeedSlider()` and `syncSpeedStepper()` keep both UIs in sync.

### Spacebar fast-forward

While the guess input is disabled (scoring sequence in progress), pressing Space toggles a 2× speed boost (capped at 4×). Press again to deactivate, or it auto-deactivates when the scoring sequence completes (input re-enables). A pulsing `▶▶` indicator (CSS triangle arrows, `#speed-boost-indicator`) appears centered on the game canvas while active.

### What does NOT scale

- Fast Money countdown timer (real-time 1000ms ticks)
- Ambient/decorative CSS animations
- Cleanup/feedback timeouts (message fades, copy confirmations)
- Sound pitch/volume (ticks naturally speed up because count-ups run faster)

### Reset

`resetGame()` sets `gameSpeedSetting = 1`, calls `setGameSpeed(1)`, and resets both UIs.

---

## Dynamic Player Rows

Team setup starts with 1 player input per team. Players add/remove rows dynamically.

### Structure

Each player row is a `.player-row` div (position: relative) containing:
- `<input>` — full-width, `padding-right: 28px` to clear the remove button
- `.player-remove-btn` — absolutely positioned inside the input (right: 4px), circular − button

A `.player-add-btn` (circular + button) is a sibling of `.player-col-body` inside `.player-col`, positioned absolutely at the bottom center (`bottom: -14px; left: 50%; transform: translateX(-50%)`). It sits outside the body to avoid being clipped by the body's `mask-image` cutout — a `radial-gradient` mask punches a 16px-radius semicircle notch at the bottom center of `.player-col-body`, creating a transparent gap (2px) between the body edge and the button. The button background uses explicit team colors (`.red-col .player-add-btn { background: var(--red-bg); }`), not `inherit`.

JS references to the add button use `.closest('.player-col').querySelector('.player-add-btn')` (not `.closest('.player-col-body')`) since the button is outside the body.

`#player-columns` uses `align-items: flex-start` so columns size independently — adding rows to one column doesn't stretch the other.

### Constraints

- **Minimum**: 1 row per team (cannot remove the last row)
- **Maximum**: 5 rows per team (`MAX_PLAYERS` constant). At max, button gets `.maxed` class (gray `#555`, no hover effect). Clicking when maxed triggers `col-nudge` animation (subtle y-axis wiggle) on the parent `.player-col`.
- **− button visibility**: hidden via `.player-row:only-child .player-remove-btn { display: none }` when only 1 row exists

### Animations

- **Enter**: new row starts with `.entering` class (`max-height: 0; opacity: 0; margin-bottom: -6px`), removed on next rAF to trigger transition to full size
- **Exit**: `.exiting` class applied, same properties transition to 0, row removed on `transitionend` (with 350ms setTimeout fallback for hidden tabs)

### SFX

`phonetype.wav` plays at 1.5× volume on both add and remove via `playKeystroke(1.5)`.

### Player name fallback logic (`startGame()`)

- **Single empty row** (default state): falls back to team name — preserves original behavior
- **Multiple rows**: each row = an active player. Empty inputs get `"Player N"` fallback names (1-indexed by row position)

### CSS inheritance

`.player-col input, .player-col button` sets `font-family: inherit; text-transform: inherit; letter-spacing: inherit` — form elements don't inherit these by default.

### Functions

- `addPlayerRow(btn)` — creates and appends a new `.player-row` with enter animation
- `removePlayerRow(btn)` — animates out and removes the row
- `resetPlayerRows()` — resets both teams to 1 empty row (called by `resetSetupSteps()`)

---

## Start Screen — CRT Effects and Dismiss Sequence

The `.crt-start-screen` class applies a composite TV effect to `#start-screen`:

- **`::before`** — animated white noise (same SVG turbulence as cat-label, `tv-static` keyframes, `overlay` blend at 0.12 opacity)
- **`::after`** — rolling scanlines (`scanline-roll` keyframes) + diagonal glare gradient (125deg white highlight)
- **Vignette** — `box-shadow: inset 0 0 120px rgba(0,0,0,0.5)`
- **Blob colors** — per-blob inline `fill` overrides set distinct colors on load; `--bg-blob-base` set to `#C00000`. These colors **persist through all setup screens** — they do not crossfade on start-screen dismiss. Inline fills are cleared in `startGame()` so `updateBlobColor()` (called via `updateTurn()`) can set `--bg-blob-base` to the first team's color. SVG blob elements have `transition: fill 1.5s ease` for smooth crossfades.
- **Copyright** — `.copyright` is a direct child of `#start-screen` (not `#start-content`), positioned absolutely at `bottom: 10px` to anchor to the canvas bottom.
- **Logo** — `#start-logo` has `pointer-events: none` and `mix-blend-mode: multiply` (blends with SVG blob background). Contains two styled spans: `#logo-good` and `#logo-answer`.

### Dismiss sequence (`_dismissStartScreen()`)
Shared by both normal click and dev mode:
1. **0ms**: h1 + `.copyright` fade out together (`.start-fade-out`, 1s). Blob colors are **not** changed.
2. **1000ms**: logo gets `.tv-off` (`logo-tv-off` keyframes, 0.5s — adapted from `crt-power-off`)
3. **1300ms**: start screen fades out (`.dismissing`), setup slides in

---

## Category Phase — Entry Animations (locked in)

The full sequence from "Start Game" click to a usable category-select screen. These animations are **committed and should not be changed without explicit instruction** — they were tuned through multiple rounds of iteration.

### Sequence overview (all fire in parallel from `startGame`)

All these run via the `anim` helper; timing is controlled by `TIMING` constants and CSS animation durations.

1. **Phase indicator container** slides down from above (`phase-slide-in`, 0.45s)
2. **Scoreboard** slides down from above (`scoreboard-slide-down`, 0.5s) — both elements start with `class="offscreen"` in HTML and are swapped to `.slide-in` via `requestAnimationFrame` so the animation replays cleanly on subsequent games
3. **Category pills area** — no container animation (would break `mix-blend-mode` background). Children stagger in individually instead.
4. **Cat-rows** slide in from the left staggered via `anim.stagger(rows, { gap: TIMING.catRowStagger })` — each row's CSS `cat-slide-in` animation (0.4s) fires after its inline `animation-delay`
5. **Coin badges** (category multiplier tokens) slide in after the last cat-row settles, 1s apart, via `anim.setDelay` on each badge. Each bounce apex triggers a chime SFX (`chime.wav` via Web Audio API) and sparkle particle burst (`.sparkle` elements appended to the `.cat-row`, not the badge, to avoid inheriting the badge's `rotateY`). Chime pitch escalates per bounce (1.0×/1.15×/1.3×) and volume escalates (0.3/0.5/0.7). Sparkle particles are 4-pointed stars using `clip-path`, colored with `--coin-glow`, 3–5.5px, travel 10–20px from the badge edge, 0.55s duration, self-remove on `animationend`.
6. **Pills divider** ("— or —") starts at `opacity: 0`, fades in via `.fade-in` class with inline `animation-delay` computed to land *after* the last cat-row settles: `(rows.length - 1) * TIMING.catRowStagger + TIMING.catRowSlideDuration + TIMING.pillsDividerBuffer`
7. **Phase text** (`ph-category-select`) drops in after a `TIMING.phaseTextEnterDelay` wait (400ms) — long enough for the container to nearly finish its slide-in

### Key constraints

- **`#category-pills-area` must NOT have opacity or transform animations applied to the container itself.** It uses `.blend-multiply` with a `::before` pseudo-element; animating opacity on the parent creates a new stacking context that blocks `mix-blend-mode` from reaching the `#game-root` backdrop. See "Blend-Multiply Utility" for the full explanation. Animate the children (cat-rows, divider) instead.
- **`#board-wrapper` must start with `class="offscreen"` in HTML**, not added via JS at game start. Without the initial class the wrapper sits at its default on-canvas position until `showCategorySelection` adds `.offscreen`, which triggers `transition: transform 0.5s ease` and causes a visible upward flash.

---

## Category Phase — Exit Animations

When a category is clicked, `pickCategory()` is async and delegates to `animateCategoryTransition()` which runs **two parallel paths** — Path A for everything that wasn't selected, Path B for the selected category. Both start simultaneously on click; Path B's second phase waits for Path A to finish before firing.

### Layout prerequisites (why the pills area doesn't teleport)

The pills area's sizing is **fully locked** before these animations run, so nothing reflows when the selected row's transform scale collapses toward zero:

- `#category-pills-area` has a `min-height: 480px` covering the full content (12 + 292 + 41 + 116 + 12 = 473 rounded up)
- `.cat-row` has a fixed `height: 80px`
- `.trivia-categories` / `.survey-categories` use **CSS grid with explicit row tracks** (`grid-template-rows: repeat(3, 80px)` and `80px` respectively), and each `.cat-row` is pinned to its track via `:nth-child` grid-row assignments.

The grid pinning is the critical bit: when the selected row's transform scales it toward zero (or if it were ever made `position: absolute`), `:nth-child` counts DOM order regardless of layout state, so the other rows keep their assigned grid tracks and don't slide into the gap. Any changes to this structure need to preserve that property or the exit animations will fall apart.

### Path A — Unselected items slide left

A single unified sequence in DOM order: trivia row 1 → trivia row 2 → trivia row 3 → **divider** → survey row 1, with the selected row filtered out. The divider is treated as row 4 of 5 and participates in the stagger using the same `cat-slide-out-left` keyframe as the cat-rows. This matches the mental model where the pills area has 5 rows (4 categories + divider) and any one of the categories can be selected.

- Leading delay: 100ms before the first item starts
- Stagger gap: `TIMING.catRowExitStagger` (default 100ms)
- Per-item animation: `cat-slide-out-left 0.3s ease-in both`
- Badges on cat-rows spin out via `badge-spin-out 0.4s forwards`
- Total Path A duration: ~700ms from click

**Critical CSS detail — `cat-slide-out-left` keyframes**: the `from` state must be explicit (`from { transform: translateX(0); opacity: 1 }`). The divider's base CSS has `opacity: 0` (for its delayed entry fade-in), and when the inline exit animation replaces the fade-in's `forwards` fill, the element would otherwise fall back to opacity 0 and the slide-out would run invisibly. Explicit `from` + fill-mode `both` keeps the divider visible throughout its pre-stagger delay and the slide itself.

### Path B — Selected category: glow ramp → CRT power-off

The selected category **does not move**. Instead, two sequential phases transform it in place:

**Phase B1 — Steady glow ramp** (`.selected-glow` class, 700ms)
- Kicks off the instant the row is clicked, running in parallel with Path A
- Freezes the button's infinite `btn3d-tilt` animation (`animation: none !important`) and snaps it to `perspective(1000px) rotateX(0deg)` — button face locks flat toward the camera
- `cat-glow-ramp` keyframe: `filter` ramps from nothing to `drop-shadow(0 0 22px color) drop-shadow(0 0 44px color) brightness(1.45) saturate(1.35)`, where `color` is the category's own `--cat-solid` CSS variable
- Uses `filter: drop-shadow` (not `box-shadow`) so the glow follows the composite rendered shape of the row + its absolutely-positioned coin badge, unifying them into a single glowing object
- Duration is tuned to match Path A's 700ms total so the glow peaks exactly as the last Path A item finishes exiting

**Phase B2 — Classic CRT power-off** (`.crt-off` class, 490ms)
- Fires via `await anim.wait(700)` after Path A completes
- `crt-power-off` keyframe runs the nostalgic cathode-ray shutdown:
  - **0–10%**: Brightness surge (residual electron-gun charge dump)
  - **10–40%**: Vertical collapse to a thin horizontal line (`scaleY(1) → scaleY(0.02)`)
  - **40–55%**: Line flashes wider and goes pure white (via `saturate(0)` + high brightness)
  - **55–70%**: Line holds briefly
  - **70–85%**: Horizontal collapse to a center dot (`scaleX(1) → scaleX(0.015)`)
  - **85–92%**: Dot persists for an instant
  - **92–100%**: Dot fades to nothing (`scale(0)`, `brightness(0)`, `opacity 0`)
- The keyframe's 0% state is **intentionally identical** to `cat-glow-ramp`'s 100% state — with fill-mode `both` on both animations, the handoff from glow → CRT is seamless (no visual jump when `.crt-off` replaces `.selected-glow`'s animation property)
- Uses `transform-origin: center center` so the collapse implodes inward from all sides

### Total timing

- 0ms: click → glow ramp starts, Path A slide-outs begin their staggered delays
- 700ms: Path A complete, glow at peak, CRT power-off triggers
- 1190ms: CRT finished, `animateCategoryTransition` resolves, `pickCategory` continues to build the `#cat-label` header

### Category class on the row

`makeBtn()` applies the category class (`cat-science` etc.) to **both the cat-row and the button**. This lets the row inherit `--cat-face` / `--cat-solid` CSS variables for its Path B animations. The category classes only define variables, so putting them on the row has no side effects beyond enabling the cascade.

### Cleanup
`initRoundState()` removes stale elements at the start of each new round: `#cat-label`, `.cat-row` remnants in `#sq-zone-content`, `.cat-mult-badge` in `.board-footer`. Resets `#content-tv` to `.ct-hidden`. Removes entrance animation classes so they replay next round. The `.selected-glow` and `.crt-off` classes are naturally cleared because the entire pills area's `innerHTML` is rebuilt each round.

---

## Custom Dialog System

Two independent dialog layers for modals and confirms. Both use frosted glass panels (`rgba(17,17,17,0.75)` + `backdrop-filter: blur(20px)`), positioned inside `#game-root` (`position: absolute`, constrained to the 1280×720 canvas).

### Two layers

- **`#dialog-backdrop`** (z-index 10000) — content dialogs. Fly-in from bottom (`translateY(720px) → 0`), no opacity transition. Used by `showContentDialog(title, html)` / `closeDialog()`.
- **`#confirm-backdrop`** (z-index 10001) — confirm dialogs. Fade + subtle slide (`translateY(40px) → 0` with opacity). Used by `showConfirm(message, opts)` → `Promise<boolean>` / `closeConfirm(result)`. Stacks above content dialogs.

### Canvas containment

Dialogs live inside `#game-root` so they scale with the canvas and cannot overflow it. Key CSS values that enforce this:
- `.dlg-backdrop`: `position: absolute` (not `fixed`), `inset: 0`
- `.dlg-panel`: `width: 90%` (not `90vw`)
- `.dlg-body`: `max-height: 400px` (not `80vh`)
- Fly-in uses `translateY(720px)` (canvas height, not `100vh`)

### Tabbed dialogs

Dialogs can include tabs via `.dlg-tabs` (flex container of `.dlg-tab` buttons) and `.dlg-tab-panels` (CSS grid wrapper). All `.dlg-tab-panel` children occupy the same grid cell (`grid-area: 1 / 1`), so the container sizes to the tallest tab — preventing height jumps when switching. Inactive panels use `visibility: hidden` (not `display: none`) to preserve this sizing. `switchSettingsTab(name)` toggles `.active` on tabs and panels.

### Shared CSS classes

`.dlg-backdrop`, `.dlg-panel`, `.dlg-title` (gold dazzle-unicase), `.dlg-body` (`max-height: 400px; overflow-y: auto`), `.dlg-actions`, `.dialog-btn` variants (`-confirm` gold, `-cancel`/`-close` subtle gray), `.dlg-tabs`, `.dlg-tab` (inactive `#333`, active `#fba300`), `.dlg-tab-panels`, `.dlg-tab-panel`.

### Nesting behavior

Content and confirm layers are independent. "Get new question" from the options dialog opens a confirm on top without dismissing options. Cancel → only confirm closes. Yes → both close.

### Escape key

Closes topmost open layer first (confirm before content).

### Where dialogs replaced old UI

- **Advanced question options** — was `<details>` dropdown, now `showContentDialog` with `.dialog-option-list` rows
- **Score edits** — was `<details>` dropdown, now `showScoreEdits()` / `showFmScoreEdits()` with `.score-edit-form` layout (team name above, +/−/input/Apply row)
- **Answer history** — was collapsible tray (`#history-tray-handle`), now `showAnswerHistory()` reading from `guessHistory` on demand
- **4 native `confirm()` calls** — all replaced with `await showConfirm()` (`getNewQuestion`, `submitEdit`, `resetGameConfirm`, `fmSubmitFM`)
- **Settings** — was a full-height slide-in tray (`#settings-tray`), now a tabbed `showContentDialog` built by `openSettingsDialog()`. Three tabs: Audio (volume sliders + mute), Game (speed, tooltip delay, hide help tips), Graphics (CRT toggle). Tab state (`_settingsTab`) persists across open/close. Hamburger button remains inside `#game-root` (`position: absolute`).

---

## Tooltip System — CSV-Driven

Hover tooltips loaded from `tooltips.csv` at page load. Content is editable in any spreadsheet app.

### CSV format

```
id,class,flavor,description
rounds-2,help,Quick game,Play a 2-round game
board-streak,evergreen,On a roll,Consecutive correct answers
```

- `id` — matches `data-tip="id"` attribute on the target element
- `class` — `"help"` (hideable via settings toggle) or `"evergreen"` (always shown)
- `flavor` — short playful text (gold italic, above the rule). Leave blank to omit.
- `description` — informative explanation (dark text below the rule)
- Fields with commas must be quoted. Literal quotes use `""` (standard CSV escaping).

### Rendering

- Off-white panel (`#f0f0f0`), `border-radius: 10px`, `max-width: 280px`
- Flavor: `#fba300`, futura-100, 0.7rem, italic, with `border-bottom: 1px solid rgba(0,0,0,0.5)` separator. Hidden via `:empty { display: none }` when blank.
- Description: `#111`, futura-100, 0.9rem, weight 500
- Pointer arrow (`::after` triangle) points toward the element, direction set via `data-placement` attribute

### Positioning logic (canvas-aware)

1. Default: appear **left** of the element
2. Element in **left 20%** of canvas → appear on right
3. Element in **bottom 10%** of canvas → appear above
4. Element in **top 10%** of canvas → appear below

All positions clamped to viewport edges.

### JS API

- `showTooltip(target, id)` — look up CSV data, position, show
- `hideTooltip()` — hide and clear timer
- Event delegation via `mouseover`/`mouseout` on `document` — works for static and dynamic elements
- Hover persistence: tracks `activeTarget` and `_pendingTarget` to prevent tooltip from flickering when cursor moves between child elements within the same `[data-tip]` boundary
- `tooltipDelay` (default 400ms) — adjustable via settings slider (0–1000ms)
- `hideHelpTips` — boolean toggled by "Hide Help Tips" setting, suppresses `help` class tooltips

### Adding tooltips to elements

Static HTML: add `data-tip="id"` directly. Dynamic JS: include in template literal or use `el.dataset.tip = "id"`. For `make3dBtn`, use the optional 4th parameter: `make3dBtn('Submit', 'submitGuess()', '', 'submit-guess')`.

### Dynamic tooltip overrides

The `dynamicTipText` map (just above `showTooltip()`) allows specific tooltip IDs to override their CSV text with live values. Each entry is a function returning `{ flavor?, description? }` — unset fields fall through to CSV. Currently used by `board-mult` to show the current multiplier value in the flavor text.

---

## Player Inventory (Placeholder)

`#player-inventory` is an empty 45px-tall debossed tray (`border-radius: 50px`, inset `box-shadow`) below the submit button in `#input-area`. Placeholder for the future items/relics system. Has a tooltip (`data-tip="player-inventory"`) explaining its purpose.

---

## Strike Animations

### Per-strike hop-slam

When `updateStrikes()` renders active strikes, only the newest (index `strikes - 1`) gets the `.strike-new` class, which plays `strike-hop-slam` (pop up 12px, slam down with bounce, 0.4s scaled by game speed).

### Three-strike glow

At 3 strikes, the `.board-stat-value` housing the strikes gets `.strikes-full` — a red inner + outer glow that fades in over 0.8s (`strikes-glow-in`) then pulses continuously (`strikes-pulse`, 1.5s cycle). On a failed steal attempt, `.strikes-full` is replaced with `.strikes-fade-out` (1s fade to no glow).

### Failed steal sequence

On incorrect steal answer: `negativebeep.wav` plays, `#board-wrapper` gets a WAAPI error wiggle (500ms lateral shake, `composite: 'add'` to layer on top of existing CSS animations), and the strikes glow fades out. No strike overlay splash screen.

### Board-wrapper exit transition — `forwards` fill gotcha

When `#board-wrapper` exits (`.slide-in` removed, `.offscreen` added), the `forwards` fill from the slide-in animation is lost. The browser may not trigger the CSS `transition` because the fill removal isn't treated as a style change. Fix: explicitly set `style.transform = 'translateY(0)'`, force reflow, clear the inline style, then add `.offscreen` — this gives the transition a clean computed starting value.

---

## Font-Ready Gate

`#game-root` starts with `opacity: 0` in CSS. At the end of the `<script>` block:

```js
document.fonts.ready.then(() => {
  document.getElementById('game-root').style.opacity = '1';
});
```

Prevents FOUT (Flash of Unstyled Text) — the start screen only renders after all web fonts (Typekit, Google Fonts, custom `@font-face`) have loaded. No transition on the opacity change — the start screen's own CRT entrance handles the visual reveal.

---

## Victory Animation — Confetti + Fireworks

When `endGame()` is called at the end of the final round, `playVictoryAnimation(winnerIdx)` launches two HTML5 canvas particle systems and a centered victory dialog.

### Two-Canvas Architecture

The victory dialog needs to be sandwiched between confetti (behind) and fireworks (in front), so two canvases are used:

- **`#victory-canvas-back`** (z-index 9998) — confetti only, behind the dialog
- **`#victory-canvas-front`** (z-index 10001) — fireworks + sparks, in front of the dialog
- **`#victory-backdrop`** (z-index 10000) — the dialog itself, between the two canvases

Both canvases are `position: absolute; inset: 0` inside `#game-root`, sized 1280×720, `pointer-events: none`, hidden by default (`display: none`).

### Confetti (continuous)

~90 rainbow-colored rectangles fall from above with gravity, horizontal wobble, and rotation. When a piece falls off the bottom it's recycled to the top — runs indefinitely until `stopVictoryAnimation()`. The `VICTORY.RAINBOW` array holds the color palette.

### Fireworks (~7 bursts over ~8 seconds)

Rockets launch from the bottom in the winning team's color (`--red-text` or `--blue-text`), rise to a random height, then explode into 50-80 sparks with gravity and fade. After all bursts fire, no more launch — confetti continues alone.

### Animation Loop

A single `requestAnimationFrame` loop (`victoryLoop`) drives both systems. Confetti draws to `ctxBack`, fireworks+sparks draw to `ctxFront`. Loop runs until `stopVictoryAnimation()` is called.

### Integration

- `playVictoryAnimation(winnerIdx)` — called by `endGame()`. Shows canvases, populates and opens the victory dialog, starts the rAF loop.
- `stopVictoryAnimation()` — cancels rAF, clears both canvases, hides dialog. Called by `resetGame()` and `startFastMoney()`.

---

## Victory Dialog

A custom dialog panel (`#victory-backdrop > .victory-panel`) that appears when the game ends. Distinct from the regular dialog system (`#dialog-backdrop`).

### Design

- **Panel background**: winning team's `--red-bg` or `--blue-bg` (set via `--victory-bg` CSS variable)
- **Header strip**: `::before` pseudo-element with `--victory-header-bg` set to the team's text color, height measured dynamically via `--victory-header-h` to cover the title area
- **Text**: white base, team name spans use `--red-text` / `--blue-text`
- **Size**: 600px width, 60% canvas height, bottom-aligned with `margin-bottom: -2px`, `border-radius: 16px 16px 0 0`
- **No backdrop dimming** — `pointer-events: none` on `.victory-backdrop` always, `pointer-events: all` on `.victory-panel` only. Clicks pass through to the game behind it.

### Structure

```html
<div class="victory-panel">
  <div class="victory-title">Victory!</div>
  <div class="victory-body">...</div>
  <div class="victory-awards">...</div>
  <div class="victory-actions">...</div>
</div>
```

### Body Text — Dynamic Messages

`buildVictoryMessage(winnerIdx)` generates contextual text based on score margin:

| Condition | Message |
|---|---|
| Scores tied (tiebreaker) | "Tied on points! [winner] wins the tiebreaker..." |
| Margin > 100 AND winner > 2× loser | Bloodbath message |
| Margin < 100 | Close game message |
| Default | "[winner] takes home the win!" |

Loser score of 0 is treated as 1 for the 2× check (`Math.max(lScore, 1)`).

### Dismiss / Restore

- **Dismiss** button adds `.victory-dismissed` class, sliding the panel to `translateY(calc(100% - 46px))` so only the title peeks above the canvas bottom edge
- The panel gets an `onclick` handler (deferred via `requestAnimationFrame` to avoid same-click bubbling) that restores on click
- **Restore** removes `.victory-dismissed` and clears the onclick
- `#questionActions` remains visible in endgame state (not hidden). The "Get new question" option inside the question options dialog is disabled via `gameEnded` flag.

### `#endRound` Sidebar

`endGame()` also populates the `#endRound` div in the sidebar with the winner message + Fast Money / Play Again buttons — retained so players can return to the board to review answers after dismissing the victory dialog.

---

## Match Log — `matchLog` Array

A per-session array that records every guess across all rounds. Cleared on `resetGame()`, persists across rounds (unlike `guessHistory` which resets per round).

### Entry Schema

```js
{
  player:       "Alice",           // individual player name (never team name)
  team:         0,                 // 0 = red, 1 = blue
  guess:        "pizza",           // raw guess text
  outcome:      "correct",         // "correct", "wrong", "steal_success", "steal_fail", "duplicate"
  points:       40,                // points earned (null for wrong/duplicate)
  multiplier:   1.2,               // answer multiplier applied (null for wrong/duplicate)
  streak:       2,                 // streak at time of guess, before increment (null for duplicate)
  streakBroken: 0,                 // streak that was active before this wrong answer reset it (0 if none)
  isSteal:      false,             // whether this was during steal phase
  round:        1,                 // round number
  question:     "Name a food",     // question text
  category:     "Survey",          // parent category string
  timestamp:    1713045600000,     // Date.now() at submission
}
```

### `individualPlayer` vs `playerName`

In `submitGuess()`, two player name variables exist:
- **`playerName`** — uses team name during steals (for `guessHistory` display, per CLAUDE.md UI decisions)
- **`individualPlayer`** — always resolves to the actual player from `teamPlayers` rotation (for `matchLog` awards)

All `logGuess()` calls use `individualPlayer` to ensure awards are never assigned to a team name.

---

## Victory Awards System

Player performance awards computed from `matchLog` data and displayed in the victory dialog.

### Data Flow

1. **`awards.json`** — static award definitions: `id`, `name`, `compute` key
2. **`tooltips.csv`** — award tooltip flavor text and descriptions, keyed by `award-{id}`
3. **`awardComputers`** (JS object) — compute functions keyed by the `compute` field. Each returns an array of tied candidates (or empty array if nobody qualifies).
4. **`computeAwards()`** — aggregates per-player stats from `matchLog`, runs compute functions, resolves ties, returns up to 6 awards.

### Per-Player Stats (aggregated in `computeAwards`)

| Stat | Source |
|---|---|
| `totalPoints` | Sum of `points` on correct/steal_success entries |
| `bestSingle` | Max `points` from a single entry |
| `correctCount` | Count of correct/steal_success outcomes |
| `guessCount` | All non-duplicate outcomes |
| `duplicateCount` | Duplicate outcomes |
| `maxStreak` | Highest `entry.streak + 1` on correct entries |
| `streaksKilled` | Count of wrong entries where `streakBroken > 0` |
| `multipliedAnswers` | Correct entries where `multiplier > 1` |
| `catPoints` | Points per parent category (object) |
| `catGuesses` | Guess count per parent category (object) |
| `uniqueCatsScored` | Number of categories with points |
| `avgAnswerTime` | Average ms gap between consecutive timestamps |

### Category Normalization

`parentCat(cat)` maps raw category strings to parent categories using the same logic as `getCategoryClass()`: Science, Geography, Pop Culture, Sports, Survey.

### Tie Resolution — Single-Pass, Least-Awarded Preference

Single pass over shuffled award definitions. For each award:
1. Compute function returns candidates
2. **Single candidate:** assigned immediately
3. **Multiple tied candidates:** filter to the subset with the fewest awards received so far this game, then randomize within that subset

Tracked via `awardCounts` map (player name → count) incremented after each assignment. A player who legitimately earns multiple awards outright can sweep — the tie-break only applies when the compute function itself returns more than one candidate. Definition order is shuffled so that when more than 6 awards are eligible, which 6 get assigned is randomized.

Examples:
- A/B/C tie for an award. All have 0 existing awards → 1/3 chance each
- A/B/C tie. A has 2 awards, B and C have 1 each → B and C split 50/50, A excluded
- A/B/C tie. A has 2, B has 1, C has 0 → C wins 100% of the time

### Adding New Awards

1. Add entry to `awards.json`: `{ "id": "my-award", "name": "My Award", "compute": "myAward" }`
2. Add compute function to `awardComputers` in `feud.html`: `myAward(players) { ... }` — return array of tied candidates using `_topTied(eligible, valueFn)` or `_bottomTied(eligible, valueFn)` helpers
3. Add tooltip row to `tooltips.csv`: `award-my-award,evergreen,Flavor text,Description text`

### Tooltip Placement Override

Award `<li>` elements use `data-tip-placement="below"` to force tooltips below them. The `showTooltip()` function checks `target.dataset.tipPlacement` before running its automatic canvas-position logic. Valid values: `"above"`, `"below"`, `"left"`, `"right"`. This attribute works on any `data-tip` element.
