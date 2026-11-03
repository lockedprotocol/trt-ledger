const D = window.TRT_DATA;
const $ = id => document.getElementById(id);
const usd = n => '$' + Math.round(n).toLocaleString();
const STATES = ["AL","AK","AZ","AR","CA","CO","CT","DE","FL","GA","HI","ID","IL","IN","IA","KS","KY","LA","ME","MD","MA","MI","MN","MS","MO","MT","NE","NV","NH","NJ","NM","NY","NC","ND","OH","OK","OR","PA","RI","SC","SD","TN","TX","UT","VT","VA","WA","WV","WI","WY"];

// Respect the system's Reduce Motion setting for scripted scrolling too
const SCROLL = matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth';
const fmtDate = iso => new Date(iso + 'T12:00').toLocaleDateString(undefined, {month:'short', day:'numeric', year:'numeric'});
// A price the weekly check couldn't re-confirm for 3+ weeks gets flagged on the page automatically
const STALE_DAYS = 21;
const staleTag = iso => iso && (Date.now() - Date.parse(iso + 'T12:00')) / 864e5 > STALE_DAYS
  ? `<span class="tag warn">Not re-checked since ${fmtDate(iso)}</span>` : '';
$('statOnline').textContent = D.clinics.length;
$('updated').textContent = fmtDate(D.updated);
fetch('clinics/index.json').then(r => r.json()).then(idx => {
  $('statInPerson').textContent = idx.total.toLocaleString();
  $('freshness').textContent = `Prices last checked ${fmtDate(D.updated)} · clinic directory refreshed ${fmtDate(idx.updated)}.`;
}).catch(() => { $('freshness').textContent = `Prices last checked ${fmtDate(D.updated)}.`; });

$('themeBtn').addEventListener('click', () => {
  const dark = document.documentElement.dataset.theme
    ? document.documentElement.dataset.theme === 'dark'
    : matchMedia('(prefers-color-scheme: dark)').matches;
  document.documentElement.dataset.theme = dark ? 'light' : 'dark';
  try { localStorage.setItem('trtTheme', document.documentElement.dataset.theme); } catch (e) {}
});
STATES.forEach(s => $('state').insertAdjacentHTML('beforeend', `<option>${s}</option>`));

// Returns true, false, or null (unknown) for whether a clinic serves a state
function servesState(c, st){
  const s = c.states || '';
  if (/not listed/i.test(s)) return null;
  if (/all except/i.test(s)) return !s.split(/except/i)[1].includes(st);
  return s.split(/,\s*/).includes(st);
}

// First-year cost, with a line-item breakdown so users can see the math
function yearOne(c, a, form){
  if (c.clinicYear1Estimate) return {total:c.clinicYear1Estimate, parts:["clinic's own year-1 estimate"], estimated:false, upfront:(c.intakeFee||c.labFee)?(c.intakeFee||0)+(c.labFee||0):null};
  const parts=[]; let total=0, estimated=false;
  const add=(amt,label,est)=>{ if(amt){ total+=amt; parts.push(usd(amt)+' '+label+(est?'*':'')); if(est) estimated=true; } };
  const formPrice = form && c.priceByForm && c.priceByForm[form];
  add((formPrice || c.monthly || 0)*12, formPrice ? `membership (${form})` : 'membership');
  add(c.intakeFee, 'intake');
  if (!c.medsIncluded) add(a.medCost*12, 'meds', true);
  if (c.labsIncluded === false) add(c.labFee ? c.labFee : a.labCost*a.labsPerYear, 'labs', !c.labFee);
  if (c.labsIncluded === null) add(a.labCost*a.labsPerYear, 'labs (unclear if included)', true);
  const upfront = c.prepaid ? c.prepaid + (c.intakeFee||0) : (c.intakeFee||0) + (c.monthly||0) + (c.labsIncluded===false ? (c.labFee||a.labCost) : 0);
  return {total, parts, estimated, upfront};
}

function yn(v){ return v===true?'<span class="yes">Yes</span>':v===false?'<span class="no">No</span>':'<span class="unk">Not stated</span>'; }

