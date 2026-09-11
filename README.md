# DC HOSA Leadership Hub

A six-page leadership resource for every role in DC HOSA. One page per audience, each with
the frameworks, tools and language that fit that level of leadership.

School year 2026–2027.

| Page | Audience |
|---|---|
| `index.html` | Portal — routes visitors to their hub |
| `members.html` | Local Chapter members |
| `officers.html` | Local Chapter officers |
| `advisors.html` | Local Chapter advisors |
| `state-officers.html` | State Executive Council |
| `state-staff.html` | State Advisor and state staff |

---

## The rules that matter

**No personal names.** Every reference is to a position, never a person, so the pages stay
correct when officers turn over. Do not reintroduce a name to any page.

**No chapter counts.** Per `DC-FACTS.md` §17, the roster fluctuates and a fixed count in page
text is always drifting toward wrong. Use "chapters across the District". Where a count is
genuinely required, take it from the current membership report and date it.

**ILC, not NLC. International HOSA, not National HOSA.**

## How it is built

Plain HTML, CSS and vanilla JavaScript. No framework, no build step, no CDN scripts. Each
page is self-contained; the only external request is Google Fonts.

Each page carries its own typography and palette by design — see
`00 Architecture/DESIGN_RATIONALE.md` in the working folder for why. Shared patterns
(navigation drawer, bottom tab bar, modal system, worksheet printer, research callouts) are
identical across all six files; only the CSS variables differ. When adding a page, copy an
existing one and change the variables rather than inventing new patterns.

Worksheets print through `window.print()` on a generated page — no PDF library, no storage.
Nothing on any page writes to `localStorage`.

## Editing

Edit the HTML directly. After any edit, confirm:

```bash
grep -c "<div" *.html && grep -c "</div>" *.html    # tags balanced
grep -o 'href="[a-z-]*\.html"' *.html | sort -u      # every link target exists
```
