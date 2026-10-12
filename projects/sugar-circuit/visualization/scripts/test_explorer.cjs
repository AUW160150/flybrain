/* Offline runtime tests of the emitted explorer's filtering and evidence logic.
 * A minimal DOM harness is used because this environment cannot launch Chrome.
 * This is not a substitute for a full browser visual/layout test.
 */
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),assert=require('node:assert/strict');
const root=path.resolve(__dirname,'..'),run=fs.readFileSync(path.join(root,'data/current_run.txt'),'utf8').trim();
const html=fs.readFileSync(path.join(root,'interactive',run,'index.html'),'utf8');
const model=JSON.parse(html.match(/<script id="model" type="application\/json">([\s\S]*?)<\/script>/)[1]);
const script=html.match(/<script>([\s\S]*?)<\/script>/)[1];
let inputs=[];
class Element{
 constructor(id=''){this.id=id;this.dataset={};this.value='';this.checked=false;this.hidden=false;this.style={};this.attributes={};this.classList={toggle(){}};this._html='';this.textContent='';this.listeners={};}
 set innerHTML(s){this._html=s;if(['groups','paperGroups','motors'].includes(this.id)){for(const x of s.matchAll(/<input[^>]*data-type="([^"]+)"([^>]*)>/g)){const el=new Element();el.dataset.type=x[1];el.checked=x[2].includes('checked');inputs.push(el);}}}
 get innerHTML(){return this._html;}
 setAttribute(k,v){this.attributes[k]=v;}
 addEventListener(k,v){this.listeners[k]=v;}
 querySelectorAll(){return[];}
 click(){if(this.onclick)this.onclick();}
}
const elements=new Map(),el=id=>{if(!elements.has(id))elements.set(id,new Element(id));return elements.get(id);};
el('model').textContent=JSON.stringify(model);el('side').value='both';el('evidence').value='all';el('weight').value='raw';el('minimum').value='1';el('zoom').value='100';
const views=['paper','sugar','candidate','raw'].map(v=>{const e=new Element();e.dataset.view=v;return e;});
const panels=['lb3b_only','lb3c_only','lb3b_lb3c_combined','difference'].map(v=>{const e=new Element();e.dataset.panel=v;return e;});
const document={getElementById:el,createElement:()=>new Element(),querySelectorAll:s=>s==='[data-type]:checked'?inputs.filter(x=>x.checked):s==='[data-type]'?inputs:s==='[data-view]'?views:s==='[data-panel]'?panels:s==='aside input,aside select'?[...inputs,...['side','evidence','weight','minimum','focus','counts'].map(el)]:[]};
const context={document,window:{},console,setTimeout,Blob,URL};vm.createContext(context);vm.runInContext(script,context);
const api=context.window.circuitExplorer;let checks=0;
const check=(test,msg)=>{assert.ok(test,msg);checks++;};
let d=api.computeDisplay();check(d.label==='PAPER-ASSOCIATED','paper label');check(d.nodes.length===37,'default body inventory');check(d.edges.every(e=>e.paper_associated),'no non-paper edges leak into paper view');check(el('graph').innerHTML.includes('marker-end="url(#arrow)"'),'arrows present');
for(const type of ['GNG232','DNg67','DNge080']){const ns=model.nodes.filter(n=>n.type===type);check(ns.every(n=>n.evidence.includes('P')&&!n.paper_counterpart&&n.evidence_sources.P.includes('C061')),'supplementary panel P is distinct from Figure 6 membership');}
const g232=inputs.find(e=>e.dataset.type==='GNG232');g232.checked=true;check(!api.computeDisplay().nodes.some(n=>n.type==='GNG232'),'paper view does not promote supplementary support to motif membership');g232.checked=false;
el('weight').value='effective';d=api.computeDisplay();check(d.edges.length===0&&d.note.includes('No raw values are substituted'),'no fallback from effective scores to raw counts');el('weight').value='raw';
views.find(v=>v.dataset.view==='sugar').click();for(const p of panels){p.click();d=api.computeDisplay();check(d.nodes.length===0&&d.edges.length===0&&d.note.includes('BLOCKED'),'pending sugar panel remains empty');check(d.label==='SUGAR-RESTRICTED EFFECTIVE-CONNECTIVITY','sugar label');}
views.find(v=>v.dataset.view==='raw').click();el('side').value='L';d=api.computeDisplay();check(d.nodes.every(n=>n.side==='L'),'left body filtering');let ids=new Set(d.nodes.map(n=>n.body_id));check(d.edges.every(e=>ids.has(e.source)&&ids.has(e.target)),'edge endpoint side filtering');
el('side').value='both';for(const code of ['D','X','E']){el('evidence').value=code;d=api.computeDisplay();check(d.nodes.length===0,'unverified evidence cannot manufacture a badge');}el('evidence').value='all';
api.showDetails('15321');check(el('details').innerHTML.includes('PREDICTED TRANSMITTER — NOT DIRECT PHYSIOLOGICAL VALIDATION'),'NT disclaimer');check(el('details').innerHTML.includes('raw_edges.csv'),'weight scope disclosed');check(el('details').innerHTML.includes('Shiu status'),'body evidence detail');
el('focus').checked=true;d=api.computeDisplay();check(d.edges.length>0&&d.edges.every(e=>e.source==='15321'||e.target==='15321'),'focused edge filter');el('focus').checked=false;
el('minimum').value='100';d=api.computeDisplay();check(d.edges.every(e=>e.raw_synapse_count>=100),'display threshold');el('minimum').value='1';
views.find(v=>v.dataset.view==='candidate').click();d=api.computeDisplay();check(d.nodes.length===12,'six independent comparison types');check(el('candidateCards').innerHTML.match(/<article class="card">/g).length===6,'independent cards');check(el('graphwrap').hidden,'comparison does not imply one pathway');
// In-memory synthetic score fixture: never saved as a scientific result.
vm.runInContext(`M.selected_results={conditions:{lb3b_only:{node_ids:['15321','523590'],edges:[{source:'15321',target:'523590',raw_synapse_count:73,effective_connectivity_score:.2,provenance:'SYNTHETIC UI TEST'}]},lb3c_only:{node_ids:['15734','523590'],edges:[{source:'15734',target:'523590',raw_synapse_count:87,effective_connectivity_score:.8,provenance:'SYNTHETIC UI TEST'}]},lb3b_lb3c_combined:{node_ids:['15321','15734','523590','27203'],edges:[{source:'15321',target:'523590',raw_synapse_count:73,effective_connectivity_score:.5,provenance:'SYNTHETIC UI TEST'}]}}}`,context);
views.find(v=>v.dataset.view==='sugar').click();panels[0].click();el('weight').value='effective';d=api.computeDisplay();check(d.nodes.length===2&&d.edges[0].effective_connectivity_score===.2,'future A consumes its own explicit selection and score');
panels[1].click();d=api.computeDisplay();check(d.edges[0].effective_connectivity_score===.8,'future B uses its own score');
panels[3].click();d=api.computeDisplay();check(d.edges.length===0&&d.note.includes('No scores were pooled'),'difference score ambiguity fails closed');
el('weight').value='raw';d=api.computeDisplay();check(d.nodes.find(n=>n.body_id==='27203').difference==='C only','combined-only membership derived from input sets');check(d.nodes.find(n=>n.body_id==='523590').difference==='A∩B','overlap derived from validated membership');check(d.edges.every(e=>e.effective_connectivity_score===null),'difference view never silently picks a condition score');
const result={status:'PASS',checks,scope:'Offline DOM harness tests of emitted HTML behavior; full browser layout not tested',run_id:run};
fs.writeFileSync(path.join(root,'data',run,'explorer_validation.json'),JSON.stringify(result,null,2)+'\n');console.log(JSON.stringify(result));