function render(){
  const a = {medCost:+$('medCost').value||0, labCost:+$('labCost').value||0, labsPerYear:+$('labsPerYear').value||0};
  const st=$('state').value, form=$('form').value;
  let list = D.clinics.map(c => ({c, y:yearOne(c,a,form), serves: st?servesState(c,st):true}))
    .filter(r => r.serves !== false)
    .filter(r => !form || r.c.forms.includes(form) || r.c.forms.length===0)
    .filter(r => !$('trtOnly').checked || !(r.c.forms.length===1 && r.c.forms[0]==='enclomiphene'))
    .filter(r => !$('labsInc').checked || r.c.labsIncluded===true)
    .filter(r => !$('noContract').checked || NO_CONTRACT.test(r.c.commitment));
  const key=$('sort').value;
  list.sort((p,q)=> key==='name'?p.c.name.localeCompare(q.c.name): key==='upfront'?(p.y.upfront??1e9)-(q.y.upfront??1e9) : p.y.total-q.y.total);
  const cheapest = list.length ? Math.min(...list.map(r=>r.y.total)) : 0;

  const openIds = [...document.querySelectorAll('#results details[open]')].map(d => d.closest('.card').id);
  $('countOnline').textContent = list.length;
  const incl = (label, v, yes, no) => `<li class="${v===true?'ok':v===false?'no':'unk'}"><i aria-hidden="true">${v===true?'✓':v===false?'✕':'?'}</i>${
    v===true ? yes : v===false ? no : label + ': not stated'}</li>`;
  $('results').innerHTML = list.length ? list.map(({c,y,serves}, i) => {
    const best = y.total===cheapest && key==='y1';
    return `<article class="card ${best?'best':''}" id="clinic-${c.id}">
      <div class="card-top">
        <div class="rank" aria-hidden="true">${i+1}</div>
        <div class="who">
          <h3>${c.name}</h3>
          <div class="tags">${best?'<span class="tag best">Lowest first-year cost</span>':''}<span class="tag model">${c.model}</span>${
            serves===null?'<span class="tag warn">Check your state</span>':''}${!c.verified?'<span class="tag warn">Unverified price</span>':''}${staleTag(c.checked)}</div>
        </div>
        <div class="cost"><span class="lbl">Est. first year</span><b>${usd(y.total)}</b><span class="mo">${c.monthly?usd(c.monthly)+'/mo':(c.monthlyLabel||'')}</span></div>
      </div>
      <ul class="inc" aria-label="What's included">
        ${incl('Labs', c.labsIncluded, 'Labs included', 'Labs extra')}
        ${incl('Medication', c.medsIncluded, 'Medication included', 'Medication extra')}
        ${incl('Estrogen blocker', c.aiIncluded, 'Estrogen blocker included', 'No estrogen blocker')}
        <li>${c.forms.length ? c.forms.map(f=>f[0].toUpperCase()+f.slice(1)).join(' · ') : 'Medication types not listed'}</li>
        <li>Start: ${y.upfront==null ? 'not published' : usd(y.upfront)}</li>
      </ul>
      <details class="more"><summary>Cost breakdown and fine print</summary>
        <div class="more-grid">
          <div><h4>How we got ${usd(y.total)}</h4><p class="breakdown">${y.parts.join(' + ')}</p>
            ${y.estimated?'<p class="note">* Uses your cost assumptions because the clinic doesn’t publish this cost.</p>':''}
            <h4>Contract</h4><p>${c.commitment}</p><h4>hCG</h4><p>${c.hcg}</p><h4>States</h4><p>${c.states}</p></div>
          <div><h4>What you get</h4><ul>${c.highlights.map(h=>`<li>${h}</li>`).join('')}</ul></div>
          <div><h4>Watch out for</h4><ul>${c.watchOuts.map(h=>`<li>${h}</li>`).join('')}</ul></div>
        </div>
      </details>
      <div class="card-foot">
        <span>Price checked ${fmtDate(c.checked)} · <a href="${c.sourceUrl}" target="_blank" rel="noopener">Source ↗</a></span>
        <a class="btn-sm" href="${c.url}" target="_blank" rel="noopener nofollow">Visit ${c.name} ↗</a>
      </div>
    </article>`;
  }).join('') : '<div class="panel empty">No clinics match. Try removing a filter.</div>';
  openIds.forEach(id => { const d = document.querySelector(`#${id} details`); if (d) d.open = true; });

  const labs=[...D.labs].sort((p,q)=>(p.price+p.fees)-(q.price+q.fees));   // cheapest first
  $('labRows').innerHTML = labs.map(l=>`<article class="lab">
    <h3>${l.test}</h3>
    <span class="by">${l.vendor} · ${l.lab} lab</span>
    <span class="total">${usd2(l.price+l.fees)}</span>
    <span class="fees">${l.fees ? `${usd2(l.price)} test + ${usd2(l.fees)} order fee` : 'No order fee'}</span>
    <div class="lab-foot"><span class="note" style="margin:0">Checked ${fmtDate(l.checked)}</span><a href="${l.sourceUrl}" target="_blank" rel="noopener">${l.verified?'Seller':'Source'} ↗</a></div>
  </article>`).join('');
  calcOverpay();
}
$('noPricing').innerHTML = (D.noPricing||[]).map(c=>`<li><a href="${c.url}" target="_blank" rel="noopener nofollow">${c.name}</a> — ${c.note} <span class="note">(checked ${c.checked})</span></li>`).join('');
function usd2(n){ return '$'+n.toFixed(2); }

// ---------- Price alerts ----------
$('alertForm').addEventListener('submit', async e=>{
  e.preventDefault();
  const msg=$('alertMsg'), user=D.buttondownUsername;
  if(!user){ msg.textContent='Alerts aren\u2019t live yet \u2014 this form is a preview.'; return; }
  const body=new FormData(e.target);
  if($('state').value) body.append('tag', $('state').value);   // lets us send state-specific alerts later
  try {
    await fetch(`https://buttondown.com/api/emails/embed-subscribe/${encodeURIComponent(user)}`, {method:'POST', body, mode:'no-cors'});
    msg.textContent='Almost done \u2014 check your inbox to confirm your email.'; e.target.reset();
  } catch(err){ msg.textContent='Something went wrong. Please try again.'; }
});

// ---------- Am I overpaying? ----------
// "No commitment listed" means the terms are unknown, so it doesn't count as no contract
const NO_CONTRACT = /no commitments?(?! listed)|no subscription|no contract|cancel anytime/i;
const assumptions = () => ({medCost:+$('medCost').value||0, labCost:+$('labCost').value||0, labsPerYear:+$('labsPerYear').value||0});
const onlyEnclo = c => c.forms.length===1 && c.forms[0]==='enclomiphene';
const DEFAULT_HINT = "Include the membership, medication and supplies. Leave out one-time fees you've already paid.";

