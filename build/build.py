#!/usr/bin/env python3
"""
DC HOSA Leadership Hub — site generator.

    python3 build/build.py

Reads data/hub.json and writes index.html, one page per domain, tools.html, and
redirect stubs for the retired audience pages. Never hand-edit the output.
No dependencies beyond the Python 3 standard library.
"""
import json, os, html, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data", "hub.json")

LEGACY = {
    "members.html":        "member",
    "officers.html":       "chapter officer",
    "advisors.html":       "advisor",
    "state-officers.html": "state officer",
    "state-staff.html":    "state staff",
}

def e(s):
    return html.escape(s if s is not None else "", quote=True)

def shell(title, desc, accent, nav_current, body, depth_note=""):
    nav = []
    nav.append(('index.html', 'Home'))
    for d in DOMAINS:
        nav.append((d["id"] + ".html", d["name"]))
    nav.append(('tools.html', 'All tools'))
    items = "".join(
        '<a href="%s"%s>%s</a>' % (h, ' aria-current="page"' if h == nav_current else '', e(t))
        for h, t in nav)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<link rel="stylesheet" href="assets/hub.css">
<style>:root{{--accent:{accent};}}</style>
</head>
<body>
<header class="top"><div class="wrap">
  <a class="brand" href="index.html">DC HOSA <span>Leadership Hub</span></a>
  <nav class="nav" aria-label="Hub sections">{items}</nav>
</div></header>
{body}
<footer class="foot"><div class="wrap">
  <p><b>DC HOSA Leadership Hub</b> · HOSA-Future Health Professionals · District of Columbia Affiliate · 2026–27</p>
  <p>Chapter advisor development lives at <a href="https://advisors.dchosa.org">advisors.dchosa.org</a>. Competitive event preparation lives in the Study Hub.</p>
  <p>Generated from <code>data/hub.json</code>. Do not hand-edit the HTML.</p>
