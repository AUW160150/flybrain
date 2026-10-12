'use strict';
const M=JSON.parse(document.getElementById('model').textContent);
const N=new Map(M.nodes.map(n=>[n.body_id,n]));
const $=id=>document.getElementById(id), esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const GROUPS=[['LB3b','LB3b'],['LB3c','LB3c'],['other','Other LB3'],['GNG042','Quasimodo / GNG042'],['GNG015','GNG015'],['GNG021','GNG021'],['GNG232','GNG232 / G2N-1'],['DNg67','Fudog / DNg67'],['DNge080','Rounddown / DNge080']];
const MORE=[['ANXXX462a','Clavicle / ANXXX462a'],['GNG585','Sternum / GNG585'],['GNG108','Roundup / GNG108'],['GNG120','Roundtree / GNG120'],['GNG472','GNG472']];
const CT=['GNG042','GNG015','GNG021','GNG232','DNg67','DNge080'];
const MOTORS=['MN4a','MN6','MN8','MN9'];
let view='paper',panel='lb3b_only',clicked=null,current={nodes:[],edges:[]};
const badges=n=>n.evidence.map(x=>`<span class="badge" title="${esc(n.evidence_sources[x])}">${x}</span>`).join('');
function checks(target,items){$(target).innerHTML=items.map(([v,label])=>`<label class="check"><input type="checkbox" data-type="${v}" ${['LB3c','GNG042','GNG015',...MOTORS].includes(v)?'checked':''}>${label}</label>`).join('');}
checks('groups',GROUPS);checks('paperGroups',MORE);checks('motors',MOTORS.map(t=>[t,t]));
$('legend').innerHTML='<h2>Biological role fill</h2>'+Object.entries(M.palette).map(([role,c])=>`<div><span class="swatch" style="background:${c}"></span>${esc(role.replace('_',' '))}</div>`).join('')+'<p class="muted">Candidate status uses outlines and badges. Gray includes bodies whose biological order is unverified.</p>';
$('discrepancies').innerHTML='<table><tr><th>Motif</th><th>Paper label</th><th>Current raw sum</th><th>Difference</th></tr>'+M.paper_comparisons.map(r=>`<tr><td>${esc(r.source_type)} → ${esc(r.target_type)}</td><td>${r.paper_figure6_label}</td><td>${r.current_all_body_sum}</td><td>${r.difference}</td></tr>`).join('')+'</table>';
function selectedTypes(){return new Set([...document.querySelectorAll('[data-type]:checked')].flatMap(x=>x.dataset.type==='other'?['LB3a','LB3d']:[x.dataset.type]));}
function computeDisplay(){
 const types=selectedTypes(),side=$('side').value,evidence=$('evidence').value,min=Math.max(1,Number($('minimum').value)||1);
 let nodes=[],edges=[],note='',label='RAW STRUCTURAL';
 const eligible=n=>(side==='both'||n.side===side)&&(evidence==='all'||n.evidence.includes(evidence));
 if(view==='sugar'){
  label='SUGAR-RESTRICTED EFFECTIVE-CONNECTIVITY';const conditions=M.selected_results.conditions;
  if(!Object.keys(conditions).length)return{nodes:[],edges:[],label,note:'BLOCKED — VALIDATED RESULTS REQUIRED\nThis panel contains no algorithm-selected membership. Raw structural reachability is not substituted.'};
  if(panel==='difference'){
   const A=new Set(conditions.lb3b_only.node_ids),B=new Set(conditions.lb3c_only.node_ids),C=new Set(conditions.lb3b_lb3c_combined.node_ids);
   const ids=new Set([...A,...B,...C]);nodes=[...ids].map(id=>({...N.get(id),difference:A.has(id)&&B.has(id)?'A∩B':A.has(id)?'A only':B.has(id)?'B only':'C only',combined:C.has(id)}));
   const em=new Map();for(const [key,c] of Object.entries(conditions))for(const e of c.edges){const id=e.source+'>'+e.target;if(!em.has(id))em.set(id,{...e,effective_connectivity_score:null,scores:{}});em.get(id).scores[key]=e.effective_connectivity_score;}edges=[...em.values()];
   note='D compares the independently validated sets. C-only membership is computed, never assumed absent. Edge hover lists per-condition scores.';
   if($('weight').value==='effective')return{nodes:[],edges:[],label,note:'A difference view has multiple condition-specific scores. Select A, B, or C to size by its effective score, or choose raw count for D. No scores were pooled.'};
  }else{const c=conditions[panel];nodes=c.node_ids.map(id=>N.get(id));edges=c.edges;}
  nodes=nodes.filter(n=>eligible(n)&&(!MOTORS.includes(n.type)||types.has(n.type)));
 }else{
  label=view==='paper'?'PAPER-ASSOCIATED':view==='candidate'?'CANDIDATE':'RAW STRUCTURAL';
  nodes=M.nodes.filter(n=>eligible(n)&&(view==='candidate'?CT.includes(n.type):types.has(n.type)));
  if(view==='paper')nodes=nodes.filter(n=>n.paper_counterpart);
  edges=M.edges.filter(e=>(view!=='paper'||e.paper_associated)&&(evidence!=='P'||e.paper_associated));
  if($('weight').value==='effective')return{nodes:[],edges:[],label,note:'Effective-connectivity scores are unavailable for this raw/paper/candidate view. Choose raw synapse count, or a validated sugar-selection panel. No raw values are substituted.'};
 }
 const ids=new Set(nodes.map(n=>n.body_id));
 edges=edges.filter(e=>ids.has(e.source)&&ids.has(e.target)&&e.raw_synapse_count>=min);
 if($('focus').checked&&clicked)edges=edges.filter(e=>e.source===clicked||e.target===clicked);
 if(!nodes.length)note='No nodes have the requested evidence/side in this view. Unverified support is not a negative result.';
 if(view==='paper')note+='\nPuddle: UNRESOLVED. Only saved mapped paper motifs are drawn. MN6 may be isolated in this motif subset.';
 if(view==='raw')note+='\nScoped induced raw graph on requested bodies; this is neither a complete connectome nor the selected sugar pathway.';
 return{nodes,edges,label,note:note.trim()};
}
function showDetails(id){
 clicked=id;const n=N.get(id);if(!n)return;
 const ins=M.edges.filter(e=>e.target===id),outs=M.edges.filter(e=>e.source===id);
 const fields={'Body ID':id,'Type':n.type,'Aliases':n.aliases||'none supplied','Side':n.side+' (from '+n.side_source+')','Soma / root side':(n.soma_side||'unknown')+' / '+(n.root_side||'unknown'),'Biological role':n.role+'; '+n.role_source,'Raw incoming / outgoing weights in frozen export':n.raw_export_incoming_weight+' / '+n.raw_export_outgoing_weight,'Weight scope':n.weight_scope,'Raw incoming / outgoing in small explorer universe':ins.reduce((a,e)=>a+e.raw_synapse_count,0)+' / '+outs.reduce((a,e)=>a+e.raw_synapse_count,0),'Predicted neurotransmitter':n.predicted_neurotransmitter,'Prediction confidence':n.nt_confidence||'unknown','Consensus neurotransmitter':n.consensus_neurotransmitter,'Paper status':n.paper_status,'Effective-connectivity status':n.effective_connectivity_status,'Shiu status':n.shiu_status,'Experimental status':n.experimental_status,'Dataset / UUID':n.dataset+' / '+n.dataset_uuid,'Source / provenance':[n.source_file,n.annotation_provenance,n.nt_provenance,JSON.stringify(n.evidence_sources,null,2)].join('\n')};
 $('details').innerHTML=`<h3>${esc(n.display_alias||n.type)} · ${esc(n.side)}</h3>${badges(n)}<p class="nt-note">PREDICTED TRANSMITTER — NOT DIRECT PHYSIOLOGICAL VALIDATION</p><dl>`+Object.entries(fields).map(([k,v])=>`<dt>${esc(k)}</dt><dd>${esc(v)}</dd>`).join('')+'</dl>';
 if($('focus').checked)render();
}
function layout(nodes){
 const pos=new Map(),layers=['sensory','second_order','unknown','higher_order','premotor','motor'];let y=135;
 for(const role of layers){const group=nodes.filter(n=>n.role===role);if(!group.length)continue;
  let maxRows=1;for(const [side,start] of [['L',35],['R',765],['unknown',765]]){
   const ns=group.filter(n=>n.side===side).sort((a,b)=>a.type.localeCompare(b.type)||Number(a.body_id)-Number(b.body_id));
   maxRows=Math.max(maxRows,Math.ceil(ns.length/3));ns.forEach((n,i)=>pos.set(n.body_id,{x:start+(i%3)*225,y:y+Math.floor(i/3)*82}));
  } y+=maxRows*82+115;
 }return{pos,height:Math.max(580,y+20)};
}
function drawGraph(data){
 const svg=$('graph'),{pos,height}=layout(data.nodes),W=1480;
 svg.setAttribute('viewBox',`0 0 ${W} ${height}`);svg.style.width=$('zoom').value+'%';svg.setAttribute('height',height*Number($('zoom').value)/100);
 let parts=[`<title>${esc(data.label)} · male-cns:v1.0 · body-level graph</title><defs><marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse" markerUnits="userSpaceOnUse"><path d="M 0 0 L 10 5 L 0 10 z" fill="#536c7d"/></marker></defs><text x="25" y="30" font-size="16" font-weight="bold" fill="#182d3c">${esc(data.label)} · male-cns:v1.0</text><text x="25" y="52" font-size="12">Arrows: pre → post · ${esc($('weight').value==='raw'?'RAW SYNAPSE COUNT':'EFFECTIVE CONNECTIVITY SCORE')} · Puddle UNRESOLVED</text><text x="360" y="90" text-anchor="middle" font-weight="bold" font-size="18">LEFT CNS</text><text x="1080" y="90" text-anchor="middle" font-weight="bold" font-size="18">RIGHT CNS</text><path d="M735 105V${height-15}" stroke="#dde5ea" stroke-dasharray="6 6"/>`];
 let edges=data.edges;
 if(edges.length>260){$('message').textContent=data.note+'\n'+edges.length+' edges pass the controls. Arrows are withheld to avoid an unreadable graph. Narrow types/targets, raise the display-only threshold, or click a body and enable focus. All matching records remain in the table.';edges=[];}
 const effective=$('weight').value==='effective',value=e=>effective?e.effective_connectivity_score:e.raw_synapse_count,max=Math.max(1,...edges.map(value));
 for(const e of edges){const a=pos.get(e.source),b=pos.get(e.target);if(!a||!b)continue;const ay=a.y+55,by=b.y;let path;
  if(e.source===e.target){path=`M${a.x+170} ${a.y+15} C${a.x+260} ${a.y-55},${a.x+260} ${a.y+95},${a.x+170} ${a.y+45}`;}
  else if(by>ay){const rail=a.x+210,approach=by-14;path=`M${a.x+196} ${a.y+28} Q${rail} ${a.y+28},${rail} ${a.y+42} L${rail} ${approach-8} Q${rail} ${approach},${rail-8} ${approach} L${b.x+98} ${approach} Q${b.x+98} ${approach},${b.x+98} ${by}`;}
  else{const rail=a.x+216,approach=b.y+69;path=`M${a.x+196} ${a.y+28} Q${rail} ${a.y+28},${rail} ${a.y+12} L${rail} ${approach+8} Q${rail} ${approach},${rail-8} ${approach} L${b.x+98} ${approach} Q${b.x+98} ${approach},${b.x+98} ${b.y+55}`;}
  const tip=`${e.source} → ${e.target}\nraw_synapse_count = ${e.raw_synapse_count}\neffective_connectivity_score = ${e.effective_connectivity_score??'UNAVAILABLE'}\n${JSON.stringify(e.scores||{})}\n${e.side_relationship||''}\n${e.query_provenance||e.provenance||''}`;
  parts.push(`<path class="edge" d="${path}" fill="none" stroke="#536c7d" opacity=".55" stroke-width="${.7+4.3*Math.sqrt(value(e)/max)}" marker-end="url(#arrow)"><title>${esc(tip)}</title></path>`);
  if($('counts').checked)parts.push(`<text x="${(a.x+b.x)/2+103}" y="${(ay+by)/2}" font-size="12" fill="#203747" stroke="white" stroke-width="3" paint-order="stroke">${esc(value(e))}</text>`);
 }
 for(const n of data.nodes){const p=pos.get(n.body_id);if(!p)continue;const label=n.display_alias?`${n.display_alias} / ${n.type}`:n.type;
  parts.push(`<g class="node" data-body="${n.body_id}" tabindex="0" role="button" aria-label="Inspect ${esc(label)} ${n.body_id}"><title>${esc(label+' | '+n.body_id+' | '+n.side+' | '+n.evidence.join('+'))}</title><rect x="${p.x}" y="${p.y}" width="196" height="55" rx="6" fill="${n.color}" stroke="#18364c" stroke-width="${n.candidate?2.4:1}" ${n.candidate?'stroke-dasharray="5 2"':''}/><text x="${p.x+98}" y="${p.y+20}" text-anchor="middle" fill="${n.role==='premotor'?'white':'#102b3d'}" font-size="13" font-weight="600">${esc(label)}</text><text x="${p.x+98}" y="${p.y+41}" text-anchor="middle" fill="${n.role==='premotor'?'white':'#102b3d'}" font-size="12">${n.body_id} · ${esc(n.side)} · ${esc(n.evidence.join('+'))}${n.difference?' · '+esc(n.difference):''}</text></g>`);
 }
 svg.innerHTML=parts.join('');
 svg.querySelectorAll('[data-body]').forEach(el=>{el.onclick=()=>showDetails(el.dataset.body);el.onkeydown=e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();showDetails(el.dataset.body);}};});
}
function renderCandidates(data){
 const cards=[];for(const t of CT){const ns=data.nodes.filter(n=>n.type===t).sort((a,b)=>a.side.localeCompare(b.side));if(!ns.length)continue;
  cards.push(`<article class="card"><h3>${esc(ns[0].display_alias?ns[0].display_alias+' / '+t:t)}</h3>${badges(ns[0])}<p>Independent comparison · role: ${esc(ns[0].role)}<br>E, D and X are shown only if supported.</p><p>Paper support: ${esc(ns[0].paper_status)}</p>`+ns.map(n=>`<button data-body="${n.body_id}"><span class="swatch" style="background:${n.color}"></span>${n.side} · ${n.body_id}</button>`).join('')+'<table><tr><th>Body</th><th>LB3b →</th><th>LB3c →</th>'+MOTORS.map(t=>`<th>→ ${t}</th>`).join('')+'</tr>'+ns.map(n=>'<tr><td>'+n.body_id+'</td>'+['LB3b','LB3c',...MOTORS].map((type,i)=>'<td>'+M.edges.filter(e=>i<2?e.target===n.body_id&&N.get(e.source).type===type:e.source===n.body_id&&N.get(e.target).type===type).reduce((v,e)=>v+e.raw_synapse_count,0)+'</td>').join('')+'</tr>').join('')+'</table><p>Fixed comparison table: complete direct type boundary sums, both partner sides; motor/type/threshold/focus controls apply to graph views, not these summaries.</p></article>');
 }$('candidateCards').innerHTML=cards.join('');$('candidateCards').querySelectorAll('[data-body]').forEach(el=>el.onclick=()=>showDetails(el.dataset.body));
}
function render(){
 current=computeDisplay();$('scientificLabel').textContent=current.label;$('sugarTabs').hidden=view!=='sugar';$('candidateCards').hidden=view!=='candidate';$('graphwrap').hidden=view==='candidate';$('message').textContent=current.note;
 document.querySelectorAll('[data-view]').forEach(b=>b.classList.toggle('active',b.dataset.view===view));document.querySelectorAll('[data-panel]').forEach(b=>b.classList.toggle('active',b.dataset.panel===panel));
 $('summary').textContent=`${current.nodes.length} bodies · ${current.edges.length} matching directed records · ${M.dataset}`;
 if(view==='candidate')renderCandidates(current);else drawGraph(current);
 $('download').disabled=view==='candidate';
 $('edgeTable').innerHTML='<tr><th>Pre → post</th><th>Raw count</th><th>Effective score</th><th>Provenance</th></tr>'+current.edges.map(e=>`<tr><td>${e.source} → ${e.target}</td><td>${e.raw_synapse_count}</td><td>${esc(e.effective_connectivity_score??'UNAVAILABLE')}</td><td>${esc(e.query_provenance||e.provenance)}</td></tr>`).join('');
}
document.querySelectorAll('aside input,aside select').forEach(el=>el.addEventListener('change',render));
document.querySelectorAll('[data-view]').forEach(el=>el.onclick=()=>{view=el.dataset.view;render();});document.querySelectorAll('[data-panel]').forEach(el=>el.onclick=()=>{panel=el.dataset.panel;render();});
$('zoom').oninput=()=>drawGraph(current);
$('reset').onclick=()=>{document.querySelectorAll('[data-type]').forEach(el=>el.checked=['LB3c','GNG042','GNG015',...MOTORS].includes(el.dataset.type));$('side').value='both';$('evidence').value='all';$('weight').value='raw';$('minimum').value=1;$('focus').checked=false;$('counts').checked=false;view='paper';render();};
$('download').onclick=()=>{const blob=new Blob([new XMLSerializer().serializeToString($('graph'))],{type:'image/svg+xml'}),u=URL.createObjectURL(blob),a=document.createElement('a');a.href=u;a.download=view+'_'+panel+'_'+$('weight').value+'.svg';a.click();setTimeout(()=>URL.revokeObjectURL(u),1000);};
render();
// Expose deterministic filtering for offline browser tests, not as scientific analysis.
window.circuitExplorer={computeDisplay,showDetails,render,get state(){return{view,panel,current};}};