$('opClinic').insertAdjacentHTML('beforeend',
  `<optgroup label="Online clinics">${D.clinics.filter(c=>!onlyEnclo(c)).map(c=>`<option value="${c.id}">${c.name}</option>`).join('')}</optgroup>` +
  `<optgroup label="In-person clinics">${D.inPerson.map(p=>`<option value="ip:${p.id}">${p.name}</option>`).join('')}</optgroup>`);

// Restore this visitor's last inputs (per-browser convenience only)
let opPrefilled = false, opLabsPrefilled = false;
try {
  const saved = JSON.parse(localStorage.getItem('trtCalc')||'null');
  if (saved) {
    if ([...$('opClinic').options].some(o=>o.value===saved.clinic)) $('opClinic').value = saved.clinic;
    $('opMonthly').value = saved.monthly||''; $('opLabs').value = saved.labs||'';
    $('opMed').value = saved.med||''; $('opNoContract').checked = !!saved.noContract;
    opPrefilled = !!saved.prefilled; opLabsPrefilled = !!saved.labsPrefilled;
  }
} catch(e){}

function opSave(){
  try { localStorage.setItem('trtCalc', JSON.stringify({clinic:$('opClinic').value, monthly:$('opMonthly').value, labs:$('opLabs').value,
    med:$('opMed').value, noContract:$('opNoContract').checked, prefilled:opPrefilled, labsPrefilled:opLabsPrefilled})); } catch(e){}
}

// One short line for screen readers, sent only after typing pauses and only when it changes
let announceTimer;
function announce(msg){
  clearTimeout(announceTimer);
  announceTimer = setTimeout(()=>{ if ($('opStatus').textContent !== msg) $('opStatus').textContent = msg; }, 700);
}

// What a current patient of clinic c pays, on the same basis yearOne() prices every other clinic
function prefillFor(c, a, med){
  if (c.ongoingMonthly) return {monthly:c.ongoingMonthly, labs:0,
    why:`${c.name}'s own average after the first year (${usd(c.ongoingMonthly)}/mo, labs and medication included)`};
  if (!c.monthly) return null;
  const base = (med && c.priceByForm && c.priceByForm[med]) || c.monthly;
  const meds = c.medsIncluded===true ? 0 : a.medCost;
  const labs = c.labsIncluded===true ? 0 : (c.labFee || a.labCost*a.labsPerYear);
  let why = `${c.name}'s listed ${usd(base)}/mo${c.prepaid ? ' (12-month prepaid plan)' : ''}`;
  if (meds) why += ` plus about ${usd(meds)}/mo for medication`;
  if (labs) why += `${meds ? ',' : ''} and about ${usd(labs)} a year for labs it doesn't include`;
  return {monthly: base+meds, labs, why};
}

function opPrefill(fromClinicChange){
  const id=$('opClinic').value, c=D.clinics.find(x=>x.id===id), pf = c && prefillFor(c, assumptions(), $('opMed').value);
  let hint = id.startsWith('ip:') ? 'Include visit fees, medication and supplies, averaged per month.' : DEFAULT_HINT;
  if (pf) {
    if (opPrefilled || !$('opMonthly').value) {
      $('opMonthly').value = Math.round(pf.monthly); opPrefilled = true;
      if (opLabsPrefilled || !$('opLabs').value) { $('opLabs').value = pf.labs ? Math.round(pf.labs) : ''; opLabsPrefilled = true; }
      hint = `Filled in with ${pf.why}. Change these to what you actually pay.`;
      if (fromClinicChange) announce(`Filled in ${usd(pf.monthly)} a month from ${c.name}'s listed price.`);
    } else {
      hint = `For reference: ${pf.why} comes to about ${usd(pf.monthly)}/mo${pf.labs ? ` plus ${usd(pf.labs)}/yr for labs` : ''}. Keep your own numbers if they're different.`;
    }
  } else {
    if (c && c.clinicYear1Estimate) hint = `${c.name} only publishes a first-year average, which includes startup fees. Enter what you pay now.`;
    // don't leave another clinic's numbers in the boxes
    if (opPrefilled) { $('opMonthly').value=''; opPrefilled=false; }
    if (opLabsPrefilled) { $('opLabs').value=''; opLabsPrefilled=false; }
  }
  $('opHint').textContent = hint;
}

