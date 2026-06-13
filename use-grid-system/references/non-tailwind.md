# Non-Tailwind fallback — the framework-free `:root` scaffold

When `probe.py` finds no Tailwind (vanilla CSS, CSS Modules, styled-components,
plain HTML), **do not add Tailwind** (no-monoculture, spec A8). Emit this
self-contained `:root` scaffold instead — the prior skill's proven approach.
`grid_tokens.py --vanilla` generates it.

## One source of truth (`:root`)
```css
:root{
  --cols:12;
  --bl:8px;              /* baseline unit */
  --lh:24px;             /* leading = 3 × baseline */
  --gutter:24px;
  --margin:72px;
  --maxw:1296px;
  --pad:96px;            /* spread top/bottom pad (× baseline) */
  --paper:#ffffff; --ink:#111315; --ink-soft:#5b6066; --accent:#e4002b;
  --g-col:rgba(228,0,43,.075);      /* column field fill */
  --g-edge:rgba(228,0,43,.40);      /* column edge / margin line */
  --g-base:rgba(0,150,140,.34);     /* major baseline line (--lh) */
  --g-base-min:rgba(0,150,140,.12); /* minor baseline line (--bl) */
}
*{box-sizing:border-box;}
```

## Grid + subgrid bands (place by column LINE)
```css
.wrap{position:relative;max-width:var(--maxw);margin:0 auto;padding:var(--pad) var(--margin);}
.grid{display:grid;grid-template-columns:repeat(var(--cols),1fr);column-gap:var(--gutter);row-gap:var(--lh);}
.band{grid-column:1 / -1;display:grid;grid-template-columns:subgrid;column-gap:var(--gutter);align-items:start;}
@supports not (grid-template-columns:subgrid){ .band{grid-template-columns:repeat(var(--cols),1fr);} }
/* children: style="grid-column:<startline> / <endline>"  e.g. 1 / 6, 6 / 13 */
```

## The overlay — MUST live in the SAME content box as the content
This is the #1 bug fix: if content is in a centered `max-width` box but the overlay
is a full-width sibling, the columns drift apart past `--maxw`. Put `.guides`
*inside* the same `.wrap`.
```css
.guides{position:absolute;inset:0;pointer-events:none;z-index:60;opacity:0;transition:opacity .26s ease;}
body.grid-on .guides{opacity:1;}
.guides .cols{position:absolute;top:0;bottom:0;left:var(--margin);right:var(--margin);
  display:grid;grid-template-columns:repeat(var(--cols),1fr);column-gap:var(--gutter);}
.guides .col{background:var(--g-col);box-shadow:inset 1px 0 0 var(--g-edge),inset -1px 0 0 var(--g-edge);position:relative;}
.guides .col span{position:absolute;top:32px;left:0;right:0;text-align:center;font:10px/1 monospace;color:var(--accent);}
.guides .rows{position:absolute;left:var(--margin);right:var(--margin);top:var(--pad);bottom:0;
  background-image:
    repeating-linear-gradient(to bottom,var(--g-base) 0 1px,transparent 1px var(--lh)),
    repeating-linear-gradient(to bottom,var(--g-base-min) 0 1px,transparent 1px var(--bl));}
.guides .mline{position:absolute;top:0;bottom:0;width:1px;background:var(--g-edge);}
.guides .mline.l{left:var(--margin);} .guides .mline.r{right:var(--margin);}
```
Markup per section: `<div class="guides"><div class="cols"></div><div class="rows"></div>
<div class="mline l"></div><div class="mline r"></div></div>` inside `.wrap`.

## Toggle (button + `g` key) + numbered columns
```js
var btn=document.getElementById('gridToggle');
function setGrid(on){document.body.classList.toggle('grid-on',on);}
if(btn) btn.addEventListener('click',function(){setGrid(!document.body.classList.contains('grid-on'));});
document.addEventListener('keydown',function(e){
  if((e.key==='g'||e.key==='G')&&!e.metaKey&&!e.ctrlKey&&!e.altKey)
    setGrid(!document.body.classList.contains('grid-on'));});
document.querySelectorAll('.guides .cols').forEach(function(h){
  var n=parseInt(getComputedStyle(document.documentElement).getPropertyValue('--cols'),10)||12;
  for(var i=1;i<=n;i++){var c=document.createElement('div');c.className='col';
    var s=document.createElement('span');s.textContent=i;c.appendChild(s);h.appendChild(c);}});
```

## Optical alignment
Identical to the Tailwind path — see `optical-alignment.md`; the module is
framework-agnostic (reads CSS variables, measures the loaded font).

## Verification
Same four checks via `audit-ui` / `automate-browser` — see `verification.md`.

The only thing that changes off-Tailwind is the **delivery** (`:root` + hand-written
classes vs `@theme` + utilities). The discipline, the overlay, the optical module,
and the verification are identical.
