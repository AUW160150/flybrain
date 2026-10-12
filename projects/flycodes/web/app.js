const $=id=>document.getElementById(id);
let data=null,activity=null,busy=false,jobTimer=null,serverOutdated=false;
const labels={fly:'Fly connectome',transformer:'Tiny Transformer','no-recurrence':'No recurrence','pretrained-llm':'Pretrained LLM'};
const fmt=n=>n==null?'—':n.toLocaleString();
async function api(path,body){if(window.FLYCODES_SNAPSHOT){if(path==='/api/dashboard'&&!body)return window.FLYCODES_SNAPSHOT;throw Error('Saved results view. Start the local server to run a new experiment.')}const r=await fetch(path,body?{method:'POST',headers:{'Content-Type':'application/json','X-Flycodes-Token':data.token},body:JSON.stringify(body)}:{});const j=await r.json();if(!r.ok)throw Error(j.error||r.statusText);return j}
function setMessage(text){$('message').textContent=text}
function findResult(arm,id){return data?.evaluations[arm]?.results.find(x=>x.problem.id===id)}
function verdict(result){
 const v=result.judgement||{},measured=v.passed!==null&&v.passed!==undefined;
 const label=v.status==='syntax_error'?'SYNTAX ERROR · PROGRAM DID NOT RUN':v.status==='unresolved_syntax'?'UNRESOLVED · LOGIC NOT ESTABLISHED':(v.status||'Not evaluated').replaceAll('_',' ').toUpperCase()+(measured?` · ${v.passed_cases??0}/${v.total_cases??0} test cases`:'');
 $('verdict').textContent=label;$('verdict').className='verdict '+(measured?(v.passed?'passed':'failed'):'');
 $('case-details').textContent=v.status==='syntax_error'?`No verified solution. ${v.detail||''}`:v.detail||`${result.output_bytes??0} bytes · ${(result.latency_seconds??0).toFixed(2)} seconds · ${result.stop_reason||''}`;
}
function configureServerVersion(){
 serverOutdated=!window.FLYCODES_SNAPSHOT&&(data.ui_api_version??0)<2;
 const box=$('server-notice');box.hidden=!serverOutdated;
 if(!serverOutdated)return;
 box.replaceChildren();
 const title=document.createElement('strong');title.textContent='Outdated server: this tab is running the earlier experiment.';
 const detail=document.createElement('p');detail.textContent=`Active run: ${data.run||'unknown'}. The current interface needs the updated server to load the expanded curriculum and syntax audit. Generating a program or displaying neuron activity does not establish a correct solution.`;
 const instruction=document.createElement('p');instruction.textContent='In the terminal running Flycodes, press Ctrl+C, then run:';
 const command=document.createElement('code');command.textContent='cd /Users/Rodela1/Code/Flybrain/sandbox/flycodes\n./flycodes.sh serve --port 8765';
 const end=document.createElement('p');end.textContent='Then refresh this page. Original scores and failed attempts remain saved. The standalone flycodes.html already contains the updated results.';
 box.append(title,detail,instruction,command,end);
 for(const id of ['load','generate','train']){$(id).disabled=true;$(id).title='Restart the outdated Flycodes server first'}
 $('run-state').textContent='OUTDATED SERVER';
}

function showResult(r,source='Saved run'){if(!r){$('code').textContent='No measured output for this model and problem.';$('output-source').textContent='Not run';$('verdict').textContent='Not evaluated';$('verdict').className='verdict';$('case-details').textContent='';activity=null;return}$('code').textContent=r.code||'(The model emitted no code.)';$('output-source').textContent=source;verdict(r);activity=r.activity?.at(-1)||null;if(activity)$('activity-caption').textContent=`Recorded mean |activity|: ${activity.mean_abs.toFixed(4)}`;else $('activity-caption').textContent='No connectome activity recorded for this output'}
function selectProblem(){if(!data)return;const id=$('problem').value;const p=data.problems.find(x=>x.id===id);if(!p)return;$('statement').textContent=p.statement;$('family').textContent=(p.evaluation_split?p.evaluation_split+' / ':'')+p.family.replaceAll('-',' ');showSavedResult($('model').value,id);const llm=findResult('pretrained-llm',id);$('llm-code').textContent=llm?.code||'No measured LLM result yet.';$('llm-status').textContent=llm?llm.judgement.status.replaceAll('_',' '):(data.protocol==='curriculum-v2'?'Deferred':'Not run')}
function renderScores(){if(data.protocol==='curriculum-v2'){renderV2Scores();return}const table=$('score-table');table.replaceChildren();for(const arm of ['fly','no-recurrence','transformer','pretrained-llm']){const e=data.evaluations[arm],s=e?.summary;const row=document.createElement('tr');const cells=[labels[arm],s?.total?`${s.solved} / ${s.total}`:'—',s?.pass_at_1!=null?`${(s.pass_at_1*100).toFixed(1)}%`:'Not measured',fmt(data.training[arm]?.parameters)];cells.forEach((text,i)=>{const td=document.createElement('td');td.textContent=text;if(i===0){const small=document.createElement('small');small.textContent=arm==='pretrained-llm'?(e?.model||'Separate pretraining history'):arm==='fly'?'Full fixed graph + learned output':arm==='transformer'?'Same 12 examples · from scratch':'Same readout · graph signal removed';td.append(small)}if(i===2&&s?.interval_95){const small=document.createElement('small');small.textContent=`95% interval: ${(s.interval_95[0]*100).toFixed(0)}–${(s.interval_95[1]*100).toFixed(0)}%`;td.append(small)}row.append(td)});table.append(row)}}

