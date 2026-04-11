# Good Answer — Project Reference

## Project Overview
Family Feud-inspired game with original features and styling. Working title: **Good Answer**. Stack: vanilla HTML/CSS/JS, no frameworks.
- Main game file: `feud.html`
- Question bank: `master_question_bank.json` (active file, includes variants — see below)
- Pre-variants backup: `question_bank_pre-variants.json`
- Sound files alongside feud.html: `correct.mp3`, `wrong.mp3`, `goodanswer.mp3`, `opentheme.mp3`, `endtheme.mp3`, `analogbuttonclick.mp3`, `flick.wav` (tick SFX), `balbg.mp3` (background music, looping)

### Branch structure
- **`main`** — active development (formerly `viewport-redesign`)
- **`coyne-feud-classic`** — the original Coyne Feud family game night tool (formerly `main`). Finished product, not under active development. Do not merge between branches — they are effectively different games.

### File organization
- **`drafts/`** — design mockups, PSD source files, Excel layouts (git-ignored)
- **`outdated/`** — deprecated questions and assets (git-ignored)
- **`.gitignore`** excludes: `drafts/`, `outdated/`, `*.psd`, `*.xlsx`, `*.rtfd`, `.DS_Store`, `.variants_batch_id`
- Audio and image files used by the game **are tracked** in git — include them in commits

---

## Long-Term Development Strategy

The goal is a polished, distributable game app without migrating away from the current HTML/JS stack. Three additive phases:

1. **HTML/JS game (current)** — continue developing `feud.html` as a single-file vanilla build. Same-room play (one device, one host, players submit guesses at the keyboard) is largely functional. Balatro-inspired contained viewport, zone-based layout, animation-rich transitions (see "Viewport Redesign" section below). This phase is "done" when the game is feature-complete and visually polished for single-session use.

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
- **Turn subtext** (`#turn-subtext`) — `--fit-base: 1.5rem`, `maxChars: 18`, called in `updateTurn()` and the mid-animation swap in `animateTurnSwap()`.
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
- `#cat-label` — CRT "screen" header using the selected category's color. 80px tall, 3rem Bitcount font, `border-radius: 14px`, `border: 3px solid var(--cat-solid)`, `overflow: hidden`, `box-shadow: inset` for vignette. Three stacked layers: `::before` = animated white noise (SVG turbulence + `tv-static` keyframes, `hard-light` blend), `::after` = CRT scanlines (repeating-linear-gradient). Text entrance uses `tv-on` animation (inverse CRT power-on: dot → line → full), then switches to horizontal marquee scroll (`cat-label-marquee` keyframes, `translateX(-50%)` on doubled text with `padding-right` gap).
- `#question-box` — sits directly below cat-label. Contains `#category` (hidden — cat-label replaces it), `#question`, and `#questionActions`.

### Zone 2: Input (`#sq-zone-input`)
- Answer history tray at top (collapsed by default)
- `#input-area` — full width, no max-width. `#turn-header` is hidden (redundant with phase indicator). Input field and submit button are stacked vertically, each 100% width.

### Board Wrapper
- 70% width, centered via `margin: 0 auto`
- Attached directly under scoreboard (border-radius on bottom corners only)
- Slides in from above the canvas (behind the scoreboard) via `board-slide-in-top` animation
- `#game-board-zone` uses `justify-content: flex-start` + `overflow: hidden` to position board at top and clip the slide-in
- **Initial state**: has `class="offscreen"` in HTML so it starts above the canvas. Without this the wrapper briefly flashes on-screen at game start before sliding up to its hidden position.

### Canvas clipping lives at `#game-root`

`#game-root` has `overflow: hidden` and is the primary clipping boundary. Overflow settings down the sidebar chain:

- **`#sidebar-zone`** — `overflow: visible`, `min-width: 0`. Visible overflow is needed for category multiplier badges that hang off `.cat-row` edges. `min-width: 0` prevents flex expansion from nowrap marquee content.
- **`#sidebar-question-answer`** — `overflow: hidden`. Clips the cat-label marquee and question content.
- **`#sq-zone-content`** — `overflow: hidden`. Additional clipping layer.
- **`#cat-label`** — `overflow: hidden`. Clips its own horizontal marquee scroll.

`question-box`'s extrude animation uses its own `clip-path` for containment, not a parent `overflow`.

---

## Question Phase — Entry Animations (locked in)

The full sequence from "category picked → ready-to-play" state. Like the category phase entry section above, these are **committed and should not be changed without explicit instruction**.

### Order — strictly serial

Each step `await`s the previous animation's completion via `anim.done` before the next begins. Orchestrated in `pickCategory()` via `anim.sequence`:

1. **`#cat-label`** slides in from the left (`.offscreen-left` → `.slide-in-left`, `cat-label-slide-in-left` keyframes, 500ms)
2. **`#cat-label > span`** TV-on effect (`.tv-on` class, `tv-on` keyframes, 700ms) — dot → line → full screen. Uses `forwards` fill; 100% keyframe explicitly sets `opacity: 1`, `transform: scale(1,1)`, `filter: brightness(1) saturate(1)`.
2b. **Marquee starts** — JS removes `.tv-on`, sets inline `opacity: 1`, duplicates text into two inner `<span>` elements (each with `padding-right: 3em` for gap), adds `.marquee-scroll`. The marquee keyframes include `scale(1)` to prevent base `scale(0)` from reasserting. `:has(> span.marquee-scroll)` switches cat-label to `justify-content: flex-start`.
3. **`#question-box`** extrudes from under cat-label (`.hidden-behind` → `.reveal-drop`, `question-box-drop` keyframes, 450ms)
4. **`#question`** text streams in via `typewriter()` (default 30ms per char; cursor blinks during `.typing`, steady during `.typed`)
5. **`#sq-zone-input`** slides up from below the canvas (`.offscreen-below` → `.input-enter`, `input-slide-up` keyframes, 500ms)

After step 5, `#guess` is focused. The board wrapper's `slide-in` from above starts in parallel at the very beginning of this sequence (separate from `anim.sequence`) so the main game area fills in while the sidebar steps play out.

### The question-box extrude technique

`#question-box` must appear to emerge from cat-label's bottom edge — not slide down from above the canvas, and not wipe in place. The trick is combining two transforms that animate in parallel:

- **`transform: translateY(-100%)` → `translateY(0)`** — the box physically moves downward from its "hidden behind cat-label" position into its natural position. This provides the motion illusion.
- **`clip-path: inset(100% 0 0 0)` → `inset(0)`** — the top inset shrinks from 100% to 0, revealing the box from its own top edge downward. This prevents the translated box from ever being visible above cat-label during the slide.

