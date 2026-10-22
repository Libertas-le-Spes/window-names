# Security review: window-names

This describes the repo at commit `f5eca8e1d9a73fd1215b7673b557fa952d693d50` on 2026-10-22. Some
of what follows is a proposal, not something already done: the findings are real, but the fixes
and the ways to seal them are planned work, not merged code. Like any document about a project
that keeps changing, this will drift from the code. Whoever fixes a finding updates this file in
the same change, so the two never disagree for long.

## What window-names is, and why its inputs are dangerous

window-names watches the open windows and writes a readable name into each one's title bar, so a
row of near-identical terminals and IDE windows can be told apart. To do that it reads two things
about every window and feeds them back out: the window's **class** (roughly, which program it is)
and the window's **title**.

Both are set by the program that owns the window, and a program can set them to anything. A web
page sets the browser tab's title to whatever its HTML says; a terminal rewrites its own title at
every shell prompt; any native program can call the Wayland or X11 "set my title" request with any
bytes it likes. So every title and class this tool handles is **attacker-controlled input**. The
question this review asks of every line is: when a title is chosen by someone hostile, what can it
do on its way through window-names and back onto the screen?

The most dangerous path is Hyprland. To set a title bar, window-names builds a line of **Lua code**
and hands it to the compositor to run. If an attacker-chosen title could break out of the string it
is placed in, a web page's tab title would be running code inside the window manager. That did not
turn out to be reachable today (see F1), but it is the thing the whole design leans on.

## Verdict

No remotely-triggered code execution was found, and nothing here is a ready-to-run exploit, so this
review was completed and opened as a normal pull request rather than held back.

The barrier that matters most — the hand-written escaping that stops a window title from becoming
Lua code in the compositor — **holds today**. That was tested, not assumed: a batch of hostile
made-up titles was pushed through the real escaper and run under all three Lua engines on this
machine, and every one arrived as inert text (F1). 

What is weaker is everything around that barrier. The long-running loop that keeps the bars updated
has no error handling at all, so a single window whose title is not valid UTF-8 stops every title
bar updating until the next login (F2). Name files dropped by other tools — a documented, supported
feature — are read with no guard, so one bad file hangs the whole tool forever (F3). On Sway, the
check that decides whether to escape markup reads only part of the config, so on a common setup an
attacker's title can inject display markup into the bar (F4). None of these is code execution; all
of them are a local program, or a web page, being able to stop or deface the tool.