function configureV2(){
 if(data.protocol!=='curriculum-v2')return;
 const previous=$('model').value;
 $('model').replaceChildren(...data.models.map(m=>{const o=document.createElement('option');o.value=m.id;o.textContent=m.label;return o}));
 if(data.models.some(m=>m.id===previous))$('model').value=previous;
 document.querySelector('.intro .eyebrow').textContent='EXPERIMENT 002 · EXPANDED CODE CURRICULUM';
 document.querySelector('.metrics .pilot').textContent='Curriculum v2';
 document.querySelector('.metrics>div:last-child small').textContent=`${data.config.training_count} training problems · frozen core`;
 document.querySelector('.contract p').textContent='Python · one candidate · 192 tokens / 2,048 bytes · no repair';
 document.querySelector('label[for="problem"]').textContent='Choose a recorded problem';
 $('train').textContent='Train a new curriculum experiment ↗';
 document.querySelector('.training-note').textContent='Calibration + 1,600 updates per model, two readout seeds. All prior runs are kept. This can take several minutes.';
 document.querySelector('.caveat').textContent='MBPP: 24 fresh tasks from the judge-compatible official-test subset. Transfer: 30 unseen-constant examples from familiar templates. Train: 8 seen examples. Two readout seeds share one fixed reservoir. These scores are not official full-MBPP or LeetCode scores.'+(data.test_audit?' Authored exercise scores use a post-run boundary-test audit; weak-test false positives are preserved in the report.':'');
 const legend=document.querySelector('.legend');legend.replaceChildren(...data.models.map((m,i)=>{const x=document.createElement('span');x.textContent='● '+m.label;x.style.color=['#db512d','#bb8955','#577194','#859aab'][i];return x}));
 document.querySelector('.chart-pane>small').textContent='Token prediction loss is a training signal. Passing program tests is the task.';
 document.querySelector('.flow span').textContent='Code tokens';
 const links=[['RESULTS_V2.md','Measured results & test audit ↗'],['PROTOCOL_V2.md','Training methods & scientific references ↗'],['LOG_V2.md','Decisions & execution log ↗']];
 document.querySelectorAll('.doc-links a').forEach((a,i)=>{a.href=(window.FLYCODES_SNAPSHOT?'docs/':'/docs/')+links[i][0];a.textContent=links[i][1]});
}
function renderV2Scores(){
 const table=$('score-table'),header=document.querySelector('thead tr');table.replaceChildren();header.replaceChildren();
 for(const title of ['Model','MBPP','Transfer','Train']){const th=document.createElement('th');th.textContent=title;header.append(th)}
 for(const score of data.scores){const tr=document.createElement('tr');for(const [i,key] of ['label','test','transfer','train-reproduction'].entries()){const td=document.createElement('td');const value=score[key];td.textContent=i===0?value:value?.total?`${value.solved} / ${value.total}`:'Not measured';if(i===0){const small=document.createElement('small');small.textContent=`${fmt(data.training[score.arm]?.parameters)} trainable readout params`;td.append(small)}tr.append(td)}table.append(tr)}
 const tr=document.createElement('tr');for(const text of ['Pretrained LLM','Deferred','—','—']){const td=document.createElement('td');td.textContent=text;tr.append(td)}table.append(tr);
}

