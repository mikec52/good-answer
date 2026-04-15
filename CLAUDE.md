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
- **`main`** — pre-Firebase local-only version, not under active development during multiplayer work
- **`multi`** — active multiplayer development (Firebase/Firestore integration)
- **`coyne-feud-classic`** — the original Coyne Feud family game night tool (formerly `main`). Finished product, not under active development. Do not merge between branches — they are effectively different games.

### Firebase project
- Project: `good-answer-game` (Firestore in `us-east1`, test-mode rules expire 2026-05-13)
- Services enabled: Firestore, Anonymous Auth, Google Auth
- Currently on **Spark (free) plan** with client-authoritative architecture. Mike is willing to upgrade to **Blaze (pay-as-you-go)** if Cloud Functions (server-authoritative) proves to be the better path for the prototype. Migration from client-authoritative to Cloud Functions is straightforward — same Firestore schema, game logic just moves from the active player's browser to a server function.

### Hosting & Deployment
- **GitHub Pages** serves the game at **https://mikec52.github.io/good-answer/feud.html**
- Source repo: `mikec52/good-answer` (public), `main` branch → auto-deploys on push
- **Deploy workflow**: `git push origin main` = live in ~60 seconds. No build step, no config files.
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

2. **Server layer — Remote Play (ACTIVE)** — add a real-time backend so multiple devices share game state. Implementation: Firebase/Firestore with client-authoritative architecture. **Phase 2A (shared state) and Phase 2B (authenticated players) are being built together on the `multi` branch.** See "Multiplayer Implementation" section below for current status and architecture details.

3. **Electron / Capacitor shell (stretch goal)** — wrap the finished game in a native app shell for distribution. Platform priority: Mac → iOS → Windows → Android → Steam. Note: Electron covers Mac/Windows/Linux (desktop only); iOS and Android require Capacitor instead. Game code inside is unchanged either way.

**Distribution phases:**
- **Phase 1 (current goal)**: Owner-hosted. Mike is always the session host; others join as players at a shared URL.
- **Phase 2 (future)**: Self-serve hosting. Other users can independently spin up and host their own game sessions.

**What this avoids:** No migration to Unity or Phaser. The current stack is the final stack. Phaser would only be reconsidered if animation/visual polish becomes a hard blocker — not anticipated.

---

## Multiplayer Implementation (multi branch)

Active development on the `multi` branch. Firebase/Firestore powers real-time state sync. The full implementation plan is at `.claude/plans/buzzing-toasting-feather.md`.

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

1. **Host submit button stays clickable during teammate's turn** — after host's scoring animation, `updateRoleUI` should disable the button but timing may not always work. Non-host side is confirmed working. Needs more testing.
2. **Return-to-lobby turn desync (intermittent)** — one test showed host thinking it was player 4's turn while non-hosts showed player 1. Could not reproduce on subsequent tests. Debug logging added to `category-select` and `play-again` phase transitions to capture state if it recurs.
3. **Awards accuracy** — `matchLog` player/team mapping may have issues. With host-authoritative model, host should compute awards and sync the results.
4. **Speed boost bug** — spacebar fast-forward persists after round-ending steal. `deactivateSpeedBoost()` fires too early in the steal path.
5. **Safari visual polish** — content-tv clipping issues. Deferring Safari pass until Chrome build is stable.
6. **Lobby UX (future)** — Captain role for Blue team (first Blue player chronologically), team name editing in lobby, team color selection.
7. **No disconnect handling** — host leaving mid-game strands all players. Lobby back button handles pre-game disconnect, but mid-game disconnects are unhandled.
8. **Debug logging cleanup** — diagnostic `console.log` statements in `category-select` transition, `play-again` transition, and `host syncing category-select` should be removed once multiplayer flows are stable.

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

### What Was Fixed (April 15 session)

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
- **`_lobbyStartingTeam`** — host-determined starting team, passed through Firestore so all clients agree.
- **`_syncedCategoryPicks`** — `{ picks, hasSurvey, multipliers, questions }` object synced by the host. Includes pre-selected questions per category.
- **`_preSelectedQuestions`** — `{ category: { question, answers, _poolIdx } }` local cache. Host generates at category time; non-host clients receive via synced `categoryPicks.questions`.
- **`_prevSnapshot`** — last Firestore snapshot data, used by `reconcileLocalState` for diffing.
- **`_readyPlayersMap`** — `{ uid: true }` map tracking ready-up clicks. `_readyCountdownEnd` / `_readyCountdownInterval` for the 10-second timer.

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

### Tie Resolution — Two-Pass System

**Pass 1** — iterate shuffled award definitions. If a compute function returns exactly 1 candidate, assign immediately and add the player to the `awarded` set. If multiple candidates (tie), defer.

**Pass 2** — for each deferred tie:
1. Prefer candidates NOT already in the `awarded` set (spread awards across players)
2. If all tied candidates already have awards (or none do), pick randomly

This ensures maximum award diversity across players.

### Adding New Awards

1. Add entry to `awards.json`: `{ "id": "my-award", "name": "My Award", "compute": "myAward" }`
2. Add compute function to `awardComputers` in `feud.html`: `myAward(players) { ... }` — return array of tied candidates using `_topTied(eligible, valueFn)` or `_bottomTied(eligible, valueFn)` helpers
3. Add tooltip row to `tooltips.csv`: `award-my-award,evergreen,Flavor text,Description text`

### Tooltip Placement Override

Award `<li>` elements use `data-tip-placement="below"` to force tooltips below them. The `showTooltip()` function checks `target.dataset.tipPlacement` before running its automatic canvas-position logic. Valid values: `"above"`, `"below"`, `"left"`, `"right"`. This attribute works on any `data-tip` element.
