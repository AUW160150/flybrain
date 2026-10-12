'use strict';
// Bounded, dependency-free Chrome CDP tests; owns and cleans up only its two children.
const fs=require('fs'),path=require('path'),cp=require('child_process');
const root=path.resolve(__dirname,'..'),report=path.join(root,'reports/current');
const delay=ms=>new Promise(r=>setTimeout(r,ms));
let server,chrome,ws,seq=0,pending=new Map(),events=[],results=[];
function assert(x,msg){if(!x)throw new Error(msg);results.push({name:msg,status:'passed'});}
function call(method,params={}){const id=++seq;return new Promise((resolve,reject)=>{pending.set(id,{resolve,reject});ws.send(JSON.stringify({id,method,params}));setTimeout(()=>{if(pending.has(id)){pending.delete(id);reject(new Error('CDP timeout '+method));}},10000).unref();});}
async function evaluate(expression){const r=await call('Runtime.evaluate',{expression,returnByValue:true,awaitPromise:true});if(r.exceptionDetails)throw new Error(JSON.stringify(r.exceptionDetails));return r.result.value;}
async function until(expression){for(let i=0;i<100;i++){if(await evaluate(expression))return;await delay(100);}throw new Error('UI wait timeout: '+expression);}
async function main(){
 const profile=path.join(root,'cache/browser-test');fs.mkdirSync(profile,{recursive:true});
 server=cp.spawn(path.join(root,'viz'),['serve','--host','127.0.0.1','--port','18765'],{stdio:['ignore','pipe','pipe']});let serverErr='';server.stderr.on('data',x=>serverErr+=x);
 let online=false;for(let i=0;i<40;i++){try{if((await fetch('http://127.0.0.1:18765/api/status')).ok){online=true;break;}}catch{}await delay(100);}if(!online)throw new Error('Local server unavailable: '+serverErr);
 chrome=cp.spawn('/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',['--headless=new','--disable-gpu','--no-first-run','--no-default-browser-check','--disable-background-networking','--disable-extensions','--disable-component-update','--remote-allow-origins=http://127.0.0.1:19222','--remote-debugging-address=127.0.0.1','--remote-debugging-port=19222','--user-data-dir='+profile,'--window-size=1440,1100','about:blank'],{stdio:['ignore','ignore','pipe']});let chromeErr='';chrome.stderr.on('data',x=>chromeErr+=x);
 let targets;for(let i=0;i<80;i++){try{targets=await(await fetch('http://127.0.0.1:19222/json')).json();break;}catch{}await delay(100);}if(!targets)throw new Error('Chrome unavailable: '+chromeErr.slice(-1500));
 ws=new WebSocket(targets.find(x=>x.type==='page').webSocketDebuggerUrl);await new Promise((res,rej)=>{ws.onopen=res;ws.onerror=rej;});ws.onmessage=e=>{const d=JSON.parse(e.data);if(d.id){const p=pending.get(d.id);if(p){pending.delete(d.id);d.error?p.reject(new Error(JSON.stringify(d.error))):p.resolve(d.result);}}else if(d.method==='Runtime.exceptionThrown')events.push(d.params);};
 await call('Page.enable');await call('Runtime.enable');await call('Page.navigate',{url:'http://127.0.0.1:18765/?scope=G3&order=model&id=10029'});
 await until("document.querySelector('#node')?.textContent.includes('model index 0') && document.querySelector('#partners')?.textContent.includes('outgoing') && document.querySelector('#geometryCoverage')?.textContent.includes('8/512')");
 assert(await evaluate("document.querySelector('#badge').textContent.includes('354ccf91b989')"),'Fixed graph hash badge is visible');
 const expected=await(await fetch('http://127.0.0.1:18765/api/partners?scope=G3&id=10029&direction=incoming&limit=25')).json();
 assert(await evaluate(`document.querySelector('#partners').textContent.includes(${JSON.stringify(expected.rows[0].source_body_id+' → '+expected.rows[0].target_body_id)})`),'Clicked real neuron shows backend incoming partner');
 await evaluate("document.querySelector('#sourceId').value='10053';document.querySelector('#targetId').value='10029';document.querySelector('#pairForm').dispatchEvent(new Event('submit',{cancelable:true}));");
 await until("document.querySelector('#pairResult').textContent.includes('synapse_count')");assert(await evaluate("JSON.parse(document.querySelector('#pairResult').textContent).record.synapse_count===23"),'Known real direction 10053 → 10029 has 23 contacts');
 // Real matrix bin -> exact cell, selecting target row zero and source column one.
 await evaluate("{const c=document.querySelector('#matrix'),r=c.getBoundingClientRect();c.dispatchEvent(new MouseEvent('click',{clientX:r.left+r.width*.002,clientY:r.top+r.height*.002}));}");
 await until("new URLSearchParams(location.search).has('viewport')");await delay(200);
 await evaluate("{const c=document.querySelector('#matrix'),r=c.getBoundingClientRect();c.dispatchEvent(new MouseEvent('click',{clientX:r.left+r.width*.375,clientY:r.top+r.height*.125}));}");
 await until("document.querySelector('#sourceId').value==='10053' && document.querySelector('#targetId').value==='10029'");
 assert(await evaluate("document.querySelector('#node').textContent.includes('10029')"),'Matrix exact-pair click synchronizes target ID and saved model index');
 await evaluate("document.querySelector('#scope').value='G1-subset';document.querySelector('#scope').dispatchEvent(new Event('change'));");
 await until("document.querySelector('#stats').textContent.includes('7,405')");assert(await evaluate("document.querySelector('#stats').textContent.includes('47,404')"),'G1 induced scope replaces G3 totals without stale cache');
 await evaluate("document.querySelector('#scope').value='G0';document.querySelector('#scope').dispatchEvent(new Event('change'));");await until("!document.querySelector('#scopeError').hidden");assert(await evaluate("document.querySelector('#scopeError').textContent.includes('E_INCOMPLETE_INGEST') && document.querySelector('#stats').textContent===''") ,'Unindexed G0 is an error panel, not stale counts or zero');
 await evaluate("document.querySelector('#scope').value='G3';document.querySelector('#scope').dispatchEvent(new Event('change'));");await until("document.querySelector('#stats').textContent.includes('3,061')");
 await evaluate("document.querySelector('#drawThreshold').value='10';document.querySelector('#drawThreshold').dispatchEvent(new Event('change'));");
 assert(await evaluate("document.querySelector('#graphCaption').textContent.includes('hidden by display threshold')"),'Render filter reports hidden edges while preserving canonical total');
 await call('Page.reload');await until("document.querySelector('#stats')?.textContent.includes('3,061') && document.querySelector('#graphCaption')?.textContent.includes('hidden by display threshold')");
 assert(await evaluate("document.querySelector('#scope').value==='G3' && document.querySelector('#drawThreshold').value==='10' && document.querySelector('#node').textContent.includes('10029')"),'Reload preserves scope, order, filter and selected ID');
 const firstRun=await evaluate("document.querySelector('#run').options[1].value");await evaluate(`document.querySelector('#run').value=${JSON.stringify(firstRun)};document.querySelector('#run').dispatchEvent(new Event('change'));`);await until("document.querySelector('#snapshot').textContent.includes('E_CHECKPOINT_UNSTABLE_OR_UNSAFE')");assert(await evaluate("document.querySelector('#snapshot').textContent.includes('SHA-256')"),'Run selector shows fixed snapshot hash and safe-loader blocker');
 const unknown=await fetch('http://127.0.0.1:18765/api/geometry?id=13506');assert(unknown.status===409,'Missing geometry request returns explicit error');
 // Browser's own numeric parsing must leave string IDs above 2**53 intact.
 assert(await evaluate("JSON.parse('{\"body_id\":\"9007199254740993\"}').body_id==='9007199254740993'"),'Browser round trip preserves decimal IDs above 2**53');
 assert(events.length===0,'No JavaScript runtime exceptions');
 await evaluate("window.scrollTo(0,0)");await delay(150);let shot=await call('Page.captureScreenshot',{format:'png'});fs.writeFileSync(path.join(report,'browser-explorer.png'),Buffer.from(shot.data,'base64'));
 await evaluate("document.querySelector('#architecture').scrollIntoView()");await delay(150);shot=await call('Page.captureScreenshot',{format:'png'});fs.writeFileSync(path.join(report,'browser-architecture.png'),Buffer.from(shot.data,'base64'));
 await evaluate("document.querySelector('#anatomy').scrollIntoView()");await delay(150);shot=await call('Page.captureScreenshot',{format:'png'});fs.writeFileSync(path.join(report,'browser-anatomy.png'),Buffer.from(shot.data,'base64'));
 fs.writeFileSync(path.join(report,'browser-validation.json'),JSON.stringify({status:'passed',browser:'Installed Google Chrome headless / CDP',tests:results,screenshots:['browser-explorer.png','browser-architecture.png','browser-anatomy.png'],exceptions:events},null,2));
}
const timer=setTimeout(()=>{throw new Error('Browser harness 90-second limit');},90000);timer.unref();
main().catch(e=>{fs.writeFileSync(path.join(report,'browser-validation.json'),JSON.stringify({status:/Local server unavailable|Chrome unavailable/.test(String(e))?'skipped':'failed',reason:String(e),tests:results},null,2));console.error(e);process.exitCode=1;}).finally(async()=>{clearTimeout(timer);if(ws)ws.close();if(chrome)chrome.kill('SIGTERM');if(server)server.kill('SIGTERM');await delay(400);});