function configureSyntaxAudit(){
 const audit=data.syntax_audit;
 if(!audit){if($('syntax-controls')){$('syntax-controls').hidden=true;$('syntax-view').value='original';$('syntax-edits').hidden=true;$('syntax-summary').hidden=true}return}
 if(!$('syntax-controls')){
  const box=document.createElement('div');box.id='syntax-controls';
  const label=document.createElement('label');label.htmlFor='syntax-view';label.textContent='Inspect saved output';
  const select=document.createElement('select');select.id='syntax-view';
  for(const [value,text] of [['original','Original model output'],['syntax','After mechanical syntax repair']]){const option=document.createElement('option');option.value=value;option.textContent=text;select.append(option)}
  select.addEventListener('change',selectProblem);box.append(label,select);$('code').before(box);
  const details=document.createElement('details');details.id='syntax-edits';details.hidden=true;
  const heading=document.createElement('summary');heading.textContent='Line edits and test evidence';
  const pre=document.createElement('pre');pre.id='syntax-edit-text';details.append(heading,pre);$('code').after(details);
  const note=document.createElement('p');note.id='syntax-summary';note.className='caveat';document.querySelector('.caveat').after(note);
 }
 $('syntax-controls').hidden=false;
 $('syntax-summary').hidden=false;
 const fly=audit.summaries.filter(x=>x.arm.startsWith('fly'));
 const total=key=>fly.reduce((n,x)=>n+x[key],0);
 $('syntax-summary').textContent=`Syntax audit: ${total('mechanically_repaired')} fly outputs made runnable; ${total('newly_recovered')} additional verified passes. ${total('unresolved_syntax')} outputs remain ambiguous or incomplete. Original benchmark scores above are preserved. `;
 const a=document.createElement('a');a.href=(window.FLYCODES_SNAPSHOT?'docs/':'/docs/')+'SYNTAX_AUDIT_RESULTS.md';a.textContent='See split-specific results and limitations ↗';$('syntax-summary').append(a);
}
function showSavedResult(arm,id){
 const original=findResult(arm,id);
 if($('syntax-edits'))$('syntax-edits').hidden=true;
 if($('syntax-view')?.value!=='syntax'){showResult(original);return}
 const row=data.syntax_audit?.results.find(x=>x.arm===arm&&x.problem.id===id);
 if(!row){showResult(null);return}
 const info=row.interpretation;
 showResult({...original,code:info.code,judgement:row.judgement},info.status==='unresolved'?'Unresolved interpretation':info.status==='repaired'?'Mechanical syntax repair':'Already valid · unchanged');
 $('syntax-edits').hidden=false;
 $('syntax-edit-text').textContent=[...info.edits,info.remaining_error?'Unresolved: '+info.remaining_error:'',row.counterexample?'Counterexample: '+JSON.stringify(row.counterexample):'',info.diff].filter(Boolean).join('\n');
 if(!info.edits.length&&!info.remaining_error)$('syntax-edit-text').textContent='No syntax edits. The original code was tested unchanged.'+(row.counterexample?'\nCounterexample: '+JSON.stringify(row.counterexample):'');
 if(row.judgement.passed===true)$('case-details').textContent=`${row.judgement.passed_cases}/${row.judgement.total_cases} cases passed under this interpretation. Split: ${row.split}. No model retraining.`;
}

