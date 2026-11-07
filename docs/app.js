'use strict';

const fmt = n => Math.round(n).toLocaleString('en-US');
const pct = (n, d = 1) => (n * 100).toFixed(d) + '%';
const $ = id => document.getElementById(id);
const COLOR = {
  PS: '--ps', 'PD-ASHM': '--pd', PSD: '--psd', 'NISMA-SHB': '--shb', MUNDESIA: '--mund', BASHKE: '--bashke',
  TJERET: '--tjeret', 'PS + PSD': '--ps', SHESHI: '--sheshi',
};
const NAME = {
  PS: 'PS', 'PD-ASHM': 'PD-ASHM', PSD: 'PSD', 'NISMA-SHB': 'Shqipëria Bëhet', MUNDESIA: 'Mundësia', BASHKE: 'L. Bashkë',
  TJERET: 'Të tjerët', 'PS + PSD': 'PS + PSD', SHESHI: 'Kualicioni Sheshit',
};
const css = key => `var(${COLOR[key]})`;

function el(tag, props = {}, ...kids) {
  const n = document.createElement(tag);
  for (const [k, v] of Object.entries(props)) {
    if (k === 'class') n.className = v;
    else if (k === 'text') n.textContent = v;
    else if (k === 'style') n.style.cssText = v;
    else n.setAttribute(k, v);
  }
  n.append(...kids.filter(k => k !== null && k !== undefined));
  return n;
}

function barRow(label, share, max, color, value, note) {
  const val = el('span', { class: 'bar-val', text: value });
  if (note) val.append(' ', el('small', { text: note }));
  return el('div', { class: 'bar-row' },
    el('span', { text: label }),
    el('div', { class: 'bar-track' }, el('div', { class: 'bar', style: `width:${max ? share / max * 100 : 0}%;background:${color}` })),
    val);
}

function pairRow(label, a, b, max, colorB, value, note) {
  const bar = (v, c) => (v === null ? el('div', { class: 'bar', style: 'width:0;min-width:0;background:none' })
    : el('div', { class: 'bar', style: `width:${v / max * 100}%;background:${c}` }));
  const val = el('span', { class: 'bar-val', text: value });
  if (note) val.append(el('small', { class: 'stack', text: note }));
  return el('div', { class: 'bar-row' }, el('span', { text: label }),
    el('div', { class: 'bar-track' }, bar(a, 'var(--ghost)'), bar(b, colorB)),
    val);
}

function table(target, head, rows, numericFrom = 1) {
  const th = head.map((h, i) => el('th', { text: h, class: i >= numericFrom ? 'n' : '', scope: 'col' }));
  const body = rows.map(r => el('tr', {}, ...r.map((c, i) => el('td', { text: c, class: i >= numericFrom ? 'n' : '' }))));
  target.replaceChildren(el('table', {}, el('thead', {}, el('tr', {}, ...th)), el('tbody', {}, ...body)));
}

function tile(value, label) { return el('div', { class: 'tile' }, el('b', { text: value }), el('span', { text: label })); }
function key(color, label) { return el('span', { class: 'key' }, el('i', { style: `background:${color}` }), label); }

function drawMap(target, map, onFocus) {
  const ns = 'http://www.w3.org/2000/svg';
  const svg = document.createElementNS(ns, 'svg');
  svg.setAttribute('viewBox', `0 0 ${map.w} ${map.h}`);
  svg.setAttribute('role', 'group');
  svg.setAttribute('aria-label', 'Harta e njësive administrative të Tiranës');
  const shapes = {};
  for (const [name, d] of Object.entries(map.paths)) {
    const p = document.createElementNS(ns, 'path');
    p.setAttribute('d', d);
    p.setAttribute('tabindex', '0');
    p.setAttribute('aria-label', name);
    if (onFocus) for (const ev of ['pointerenter', 'focus', 'click']) p.addEventListener(ev, () => onFocus(name));
    svg.append(p);
    shapes[name] = p;
  }
  target.replaceChildren(svg);
  return shapes;
}

// ---- subjects from a unit's vote array: [PS, PSD, PD, SHB, MUND, BASHKE, Other]
const parts = v => ({ ps: v[0] + v[1], pd: v[2], fl: v[3] + v[4] + v[5], ot: v[6] });
function scenario(v, x, y) {
  const b = parts(v);
  return { ps: b.ps * (1 - x), pd: b.pd * (1 - y), fl: b.fl + x * b.ps + y * b.pd, ot: b.ot };
}
const RIVAL = { ps: 'PS + PSD', pd: 'PD-ASHM', ot: 'TJERET' };
function rival(s) {
  return ['ps', 'pd', 'ot'].reduce((a, k) => (s[k] > s[a] ? k : a), 'ps');
}

