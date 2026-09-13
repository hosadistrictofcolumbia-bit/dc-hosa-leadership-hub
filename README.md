# DC HOSA Leadership Hub

A leadership development product for every role in DC HOSA. Competition readiness is a byproduct
of it, never its organizing principle — competitive event preparation belongs to the Study Hub.

School year 2026–2027. Live at **leadership.dchosa.org**.

---

## Structure

Navigation is by **capability domain**. Progression is by **level**. Audience is a filter, not a page.

| Domain | Develops |
|---|---|
| Self | Knowing your strengths, setting goals that survive contact, staying steady |
| Voice | Being understood — speaking, presenting, writing, advocating |
| Team | Working with people, and getting a group to function |
| Governance | Running meetings, and understanding how the organization works |
| Community | Health literacy, service, and acting on what a neighbourhood needs |

| Level | Question it answers |
|---|---|
| Lead Yourself | What do I do? |
| Lead a Team | How do I get a group to do it? |
| Lead Beyond | How do I change something outside this room? |

Advisors and state staff are not a fourth level. They are a **coaching layer**: every card carries a
coach note. The deep, credential-bearing advisor programme lives at `advisors.dchosa.org` and the
Hub links to it rather than competing with it.

---

## The rule that matters

**`data/hub.json` is the only place a card is stored.** `index.html`, the five domain pages and
`tools.html` are generated from it.

```bash
python3 build/build.py
```

**Never hand-edit the generated HTML.** Edit the data, rebuild, commit both. No dependencies beyond
the Python 3 standard library. Same convention as `dc-hosa-advisor-tools`, deliberately.

### Card schema

Every card is the same object: `id` · `title` · `domain` · `level` · `pillar` · `minutes` ·
`audiences` · `why` · `parts[]` · `steps[]` · `worksheet` · `where` · `coach` ·
`grounding{model, grade, citation, caveat}` · `ce` · `provenance`.

`grounding.grade` is **R** (peer-reviewed or a federal practice standard, may be stated as
established) · **P** (practitioner framework, label it, never call it research) · **C** (contested —
retire, or keep only with a stated caveat). The grade renders on the card inside a collapsed
"Grounded in" panel. **The grade travels with the content**, which is what stops a future session
quietly reintroducing a retired model.

`provenance` records where a card came from and what was changed. Keep it accurate.

---

## House rules

**No personal names.** Positions only, so pages stay correct when officers turn over.

**No hard-coded chapter counts.** Per `DC-FACTS.md` §17 the roster fluctuates; a fixed count in page
text is always drifting toward wrong. Say "chapters across the District." Where a count is genuinely
required, take it from the current membership report and date it.

**ILC, not NLC. International HOSA, not National HOSA.**

**No browser storage.** Nothing writes to `localStorage`.

**Printing is per card, sized for Letter.** The *Print this card* button clones that one card into an
isolated print host and prints only it — never the page around it. Portrait gives a single column;
landscape gives a two-column grid, read on the left and act on the right. A card that carries a
figure prints the diagram across the sheet in portrait and then drops into two columns underneath,
so the figure stays legible without costing a page. Either orientation is chosen in the print
dialog, not by the page. Type is set in points for paper, a footer with the card’s URL repeats on
every sheet (a table footer, which every browser repeats — fixed positioning overlapped the last
line), and the *Do this*, *Coach note* and *Grounded in* blocks never split across a sheet. About
three quarters of printable cards fit on one page in either orientation (32 of 43 portrait, 30 of 43
landscape); the rest are the longest cards and take two. Cmd+P on a whole page still works and
prints every card on it compactly.

**No external requests.** Type is self-hosted in `assets/fonts/`. The Hub works offline and on a
locked-down school network. Do not add a CDN or a font CDN back.

---

## Layout

```
data/hub.json        the content — the only file you edit
build/build.py       the generator
assets/hub.css       one type system, one neutral palette, one accent per domain
assets/fonts/        Fraunces (display) + Inter (text), self-hosted, Latin subset
index.html           GENERATED — the ladder
self|voice|team|governance|community.html   GENERATED — one per domain
tools.html           GENERATED — every card, filterable
members|officers|advisors|state-officers|state-staff.html   GENERATED — redirect stubs
```

The retired audience pages redirect to the matching filter state on `tools.html` so anything already
shared keeps working. They cost nothing and links outlive memory — leave them.

---

## Checks before committing

```bash
python3 build/build.py
grep -oh 'href="[a-z-]*\.html' *.html | sort -u     # every target exists
grep -oh 'https\?://[^"]*' *.html assets/hub.css     # only advisors.dchosa.org
grep -on "\bNLC\b\|10 chapters\|Shreyas" *.html data/hub.json   # should be empty
```

Working documents — the research set, the rebuild specification, the salvage audit, the decision
record — live in `Leadership Hub / 00 Architecture /`, **beside this folder, never inside it.**
Everything in this folder is published.