</div></footer>
<script>
function preparePrint(id){{
  var card=document.getElementById(id); if(!card) return null;
  var old=document.getElementById('printhost'); if(old) old.remove();
  var host=document.createElement('div'); host.id='printhost';
  var clone=card.cloneNode(true); clone.classList.add('print-target'); clone.removeAttribute('id');
  clone.querySelectorAll('details').forEach(function(d){{ d.open=true; }});
  var foot=clone.querySelector('.printfoot');
  var tbl=document.createElement('table'); tbl.className='printtable';
  if(foot){{ var tf=document.createElement('tfoot'); var ftr=document.createElement('tr'); var ftd=document.createElement('td');
    ftd.appendChild(foot); ftr.appendChild(ftd); tf.appendChild(ftr); tbl.appendChild(tf); }}
  var tb=document.createElement('tbody'); var tr=document.createElement('tr'); var td=document.createElement('td');
  td.appendChild(clone); tr.appendChild(td); tb.appendChild(tr); tbl.appendChild(tb);
  host.appendChild(tbl); document.body.appendChild(host);
  document.body.classList.add('printing');
  return host;
}}
function printCard(id){{
  var host=preparePrint(id); if(!host) return;
  function done(){{ document.body.classList.remove('printing'); host.remove(); window.removeEventListener('afterprint',done); }}
  window.addEventListener('afterprint',done);
  window.print();
  setTimeout(done,3000);
}}
// A bare Cmd+P / File > Print (no button — the whole page as it sits) still has to show
// everything: closed <details> (Coach note, Grounded in, a card's later parts) don't reliably
// reveal their content from print CSS alone in current browsers, so force them open right
// before printing and put them back after, whichever way printing was triggered.
(function(){{
  var reopen = [];
  window.addEventListener('beforeprint', function(){{
    reopen = [];
    document.querySelectorAll('details:not([open])').forEach(function(d){{ reopen.push(d); d.open = true; }});
  }});
  window.addEventListener('afterprint', function(){{
    reopen.forEach(function(d){{ d.open = false; }});
    reopen = [];
  }});
}})();
</script>
</body>
</html>
"""

def figure_html(c):
    """Inline assets/figures/<card-id>.svg if it exists. Inlined so it takes the domain accent
    from CSS and prints as vectors."""
    fp = os.path.join(ROOT, "assets", "figures", c["id"] + ".svg")
    if not os.path.exists(fp):
        return ""
    svg = open(fp, encoding="utf-8").read().strip()
    cap = c.get("figure_caption")
    return '<figure class="fig">%s%s</figure>' % (
        svg, ('<figcaption>%s</figcaption>' % e(cap)) if cap else "")

def card_html(c, dom_by_id):
    d = dom_by_id[c["domain"]]
    lvl = LEVEL_BY_ID[c["level"]]
    badges = ['<span class="badge lvl">%s</span>' % e(lvl["name"]),
              '<span class="badge">%s</span>' % e(d["name"])]
    if c.get("pillar"):
        badges.append('<span class="badge">%s</span>' % e(c["pillar"]))
    if c.get("minutes"):
        badges.append('<span class="badge time">%s min</span>' % c["minutes"])
    if c.get("ce"):
        badges.append('<span class="badge">CE: %s</span>' % e(c["ce"]))

    parts = ""
    part_list = c.get("parts", [])
    for idx, p in enumerate(part_list):
        lis = "".join("<li>%s</li>" % e(i) for i in p.get("items", []))
        inner = (("<p>%s</p>" % e(p["body"])) if p.get("body") else "") + \
                (("<ul>%s</ul>" % lis) if lis else "")
        if idx == 0:
            parts += '<div class="part"><h5>%s</h5>%s</div>' % (e(p["heading"]), inner)
        else:
            # Parts after the first fold behind a heading-styled <details> so a card with
            # several parts doesn't read as one long scroll — first part (usually the setup
            # a reader needs before "Do this") stays open, the rest are one click away.
            # Reuses the .body class so the existing print rule (details .body{display:block})
            # force-opens these on any print path, including a bare Cmd+P.
            parts += '<details class="foldpart"><summary>%s</summary><div class="body"><div class="part">%s</div></div></details>' % (
                e(p["heading"]), inner)

    steps = ""
    if c.get("steps"):
        steps = '<div class="steps"><h5>Do this</h5><ol>%s</ol></div>' % "".join(
            "<li>%s</li>" % e(s) for s in c["steps"])

    g = c.get("grounding") or {}
    cav = ('<div class="caveat">%s</div>' % e(g["caveat"])) if g.get("caveat") else ""
    grounded = ""
    if g:
        grounded = ('<details><summary>Grounded in</summary><div class="body">'
                    '<span class="grade %s">%s</span><b>%s</b><br>%s%s</div></details>') % (
            e(g.get("grade", "")), e(g.get("grade", "")), e(g.get("model", "")),
            e(g.get("citation", "")), cav)

    coach = ""
    if c.get("coach"):
        coach = ('<details><summary>Coach note</summary><div class="body">%s</div></details>'
                 % e(c["coach"]))

    printbtn = ('<button class="printbtn" type="button" onclick="printCard(\'%s\')">Print this card</button>'
                % e(c['id'])) if c.get("worksheet") else ""
    printfoot = ('<div class="printfoot">DC HOSA Leadership Hub &nbsp;·&nbsp; leadership.dchosa.org/%s.html#%s'
                 ' &nbsp;·&nbsp; %s &nbsp;·&nbsp; %s</div>') % (e(c['domain']), e(c['id']), e(lvl['name']), e(d['name']))

    return f"""<article class="card" id="{e(c['id'])}" style="--accent:{d['accent']}"
   data-domain="{e(c['domain'])}" data-level="{c['level']}"
   data-minutes="{c.get('minutes','')}" data-print="{'1' if c.get('worksheet') else '0'}"
   data-audiences="{e('|'.join(c.get('audiences', [])))}"{' data-fig="1"' if figure_html(c) else ''}>
  <div class="cols">
  <header>
    <h4>{e(c['title'])}</h4>
    <div class="badges">{''.join(badges)}</div>
  </header>
  <p class="why">{e(c['why'])}</p>
  {figure_html(c)}<div class="colA">{parts}</div>
  <div class="colB">
  {steps}
  <p class="where"><b>Where it shows up:</b> {e(c.get('where',''))}</p>
  {coach}
  {grounded}
  </div>
  </div>
  {printbtn}
  {printfoot}