function init(d) {
  $('updated').textContent = d.updated;
  const total = d.national.reduce((a, p) => a + p.votes, 0);
  const abroad = d.national.reduce((a, p) => a + p.abroad, 0);
  const fl = d.national.filter(p => ['NISMA-SHB', 'MUNDESIA', 'BASHKE'].includes(p.code));
  $('hero-tiles').append(
    tile(fmt(total), 'vota të vlefshme në 2025'),
    tile('140', 'mandate në 12 qarqe'),
    tile(fmt(abroad), 'vota nga diaspora'),
    tile(pct(fl.reduce((a, p) => a + p.votes, 0) / total), 'Mundësia, L. Bashkë dhe Shqipëria Bëhet gjithsej'));

  // national
  const seated = d.national.filter(p => p.seats > 0).sort((a, b) => b.seats - a.seats);
  $('seat-bar').append(...seated.map(p => el('div', {
    class: 'seat', style: `flex:${p.seats} 1 0;background:${css(p.code)}`, title: `${p.label}: ${p.seats} mandate`,
    role: 'img', 'aria-label': `${p.label}: ${p.seats} mandate`, text: p.seats >= 20 ? `${p.label} ${p.seats}` : '',
  })));
  $('seat-legend').append(...seated.map(p => key(css(p.code), `${p.label} ${p.seats}`)));
  const main = d.national.filter(p => COLOR[p.code]);
  const rest = d.national.filter(p => !COLOR[p.code]).reduce((a, p) => a + p.votes, 0);
  const rows = [...main.map(p => [p.label, p.votes, p.code, p.seats]), ['Të tjerët', rest, 'TJERET', 0]];
  const maxN = Math.max(...rows.map(r => r[1]));
  $('national-bars').append(...rows.map(r => barRow(r[0], r[1], maxN, css(r[2]), pct(r[1] / total), r[3] ? `${r[3]} mand.` : '')));
  table($('national-table'), ['Subjekti', 'Vota', '%', 'Nga diaspora', 'Mandate'],
    d.national.map(p => [p.name, fmt(p.votes), pct(p.votes / total), fmt(p.abroad), p.seats]));

  // districts
  const codes = ['PS', 'PD-ASHM', 'PSD', 'NISMA-SHB', 'MUNDESIA', 'BASHKE', 'TJERET'];
  const sel = $('region-select');
  d.regions.forEach(q => sel.append(el('option', { value: q.name, text: q.name })));
  sel.value = 'Tiranë';
  const showRegion = () => {
    const q = d.regions.find(r => r.name === sel.value);
    const sum = Object.values(q.votes).reduce((a, b) => a + b, 0);
    const seats = Object.values(q.seats).reduce((a, b) => a + b, 0);
    $('region-title').textContent = `${q.name}: ${fmt(sum)} vota, ${seats} mandate`;
    const list = codes.slice().sort((a, b) => q.votes[b] - q.votes[a]);
    const max = q.votes[list[0]];
    $('region-bars').replaceChildren(...list.map(c => barRow(NAME[c], q.votes[c], max, css(c), pct(q.votes[c] / sum),
      q.seats[c] ? `${q.seats[c]} mand.` : '')));
  };
  sel.addEventListener('change', showRegion);
  showRegion();
  table($('region-table'), ['Qarku', 'Mandate', ...codes.slice(0, 6).map(c => NAME[c])], d.regions.map(q => {
    const sum = Object.values(q.votes).reduce((a, b) => a + b, 0);
    return [q.name, Object.values(q.seats).reduce((a, b) => a + b, 0), ...codes.slice(0, 6).map(c => pct(q.votes[c] / sum))];
  }));

  // Tirana map
  const U = d.units;
  const sum = a => a.reduce((x, y) => x + y, 0);
  const METRICS = {
    'PS + PSD': u => (u.v25[0] + u.v25[1]) / sum(u.v25),
    'PD-ASHM': u => u.v25[2] / sum(u.v25),
    'Kualicioni Sheshit': u => (u.v25[3] + u.v25[4] + u.v25[5]) / sum(u.v25),
    'Mundësia': u => u.v25[4] / sum(u.v25),
    'Shqipëria Bëhet': u => u.v25[3] / sum(u.v25),
    'L. Bashkë': u => u.v25[5] / sum(u.v25),
    'Pjesëmarrja': u => u.voters25 / u.reg25,
  };
  const ms = $('map-select');
  Object.keys(METRICS).forEach(k => ms.append(el('option', { value: k, text: k })));
  ms.value = 'Kualicioni Sheshit';
  let current = 'Nj.Ad. Nr. 5';
  const showUnit = name => {
    current = name;
    Object.entries(shapes).forEach(([n, p]) => p.classList.toggle('on', n === name));
    const u = U.find(x => x.name === name);
    const t = sum(u.v25);
    const list = [['PS', 0], ['PSD', 1], ['PD-ASHM', 2], ['MUNDESIA', 4], ['NISMA-SHB', 3], ['BASHKE', 5], ['TJERET', 6]]
      .map(([c, i]) => [c, u.v25[i]]).sort((a, b) => b[1] - a[1]);
    $('unit-panel').replaceChildren(
      el('h3', { text: name }),
      el('p', { text: `${fmt(t)} vota, pjesëmarrje ${pct(u.voters25 / u.reg25)}` }),
      el('div', { class: 'bars' }, ...list.map(([c, v]) => barRow(NAME[c], v, list[0][1], css(c), pct(v / t)))));
  };
  const shapes = drawMap($('map'), d.map, showUnit);
  const showMetric = () => {
    const f = METRICS[ms.value];
    const vals = U.map(f);
    const lo = Math.min(...vals), hi = Math.max(...vals), step = (hi - lo) / 5 || 1;
    U.forEach(u => {
      const bin = Math.min(4, Math.floor((f(u) - lo) / step));
      shapes[u.name].style.fill = `var(--s${bin + 1})`;
      shapes[u.name].setAttribute('aria-label', `${u.name}: ${pct(f(u))}`);
    });
    $('map-legend').replaceChildren(...[0, 1, 2, 3, 4].map(i =>
      key(`var(--s${i + 1})`, `${pct(lo + i * step, 0)}–${pct(lo + (i + 1) * step, 0)}`)));
    table($('unit-table'), ['Njësia', ms.value], U.slice().sort((a, b) => f(b) - f(a)).map(u => [u.name, pct(f(u))]));
  };
  ms.addEventListener('change', showMetric);
  showMetric();
  showUnit(current);

  // 2023 and 2025
  const tot = k => d.groups.map((_, i) => sum(U.map(u => u[k][i])));
  const t23 = tot('v23'), t25 = tot('v25');
  const s23 = sum(t23), s25 = sum(t25);
  const cmp = [['PS', 0], ['PD-ASHM', 2], ['PSD', 1], ['NISMA-SHB', 3], ['BASHKE', 5], ['MUNDESIA', 4], ['TJERET', 6]];
  const maxC = Math.max(...cmp.flatMap(([, i]) => [t23[i] / s23, t25[i] / s25]));
  $('compare-legend').append(key('var(--ghost)', '2023'), key('var(--s4)', '2025'));
  $('compare-bars').append(...cmp.map(([c, i]) => {
    const a = t23[i] ? t23[i] / s23 : null;
    return pairRow(NAME[c], a, t25[i] / s25, maxC, 'var(--s4)', `${a === null ? 'pa listë' : pct(a)} → ${pct(t25[i] / s25)}`);
  }));

  // scenario
  const base = parts(t25);
  const scenShapes = drawMap($('scen-map'), d.map);
  const LEAD = { fl: 'SHESHI', ps: 'PS + PSD', pd: 'PD-ASHM', ot: 'TJERET' };
  const MAPC = { SHESHI: 'var(--map-sheshi)', 'PS + PSD': 'var(--map-ps)', 'PD-ASHM': 'var(--map-pd)', TJERET: 'var(--tjeret)' };
  $('scen-map-legend').append(...['SHESHI', 'PS + PSD', 'PD-ASHM'].map(k => key(MAPC[k], NAME[k])));
  $('scen-legend').append(key('var(--ghost)', 'Rezultati 2025'), 'Shiriti me ngjyrë: skenari');
  const X = $('x'), Y = $('y');

  const render = () => {
    const x = X.value / 100, y = Y.value / 100;
    $('x-out').textContent = `${X.value}%`;
    $('y-out').textContent = `${Y.value}%`;
    const s = scenario(t25, x, y);
    const rk = rival(s);
    const diff = s.fl - s[rk];
    const rank = 1 + ['ps', 'pd', 'ot'].filter(k => s[k] >= s.fl).length;
    const win = diff > 0;
    const verdict = $('verdict');
    verdict.replaceChildren(el('b', { class: win ? 'yes' : 'no', text: win ? 'PO' : 'JO' }),
      win ? `Kualicioni Sheshit del i pari, ${fmt(diff)} vota mbi ${NAME[RIVAL[rk]]}`
        : `Kualicioni Sheshit del i ${rank}-ti, ${fmt(-diff)} vota pas ${NAME[RIVAL[rk]]}`);

    const lead = U.map(u => { const c = scenario(u.v25, x, y); const r = rival(c); return { u, c, r, won: c.fl - c[r] > 0 }; });
    const won = lead.filter(l => l.won).length;
    const bY = base.fl + y * base.pd;
    const xMin = Math.max(0, (base.ps - bY) / (2 * base.ps), (base.pd * (1 - y) - bY) / base.ps, (base.ot - bY) / base.ps);
    const bX = base.fl + x * base.ps;
    const yMin = Math.max(0, (base.ps * (1 - x) - bX) / base.pd, (base.pd - bX) / (2 * base.pd), (base.ot - bX) / base.pd);
    $('scen-tiles').replaceChildren(
      tile(fmt(s.fl), 'vota për Sheshin'),
      tile(pct(s.fl / s25), 'e votave'),
      tile((diff > 0 ? '+' : '') + fmt(diff), `diferenca nga ${NAME[RIVAL[rk]]}`),
      tile(`${won} nga 24`, 'njësi ku del i pari'),
      tile(pct(xMin), 'X e nevojshme me këtë Y'),
      tile(yMin > 1 ? 'E pamundur' : pct(yMin), 'Y e nevojshme me këtë X'));

    const list = [['SHESHI', base.fl, s.fl], ['PS + PSD', base.ps, s.ps], ['PD-ASHM', base.pd, s.pd], ['TJERET', base.ot, s.ot]]
      .sort((a, b) => b[2] - a[2]);
    const maxS = Math.max(...list.flatMap(r => [r[1], r[2]]));
    $('scen-bars').replaceChildren(...list.map(([k, a, b]) => pairRow(NAME[k], a, b, maxS, css(k), fmt(b), pct(b / s25))));

    lead.forEach(l => {
      const k = l.won ? 'SHESHI' : LEAD[l.r];
      scenShapes[l.u.name].style.fill = MAPC[k];
      scenShapes[l.u.name].setAttribute('aria-label', `${l.u.name}: i pari ${NAME[k]}`);
    });
    table($('scen-table'), ['Njësia', 'Sheshi', 'PS + PSD', 'PD-ASHM', 'Diferenca', 'I pari'],
      lead.slice().sort((a, b) => (b.c.fl - b.c[b.r]) - (a.c.fl - a.c[a.r])).map(l => {
        const t = sum(l.u.v25);
        const df = l.c.fl - l.c[l.r];
        return [l.u.name, pct(l.c.fl / t), pct(l.c.ps / t), pct(l.c.pd / t), (df > 0 ? '+' : '') + fmt(df), l.won ? 'Sheshi' : NAME[LEAD[l.r]]];
      }));
  };
  X.addEventListener('input', render);
  Y.addEventListener('input', render);
  [['Pa kalime', 0, 0], ['20% / 20%', 20, 20], ['30% / 30%', 30, 30], ['38% / 10%', 38, 10]].forEach(([label, a, b]) => {
    const btn = el('button', { type: 'button', text: label });
    btn.addEventListener('click', () => { X.value = a; Y.value = b; render(); });
    $('presets').append(btn);
  });
  render();
  window.scrollSpyUpdate();
}