Without the clip-path, the box peeks through the gap above cat-label (cat-label's 30px `margin-top`) and looks like a drop-in from the top. Without the translate, it's a pure wipe reveal with no motion. Both together = extrusion. Keyframes:

```css
@keyframes question-box-drop {
  from { transform: translateY(-100%); clip-path: inset(100% 0 0 0); }
  to   { transform: translateY(0);     clip-path: inset(0 0 0 0); }
}
```

### `typewriter()` helper

`typewriter(el, text, charMs = 30)` streams characters into `el` one at a time via `setTimeout`, returns a promise that resolves when done. Sequence:
- Clears `el.textContent`, removes `.typed`, adds `.typing` (opacity 1 + blinking `::after` cursor)
- Appends one char per `charMs` via `el.textContent = text.slice(0, i)`
- On completion, swaps `.typing` → `.typed` (opacity 1, no cursor)

**Call `fitByCharCount(el, max, finalText)` BEFORE clearing and streaming** — the fit scale needs to be computed against the full final text, not each intermediate substring, so the layout is stable while chars stream in.

Hidden-tab caveat: Chrome throttles `setTimeout` in background tabs, so the typewriter runs at ~1s/char in the Claude Preview hidden tab. Full visible runs need an in-browser check.

### Cleanup between rounds

`initRoundState()` resets all of these back to their off-canvas / hidden states so the sequence replays cleanly:
- `#question-box`: remove `.reveal-drop`, add `.hidden-behind`
- `#sq-zone-input`: remove `.input-enter`, add `.offscreen-below`
- `#question`: remove `.typing`, `.typed`
- `#cat-label`: the entire element is removed (the next round recreates it with `.offscreen-left` applied at insertion)

---

## Stat Change Chevrons

`#board-streak` and `#board-mult` (`.board-stat-value` elements) show directional chevron indicators when their values change:

- **`flashChevron(el, dir)`** — creates a `<span class="stat-chevron up|down">` with `▲` or `▼`, appends to the stat element, self-removes on `animationend`.
- **Up** (value increased): green `#4caf50`, starts at `bottom: 6px`, animates upward 45px.
- **Down** (value decreased): red `var(--red-text)`, starts at `top: 10px`, animates downward 45px.
- Both animations: 0.75s, 3 keyframe stops, opacity stays 1 until 99.9% then snaps to 0 (abrupt disappear, no fade).
- **`_prevStreak` / `_prevMultiplier`** track previous values for direction detection. Reset in `initRoundState()`.
- **`updateStreakValue()`** and **`updateMultValue()`** are separate async functions that each handle their own count-up + chevron and return a Promise. `updateStreakDisplay()` is a synchronous wrapper that calls both (used by the wrong-answer path where sequencing doesn't matter).
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

## Turn Swap Animation

`animateTurnSwap()` provides visual feedback when the active player changes after a guess:

- Captures old text, calls `updateTurn()` (which sets new text + all game state), then if text changed: restores old text, plays `turn-swap` animation (0.45s), swaps to new text at 160ms (peak of the jump).
- `@keyframes turn-swap`: pop up 14px → slam down 2px past center with 1.12× scale → small bounce → settle.
- **Not used** when 3 strikes trigger steal phase — plain `updateTurn()` runs instead to avoid the 160ms setTimeout racing with the steal-phase UI update.
- **Not used** when the correct answer reveals the final tile — round is ending, no next turn.
- `#turn-subtext` uses `fitByCharCount` with `maxChars: 18`.

---

## 3D Isometric Round-Select Buttons

Setup step 1 uses inline SVG buttons (`.rounds-svg`) for round count selection (2/4/6):

- **Structure**: isometric projected rhombus (top face `#C00000`, sides `#7A0000`) with `<text>` numbers sharing the same isometric `transform="matrix(0.866025 -0.5 0.866025 0.5 ...)"` as the face so they appear on the 3D surface.
- **Height states**: `setButtonDepressed(svg, bool)` modifies SVG attributes directly (transform matrix Y offset, side strip y/height, clip-path) — CSS transforms can't be used because clip-paths need to stay in sync. Raised = y=43, height=16. Depressed = y=51, height=8.
- **Glow**: CSS `filter: drop-shadow()` on `.btn-number` for hover/selected states. Dormant LED look (`fill: rgba(255,180,180,0.35)`) for non-active state.
- **Sound**: `analogbuttonclick.mp3` plays on selection via `playSound(sfxButtonClick)`.
- **Unique SVG IDs**: each button uses suffixed IDs (`clip-r2`/`clip-r4`/`clip-r6`) to avoid conflicts in shared DOM.
- **`selectRounds(n, el)`** uses `el.closest('.rounds-svg')` to handle clicks on child SVG elements.

---

## Setup Step Transitions

Three navigation flows between setup screens. All use `async`/`await` with `anim.play`/`anim.done` — no raw `animationend` listeners (see animation rule 8).

### `#selected-rounds` — round count display

Absolutely positioned on the left side of `#setup-step-2`. Contains:
- `.game-length` label ("GAME LENGTH") — Futura weight 100
- `.rounds-number` — large round count (Futura 700, 6rem, `#fba300`)
- `.rounds-label` — "ROUNDS" (Futura 700, 1.4rem, `#fba300`)
- `#setup-back-btn` — rewind icon (two overlapping `◀` glyphs with staggered `rw-grow` scale animation, 2s cycle, always running) + "BACK" label. All `#fba300`.

Fade-in: 2s. Fade-out: 1s. Both via `.fade-in` / `.fade-out` classes with `forwards` fill.

### Forward: Step 1 → Step 2 (`proceedToTeamSetup`)

| Step | Action | Duration |
|------|--------|----------|
| 1 | Step 1 flies out right (`setup-fly-out`) | 0.28s |
| 2 | Step 1 hidden, step 2 shown, flies in from left (`setup-fly-in`) | 0.30s |
| 3 | `#selected-rounds` fades in | 2s |

### Back: Step 2 → Step 1 (`backToRoundSelect`)

| Step | Action | Duration |
|------|--------|----------|
| 1 | `#selected-rounds` fades out | 1s |
| 2 | Step 2 flies out left (`setup-fly-out-left`) | 0.28s |
| 3 | Step 2 hidden, step 1 shown, flies in from right (`setup-fly-in-right`) | 0.30s |

Team names and player inputs are preserved across back/forward navigation (DOM state is untouched). Round selection SVG button state is also preserved.

### Game start: Step 2 → Game (`beginStartGameExit`)

Two parallel tracks, `startGame()` fires after both complete:

| Time | Track 1: beat sequence | Track 2: selected-rounds |
|------|----------------------|--------------------------|
| 0ms | Start Game btn slides down (0.14s) | Fade-out begins (1s) |
| 190ms | Player columns slide right (0.14s) | ...fading... |
| 380ms | Title slides up (0.14s) | ...fading... |
| 520ms | *Track 1 done* | ...fading... |
| 1000ms | *(waiting)* | *Track 2 done* |
| 1000ms | `startGame()` fires | |

`TIMING.setupExitBeatGap` (50ms) controls the pause between beats. Track 2 (1s fade-out) currently gates the transition.

### Dev mode dismiss

`activateDevMode()` calls `_dismissStartScreen()` — the same animated sequence as a normal start screen click (blob crossfade → logo TV-off → screen fade). No instant skip.

---

## Start Screen — CRT Effects and Dismiss Sequence

The `.crt-start-screen` class applies a composite TV effect to `#start-screen`:

- **`::before`** — animated white noise (same SVG turbulence as cat-label, `tv-static` keyframes, `overlay` blend at 0.12 opacity)
- **`::after`** — rolling scanlines (`scanline-roll` keyframes) + diagonal glare gradient (125deg white highlight)
- **Vignette** — `box-shadow: inset 0 0 120px rgba(0,0,0,0.5)`
- **Blob colors** — per-blob inline `fill` overrides set distinct colors on load; `--bg-blob-base` set to black. On dismiss, `_restoreStartBlobs()` crossfades each blob's inline fill to `BG_BLOB_DEFAULT` and transitions `--bg-blob-base` back. SVG blob elements have `transition: fill 1.5s ease`. After 1.6s, inline fills are cleared so blobs respond to future `--bg-blob-base` changes.

### Dismiss sequence (`_dismissStartScreen()`)
Shared by both normal click and dev mode:
1. **0ms**: blob crossfade starts (1.5s) + `h1.drop-out` animation (drops off bottom)
2. **1500ms**: logo gets `.tv-off` (`logo-tv-off` keyframes, 0.5s — adapted from `crt-power-off`)
3. **1800ms**: start screen fades out (`.dismissing`), setup slides in

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