</article>"""

def build():
    with open(DATA, encoding="utf-8") as f:
        hub = json.load(f)
    global DOMAINS, LEVEL_BY_ID
    DOMAINS = hub["domains"]
    LEVELS = hub["levels"]
    LEVEL_BY_ID = {l["id"]: l for l in LEVELS}
    dom_by_id = {d["id"]: d for d in DOMAINS}
    cards = hub["cards"]

    for c in cards:
        if c["domain"] not in dom_by_id:
            sys.exit("card %s: unknown domain %s" % (c["id"], c["domain"]))
        if c["level"] not in LEVEL_BY_ID:
            sys.exit("card %s: unknown level %s" % (c["id"], c["level"]))
    ids = [c["id"] for c in cards]
    if len(ids) != len(set(ids)):
        sys.exit("duplicate card ids")

    written = []

    # ---------- index ----------
    head = "".join('<th>%s<small>%s</small></th>' % (e(l["name"]), e(l["question"])) for l in LEVELS)
    rows = ""
    for d in DOMAINS:
        cells = ""
        for l in LEVELS:
            n = sum(1 for c in cards if c["domain"] == d["id"] and c["level"] == l["id"])
            cells += ('<td><div class="cellcount%s">%d</div>'
                      '<div class="cellnote">%s</div></td>') % (
                "" if n else " zero", n, "card" if n == 1 else "cards")
        rows += ('<tr><td class="dom"><a href="%s.html" style="color:%s">%s</a>'
                 '<p>%s</p></td>%s</tr>') % (d["id"], d["accent"], e(d["name"]), e(d["blurb"]), cells)

    onramp = ""
    starters = [c for c in cards if c["level"] == 1][:3]
    if starters:
        onramp = ('<section class="sec"><div class="wrap"><h2>Start here</h2>'
                  '<p class="lede">Three cards at Lead Yourself. Each one is short, and each one '
                  'is used in an actual chapter meeting rather than read and filed.</p>'
                  + "".join(card_html(c, dom_by_id) for c in starters) + '</div></section>')

    body = f"""<section class="orient"><div class="wrap">
  <p class="orient-h1">Chapter officer or state officer — or thinking about becoming one?</p>
  <p class="orient-sub">You&rsquo;re in the right place. This Hub turns what officers actually do
  into short, usable cards &mdash; not more reading.</p>
</div></section>
<section class="hero"><div class="wrap">
  <div class="eyebrow">DC HOSA · Washington, DC · 2026–27</div>
  <h1>Leadership, one rung at a time.</h1>
  <p>Five capability domains, three levels each. Start where you are and the next rung is
  visible from day one — whether you joined last week or you are running the affiliate.</p>
</div></section>

<section class="sec"><div class="wrap">
  <h2>The ladder</h2>
  <p class="lede">Domains run down. Levels run across. Every card in the Hub sits in exactly one cell.</p>
  <div class="ladder"><table>
    <thead><tr><th>Domain</th>{head}</tr></thead>
    <tbody>{rows}</tbody>
  </table></div>
</div></section>
{onramp}"""
    open(os.path.join(ROOT, "index.html"), "w", encoding="utf-8").write(
        shell("DC HOSA Leadership Hub", "Leadership development for every role in DC HOSA — five domains, three levels.",
              "#0e6b5e", "index.html", body))
    written.append("index.html")

    # ---------- domain pages ----------
    for d in DOMAINS:
        secs = ""
        for l in LEVELS:
            sel = [c for c in cards if c["domain"] == d["id"] and c["level"] == l["id"]]
            secs += '<div class="levelhead"><h3>%s</h3><span class="q">%s</span></div>' % (
                e(l["name"]), e(l["question"]))
            secs += ("".join(card_html(c, dom_by_id) for c in sel) if sel
                     else '<div class="empty">No cards at this level yet.</div>')
        body = f"""<section class="hero"><div class="wrap">
  <div class="eyebrow">Domain</div><h1>{e(d['name'])}</h1><p>{e(d['blurb'])}</p>
</div></section>
<section class="sec"><div class="wrap">{secs}</div></section>"""
        open(os.path.join(ROOT, d["id"] + ".html"), "w", encoding="utf-8").write(
            shell("%s — DC HOSA Leadership Hub" % d["name"], d["blurb"], d["accent"],
                  d["id"] + ".html", body))
        written.append(d["id"] + ".html")

    # ---------- tools ----------
    dopts = "".join('<option value="%s">%s</option>' % (d["id"], e(d["name"])) for d in DOMAINS)
    lopts = "".join('<option value="%d">%s</option>' % (l["id"], e(l["name"])) for l in LEVELS)
    aopts = "".join('<option value="%s">%s</option>' % (e(a), e(a.title())) for a in hub["audiences"])
    allcards = "".join(card_html(c, dom_by_id) for c in
                       sorted(cards, key=lambda c: (c["level"], c["domain"], c["title"])))
    body = f"""<section class="hero"><div class="wrap">
  <div class="eyebrow">Index</div><h1>All tools.</h1>
  <p>Every card in the Hub, filterable. Audience is a filter here, not a separate page —
  an advisor can find the member card, and a member can find the officer one.</p>