function svgNode(tag,attrs,text){const n=document.createElementNS('http://www.w3.org/2000/svg',tag);Object.entries(attrs).forEach(([k,v])=>n.setAttribute(k,v));if(text)n.textContent=text;return n}
function chart(){const s=$('loss-chart');s.replaceChildren();const arms=data.protocol==='curriculum-v2'?data.models.map(m=>m.id):['fly','transformer','no-recurrence'];const colors=['#db512d','#bb8955','#577194','#859aab'];const histories=arms.map(a=>data.training[a]?.history||[]);const points=histories.flat();if(!points.length){s.append(svgNode('text',{x:100,y:100,fill:'#788078','font-size':12},'No training measurements yet'));return}const maxY=Math.max(...points.map(p=>p.validation_loss))*1.08,maxX=Math.max(1,...points.map(p=>p.step));for(let i=0;i<=4;i++){const y=180-i*38;s.append(svgNode('line',{x1:35,x2:450,y1:y,y2:y,stroke:'#e4e6dd'}));s.append(svgNode('text',{x:5,y:y+3,fill:'#788078','font-size':9},(maxY*i/4).toFixed(1)))}histories.forEach((h,i)=>s.append(svgNode('polyline',{points:h.map(p=>`${35+p.step/maxX*415},${180-p.validation_loss/maxY*152}`).join(' '),fill:'none',stroke:colors[i],'stroke-width':2})));s.append(svgNode('text',{x:35,y:203,fill:'#788078','font-size':9},'0'));s.append(svgNode('text',{x:410,y:203,fill:'#788078','font-size':9},`${maxX} steps`))}
function renderEvents(){const box=$('events');box.replaceChildren();for(const e of (data.events||[]).slice(-25).reverse()){const row=document.createElement('div'),time=document.createElement('time'),desc=document.createElement('span');time.textContent=new Date(e.time).toLocaleTimeString([], {hour12:false});desc.textContent=[e.event.replaceAll('_',' '),e.arm,e.problem,e.step!=null?`step ${e.step}`:'',e.validation_loss!=null?`val ${e.validation_loss.toFixed(3)}`:'',e.status].filter(Boolean).join(' · ');row.append(time,desc);box.append(row)}}
async function refresh(){const old=$('problem').value;data=await api('/api/dashboard');configureV2();configureSyntaxAudit();$('neurons').textContent=fmt(data.graph?.neurons);$('edges').textContent=fmt(data.graph?.directed_edges);$('run-state').textContent=data.status?.state.toUpperCase()||'READY';$('run-id').textContent=data.run||'No run yet';$('problem').replaceChildren(...data.problems.map(p=>{const o=document.createElement('option');o.value=p.id;o.textContent=(p.evaluation_split?p.evaluation_split+' · ':'')+p.id.split('-').map(w=>w?w[0].toUpperCase()+w.slice(1):'').join(' ');return o}));if(old)$('problem').value=old;renderScores();chart();renderEvents();if(!busy)selectProblem();configureServerVersion();setMessage(serverOutdated?'This tab is connected to an outdated server. Restart Flycodes using the notice above.':data.run?`Showing recorded experiment ${data.run}. Re-running a task is saved separately from benchmark scores.`:'Prepare the graph and run the first training pilot to collect results.')}
function setBusy(value){busy=value;for(const id of ['load','generate','train','problem','model'])$(id).disabled=value;if($('syntax-view'))$('syntax-view').disabled=value}
async function start(action,body){if(serverOutdated){setMessage('Restart the outdated server before starting a new attempt.');return}try{if(action==='generate'&&$('syntax-view')){$('syntax-view').value='original';$('syntax-edits').hidden=true}setBusy(true);activity=null;setMessage(action==='train'?'Training a full local pilot. The run is recorded on disk; this can take a few minutes.':action==='load'?'Loading graph and verifying file hashes…':'Running the selected checkpoint. Waiting for real model output…');const job=await api(`/api/${action}`,body||{});const poll=async()=>{try{const j=await api(`/api/jobs/${job.id}`);if(j.code){$('code').textContent=j.code;$('output-source').textContent='Live run'}if(j.activity){activity=j.activity;$('activity-caption').textContent=`Live mean |activity|: ${activity.mean_abs.toFixed(4)}`}$('brain-state').textContent=j.status==='running'?'Model running · measured activity':'Graph loaded · core frozen';if(j.status==='running'){jobTimer=setTimeout(poll,500);return}setBusy(false);if(j.status==='failed'){setMessage(`Experiment failed: ${j.error}`);return}if(action==='generate'){showResult(j.result,'Generated attempt');const outcome=j.result.judgement;setMessage(outcome?.passed===true?'Candidate passed the supplied tests. This attempt is saved separately from benchmark scores.':outcome?.passed===false?`No verified solution: ${(outcome.status||'failed').replaceAll('_',' ')}. The generated attempt is saved separately.`:'Candidate generated but not scored; no correctness claim is available.')}else if(action==='load'){setMessage(`Loaded and verified ${fmt(j.result.neurons)} neurons and ${fmt(j.result.edges)} connections.`)}else{await refresh();setMessage('Training and held-out evaluation finished. The new run is now displayed.')}}catch(e){setBusy(false);setMessage(e.message)}};poll()}catch(e){setBusy(false);setMessage(e.message)}}
$('problem').addEventListener('change',selectProblem);$('model').addEventListener('change',selectProblem);
$('load').addEventListener('click',()=>start('load',{}));$('train').addEventListener('click',()=>start('train',{protocol:data.protocol||'pilot-v1'}));
$('generate').addEventListener('click',()=>{const custom=$('custom').value.trim();start('generate',{arm:$('model').value,...(custom?{statement:custom}:{problem:$('problem').value})})});