let opLastHtml = '';
function calcOverpay(){
  const el=$('opResult'), st=$('state').value, med=$('opMed').value;
  $('opState').textContent = st ? NAMES[st] : 'not set';
  if (opPrefilled || opLabsPrefilled) opPrefill();   // keep prefilled numbers in step with the assumptions
  opSave();
  const monthly=Math.max(0,+$('opMonthly').value||0), labs=Math.max(0,+$('opLabs').value||0);
  const show = html => {
    if (html === opLastHtml) return;                   // nothing changed: don't rebuild (keeps <details> state)
    const open = el.querySelector('details')?.open;
    el.innerHTML = opLastHtml = html;
    if (open && el.querySelector('details')) el.querySelector('details').open = true;
  };
  if (!monthly) {
    show(`<h3>See how your price compares</h3><p class="note">Enter what you pay each month. Your numbers stay in your browser.</p>`);
    announce(''); return;
  }
  const a=assumptions(), mine=Math.round(monthly*12+labs), cur=$('opClinic').value;
  const all = D.clinics.filter(c=>!onlyEnclo(c) && c.id!==cur)
    .map(c=>{ const y=yearOne(c,a,med); return {c, y, cost:Math.round(y.total), serves: st?servesState(c,st):null}; })
    .filter(r=>r.serves!==false)
    .filter(r=>!med || r.c.forms.length===0 || r.c.forms.includes(med))
    .filter(r=>!$('opNoContract').checked || NO_CONTRACT.test(r.c.commitment))
    .sort((p,q)=>p.cost-q.cost);
  if (!all.length) {
    show(`<h3>No matching clinics</h3><p class="note">None of the clinics we track match these filters. Try "Any" medication or allow contracts.</p>`);
    announce('No matching clinics.'); return;
  }
  // Verdicts only come from clinics confirmed to serve the state and offer the chosen medication
  const sure = r => (!st || r.serves===true) && (!med || r.c.forms.includes(med));
  const conf = all.filter(sure), unsure = all.filter(r=>!sure(r));
  const where = st ? `confirmed to serve ${NAMES[st]}` : 'we track';
  const tags = r => [
    st && r.serves===null ? '<span class="tag warn">Check your state</span>' : '',
    med && !r.c.forms.length ? '<span class="tag warn">Medications not listed</span>' : '',
    !r.c.verified ? '<span class="tag warn">Unverified price</span>' : '',
    r.c.prepaid ? `<span class="tag warn">${usd(r.c.prepaid)} paid upfront</span>` : '',
    r.c.clinicYear1Estimate ? '<span class="tag model">Clinic’s own estimate</span>' : '',
    r.y.estimated ? '<span class="tag model">Uses your assumptions</span>' : '',
    staleTag(r.c.checked)].join(' ');
  const best = conf[0], save = best ? mine - best.cost : null;

  let eyebrow, big, line;
  if (!best) {
    eyebrow = 'We can’t confirm a match'; big = usd(mine);
    line = `a year. None of the clinics we track ${st ? `confirm they serve ${NAMES[st]}` : 'list'}${med ? ` and offer ${med} treatment` : ''}. The ones below might — check with them.`;
  } else if (save >= 120) {
    eyebrow = 'You could save up to'; big = usd(save);
    line = `a year by switching to <b>${best.c.name}</b> — about ${usd(best.cost)} in the first year vs. the ${usd(mine)} you pay now. ${tags(best)}`;
  } else if (save > 0) {
    eyebrow = 'You’re paying about the going rate'; big = usd(mine);
    line = `a year. The cheapest clinic ${where}, <b>${best.c.name}</b>, would save you only about ${usd(save)} a year. ${tags(best)}`;
  } else if (save === 0) {
    eyebrow = 'You’re paying the going rate'; big = usd(mine);
    line = `a year — the same as the cheapest clinic ${where}, <b>${best.c.name}</b>.`;
  } else {
    eyebrow = 'Good news — you’re not overpaying'; big = usd(mine);
    line = `a year, which is less than every clinic ${where} that matches your filters. The cheapest is <b>${best.c.name}</b> at about ${usd(best.cost)}.`;
  }
  const maybe = unsure.find(r => r.cost < mine && (!best || r.cost < best.cost));
  const maybeLine = maybe ? `<p class="note">${maybe.c.name} might cost less (about ${usd(maybe.cost)} a year), but it doesn’t list ${
    st && maybe.serves===null ? 'which states it serves' : 'which medications it offers'} — confirm with them before switching.</p>` : '';
  const cheaperConf = conf.filter(r=>r.cost<mine), cheaperUnsure = unsure.filter(r=>r.cost<mine);
  const rank = `${cheaperConf.length} of ${conf.length} clinics ${where} cost less than you pay.` +
    (unsure.length ? ` ${unsure.length} more can’t be confirmed${st ? ` for ${NAMES[st]}` : ''}${med ? ' or your medication' : ''}.` : '') +
    (st ? '' : ' <a href="#top" data-focus="zip">Enter your ZIP or state</a> to only see clinics that can treat you.');

  // Emphasis chart: "You" in --hl, clinics in de-emphasis gray, sorted low to high
  const items = all.map(r=>({name:r.c.name, v:r.cost, r})).concat([{name:'You now', v:mine, you:true}]).sort((p,q)=>p.v-q.v);
  const max = Math.max(...items.map(i=>i.v));
  const bars = items.map(i=>{
    const diff = i.you ? 'What you pay now, per year' :
      `${usd(i.v)} est. first year · ${i.v<mine ? usd(mine-i.v)+' less than you' : i.v>mine ? usd(i.v-mine)+' more than you' : 'same as you'}${sure(i.r) ? '' : ' · not confirmed for your filters'}`;
    return `<li class="barrow ${i.you?'you':''}">
      <span class="nm">${i.name}${!i.you && !sure(i.r) ? ' <small>(unconfirmed)</small>' : ''}</span>
      <span class="track"><span class="bar" style="--r:${(i.v/max).toFixed(4)}"></span><span class="val">${usd(i.v)}</span></span>
      <span class="sr">${diff}</span><span class="tip" aria-hidden="true">${diff}</span></li>`;
  }).join('');

  const labsTxt = c => c.clinicYear1Estimate ? 'labs and meds as the clinic counts them' :
    c.labsIncluded===true ? 'labs included' : c.labsIncluded===false ? 'labs extra' : 'labs unclear';
  const picks = cheaperConf.concat(cheaperUnsure).slice(0,3).map(r=>`<div class="pick">
      <div><b>${r.c.name}</b> ${tags(r)}</div><div class="save">Save ${usd(mine-r.cost)}/yr</div>
      <div class="sub2">${usd(r.cost)} first year · ${labsTxt(r.c)} · ${r.c.commitment} ·
        <a href="#clinic-${r.c.id}" data-goto="${r.c.id}">Details</a> · <a href="${r.c.url}" target="_blank" rel="noopener nofollow">Visit ↗</a></div>
    </div>`).join('');

  const shareText = save >= 120 ? `I could save ${usd(save)} a year on TRT. See what clinics really cost:` : `I checked my TRT costs against the online clinics. See what they really cost:`;
  show(`
    <div class="eyebrow">${eyebrow}</div>
    <div class="hero-num">${big}</div>
    <p>${line}</p>
    ${maybeLine}
    <p class="note">${rank}</p>
    <ul class="bars" aria-label="Yearly cost: you vs. each clinic">${bars}</ul>
    ${picks ? `<div class="picks">${picks}</div>` : ''}
    <p class="note" style="margin-top:12px">Clinic figures are first-year estimates that include startup fees.
      Where a clinic doesn't publish a cost we use your assumptions (meds ${usd(a.medCost)}/mo, labs ${usd(a.labCost)} × ${a.labsPerYear} a year) — <a href="#compare" data-goto="assumptions">change them</a>. Add-ons like hCG aren't compared.</p>
    <details><summary>Before you switch</summary><ul>
      <li>Check whether you'd lose money left on a prepaid plan.</li>
      <li>Ask whether the new clinic will continue your current dose and medication.</li>
      <li>Most clinics need recent labs — ask whether yours are accepted.</li>
      <li>Don't stop treatment between clinics without talking to a clinician.</li></ul></details>
    <div class="opactions">
      <button type="button" data-share="${shareText.replace(/"/g,'&quot;')}">Share my result</button>
      <a class="btn2" href="#alerts">Alert me if a cheaper clinic appears</a>
      <span class="note" id="shareMsg" role="status"></span>
    </div>`);
  announce(`${eyebrow} ${big}${eyebrow.startsWith('You could') ? ' a year' : ''}.`);
}

