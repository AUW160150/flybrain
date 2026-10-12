import { lazy, Suspense, useEffect, useRef, useState } from 'react';
import { readBoundedResponse } from '../realdata/schema';
import { bodyColor } from './geometry';
import { DATASET, DATASET_UUID, MAX_BODIES, type Edge, type Neuron, type IndexManifest, type Skeleton, type Region, type RegionMesh, type SynapseResult } from './types';

const CircuitScene=lazy(()=>import('./CircuitScene'));
const recoveryIds=['71254','72059','15321','28181','18295'];
const emptySynapses:SynapseResult['synapses']=[];
type Search={neurons:Neuron[];total:number;offset:number;query:string};
type Graph={neurons:Neuron[];edges:Edge[];total:number;filteredOut:number};
type Partners={partners:{neuron:Neuron;edge:Edge}[];total:number;offset:number};
async function api<T>(route:string,params:Record<string,string>={},signal?:AbortSignal):Promise<T> {
  const response=await fetch('/api/connectome/'+route+'?'+new URLSearchParams(params),{signal});
  if(!(response.headers.get('content-type')??'').includes('json')) throw new Error('The real circuit atlas needs the local development server and its 1.5 GB MaleCNS index (npm run dev). It is not part of the hosted demo.');
  const bounded=response.ok?response:new Response(response.body,{status:200});
  const data=JSON.parse(new TextDecoder().decode(await readBoundedResponse(bounded,response.ok?24*1024*1024:65536)));
  if(!response.ok || data.error) throw new Error(data.error??`Request failed: ${response.status}`);
  return data as T;
}
function message(error:unknown){return error instanceof Error?error.message:'Data request failed';}
function publicScene(ids:string[]) {
  const state={dimensions:{x:[8e-9,'m'],y:[8e-9,'m'],z:[8e-9,'m']},layers:[{type:'segmentation',name:'MaleCNS v1.0',source:'precomputed://gs://flyem-male-cns/v1.0/segmentation',segments:ids}],layout:'3d'};
  return 'https://neuroglancer-demo.appspot.com/#!'+encodeURIComponent(JSON.stringify(state));
}

