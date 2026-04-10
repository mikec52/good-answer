# Coyne Feud — Project Reference

## Project Overview
Single-file Family Feud-style game. Stack: vanilla HTML/CSS/JS, no frameworks.
- Main game file: `feud.html`
- Question bank: `master_question_bank.json` (active file, includes variants — see below)
- Pre-variants backup: `question_bank_pre-variants.json`
- Sound files alongside feud.html: `correct.mp3`, `wrong.mp3`, `goodanswer.mp3`, `opentheme.mp3`, `endtheme.mp3`

---

## Long-Term Development Strategy

The goal is a polished, distributable game app without migrating away from the current HTML/JS stack. Three additive phases:

1. **HTML/JS game (current)** — continue developing `feud.html` as a single-file vanilla build. Same-room play (one device, one host, players submit guesses at the keyboard) is largely functional. Currently undergoing a major **UI overhaul** on the `viewport-redesign` branch — Balatro-inspired contained viewport, zone-based layout, animation-rich transitions (see "Viewport Redesign" section below). This phase is "done" when the game is feature-complete and visually polished for single-session use.

2. **Server layer — Remote Play** — add a real-time backend so multiple devices share game state. Preferred implementation: Firebase (managed, no self-hosted server). Two sub-phases:
   - **Phase A — Shared state, no authentication**: All users connect to a unique game URL and see/interact with the same instance. The game does not track individual identity — players coordinate externally (e.g. over a Discord call). Any connected user can submit a guess at any time.
   - **Phase B — Authenticated players**: Users are identified to the server (logged in or session-assigned). UI becomes player-specific — e.g. only the active player sees the guess input field. Enables a self-contained, immersive experience without relying on a side channel.

3. **Electron / Capacitor shell (stretch goal)** — wrap the finished game in a native app shell for distribution. Platform priority: Mac → iOS → Windows → Android → Steam. Note: Electron covers Mac/Windows/Linux (desktop only); iOS and Android require Capacitor instead. Game code inside is unchanged either way.

**Distribution phases:**
- **Phase 1 (current goal)**: Owner-hosted. Mike is always the session host; others join as players at a shared URL.
- **Phase 2 (future)**: Self-serve hosting. Other users can independently spin up and host their own game sessions.

**What this avoids:** No migration to Unity or Phaser. The current stack is the final stack. Phaser would only be reconsidered if animation/visual polish becomes a hard blocker — not anticipated.

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

## Viewport Redesign (branch: `viewport-redesign`)

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
        #question-box, #questionActions, #input-area, #message, #history
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

1. **Start screen** — logo centered at 40% width, "Click anywhere to start", CRT overlay fades out on click
2. **Setup step 1** — game mode selection (target score vs. rounds). "Proceed to Team Setup" button.
3. **Setup step 2** — team/player name entry. Flies in from left after step 1 flies right.
4. **Game start exit** — 3-beat animation: Start button slides down → player columns slide right → title slides up → game loads
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

CSS variables in `:root` — used for 3D category buttons, potentially other UI elements later:

```css
--cat-science:    #3a8fd4;   /* blue */
--cat-geography:  #2d8659;   /* green */
--cat-popculture: #c44d8a;   /* pink */
--cat-survey:     #d4852a;   /* orange */
--cat-sports:     #c8a820;   /* yellow — uses black text */
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

- **`#222` frame** — the background color of the wrapper. All labels (column headers, stat labels, team names, "Turn Order", "Round") sit directly on this frame.
- **`#111` value fields** — data cells (player lists, round info, stat values, answer tiles) have `background: #111` with `border-radius: 6px`.
- **Team-colored exception** — `.team-points` fields use `var(--red-bg)` / `var(--blue-bg)` instead of `#111`.
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
function fitByCharCount(el, maxChars, text) {
  if (!el) return;
  const len = (text ?? el.textContent).trim().length;
  const scale = len <= maxChars ? 1 : maxChars / len;
  el.style.setProperty("--fit-scale", scale);
}
```

Call it immediately after assigning `textContent` — no deferral, no rAF, no observers.

### Where it's currently applied

- **Team labels** (`.team-score-box .team-label h4`) — `--fit-base: 1.5rem`, `maxChars: 10`, called in `startGame()` at the `textContent` assignment.
- **Question text** (`#question`) — `--fit-base: 1.8rem`, `maxChars: 45`, called in the question-render block. `#question-box` has `max-height: 180px; overflow: hidden` as a safety net.
- **NOT the players list** — char-count wasn't the right tool there (see marquee below).