// Schematic avatar. Only neuron color encodes measured activity; positions are decorative.
const canvas=$('fly'),ctx=canvas.getContext('2d');
function draw(){const rect=canvas.getBoundingClientRect(),dpr=window.devicePixelRatio||1;if(canvas.width!==Math.round(rect.width*dpr)||canvas.height!==Math.round(rect.height*dpr)){canvas.width=Math.round(rect.width*dpr);canvas.height=Math.round(rect.height*dpr)}ctx.setTransform(dpr,0,0,dpr,0,0);ctx.clearRect(0,0,rect.width,rect.height);const scale=Math.min(rect.width/320,rect.height/350);ctx.translate(rect.width/2,rect.height/2);ctx.scale(scale,scale);ctx.strokeStyle='#d2d9ca';ctx.lineWidth=.7;for(let r=55;r<150;r+=35){ctx.beginPath();ctx.arc(0,0,r,0,Math.PI*2);ctx.stroke()}ctx.setLineDash([2,5]);ctx.beginPath();ctx.moveTo(-145,0);ctx.lineTo(145,0);ctx.moveTo(0,-155);ctx.lineTo(0,155);ctx.stroke();ctx.setLineDash([]);
function ellipse(x,y,rx,ry,rotation,fill,stroke='#61715b'){ctx.beginPath();ctx.ellipse(x,y,rx,ry,rotation,0,Math.PI*2);ctx.fillStyle=fill;ctx.fill();ctx.strokeStyle=stroke;ctx.stroke()}
ctx.lineWidth=1.4;ctx.strokeStyle='#798674';for(const side of [-1,1]){for(let j=0;j<3;j++){ctx.beginPath();ctx.moveTo(side*17,j*14-20);ctx.lineTo(side*(50+j*9),j*38-65);ctx.lineTo(side*(74+j*11),j*49-81);ctx.stroke()}}ellipse(0,54,25,56,0,'#728364');for(let y=29;y<99;y+=15){ctx.beginPath();ctx.ellipse(0,y,21,7,0,0,Math.PI);ctx.stroke()}const flutter=busy?Math.sin(performance.now()/40)*.045:0;ellipse(-42,21,27,74,-.58+flutter,'#e4ebe1d9','#a8b6a0');ellipse(42,21,27,74,.58-flutter,'#e4ebe1d9','#a8b6a0');ctx.strokeStyle='#b4c0ad';for(const side of [-1,1])for(let j=0;j<3;j++){ctx.beginPath();ctx.moveTo(side*12,-23);ctx.quadraticCurveTo(side*(45+j*7),28,side*(45+j*8),80);ctx.stroke()}ellipse(0,-5,27,35,0,'#65775c');ellipse(0,-49,35,29,0,'#cbd6ba');ellipse(-29,-52,12,19,-.4,'#ad6245','#9b6049');ellipse(29,-52,12,19,.4,'#ad6245','#9b6049');ctx.strokeStyle='#526747';for(const side of [-1,1]){ctx.beginPath();ctx.moveTo(side*8,-70);ctx.lineTo(side*16,-94);ctx.lineTo(side*26,-99);ctx.stroke()}
const samples=activity?.sample||[];for(let i=0;i<80;i++){const angle=i*2.39996,r=Math.sqrt((i%40)/40)*19,side=i<40?-1:1,x=side*12+Math.cos(angle)*r*.7,y=-49+Math.sin(angle)*r*.75,v=samples[i]?.value;ctx.beginPath();ctx.arc(x,y,1.55,0,Math.PI*2);ctx.fillStyle=v===undefined?'#869c70':v>0?`rgba(219,81,45,${.25+Math.min(1,Math.abs(v)*3)*.75})`:`rgba(65,106,132,${.25+Math.min(1,Math.abs(v)*3)*.75})`;ctx.fill()}requestAnimationFrame(draw)}
draw();refresh().then(()=>{if(window.FLYCODES_SNAPSHOT){for(const id of ['load','generate','train']){$(id).disabled=true;$(id).title='Start the local server to use this action';$(id).style.cursor='default'}$('run-state').textContent='SAVED RESULTS';$('brain-state').textContent='Recorded activity · saved results view';setMessage('Saved results view. Explore real outputs below. To load the brain or run new experiments: ./flycodes.sh serve');const blob=new Blob([JSON.stringify(data,null,2)],{type:'application/json'});document.querySelector('a[download]').href=URL.createObjectURL(blob)}}).catch(e=>setMessage(`Could not load local data: ${e.message}`));