export default function CircuitExplorer({showWorld}:{showWorld:()=>void}) {
  const [manifest,setManifest]=useState<IndexManifest|null>(null),[error,setError]=useState('');
  const [query,setQuery]=useState('LB3b'),[search,setSearch]=useState<Search|null>(null),[searching,setSearching]=useState(false);
  const [ids,setIds]=useState<string[]>([]),[selected,setSelected]=useState<string|null>(null),[graph,setGraph]=useState<Graph|null>(null);
  const [minWeight,setMinWeight]=useState(1),[direction,setDirection]=useState('downstream'),[offset,setOffset]=useState(0),[partners,setPartners]=useState<Partners|null>(null);
  const [skeletons,setSkeletons]=useState<Record<string,Skeleton>>({}),[geometryErrors,setGeometryErrors]=useState<Record<string,string>>({});
  const [regions,setRegions]=useState<Region[]>([]),[meshes,setMeshes]=useState<Record<string,RegionMesh>>({}),[visibleRegions,setVisibleRegions]=useState<string[]>([]),[regionError,setRegionError]=useState('');
  const [synapses,setSynapses]=useState<SynapseResult|null>(null),[synapsePending,setSynapsePending]=useState(false),[synapseError,setSynapseError]=useState('');
  const [confidence,setConfidence]=useState(0.5),[connection,setConnection]=useState<Edge|null>(null),[frame,setFrame]=useState(0);
  const searchRequest=useRef<AbortController|null>(null);
  const skeletonCache=useRef<Record<string,Skeleton>>({});
  const meshCache=useRef<Record<string,RegionMesh>>({});
  const idKey=ids.join(',');
  const choose=(id:string)=>{setSelected(id);setOffset(0);};
  const add=(id:string)=>{
    if(ids.includes(id)){choose(id);return;}
    if(ids.length>=MAX_BODIES){setError(`The view holds ${MAX_BODIES} neurons. Remove one before expanding.`);return;}
    setIds(current=>current.includes(id)?current:[...current,id]); choose(id);
  };
  const find=async(q:string,page=0)=>{
    searchRequest.current?.abort(); const abort=new AbortController();searchRequest.current=abort;
    setSearching(true);setError('');
    try{setSearch(await api<Search>('search',{q,offset:String(page)},abort.signal));}
    catch(e){if(!abort.signal.aborted)setError(message(e));}
    finally{if(!abort.signal.aborted)setSearching(false);}
  };
  useEffect(()=>{
    const abort=new AbortController();
    void api<IndexManifest>('status',{},abort.signal).then(data=>{
      if(data.dataset!==DATASET || data.uuid!==DATASET_UUID)throw new Error('Dataset identity mismatch');setManifest(data);
    }).catch(e=>{if(!abort.signal.aborted)setError(message(e));});
    void find('LB3b');
    void api<Region[]>('regions',{},abort.signal).then(data=>{setRegions(data);setVisibleRegions(data.map(r=>r.id));}).catch(e=>{if(!abort.signal.aborted)setRegionError(message(e));});
    return()=>{abort.abort();searchRequest.current?.abort();};
  },[]);
  useEffect(()=>{
    const abort=new AbortController();setGraph(null);setConnection(null);setSynapses(null);
    if(ids.length)void api<Graph>('graph',{ids:idKey,minWeight:String(minWeight)},abort.signal).then(setGraph).catch(e=>{if(!abort.signal.aborted)setError(message(e));});
    return()=>abort.abort();
  },[idKey,minWeight]);
  useEffect(()=>{
    const abort=new AbortController();setPartners(null);
    if(selected)void api<Partners>('partners',{id:selected,direction,minWeight:String(minWeight),offset:String(offset)},abort.signal).then(setPartners).catch(e=>{if(!abort.signal.aborted)setError(message(e));});
    return()=>abort.abort();
  },[selected,direction,minWeight,offset]);
  useEffect(()=>{
    const abort=new AbortController();setGeometryErrors({});
    void(async()=>{
      const cached={...skeletonCache.current};
      let points=0; const loaded:Record<string,Skeleton>={};
      for(const id of ids){
        if(abort.signal.aborted)return;
        try{
          const data=cached[id]??await api<Skeleton>('skeleton',{id},abort.signal);
          if(data.bodyId!==id || data.units!=='8 nm' || data.coordinateSpace!=='MaleCNS native EM')throw new Error('Skeleton identity or coordinates mismatch');
          if(points+data.points.length>800000)throw new Error('View exceeds 800,000 source points. Remove neurons to load this skeleton.');
          points+=data.points.length;loaded[id]=data;
          if(!abort.signal.aborted){skeletonCache.current={...loaded};setSkeletons({...loaded});}
        }catch(e){if(!abort.signal.aborted)setGeometryErrors(current=>({...current,[id]:message(e)}));}
      }
      if(!abort.signal.aborted)setSkeletons(loaded);
    })();
    return()=>abort.abort();
  },[idKey]);
  useEffect(()=>{
    const abort=new AbortController();
    void(async()=>{
      for(const id of visibleRegions){
        if(abort.signal.aborted)return;
        try{
          const mesh=meshCache.current[id]??await api<RegionMesh>('region',{id},abort.signal);
          if(mesh.units!=='nm'||mesh.id!==id)throw new Error('Reference coordinate mismatch');
          if(!abort.signal.aborted){meshCache.current[id]=mesh;setMeshes(current=>({...current,[id]:mesh}));}
        }catch(e){if(!abort.signal.aborted)setRegionError(message(e));}
      }
    })();return()=>abort.abort();
  },[visibleRegions.join(',')]);
  useEffect(()=>{
    const abort=new AbortController();setSynapses(null);setSynapseError('');setSynapsePending(false);
    if(connection){setSynapsePending(true);void api<SynapseResult>('synapses',{source:connection.source,target:connection.target,confidence:String(confidence)},abort.signal)
      .then(data=>{if(data.source!==connection.source||data.target!==connection.target||data.units!=='8 nm')throw new Error('Synapse identity or coordinates mismatch');setSynapses(data);})
      .catch(e=>{if(!abort.signal.aborted)setSynapseError(message(e));})
      .finally(()=>{if(!abort.signal.aborted)setSynapsePending(false);});}
    return()=>abort.abort();
  },[connection,confidence]);
  const selectedNode=graph?.neurons.find(n=>n.bodyId===selected);
  const rendered=ids.flatMap(id=>skeletons[id]?[skeletons[id]]:[]);
  return <section className="circuit-explorer" aria-label="Real circuit anatomy">
    <header className="circuit-heading"><div><span className="eyebrow">MALECNS v1.0 · RAW STRUCTURAL</span><h2>Explore connected neurons.</h2><p>{manifest?`${manifest.neuronCount.toLocaleString()} Traced neurons · ${manifest.edgeCount.toLocaleString()} recorded connections`:'Connecting to the local catalogue…'}</p></div><button onClick={showWorld}>← Back to fly</button></header>
    <p className="circuit-notice">Source-backed anatomy in shared native coordinates. Anatomical axis directions and alignment to the procedural fly remain unverified. No neural activity is simulated.</p>
    {error&&<p role="alert" className="real-error">{error}</p>}
    <div className="circuit-layout"><aside className="circuit-search">
      <form onSubmit={e=>{e.preventDefault();void find(query);}}><label>Neuron type, body ID or source alias<input aria-label="Search real neurons" value={query} maxLength={100} onChange={e=>setQuery(e.target.value)} placeholder="LB3b, 71254, Quasimodo…"/></label><button disabled={searching}>Search neurons</button></form>
      <p className="small muted">Search uses source annotations. A behavior name does not define a validated functional circuit.</p>
      <button onClick={()=>{setIds(recoveryIds);choose(recoveryIds[0]);setError('');}}>Load recovery five</button>
      <p data-testid="neuron-search-count">{searching?'Searching…':search?`${search.total.toLocaleString()} matches · showing ${search.neurons.length} from ${search.offset+1}`:'No search results'}</p>
      <button disabled={!search||!search.total||search.total>MAX_BODIES||search.neurons.length!==search.total} onClick={()=>{if(search){setIds(search.neurons.map(n=>n.bodyId));choose(search.neurons[0].bodyId);setError('');}}}>Load this result set</button>
      {search&&search.total>MAX_BODIES&&<p className="small muted">Narrow this search or add individual neurons; a view holds up to {MAX_BODIES}.</p>}
      <div className="circuit-results" aria-label="Neuron search results">{search?.neurons.map(n=><div key={n.bodyId}><span><strong>{n.type??'Type unknown'}</strong><small>{n.bodyId} · soma {n.somaSide??'unknown'}</small></span><button onClick={()=>add(n.bodyId)} disabled={ids.includes(n.bodyId)} aria-label={`Add neuron ${n.bodyId}`}>{ids.includes(n.bodyId)?'Added':'Add'}</button></div>)}</div>
      {search&&search.total>50&&<div className="circuit-actions"><button disabled={search.offset===0} onClick={()=>void find(search.query,Math.max(0,search.offset-50))}>Previous results</button><button disabled={search.offset+50>=search.total} onClick={()=>void find(search.query,search.offset+50)}>Next results</button></div>}
      <h3>Anatomical context</h3><p className="small muted">Region surfaces use a 2-µm preview grid. Skeletons retain the official coarse SWC cables; synapses retain source coordinates.</p>{regions.map(r=><label className="circuit-checkbox" key={r.id}><input type="checkbox" checked={visibleRegions.includes(r.id)} onChange={e=>setVisibleRegions(current=>e.target.checked?[...current,r.id]:current.filter(id=>id!==r.id))}/>{r.label} <small>({r.group})</small></label>)}
      <details><summary>Reference surface evidence</summary>{regions.filter(r=>meshes[r.id]).map(r=><div key={r.id}><strong>{r.label}</strong><p className="small">{meshes[r.id].simplification.sourceVertices.toLocaleString()} source vertices → {(meshes[r.id].vertices.length/3).toLocaleString()} preview vertices.</p>{meshes[r.id].sources.map(s=><p className="circuit-source" key={s.url}><a href={s.url} target="_blank" rel="noreferrer">Official mesh source</a> · SHA256 {s.sha256}</p>)}</div>)}</details>
      {regionError&&<p className="real-error">Reference surfaces unavailable: {regionError}</p>}
    </aside><div className="circuit-center">
      <div className="circuit-actions"><strong data-testid="circuit-loaded">{rendered.length}/{ids.length} skeletons loaded</strong><button onClick={()=>setFrame(v=>v+1)}>Fit anatomy</button><button onClick={()=>{setIds([]);setSelected(null);setPartners(null);}}>Clear neurons</button><a href={publicScene(ids)} target="_blank" rel="noreferrer">Open same IDs in Neuroglancer ↗</a></div>
      <Suspense fallback={<p>Loading anatomy renderer…</p>}><CircuitScene skeletons={rendered} regions={visibleRegions.flatMap(id=>meshes[id]?[meshes[id]]:[])} synapses={synapses?.synapses??emptySynapses} selected={selected} onSelect={choose} frame={frame}/></Suspense>
      <p className="small muted">Drag to orbit · scroll to zoom · click a neuron to inspect. Skeleton cables show shape; the connection table records synaptic partners. Source lengths use micrometers in this view.</p>
      <div className="circuit-selection" aria-label="Selected neurons">{ids.map(id=><span key={id} style={{borderColor:bodyColor(id)}}><button aria-pressed={id===selected} onClick={()=>choose(id)}>{graph?.neurons.find(n=>n.bodyId===id)?.type??id} · {id}</button><button aria-label={`Remove neuron ${id}`} onClick={()=>{setIds(current=>current.filter(v=>v!==id));if(selected===id)setSelected(null);}}>×</button>{geometryErrors[id]&&<small role="alert">Anatomy unavailable: {geometryErrors[id]}</small>}</span>)}</div>
      <div className="circuit-actions"><h3>Recorded connections</h3><label>Minimum synapse count<input aria-label="Minimum synapse count" type="number" min={1} max={1000000} value={minWeight} onChange={e=>{const n=Number(e.target.value);if(Number.isInteger(n)&&n>=1&&n<=1000000){setMinWeight(n);setOffset(0);}}}/></label></div>
      <p data-testid="circuit-edge-count">{graph?`${graph.edges.length} shown / ${graph.total} connections among selected neurons · ${graph.filteredOut} below threshold`:'Select neurons to inspect their connections.'}</p>
      <div className="circuit-table"><table><thead><tr><th>Source → target</th><th>Synapses</th><th>Inspect</th></tr></thead><tbody>{graph?.edges.map(e=><tr key={e.source+':'+e.target}><td>{e.source} → {e.target}</td><td>{e.weight}</td><td><button aria-label={`Inspect synapses ${e.source} to ${e.target}`} onClick={()=>setConnection(e)}>Synapse sites</button></td></tr>)}</tbody></table></div>
      {connection&&<div className="circuit-synapses"><h3>{connection.source} → {connection.target}</h3><label>Synapse confidence ≥<input aria-label="Synapse confidence" type="number" min={0.5} max={1} step={0.05} value={confidence} onChange={e=>{const v=Number(e.target.value);if(v>=0.5&&v<=1)setConfidence(v);}}/></label>
        {synapsePending&&<p role="status">Loading recorded synapse sites…</p>}{synapseError&&<p role="alert">Synapse sites unavailable: {synapseError}</p>}
        {synapses&&<><p data-testid="synapse-count">{synapses.shown} shown / {synapses.total} matching synaptic contacts · orange: presynaptic · blue: postsynaptic</p>{confidence===0.5&&synapses.total!==connection.weight&&<p className="real-error">Source mismatch: the connection table has {connection.weight} contacts; the coordinate source returns {synapses.total}. Both values are preserved.</p>}<details><summary>Synapse coordinates and evidence</summary><p>Native XYZ in 8-nm units. Showing the first 100 rows; all displayed markers retain source coordinates.</p><div className="circuit-table"><table><thead><tr><th>Pre XYZ</th><th>Post XYZ</th><th>Confidence pre / post</th><th>Region</th></tr></thead><tbody>{synapses.synapses.slice(0,100).map(s=><tr key={s.id}><td>{s.pre.join(', ')}</td><td>{s.post.join(', ')}</td><td>{s.confidencePre.toFixed(3)} / {s.confidencePost.toFixed(3)}</td><td>{s.roi??'Unknown'}</td></tr>)}</tbody></table></div>{synapses.sources.map(s=><p className="circuit-source" key={s.sha256}><a href={s.url} target="_blank" rel="noreferrer">Official source</a> · SHA256 {s.sha256}{s.range&&` · bytes [${s.range.join(', ')})`}</p>)}</details></>}
      </div>}
    </div><aside className="circuit-inspector"><h3>Neuron record</h3>{selectedNode?<><strong>{selectedNode.type??'Type unknown'} · {selectedNode.bodyId}</strong><dl>{[['Instance',selectedNode.instance],['Source aliases',selectedNode.synonyms],['Superclass',selectedNode.superclass],['Class',selectedNode.class],['Soma side',selectedNode.somaSide],['Root side',selectedNode.rootSide],['Status',selectedNode.status]].map(([k,v])=><div key={k}><dt>{k}</dt><dd>{v??'Unknown'}</dd></div>)}</dl>{skeletons[selectedNode.bodyId]&&<details><summary>Geometry provenance</summary><p className="circuit-source">{skeletons[selectedNode.bodyId].points.length.toLocaleString()} native points · 8-nm units · orientation UNVERIFIED</p><a href={skeletons[selectedNode.bodyId].source.url} target="_blank" rel="noreferrer">Official SWC</a><p className="circuit-source">SHA256 {skeletons[selectedNode.bodyId].source.sha256}</p></details>}</>:<p>Select a neuron to inspect its source record and partners.</p>}
      {selected&&<><h3>Expand connections</h3><label>Direction<select aria-label="Partner direction" value={direction} onChange={e=>{setDirection(e.target.value);setOffset(0);}}><option value="downstream">Downstream outputs</option><option value="upstream">Upstream inputs</option></select></label><p>{partners?`${partners.total.toLocaleString()} partners among Traced neurons`:'Loading partners…'}</p><div className="circuit-results" aria-label="Connected partners">{partners?.partners.map(p=><div key={p.neuron.bodyId}><span><strong>{p.neuron.type??'Type unknown'}</strong><small>{p.neuron.bodyId} · {p.edge.weight} synapses</small></span><button disabled={ids.includes(p.neuron.bodyId)} aria-label={`Expand to neuron ${p.neuron.bodyId}`} onClick={()=>add(p.neuron.bodyId)}>{ids.includes(p.neuron.bodyId)?'Added':'Add'}</button></div>)}</div>{partners&&partners.total>50&&<div className="circuit-actions"><button disabled={!offset} onClick={()=>setOffset(v=>Math.max(0,v-50))}>Previous partners</button><button disabled={offset+50>=partners.total} onClick={()=>setOffset(v=>v+50)}>Next partners</button></div>}</>}
    </aside></div>
    <details className="circuit-provenance"><summary>Dataset, scope and source evidence</summary><p>{DATASET} · UUID {DATASET_UUID}. Catalogue: source status Traced. Connections: induced Traced-to-Traced graph at source confidence 0.5; glia and untraced fragments are excluded. Up to {MAX_BODIES} selected neurons, 800,000 skeleton points and 5,000 synaptic contacts per connection.</p><p>Reference region surfaces are for visual context. Anatomical directions, current mutation alignment and avatar registration remain unverified. A recorded structural path does not establish a functional circuit.</p>{manifest&&Object.values(manifest.sources).map(s=><p className="circuit-source" key={s.name}><a href={s.url}>{s.name}</a> · SHA256 {s.sha256}</p>)}<p>Data: FlyEM / HHMI Janelia and collaborators, CC-BY. The full graph stays on the local server; only requested records and geometry enter this browser.</p></details>
  </section>;
}