</div></section>
<section class="sec"><div class="wrap">
  <div class="filters">
    <select id="fd"><option value="">All domains</option>{dopts}</select>
    <select id="fl"><option value="">All levels</option>{lopts}</select>
    <select id="fa"><option value="">All audiences</option>{aopts}</select>
    <select id="ft"><option value="">Any length</option><option value="15">15 min or less</option><option value="30">30 min or less</option></select>
    <select id="fp"><option value="">Printable or not</option><option value="1">Printable only</option></select>
    <button id="fr" type="button">Reset</button>
  </div>
  <div class="count" id="count"></div>
  {allcards if cards else '<div class="empty">No cards yet.</div>'}
  <div class="empty" id="none" hidden>Nothing matches those filters.</div>
</div></section>
<script>
(function(){{
  var cards=[].slice.call(document.querySelectorAll('.card'));
  var f={{d:document.getElementById('fd'),l:document.getElementById('fl'),
         a:document.getElementById('fa'),t:document.getElementById('ft'),
         p:document.getElementById('fp')}};
  function apply(){{
    var n=0;
    cards.forEach(function(c){{
      var ok=true;
      if(f.d.value && c.dataset.domain!==f.d.value) ok=false;
      if(f.l.value && c.dataset.level!==f.l.value) ok=false;
      if(f.a.value && (c.dataset.audiences||'').split('|').indexOf(f.a.value)<0) ok=false;
      if(f.t.value && (parseInt(c.dataset.minutes||'9999',10)>parseInt(f.t.value,10))) ok=false;
      if(f.p.value && c.dataset.print!=='1') ok=false;
      c.hidden=!ok; if(ok) n++;
    }});
    document.getElementById('count').textContent=n+(n===1?' card':' cards');
    document.getElementById('none').hidden=(n!==0);
  }}
  var q=new URLSearchParams(location.search);
  if(q.get('audience')){{ f.a.value=q.get('audience'); }}
  if(q.get('domain')){{ f.d.value=q.get('domain'); }}
  if(q.get('level')){{ f.l.value=q.get('level'); }}
  Object.keys(f).forEach(function(k){{f[k].addEventListener('change',apply);}});
  document.getElementById('fr').addEventListener('click',function(){{
    Object.keys(f).forEach(function(k){{f[k].value='';}}); apply();
  }});
  apply();
}})();
</script>"""
    open(os.path.join(ROOT, "tools.html"), "w", encoding="utf-8").write(
        shell("All tools — DC HOSA Leadership Hub", "Every Leadership Hub card, filterable by domain, level, audience and length.",
              "#0e6b5e", "tools.html", body))
    written.append("tools.html")

    # ---------- legacy redirects ----------
    for fn, aud in LEGACY.items():
        target = "tools.html?audience=" + aud.replace(" ", "+")
        open(os.path.join(ROOT, fn), "w", encoding="utf-8").write(
f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8">
<title>Moved — DC HOSA Leadership Hub</title>
<link rel="canonical" href="{target}">
<meta http-equiv="refresh" content="0; url={target}">
<link rel="stylesheet" href="assets/hub.css">
</head><body><div class="wrap" style="padding:80px 28px">
<h1 style="font-family:var(--display);font-weight:900;font-size:34px">This page moved.</h1>
<p style="margin-top:14px;max-width:56ch;color:var(--ink-2)">The Hub is organised by capability
domain now rather than by audience. The {e(aud)} material lives across the five domains, and
audience is a filter.</p>
<p style="margin-top:18px"><a href="{target}">Continue to the {e(aud)} view</a> ·
<a href="index.html">Hub home</a></p>
</div></body></html>""")
        written.append(fn)

    print("built %d files:" % len(written))
    for w in written:
        print("   ", w)
    print("cards: %d across %d domains" % (len(cards), len(DOMAINS)))

if __name__ == "__main__":
    build()