The single most valuable hardening is structural: stop generating Lua at all (F1's seal), so the
barrier cannot be broken by a future edit. The two most valuable fixes are making the loop survive
bad input (F2) and treating name files as hostile (F3).

## Findings

| id | severity | title | location |
|---|---|---|---|
| F1 | Medium | A window title becomes Lua code in the compositor; only hand-written escaping stops injection | `window_names/desktops/hyprland.py:38` |
| F2 | Medium | One bad title stops every title bar until next login; the loop has no error handling | `window_names/service.py:12`, `window_names/desktops/hyprland.py:57` |
| F3 | Medium | Name files from other tools are read unguarded; a pipe hangs the tool, a huge file floods it | `window_names/given_names.py:10` |
| F4 | Medium | Sway markup check reads only the main config file; an attacker title can inject pango markup | `window_names/desktops/sway.py:18` |
| F5 | Low | The name folder is world-readable, exposing which windows have hand-given names | `window_names/given_names.py:17` |
| F6 | Info | No CI: tests never run automatically, and no pinned, least-privilege workflow exists | repository (no `.github/`) |

Severity reflects how bad the outcome is and who can cause it, ranked by safety and nothing else.
Code execution in the compositor sits behind F1, which is why it leads even though it is not
exploitable today.

---

### F1 — A window title becomes Lua code in the compositor

**What it is.** To put text in a Hyprland title bar, window-names asks the compositor to run a line
of Lua. For a title like `Rider — notes`, the line it sends is
`eval hl.plugin.hyprbars.set_title("address:0x1a2b", "Rider — notes")`. The title is pasted straight
into the middle of that Lua string literal, between the quotes.

**The point.** The title is chosen by the window's program — for an ordinary browser window, that is
the web page. If a title could contain a `"` that closes the string early, the rest of the title
would be read as Lua and run inside the window manager. That is the difference between "a web page
named a tab" and "a web page ran code in your compositor."

**What stops it today, and does it hold.** Before building the line, the code rewrites every `"`,
every `\`, and every control byte as a Lua numeric escape (`\034` for `"`, and so on), at
`window_names/desktops/hyprland.py:38`. To check this is not just plausible but true, a set of
hostile made-up titles was run through the real `_set_title` and the resulting Lua was executed
under `lua5.4`, `lua` and `luajit`, with a `marker()` function planted that screams if it is ever
called:

| Made-up title fed in | `marker()` ran? | Title seen by `set_title` |
|---|---|---|
| `quote " then ) ; marker()` | no | the text, unchanged |
| `ends with backslash \` | no | the text, unchanged |
| `new`⏎`line` (embedded newline) | no | the text, unchanged |
| `nul‹00›byte` (embedded NUL) | no | the text, unchanged |

Every title arrived as inert text; the injection attempt never executed. So **there is no working
injection here now.** This finding is about how thin and how load-bearing that one line is.

**What happens if left alone.** Nothing, until someone edits that line — adds a format, trims an
"unneeded" branch, swaps the comprehension for something read more easily. The escaper is written by
hand with no type or structure forcing it to be complete, and the one thing it defends against is
arbitrary code execution in the compositor, reachable from a web page's title. A silent mistake
there is not a cosmetic bug; it is the whole castle.

**Fix options.**

- **(a) Keep generating Lua, lean harder on the escaper.** Leave the mechanism, add tests that pin
  it (below). *Fails to stop:* a future refactor that is still "green" against a finite set of test
  strings but wrong on an input nobody thought of. The barrier stays a thing one edit can break.
- **(b) Stop generating Lua. Pass the title as data, not code.** The title bars come from a fork of
  hyprbars that this project controls (the `set-title` change, offered upstream in hyprland-plugins
  PR #716). Expose the title-setting as a hyprctl dispatcher or keyword that takes the address and
  the title as plain arguments, so window-names sends the title as an argument string the compositor
  never parses as Lua. *Fails to stop:* an injection into *that* argument format instead — but that
  format is a flat `key value` line, far smaller and easier to get right than embedding in a Lua
  string, and the payoff is that no amount of title content is ever evaluated as code.

**Recommendation: (b), with (a)'s tests kept as a second layer.** The safe design is the one where
the wrong outcome is impossible, not merely currently avoided. Moving the title off the Lua `eval`
path means an attacker title can never be code, whatever a future edit does — it fails closed by
construction. Because the fork is ours, this is a change we can make. Until the fork exposes that
argument API, (a)'s tests are the stopgap; they are worth keeping even after (b) lands, as the
second layer that catches a regression in whatever escaping the argument format still needs.

**How to seal it.**

- A round-trip property test: for a large pile of random and adversarial made-up titles, assert the
  compositor's `set_title` receives the title **byte-for-byte**, and that a planted sentinel
  function is never called. (The review's throwaway version of this is the table above; make it a
  committed test.)
- Once (b) lands, an architecture test — a test that greps the desktop code — asserting the string
  `eval ` is never built from a window title again, so the Lua path cannot quietly return.

---

### F2 — One bad title stops every title bar until next login

**What it is.** The `run` loop asks the compositor for the window list, decodes the reply, and
updates every bar, over and over (`window_names/service.py:12`). Reading the reply ends in
`.decode()` at `window_names/desktops/hyprland.py:57`, which demands valid UTF-8.

**The point.** Titles are supposed to be UTF-8, but "supposed to" is not "enforced." A native
program can set a title containing bytes that are not valid UTF-8. When that title comes back in the
window list, the decode throws, and because the loop catches nothing, the exception travels all the
way up and the process exits.

**What happens if left alone.** This was run against a made-up window list with one title carrying a
single invalid byte:

| Window list fed in | Result |
|---|---|
| a title that is valid UTF-8 | refreshed fine |
| a title with one invalid UTF-8 byte | `UnicodeDecodeError`, the service stops |

In practice: one unlucky or malicious program opens a window, and from that moment **every** window
on the desktop stops getting its name — all the bars freeze at whatever they last said — until the
user logs out and back in. The person sees a tool that silently died and cannot tell why. And the
decode is only the example; any transient hiccup (a socket reset, a window that vanishes mid-refresh
and malforms a reply) does the same, because the loop protects against none of it.

**Fix options.**

- **(a) Decode leniently.** Replace undecodable bytes instead of throwing. *Fails to stop:* every
  other error — socket drops, malformed JSON, a kind that raises on a weird title. The loop is still
  one exception away from death.
- **(b) Make the loop survive a bad pass.** Wrap one refresh so a failure is logged and the loop
  sleeps and tries again, never exiting on a per-refresh error. *Fails to stop:* a genuinely
  persistent fault becomes a tight error-log loop rather than a clean stop — acceptable, and
  visible, where a dead tool is neither.
- **(c) Both, plus leniency at the one window that is bad** so a single poison title degrades to a
  replacement character on that one bar and leaves its neighbours correct.

**Recommendation: (c).** For a tool whose whole value is staying up, the safe failure is to keep
running and lose as little as possible, not to stop. Leniency alone (a) still lets any other error
kill the loop; a surviving loop alone (b) throws away a whole refresh for one bad window. Together
they fail open on availability, which is the right direction here: a slightly wrong name beats no
names at all, and a logged, surviving loop beats a silent death.

**How to seal it.** A test that drives `refresh` with a made-up window list containing one invalid
UTF-8 title and asserts the other windows are still named and the call returns normally; and a test
that makes `windows()` raise once and asserts `run`'s loop keeps going.

---

### F3 — Name files from other tools are read unguarded

**What it is.** Other tools can name a window by dropping a file into `~/.local/state/window-names`,
named after the window id, containing the name. This is a documented, supported feature (the README
describes it; Hiru Tsatsi uses it). window-names reads each such file with
`(folder / window_id).read_text()` at `window_names/given_names.py:10`.

**The point.** That folder is writable by anything the user runs. The feature trusts whatever is
there to be a small regular file with a line of text in it. Nothing checks that it is.

**What happens if left alone.** Two made-up files were placed in the folder and read:

| File dropped in | Result |
|---|---|
| a regular file with `Made-up name` | read fine |
| a named pipe (FIFO) | the read **blocks forever** |

A pipe makes `read_text` wait for a writer that never comes. Because this read happens for every
window on every refresh, one such file hangs the entire tool indefinitely — every bar stops, with no
error and no exit, harder to diagnose than a clean crash. A second shape has the same root cause: a
very large file (a tool gone wrong, or deliberate) is read whole into memory and then pushed toward
the compositor as a "name." The fix is the same for both: read these files as hostile input.

**Fix options.**

- **(a) Open without blocking and require a regular file.** Open with `O_NONBLOCK` and `fstat` the
  handle; if it is not a regular file, treat it as no name (fall back to the computed default).
  *Fails to stop:* a huge regular file.
- **(b) Add a size cap.** Read at most a kilobyte or two; ignore anything longer. *Fails to stop:* a
  pipe, on its own.
- **(c) Both, and fail closed:** anything not a small regular file yields no name, not an error and
  not a hang.

**Recommendation: (c).** Each option covers the other's gap, so layer them: non-blocking open with a
regular-file check stops the pipe, a size cap stops the flood, and when either check cannot be
satisfied the window simply gets its computed default name. Failing closed to "no custom name" keeps
the tool alive and the window still readable, which is the safe outcome.

Note this guards the **read** side only, which is what window-names owns. A tool that writes a name
file still chooses its own filename; this review does not change that side.

**How to seal it.** Tests that put a FIFO and an oversized file in a made-up folder and assert
`name_of` returns `None` promptly (no hang), with made-up names and ids throughout.

---

### F4 — Sway markup check reads only the main config file

**What it is.** On Sway and i3, window-names sets a bar by giving the compositor a `title_format`.
If the bar font is a **pango** font, that format string is interpreted as pango markup, so `<b>` is
bold and `&` starts an entity — which means an attacker title must have its markup escaped before it
goes in. window-names decides whether to escape by asking Sway for its config and searching it for a
`font pango:` line (`window_names/desktops/sway.py:18`).

**The point.** Sway's "give me the config" reply contains only the **main** config file's text, not
the contents of files pulled in with `include`. Splitting config across `~/.config/sway/config.d/`
is a common setup — window-names' own installer adds itself that way. If the user's `font pango:`
line lives in an included file, the search does not see it, `reads_markup()` returns false, and the
escaping is skipped while pango is actually on.

**What happens if left alone.** With escaping skipped, a title's markup passes straight through:

| Made-up title | markup detected (escaped) | markup missed (raw) |
|---|---|---|
| `a & <b> c` | `a &amp; &lt;b&gt; c` | `a & <b> c` |

The raw form reaches pango, which renders `<b>` as formatting instead of text. A hostile title — an
ordinary browser window's title is set by the web page — can then style, resize, recolour or blank
the title bar, forging or hiding the very name the tool exists to show. It is display spoofing, not
code execution, and this whole Sway path is marked "not tested on a real desktop" in the README, so
the finding is real but unproven in the wild.

**Fix options.**

- **(a) Detect markup more thoroughly.** Resolve includes and search them too. *Fails to stop:* the
  next config shape the parser gets wrong; detection is a guessing game with an attacker-facing
  downside when it loses.
- **(b) Fail closed: always escape.** Drop the detection and always escape markup. When the font is
  *not* pango, an escaped `&` shows as the literal `&amp;` — a cosmetic wart on a title that
  contained markup characters, and nothing worse. *Fails to stop:* nothing security-relevant; its
  only cost is that cosmetic case.

**Recommendation: (b).** Rank by safety: the detection exists only to avoid a cosmetic artefact when
markup is off, and it pays for that with a markup-injection hole whenever it guesses wrong. Always
escaping removes the hole entirely and fails closed — the worst case becomes an over-escaped
character, never an under-escaped one. Give up the cosmetic nicety for the safe default.

**How to seal it.** Once escaping is unconditional, a test asserting the escaped form is produced
regardless of what the config says, so the markup branch cannot come back; and keep a config-with-an-
include case in the tests to document why detection was dropped.

---

### F5 — The name folder is world-readable

**What it is.** When window-names first writes a name, it creates `~/.local/state/window-names-by-hand`
with the process umask, which on this machine leaves it mode 755 (`window_names/given_names.py:17`).
The name files inside are mode 600, so other local users cannot read a name's text — but they can
list the folder and see which window ids have hand-given names.

**The point and what happens if left alone.** On a single-user machine this is nothing. On a shared
host, another user learns that certain windows were named by hand and how many — a thin metadata
leak, no contents. It lands as a small privacy erosion, not a break-in.

**Fix and seal.** Create the folder mode 700. Seal with a test asserting the created folder is not
group- or other-accessible. Low priority; do it when F3 is already touching this file.

---

### F6 — No CI

**What it is.** There is no `.github/` and no workflow. The test suite (33 tests, all passing here)
runs only when someone remembers to run it, and the seals proposed above are only as good as a
check that actually runs them.

**The point.** Every fix above ends in "add a test." Those tests defend nothing if a later change
can merge red. And when a workflow is added, it should be added safely: least-privilege token,
actions pinned to a commit, and no `pull_request_target` (which would run with repo secrets against
a fork's code).

**Fix and seal.** Add one workflow that runs the tests on push and pull request, with
`permissions: contents: read`, third-party actions pinned by full commit SHA, and the default
`pull_request` trigger. That workflow is itself the seal for F1–F5: it is what makes their tests
binding.

---

## What was checked and found sound

These were examined and did not yield a finding. They are listed so the next reviewer need not
re-derive them, and so a change that breaks one is noticed.

- **The Lua escaper's correctness (F1's barrier), today.** Proven by round-trip under all three Lua
  engines, as tabled in F1. Sound now; F1 is about its fragility, not a current defect.
- **Hyprland event socket is not trusted.** The second socket is read only as a wake-up and its
  bytes are discarded (`window_names/desktops/hyprland.py:42`); no decision is made from event
  content, so a forged event cannot steer anything.
- **X11 titles are set through argv, not a shell.** `xprop` is invoked as an argument list, never a
  shell string (`window_names/desktops/xprop.py:38`), so a title cannot inject a shell command. The
  window id handed to `xprop` is constrained to `0x[0-9a-f]+` by the regex that produced it.
- **The rename prompt is invoked through argv, not a shell.** `omarchy-menu-input`, `zenity` and
  `kdialog` are run as argument lists (`window_names/prompts/command_prompt.py:13`); the question
  text is a fixed string.
- **Window ids never reach a file path or a socket string from attacker data.** Every id used as a
  filename or inside the Lua string comes from the compositor's own addressing (`0x…`, or an integer
  container id), not from a title or class.
- **Hand-given names are written atomically.** `give` writes a temp file and `os.replace`s it into
  place (`window_names/given_names.py:16`), and the temp file is created mode 600, so a reader never
  sees a half-written name and other users never read a name's text. (Only the folder mode is weak —
  F5.)
- **Regular-expression cost is linear (no ReDoS).** Every pattern — the Claude status-mark strip, the
  web-app class match, the xprop quote/number scanners, the Sway pango-font search — was timed on
  100,000-character adversarial made-up inputs and each finished in under 4 ms. No catastrophic
  backtracking.

## Ordered plan

Small, independently shippable steps, each safe to merge on its own, ordered so the highest-safety
work lands first and so the check that makes the seals binding exists early.

1. **Add the CI workflow (F6).** Least-privilege token, SHA-pinned actions, `pull_request` trigger.
   Nothing below is truly sealed until this runs, so it goes first.
2. **Make the service loop survive a bad pass, and decode leniently (F2).** One hostile title stops
   killing every bar. Ship with its tests.
3. **Treat name files as hostile: non-blocking open, regular-file check, size cap, fail closed (F3).**
   Ship with its FIFO and oversized-file tests.
4. **Always escape markup on Sway/i3; drop the include-blind detection (F4).** Ship with its test.
5. **Pin the Lua escaper with a round-trip property test (F1, stopgap).** The second layer, landed
   before the structural change so the change has a safety net.
6. **Move the Hyprland title off the Lua `eval` path onto a plain-argument API in the fork (F1,
   structural).** The injection class becomes impossible by construction. Add the architecture test
   that forbids building `eval ` from a title.
7. **Create the name folder mode 700 (F5).** Small; fold in while F3 is in the same file.

## Sources

- Hyprland IPC, synchronous request socket and event line format — https://wiki.hypr.land/0.55.0/IPC/
- Hyprland control-socket request handling (`eval`, batch, flag parsing, 1023-byte read loop), v0.56.2 — https://github.com/hyprwm/Hyprland/blob/v0.56.2/src/debug/HyprCtl.cpp
- Hyprland JSON string escaping helper, v0.56.2 — https://github.com/hyprwm/Hyprland/blob/v0.56.2/src/helpers/MiscFunctions.cpp
- hyprbars `set_title`, offered upstream — https://github.com/hyprwm/hyprland-plugins/pull/716
- Sway IPC `GET_CONFIG` returns only the main config file's text (`read_config`, `current_config`) — https://github.com/swaywm/sway/blob/master/sway/config.c
- Sway command splitting that honours quotes and backslashes (`argsep`) — https://github.com/swaywm/sway/blob/master/common/stringop.c
- Sway pango markup is enabled by a `font pango:` line — https://github.com/swaywm/sway/blob/master/sway/commands/font.c
- Pango markup injection discussed as a security class — https://discourse.gnome.org/t/is-pango-markup-injection-a-security-vulnerability/2038
- Terminal title-reporting turned into command injection (CVE-2003-0063), the archetype for "a title is attacker input" — https://security-tracker.debian.org/tracker/CVE-2003-0063
- OWASP Injection Prevention Cheat Sheet — https://cheatsheetseries.owasp.org/cheatsheets/Injection_Prevention_Cheat_Sheet.html
- OWASP OS Command Injection Defense Cheat Sheet — https://cheatsheetseries.owasp.org/cheatsheets/OS_Command_Injection_Defense_Cheat_Sheet.html
- CWE-77 Command Injection — https://cwe.mitre.org/data/definitions/77.html
- CWE-78 OS Command Injection — https://cwe.mitre.org/data/definitions/78.html
- CWE-1333 Inefficient Regular Expression Complexity (ReDoS) — https://cwe.mitre.org/data/definitions/1333.html
- CWE-59 Link Following (symlink/TOCTOU) — https://cwe.mitre.org/data/definitions/59.html