### Caveats and tuning

- Char count is a width *proxy*. Works cleanly for monospace-ish fonts (Bitcount Single). For proportional fonts it's "close enough for a fallback" — `maxChars` is tuned by eye.
- **Not for multi-line wrapping text.** Char count doesn't know about line breaks. If the container can grow taller (wrapping), use a different approach.
- **Tune `maxChars` by watching real content.** Questions that still look cramped at scale 1 → lower `maxChars`. Too many things shrinking unnecessarily → raise it.
- **Grid cells must have `minmax(0, 1fr)`**, not bare `1fr`. Bare `1fr` tracks expand to fit content, so an overflowing child can blow out the whole layout *before* the fit helper sees any overflow. The scoreboard and any similar grid layout using fit-shrink children need explicit `minmax(0, 1fr)`.

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
- **"Advanced question options"** — question admin links (get new question, flag for removal, fact check, copy answers) are collapsed under a `<details>` element during a round. This element must be explicitly closed when a new question loads (`removeAttribute("open")`).
- **End-of-round state** repurposes the turn-input-box: header shows the round result message, body shows Reveal All / Next Round buttons. Score edits live in a separate `<details>` element outside the box.
- **Score edits** use a `<details>` element labeled "Score edits needed?" to keep them collapsed by default.

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

- `setPhase()` handles the outgoing span's exit animation and the incoming span's entry animation. In normal mode the swap is immediate; in `knock` mode there's a 120ms overlap window (`TIMING.phaseKnockOverlap`) before `data-phase` flips, so both spans render simultaneously and visually collide.
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
- `#cat-label` — flat colored rectangle header using the selected category's color. 80px tall, 2.5rem Bitcount font, no border-radius. Text has a "pop-through" entrance animation (scale from 0 → overshoot → settle).
- `#question-box` — sits directly below cat-label (no top border-radius, flush join). Contains `#category` (hidden — cat-label replaces it), `#question`, and `#questionActions`.

### Zone 2: Input (`#sq-zone-input`)
- Answer history tray at top (collapsed by default)
- `#input-area` — full width, no max-width. `#turn-header` is hidden (redundant with phase indicator). Input field and submit button are stacked vertically, each 100% width.

### Board Wrapper
- 70% width, centered via `margin: 0 auto`
- Attached directly under scoreboard (border-radius on bottom corners only)
- Slides in from above the canvas (behind the scoreboard) via `board-slide-in-top` animation
- `#game-board-zone` uses `justify-content: flex-start` + `overflow: hidden` to position board at top and clip the slide-in
- **Initial state**: has `class="offscreen"` in HTML so it starts above the canvas. Without this the wrapper briefly flashes on-screen at game start before sliding up to its hidden position.

---

## Category Phase — Entry Animations (locked in)

The full sequence from "Start Game" click to a usable category-select screen. These animations are **committed and should not be changed without explicit instruction** — they were tuned through multiple rounds of iteration.

### Sequence overview (all fire in parallel from `startGame`)

All these run via the `anim` helper; timing is controlled by `TIMING` constants and CSS animation durations.

1. **Phase indicator container** slides down from above (`phase-slide-in`, 0.45s)
2. **Scoreboard** slides down from above (`scoreboard-slide-down`, 0.5s) — both elements start with `class="offscreen"` in HTML and are swapped to `.slide-in` via `requestAnimationFrame` so the animation replays cleanly on subsequent games
3. **Category pills area** — no container animation (would break `mix-blend-mode` background). Children stagger in individually instead.
4. **Cat-rows** slide in from the left staggered via `anim.stagger(rows, { gap: TIMING.catRowStagger })` — each row's CSS `cat-slide-in` animation (0.4s) fires after its inline `animation-delay`
5. **Coin badges** (category multiplier tokens) slide in after the last cat-row settles, 1s apart, via `anim.setDelay` on each badge
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
`initRoundState()` removes stale elements at the start of each new round: `#cat-label`, `.cat-row` remnants in `#sq-zone-content`, `.cat-mult-badge` in `.board-footer`. Re-shows `#category` element. Removes entrance animation classes so they replay next round. The `.selected-glow` and `.crt-off` classes are naturally cleared because the entire pills area's `innerHTML` is rebuilt each round.