// Highlight the toolbar link of the section being read
(function scrollSpy() {
  const links = [...document.querySelectorAll('nav a[href^="#"]')];
  const sections = links.map(a => document.getElementById(a.getAttribute('href').slice(1))).filter(Boolean);
  let current = null;
  const update = () => {
    const line = innerHeight * 0.3;
    let active = null;
    for (const s of sections) if (s.getBoundingClientRect().top <= line) active = s;
    if (innerHeight + scrollY >= document.documentElement.scrollHeight - 4) active = sections[sections.length - 1];
    const id = active ? active.id : null;
    if (id === current) return;
    current = id;
    links.forEach(a => {
      const on = a.getAttribute('href') === `#${id}`;
      a.classList.toggle('active', on);
      if (on) { a.setAttribute('aria-current', 'location'); a.scrollIntoView({ block: 'nearest', inline: 'center' }); }
      else a.removeAttribute('aria-current');
    });
  };
  let queued = false;
  addEventListener('scroll', () => { if (!queued) { queued = true; requestAnimationFrame(() => { queued = false; update(); }); } }, { passive: true });
  addEventListener('resize', update);
  update();
  window.scrollSpyUpdate = update;
}());

fetch('data/site.json?v=5')
  .then(r => { if (!r.ok) throw new Error(r.status); return r.json(); })
  .then(init)
  .catch(() => {
    $('hero-tiles').replaceChildren(el('p', { class: 'note', text: 'Të dhënat nuk u ngarkuan. Rifresko faqen.' }));
  });