$('opMonthly').addEventListener('input', ()=>{ opPrefilled=false; });
$('opLabs').addEventListener('input', ()=>{ opLabsPrefilled=false; });
$('opClinic').addEventListener('input', ()=>opPrefill(true));
$('opForm').addEventListener('submit', e=>e.preventDefault());
$('opResult').addEventListener('click', async e=>{
  const go = e.target.closest('[data-goto]');
  if (go) {
    e.preventDefault();
    if ($('compare').hidden) $('tabOnline').click();
    if (go.dataset.goto === 'assumptions') {
      $('assume').open = true;
      $('assume').scrollIntoView({behavior:SCROLL, block:'center'});
      $('medCost').focus({preventScroll:true});
      return;
    }
    let card = $('clinic-'+go.dataset.goto);
    if (!card) {   // hidden by the Compare filters: clear the ones that can hide it
      $('labsInc').checked = false; $('noContract').checked = false; $('form').value = '';
      render(); card = $('clinic-'+go.dataset.goto);
    }
    if (!card) { $('compare').scrollIntoView({behavior:SCROLL}); return; }
    card.setAttribute('tabindex','-1');
    card.scrollIntoView({behavior:SCROLL, block:'start'});
    card.focus({preventScroll:true});
    return;
  }
  const sh = e.target.closest('[data-share]');
  if (!sh) return;
  const url = location.origin + location.pathname + '#overpaying', text = sh.dataset.share;
  try {
    if (navigator.share) { await navigator.share({title:'TRT Ledger', text, url}); return; }
    await navigator.clipboard.writeText(`${text} ${url}`);
    $('shareMsg').textContent = 'Copied — paste it anywhere.';
  } catch(err) {
    if (err.name !== 'AbortError') $('shareMsg').textContent = 'Couldn’t copy. Share this page’s link instead.';
  }
});
if ($('opClinic').value) opPrefill();

// ---------- State finder ----------
const NAMES={AL:"Alabama",AK:"Alaska",AZ:"Arizona",AR:"Arkansas",CA:"California",CO:"Colorado",CT:"Connecticut",DE:"Delaware",FL:"Florida",GA:"Georgia",HI:"Hawaii",ID:"Idaho",IL:"Illinois",IN:"Indiana",IA:"Iowa",KS:"Kansas",KY:"Kentucky",LA:"Louisiana",ME:"Maine",MD:"Maryland",MA:"Massachusetts",MI:"Michigan",MN:"Minnesota",MS:"Mississippi",MO:"Missouri",MT:"Montana",NE:"Nebraska",NV:"Nevada",NH:"New Hampshire",NJ:"New Jersey",NM:"New Mexico",NY:"New York",NC:"North Carolina",ND:"North Dakota",OH:"Ohio",OK:"Oklahoma",OR:"Oregon",PA:"Pennsylvania",RI:"Rhode Island",SC:"South Carolina",SD:"South Dakota",TN:"Tennessee",TX:"Texas",UT:"Utah",VT:"Vermont",VA:"Virginia",WA:"Washington",WV:"West Virginia",WI:"Wisconsin",WY:"Wyoming"};
// First 3 digits of a ZIP -> state (USPS prefix ranges; territories and military omitted)
const ZIP3=[[5,5,"NY"],[10,27,"MA"],[28,29,"RI"],[30,38,"NH"],[39,49,"ME"],[50,54,"VT"],[55,55,"MA"],[56,59,"VT"],[60,69,"CT"],[70,89,"NJ"],[100,149,"NY"],[150,196,"PA"],[197,199,"DE"],[201,201,"VA"],[206,219,"MD"],[220,246,"VA"],[247,268,"WV"],[270,289,"NC"],[290,299,"SC"],[300,319,"GA"],[320,339,"FL"],[341,349,"FL"],[350,369,"AL"],[370,385,"TN"],[386,397,"MS"],[398,399,"GA"],[400,427,"KY"],[430,459,"OH"],[460,479,"IN"],[480,499,"MI"],[500,528,"IA"],[530,549,"WI"],[550,567,"MN"],[570,577,"SD"],[580,588,"ND"],[590,599,"MT"],[600,629,"IL"],[630,658,"MO"],[660,679,"KS"],[680,693,"NE"],[700,714,"LA"],[716,729,"AR"],[730,732,"OK"],[733,733,"TX"],[734,749,"OK"],[750,799,"TX"],[800,816,"CO"],[820,831,"WY"],[832,838,"ID"],[840,847,"UT"],[850,865,"AZ"],[870,884,"NM"],[885,885,"TX"],[889,898,"NV"],[900,961,"CA"],[967,968,"HI"],[970,979,"OR"],[980,994,"WA"],[995,999,"AK"]];
function zipToState(zip){
  if(!/^\d{5}$/.test(zip)) return null;
  const n=+zip.slice(0,3), hit=ZIP3.find(([lo,hi])=>n>=lo&&n<=hi);
  return hit ? hit[2] : null;
}
let currentZip='';
const isTRT = c => !(c.forms.length===1 && c.forms[0]==='enclomiphene');

function stateInfo(st){
  const online = D.clinics.filter(isTRT).map(c=>({c, s:servesState(c,st)}));
  const ip = D.inPerson.map(p=>{
    const n = p.locations[st]||0;
    const status = n ? 'confirmed' : p.statesReported.includes(st) ? 'reported' : p.everywhere ? 'likely' : 'none';
    return {p, n, status};
  });
  return {
    onlineYes: online.filter(o=>o.s===true).length,
    onlineCheck: online.filter(o=>o.s===null).length,
    ipConfirmed: ip.filter(i=>i.status==='confirmed').reduce((a,i)=>a+i.n,0),
    ip
  };
}

// ---------- Clinics near a ZIP (nationwide directory, see pipeline/) ----------
const CAT_LABEL = {trt:"TRT / men's clinic", hormone:'Hormone clinic', urology:'Urology', endocrinology:'Endocrinology'};
const CAT_RANK = {trt:0, hormone:1, urology:2, endocrinology:3};
const near = {limit:20, cats:new Set(Object.keys(CAT_LABEL)), token:0};
const jsonCache = new Map();
function getJSON(url){
  if (!jsonCache.has(url)) jsonCache.set(url, fetch(url).then(r=>{ if(!r.ok) throw new Error(r.status); return r.json(); })
    .catch(e=>{ jsonCache.delete(url); throw e; }));
  return jsonCache.get(url);
}
function miles(lat1, lon1, lat2, lon2){
  const t=Math.PI/180, x=Math.sin((lat2-lat1)*t/2)**2 + Math.cos(lat1*t)*Math.cos(lat2*t)*Math.sin((lon2-lon1)*t/2)**2;
  return 7917.6*Math.asin(Math.sqrt(x));
}
async function zipLatLon(zip){
  const centers = await getJSON('geo/zip3-centroids.json');
  if (!centers[zip.slice(0,3)]) return null;   // no Census ZIP areas with this prefix (e.g. IRS-only ZIPs)
  try { const shard = await getJSON(`geo/zip3/${zip.slice(0,3)}.json`); if (shard[zip]) return shard[zip]; } catch(e){}
  return centers[zip.slice(0,3)];   // PO-box ZIPs: use the area's center
}
const telLink = p => p ? `<a href="tel:+1${p.replace(/\D/g,'').slice(-10)}">${p}</a>` : '';
const esc = s => String(s??'').replace(/[&<>"]/g, c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));

async function searchNear(){
  const tok = ++near.token, list = $('nearList'), R = +$('nearRadius').value;
  const done = html => {
    if (tok !== near.token) return;
    list.innerHTML = html; $('nearMore').hidden = true;
    $('countInperson').textContent = ''; $('nearChips').innerHTML = ''; $('nearStatus').textContent = '';
    const nc = $('nearCount'); if (nc) nc.textContent = '\u2014';
  };
  if (!currentZip) {
    $('nearTitle').textContent = 'Clinics near you'; $('nearChips').innerHTML = ''; $('nearNote').textContent = ''; $('countInperson').textContent = '';
    return done('<li class="note">Enter your ZIP code above to see TRT clinics, hormone clinics, urologists and endocrinologists near you.</li>');
  }
  $('nearTitle').textContent = `Clinics within ${R} miles of ${currentZip}`;
  let here, idx, rows;
  try {
    [here, idx] = await Promise.all([zipLatLon(currentZip), getJSON('clinics/index.json')]);
    if (!here) return done('<li class="note">We couldn’t locate that ZIP code.</li>');
    const [lat, lon] = here;
    // only download the ZIP-prefix files whose clinics could fall inside the radius
    const shards = Object.entries(idx.shards).filter(([, [, a, b, c, d]]) =>
      miles(lat, lon, Math.min(Math.max(lat, a), c), Math.min(Math.max(lon, b), d)) <= R).map(([z]) => z);
    rows = (await Promise.all(shards.map(z => getJSON(`clinics/${z}.json`)))).flat()
      .map(r => ({...r, mi: miles(lat, lon, r.lat, r.lon)})).filter(r => r.mi <= R);
  } catch(e) {
    return done('<li class="note">Couldn’t load the clinic directory. Check your connection and try again.</li>');
  }
  if (tok !== near.token) return;

  $('countInperson').textContent = rows.length.toLocaleString();
  $('nearStatus').textContent = `${rows.length.toLocaleString()} clinics within ${R} miles of ${currentZip}.`;
  const nc = $('nearCount'); if (nc) { nc.textContent = rows.length.toLocaleString(); $('nearCountLbl').textContent = `in-person clinics within ${R} mi`; }
  $('nearChips').innerHTML = Object.entries(CAT_LABEL).map(([c, label]) =>
    `<label class="chip"><input type="checkbox" value="${c}" ${near.cats.has(c)?'checked':''}> ${label} <span class="n">${rows.filter(r=>r.cats.includes(c)).length}</span></label>`).join('');
  const byType = $('nearSort').value === 'type';
  const shown = rows.filter(r => r.cats.some(c => near.cats.has(c)))
    .sort((a, b) => (byType ? CAT_RANK[a.cats[0]] - CAT_RANK[b.cats[0]] : 0) || a.mi - b.mi || CAT_RANK[a.cats[0]] - CAT_RANK[b.cats[0]]);
  if (!shown.length) {
    done(`<li class="note">No clinics of these types within ${R} miles. Try a wider radius or more clinic types.</li>`);
  } else {
    list.innerHTML = shown.slice(0, near.limit).map(r => {
      const chain = r.chain && D.inPerson.find(p => p.id === r.chain);
      const where = [r.addr, r.city, `${r.st} ${r.zip}`].filter(Boolean).join(', ');
      const maps = 'https://www.google.com/maps/search/?api=1&query=' + encodeURIComponent(`${r.name}, ${where}`);
      const docs = r.ndocs > 1 ? `${r.ndocs} doctors: ${r.docs.slice(0,3).map(esc).join(', ')}${r.ndocs>3?', …':''}`
                 : r.ndocs === 1 && r.docs[0] !== r.name ? esc(r.docs[0]) : '';
      return `<li class="near">
        <div><b>${esc(r.name)}</b> ${r.cats.map(c=>`<span class="tag ${c==='trt'?'trt':'model'}">${CAT_LABEL[c]}</span>`).join(' ')}</div>
        <div class="dist">${r.mi < 1 ? 'In your area' : (r.mi < 10 ? r.mi.toFixed(1) : Math.round(r.mi)) + ' mi'}</div>
        <div class="row">${esc(where)}${r.phone ? ' · ' + telLink(esc(r.phone)) : ''} · <a href="${maps}" target="_blank" rel="noopener">Map ↗</a>${r.url ? ` · <a href="${esc(r.url)}" target="_blank" rel="noopener nofollow">Website ↗</a>` : ''}</div>
        ${docs ? `<div class="row">${docs}</div>` : ''}
        ${chain && !/^Not published/.test(chain.pricing) ? `<div class="row"><b>Pricing:</b> ${chain.pricing}</div>` : ''}
      </li>`;
    }).join('');
    $('nearMore').hidden = shown.length <= near.limit;
    $('nearMore').textContent = `Show more (${(shown.length - near.limit).toLocaleString()} left)`;
  }
  $('nearNote').innerHTML = `Distances are approximate (ZIP to ZIP). Urologists, endocrinologists and hormone clinics come from the federal
    <a href="https://npiregistry.cms.hhs.gov/" target="_blank" rel="noopener">NPI registry</a> — not all of them offer TRT, so call and ask.
    TRT clinics are matched by name or from each chain's own location list. Directory updated ${idx.updated}.`;
}
$('nearChips').addEventListener('change', e => {
  if (e.target.checked) near.cats.add(e.target.value); else near.cats.delete(e.target.value);
  near.limit = 20; searchNear();
});
$('nearRadius').addEventListener('change', () => { near.limit = 20; searchNear(); });
$('nearSort').addEventListener('change', () => { near.limit = 20; searchNear(); });
$('nearMore').addEventListener('click', () => { near.limit += 20; searchNear(); });

function drawSummary(st){
  if(!st){
    $('summary').innerHTML = `<div><h3>Where do you live?</h3><p class="lead">Enter your ZIP code above, or choose a state, to see only the clinics that can treat you.</p></div>`;
    $('countInperson').textContent = '';
    $('ipResults').innerHTML = '<div class="panel empty">Pick a state to see which clinic chains operate there.</div>';
    return;
  }
  const i=stateInfo(st), where=currentZip||NAMES[st], q=encodeURIComponent('testosterone replacement therapy clinic near '+where);
  $('summary').innerHTML = `<div><h3>TRT in ${NAMES[st]}${currentZip?` <span class="note">near ${currentZip}</span>`:''}</h3>
      <p class="lead">"Check state" means a clinic doesn't publish which states it serves.</p></div>
    <div class="stats">
      <div class="stat"><b>${i.onlineYes}</b><span>online clinics confirmed</span></div>
      <div class="stat"><b>${i.onlineCheck}</b><span>online — check state</span></div>
      ${currentZip ? `<div class="stat"><b id="nearCount">…</b><span id="nearCountLbl">in-person clinics within ${$('nearRadius').value} mi</span></div>`
                   : `<div class="stat"><b>${i.ipConfirmed}</b><span>chain clinic locations</span></div>`}
    </div>
    <div class="actions">
      ${currentZip ? `<button type="button" id="seeNear">See in-person clinics near ${currentZip}</button>` : ''}
      <a class="maps" href="https://www.google.com/maps/search/${q}" target="_blank" rel="noopener">Search Google Maps ↗</a>
    </div>`;

  const order={confirmed:0,reported:1,likely:2,none:3};
  const rows=i.ip.filter(r=>r.status!=='none').sort((a,b)=>order[a.status]-order[b.status]||b.n-a.n);
  const label={confirmed:n=>`<span class="tag ok">${n} location${n>1?'s':''} in ${st}</span>`, reported:()=>'<span class="tag warn">Reported in '+st+' — confirm</span>', likely:()=>'<span class="tag model">Nationwide franchise — check locator</span>'};
  $('ipResults').innerHTML = (rows.length ? rows.map(({p,n,status})=>`<article class="ip">
      <h3>${p.name} ${label[status](n)}</h3>
      <div class="row"><b>Pricing:</b> ${p.pricing}${p.pricingSource?` · <a href="${p.pricingSource}" target="_blank" rel="noopener">source ↗</a>`:''}</div>
      <div class="row">${p.notes} · checked ${fmtDate(p.checked)}</div>
      <div class="row"><a href="${p.locatorUrl}" target="_blank" rel="noopener nofollow">Find a ${p.name} location ↗</a></div>
    </article>`).join('') : '<div class="panel empty">No tracked chains have confirmed locations here yet.</div>')
    + `<div class="panel"><b>Still not finding one?</b><p class="note" style="margin:4px 0 12px">Most primary care doctors can also test for and treat low testosterone.</p><a class="maps" href="https://www.google.com/maps/search/${q}" target="_blank" rel="noopener">Search near ${where} on Google Maps ↗</a></div>`;
}

function setState(st, scroll){
  $('state').value = st||''; $('stateTop').value = st||'';
  try { st ? localStorage.setItem('trtState',st) : localStorage.removeItem('trtState'); } catch(e){}
  if (!location.hash || /^#state=/.test(location.hash)) history.replaceState(null,'', st ? '#state='+st : location.pathname);
  drawSummary(st); render(); searchNear();
  if(scroll) $('summary').scrollIntoView({behavior:SCROLL,block:'nearest'});
}

STATES.forEach(s => $('stateTop').insertAdjacentHTML('beforeend', `<option value="${s}">${NAMES[s]}</option>`));
$('zip').addEventListener('input', e=>{ e.target.value=e.target.value.replace(/\D/g,'').slice(0,5); if(e.target.value.length===5) $('zipForm').requestSubmit(); });
$('zipForm').addEventListener('submit', e=>{
  e.preventDefault();
  const zip=$('zip').value, st=zipToState(zip), msg=$('zipMsg');
  if(!st){ msg.textContent = zip.length<5 ? 'Enter a 5-digit ZIP code.' : 'We couldn\u2019t match that ZIP to a U.S. state. Pick your state below.'; msg.className='note err'; $('zip').setAttribute('aria-invalid','true'); return; }
  $('zip').removeAttribute('aria-invalid');
  currentZip=zip; msg.textContent=`${zip} is in ${NAMES[st]}.`; msg.className='note';
  try { localStorage.setItem('trtZip',zip); } catch(e){}
  setState(st, true);
});
$('stateTop').addEventListener('input', ()=>{ currentZip=''; $('zip').value=''; $('zipMsg').textContent='Your ZIP stays in your browser.'; $('zipMsg').className='note'; try{localStorage.removeItem('trtZip')}catch(e){} setState($('stateTop').value, true); });
$('summary').addEventListener('click', e=>{
  if (e.target.id !== 'seeNear') return;
  $('tabInperson').click();
  $('nearPanel').scrollIntoView({behavior:SCROLL, block:'start'});
});
const tabs = [...document.querySelectorAll('.seg [role="tab"]')];
tabs.forEach((t, i) => t.addEventListener('keydown', e => {
  const to = {ArrowRight: i+1, ArrowLeft: i-1, Home: 0, End: tabs.length-1}[e.key];
  if (to === undefined) return;
  e.preventDefault();
  const next = tabs[(to + tabs.length) % tabs.length];
  next.click(); next.focus();
}));
document.querySelectorAll('.seg button').forEach(b=>b.addEventListener('click',()=>{
  document.querySelectorAll('.seg button').forEach(x=>{ x.setAttribute('aria-selected', x===b); x.tabIndex = x===b ? 0 : -1; });
  const ip = b.dataset.tab==='inperson';
  $('inpersonPane').hidden = !ip; $('compare').hidden = ip;
}));

document.querySelectorAll('select,input:not(#alertEmail):not(#zip)').forEach(el=>el.addEventListener('input',render));
$('state').addEventListener('input', ()=>{
  currentZip=''; $('zip').value=''; $('zipMsg').textContent='Your ZIP stays in your browser.'; $('zipMsg').className='note';
  try{localStorage.removeItem('trtZip')}catch(e){}
  setState($('state').value);
});
// "change your state" links go to the search box at the top and put the cursor in it
document.addEventListener('click', e=>{
  if (e.target.closest('[data-focus="zip"]')) setTimeout(()=>$('zip').focus({preventScroll:true}), 350);
});

const startHash = location.hash;
let initial = (startHash.match(/state=([A-Z]{2})/)||[])[1];
if(!initial){ try { initial = localStorage.getItem('trtState'); } catch(e){} }
try { const z=localStorage.getItem('trtZip'); if(z && zipToState(z)===initial){ currentZip=z; $('zip').value=z; } } catch(e){}
setState(NAMES[initial] ? initial : '');
if (startHash && !/^#state=/.test(startHash)) document.getElementById(startHash.slice(1))?.scrollIntoView();
