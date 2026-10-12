"""Create and cell-validate an Excel workbook from the frozen connection tables.

Run with the project's virtual environment and requirements-excel.txt.
This changes presentation only; it does not select a circuit or refresh data.
"""
import csv
import datetime as dt
import hashlib
import json
from pathlib import Path
import re
import sys
import xml.etree.ElementTree as ET
import zipfile

import xlsxwriter

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'results/connection_tables/20261007T220046456321Z'
SHEETS = [
    ('Neurons', 'all_lb3_motor_nodes_up_to_4_hops.csv', 'BROAD: all bodies/segments on saved LB3-to-motor routes of up to four hops.'),
    ('Connections', 'all_lb3_motor_direct_edges_up_to_4_hops.csv', 'BROAD: all constituent directed edges in that four-hop path union.'),
    ('LB3 Motor Reachability', 'all_lb3_motor_body_pair_reachability.csv', 'BROAD: all 770 sensory-to-motor body pairs, distances and exact bounded path counts.'),
    ('Network Growth', 'network_size_by_hop.csv', 'BROAD: exact path-union size at each hop bound.'),
    ('Tracked Neurons', 'tracked_neurons.csv', 'COMPACT: 110 previously tracked bodies only.'),
    ('Tracked Direct Edges', 'tracked_direct_edges.csv', 'COMPACT: direct edges among the 110 tracked bodies.'),
    ('Tracked Pair Routes', 'tracked_body_pairs_direct_and_indirect.csv', 'COMPACT: all 11,990 ordered distinct pairs among 110 bodies; indirect examples use only that view.'),
    ('Tracked Type Matrix', 'tracked_type_connection_matrix.csv', 'COMPACT: 19-type matrix; D = direct synapse total, I = minimum indirect hops, + = both.'),
    ('Tracked Type Pairs', 'tracked_type_pair_details.csv', 'COMPACT: type-pair summaries backed by body-resolved routes.'),
]
INTEGER_FIELDS = {'weight','raw_synapses','nodes','edges','max_hops','shortest_hops','direct_synapse_count',
    'shortest_path_count','shortest_paths_saved','bound_hops','minimum_bounded_path_hops',
    'direct_synapses','shortest_indirect_hops','direct_pooled_synapses','direct_body_pairs',
    'body_pairs_with_indirect_route','minimum_indirect_hops'}
ID_FIELDS = {'body_id','source','target'}


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1024*1024), b''):
            h.update(block)
    return h.hexdigest()


def converted(field, value):
    if not value or field in ID_FIELDS:
        return value
    if value in ['True','False']:
        return value=='True'
    if field in INTEGER_FIELDS or field.startswith('simple_paths_h'):
        return int(value)
    return value


def row_digest(hasher, values):
    hasher.update((json.dumps(values,ensure_ascii=False,separators=(',',':'))+'\n').encode())


def cell_column(reference):
    n=0
    for char in re.match(r'[A-Z]+',reference)[0]:
        n=n*26+ord(char)-64
    return n-1


def validate_workbook(path, expected):
    """Independently parse OOXML and compare every typed data cell to the CSVs."""
    ns={'s':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
    result={}
    with zipfile.ZipFile(path) as z:
        assert z.testzip() is None
        for sheet_index, (sheet, info) in enumerate(expected.items(),2):
            # Guide is sheet1; the nine data sheets follow in declared order.
            h=hashlib.sha256(); count=0; frozen=False; filtered=False
            with z.open(f'xl/worksheets/sheet{sheet_index}.xml') as f:
                for _,element in ET.iterparse(f,events=('end',)):
                    tag=element.tag.rsplit('}',1)[-1]
                    if tag=='pane':
                        frozen=element.get('state')=='frozen' and element.get('ySplit')=='1'
                    if tag=='autoFilter':
                        filtered=True
                    if tag!='row':
                        continue
                    values=['']*len(info['headers'])
                    for cell in element.findall('s:c',ns):
                        col=cell_column(cell.get('r'))
                        kind=cell.get('t')
                        if kind=='inlineStr':
                            value=''.join(t.text or '' for t in cell.findall('.//s:t',ns))
                        else:
                            text=cell.findtext('s:v',default='',namespaces=ns)
                            if kind=='b': value=text=='1'
                            elif text: value=int(text)
                            else: value=''
                        assert cell.find('s:f',ns) is None, 'Unexpected formula in data sheet'
                        if count>0 and info['headers'][col] in ID_FIELDS and value!='':
                            assert kind=='inlineStr' and isinstance(value,str), 'Body ID was converted to a number'
                        values[col]=value
                    if count==0:
                        assert values==info['headers']
                    else:
                        row_digest(h,values)
                    count+=1
                    element.clear()
            assert count-1==info['rows'],(sheet,count,info['rows'])
            assert h.hexdigest()==info['typed_data_sha256'], f'Cell mismatch: {sheet}'
            assert frozen and filtered
            result[sheet]=dict(data_rows=count-1,all_typed_cells_match_csv=True,body_ids_preserved_as_text=True,
                               frozen_headers=True,filters=True)
    return result


def main():
    stamp=dt.datetime.now(dt.timezone.utc)
    out=ROOT/'results/excel'/stamp.strftime('%Y%m%dT%H%M%S%fZ')
    out.mkdir(parents=True,exist_ok=False)
    output=out/'MaleCNS_LB3_Broader_Network.xlsx'
    manifest=json.loads((SOURCE/'manifest.json').read_text())
    expected_hash={r['path']:r['sha256'] for r in manifest['output_files']}
    assert manifest['dataset']=='male-cns:v1.0' and manifest['dataset_uuid']=='4b2087c0fbe046bfaf0d60bc970e3e5d'
    inputs=[]
    for _,filename,_ in SHEETS:
        p=SOURCE/filename;sha=digest(p)
        assert sha==expected_hash[str(p.relative_to(ROOT))],f'Input changed: {p}'
        inputs.append(dict(path=str(p.relative_to(ROOT)),sha256=sha,bytes=p.stat().st_size))
    summary=json.loads((SOURCE/'summary.json').read_text())
    assert digest(SOURCE/'summary.json')==expected_hash[str((SOURCE/'summary.json').relative_to(ROOT))]
    book=xlsxwriter.Workbook(str(output),{'constant_memory':True,'strings_to_formulas':False,'strings_to_urls':False})
    book.set_properties({'title':'MaleCNS LB3 broader structural network','subject':'Complete saved four-hop LB3-to-motor path union',
        'author':'Flybrain research project','comments':'Saved male-cns:v1.0 snapshot from 6 October 2026; structural connectivity only.'})
    title=book.add_format({'bold':True,'font_size':20,'font_color':'#FFFFFF','bg_color':'#16324F','valign':'vcenter'})
    header=book.add_format({'bold':True,'font_color':'#FFFFFF','bg_color':'#16324F','text_wrap':True,'valign':'vcenter','border':0})
    guide_key=book.add_format({'bold':True,'font_color':'#16324F','valign':'top','text_wrap':True})
    guide_value=book.add_format({'text_wrap':True,'valign':'top'})
    link_format=book.add_format({'font_color':'#166A91','underline':True,'bold':True})
    formats={}
    for striped in [False,True]:
        base={'valign':'top','bg_color':'#EFF4F8' if striped else '#FFFFFF','font_size':10}
        formats[striped,'text']=book.add_format(base)
        formats[striped,'id']=book.add_format({**base,'num_format':'@'})
        formats[striped,'number']=book.add_format({**base,'num_format':'#,##0'})
    guide=book.add_worksheet('Guide');guide.hide_gridlines(2);guide.set_tab_color('#16324F')
    guide.set_column('A:A',30);guide.set_column('B:B',116)
    guide.merge_range('A1:B1','LB3 → feeding motor network',title);guide.set_row(0,38)
    guide.write_row(2,0,['Dataset','male-cns:v1.0 | saved 6 October 2026'],guide_value)
    facts=[
        ('Scope','Complete saved LB3a–d → MN4a/MN6/MN8/MN9 structural path union, up to four edges per route.'),
        ('Bodies / segments',f"{summary['broad_nodes']:,} entries; {summary['broad_unannotated_nodes']:,} lack annotations. They are not all identified neurons."),
        ('Direct connections',f"{summary['broad_edges']:,} directed edges, with raw synapse counts; no rows removed for Excel."),
        ('Indirect connectivity','LB3 Motor Reachability gives all 770 sensory-to-motor pairs and exact counts of simple paths at 1, 2, 3 and 4 hops.'),
        ('How to explore','Start with Neurons or Connections. Use the header filter arrows to select a type, body ID, side or starting LB3 subtype. Headers and identifying columns stay visible while scrolling.'),
        ('Direction','Each Connections row is source → target. The reverse direction is a separate row when present.'),
        ('Body identifiers','IDs are stored as text to preserve all digits. Synapse/path counts are numeric, so you can sort and sum them.'),
        ('Missing annotations','Blank type or side fields stay blank. Use annotation_present to distinguish missing annotation records.'),
        ('Path membership','Connections lists edges participating in at least one complete saved LB3-to-motor path of up to four hops. It is not every possible edge between these nodes.'),
        ('Bounded completeness','No whole-connectome all-pairs catalog or full listing of the 223,674,804 individual bounded routes is included. Complete saved node/edge membership and endpoint path counts are included.'),
        ('Compact reference sheets','Tabs starting with Tracked contain the smaller 110-body view. Their indirect routes use only those bodies; a missing route there is not whole-network absence.'),
        ('Scientific interpretation','Raw structural connectivity only. Connection counts and path existence do not establish effective connectivity, physiological activation, or a selected sugar circuit.'),
        ('Source identity',manifest['dataset_uuid']),
        ('Workbook created',stamp.isoformat()),
    ]
    for row,(key,value) in enumerate(facts,4):
        guide.write_string(row,0,key,guide_key);guide.write_string(row,1,value,guide_value)
        guide.set_row(row,42 if len(value)>140 else 31)
    row=20
    guide.write_row(row,0,['Open a sheet','Contents'],header);guide.set_row(row,28)
    for sheet,_,scope in SHEETS:
        row+=1
        guide.write_url(row,0,f"internal:'{sheet}'!A1",link_format,sheet)
        guide.write_string(row,1,scope,guide_value);guide.set_row(row,30)
    guide.freeze_panes(3,0)
    schemas={}
    for sheet,filename,scope in SHEETS:
        ws=book.add_worksheet(sheet);ws.hide_gridlines(2)
        ws.set_tab_color('#784C9E' if sheet.startswith('Tracked') else '#166A91')
        ws.freeze_panes(1,3 if sheet=='Connections' else 1)
        ws.set_zoom(90);ws.set_row(0,38)
        h=hashlib.sha256();count=0
        with (SOURCE/filename).open() as f:
            reader=csv.DictReader(f);fields=reader.fieldnames
            ws.write_row(0,0,fields,header)
            for col,field in enumerate(fields):
                width=17 if field in ID_FIELDS else 20
                if field in ['type','source_type','target_type']:width=22
                if 'side' in field:width=13
                if field in ['source_label','target_label','instance']:width=34
                if field in ['scope','provenance','query_provenance','example_route']:width=64
                if field in ['example_body_ids','example_edge_synapses','source_subtype_membership']:width=38
                ws.set_column(col,col,width)
            for count,row in enumerate(reader,1):
                values=[converted(field,row[field]) for field in fields]
                row_digest(h,values)
                for col,(field,value) in enumerate(zip(fields,values)):
                    fmt=formats[bool(count%2),'id' if field in ID_FIELDS else 'number' if isinstance(value,int) and not isinstance(value,bool) else 'text']
                    if value=='':ws.write_blank(count,col,None,fmt)
                    elif isinstance(value,bool):ws.write_boolean(count,col,value,fmt)
                    elif isinstance(value,int):ws.write_number(count,col,value,fmt)
                    else:ws.write_string(count,col,value,fmt)
        assert count+1<=1_048_576
        ws.autofilter(0,0,count,len(fields)-1)
        schemas[sheet]=dict(rows=count,headers=fields,source=filename,typed_data_sha256=h.hexdigest(),scope=scope)
        print(f'Wrote {sheet}: {count:,} rows',flush=True)
    assert schemas['Neurons']['rows']==23207 and schemas['Connections']['rows']==354639
    assert schemas['LB3 Motor Reachability']['rows']==770 and schemas['Tracked Pair Routes']['rows']==11990
    definitions=[
        ('body_id / source / target','Exact reconstruction body/segment identifier. Text cells preserve identifiers.'),
        ('type / source_type / target_type','Saved cell-type annotation; blank means no type annotation supplied.'),
        ('side / source_side / target_side','Saved soma/root-side annotation; not proof of where a synapse crosses the midline.'),
        ('annotation_present','Whether an annotation record was present; does not imply complete typing or proofreading.'),
        ('classification / role','Saved display grouping; no new biological classification assigned.'),
        ('weight / raw_synapses / direct_synapses','Raw count of synapses from the source body to the target body.'),
        ('source_subtype_membership','Starting LB3 subtypes whose saved bounded sensory-to-motor paths include this node/edge. Not necessarily direct sensory input.'),
        ('minimum_bounded_path_hops','Shortest COMPLETE sensory-to-motor path containing the edge in the prior structural export. Not the position of this edge within a path.'),
        ('reachable / shortest_hops','Saved full-released-graph reachability and minimum directed hop distance for the stated sensory/motor body pair.'),
        ('simple_paths_h1 ... h4','Exact counts of body-distinct paths at each exact hop length in the prior full-graph search; example-saving caps do not affect counts.'),
        ('shortest_path_count / shortest_paths_saved','Count and saved-example count from the original structural run; route strings are stored separately in that run.'),
        ('indirect_within_4_hops','Existence of a 2–4-edge simple route among the 110 tracked bodies, excluding the direct edge as an alternative.'),
        ('shortest_indirect_hops / minimum_indirect_hops','Minimum indirect route length in the tracked view. Blank means no route found within that view/bound.'),
        ('example_route / example_body_ids','One checked body-level indirect witness, selected deterministically; not necessarily the strongest or paper-selected route.'),
        ('example_edge_synapses','Raw synapse counts in the same order as consecutive steps in example_route.'),
        ('Tracked Type Matrix cells','D<number> = summed direct raw synapses; I<number> = minimum indirect hops; + = both; - = neither found in the tracked view. Diagonals can involve different bodies.'),
        ('direct_pooled_synapses / direct_body_pairs','Sum of raw counts / count of directed body pairs in the compact type-pair view; display pooling only.'),
        ('body_pairs_with_indirect_route','Number of distinct ordered body pairs of the given types with an indirect route in the tracked view.'),
        ('query_provenance / provenance','Relative file references in results/structural/20261006T180116Z, unless a full project-relative path is supplied.'),
        ('circuit A / Network Growth','All LB3a–d sources to the requested feeding-motor bodies, with all allowed intermediate types retained.'),
    ]
    columns=book.add_worksheet('Column Guide');columns.hide_gridlines(2)
    columns.set_column(0,0,46);columns.set_column(1,1,116);columns.freeze_panes(1,0)
    columns.write_row(0,0,['Field / concept','Definition'],header);columns.set_row(0,28)
    for i,(field,definition) in enumerate(definitions,1):
        columns.write_string(i,0,field,guide_key);columns.write_string(i,1,definition,guide_value);columns.set_row(i,42)
    provenance=book.add_worksheet('Provenance');provenance.hide_gridlines(2);provenance.freeze_panes(1,1)
    provenance.set_column(0,0,30);provenance.set_column(1,1,97);provenance.set_column(2,2,70);provenance.set_column(3,3,16)
    provenance.write_row(0,0,['Sheet / artifact','Source path','SHA256','Data rows'],header)
    for i,((sheet,filename,_),source) in enumerate(zip(SHEETS,inputs),1):
        provenance.write_row(i,0,[sheet,source['path'],source['sha256'],schemas[sheet]['rows']],guide_value)
    provenance.write_row(len(SHEETS)+1,0,['Source manifest',str((SOURCE/'manifest.json').relative_to(ROOT)),digest(SOURCE/'manifest.json')],guide_value)
    provenance.write_row(len(SHEETS)+2,0,['Export script',str(Path(__file__).relative_to(ROOT)),digest(Path(__file__))],guide_value)
    provenance.write_row(len(SHEETS)+3,0,['Writer library',f'XlsxWriter {xlsxwriter.__version__}'],guide_value)
    book.close()
    print('Workbook saved; checking every data cell against the source CSVs...',flush=True)
    checks=validate_workbook(output,schemas)
    export_manifest=dict(timestamp=stamp.isoformat(),dataset=manifest['dataset'],dataset_uuid=manifest['dataset_uuid'],
        source_manifest=str((SOURCE/'manifest.json').relative_to(ROOT)),source_manifest_sha256=digest(SOURCE/'manifest.json'),
        inputs=inputs,workbook=str(output.relative_to(ROOT)),workbook_sha256=digest(output),workbook_bytes=output.stat().st_size,
        sheets=schemas,validation=checks,python=sys.version,xlsxwriter_version=xlsxwriter.__version__,
        script_sha256=digest(Path(__file__)),scope='Complete saved four-hop LB3-to-motor path union plus explicitly separate tracked-view reference sheets',
        new_scientific_analysis=False,data_rows_omitted=0,body_ids_as_text=True)
    (out/'manifest.json').write_text(json.dumps(export_manifest,indent=2)+'\n')
    for log in ['STATUS.md','CHANGELOG.md']:
        with (ROOT/log).open('a') as f:
            f.write(f'\n### {stamp.isoformat()} — Excel export of broader structural network\n\n'
                f'Created [{output.name}]({output.relative_to(ROOT)}): all 23,207 saved broad-network nodes/segments,354,639 edges and770 sensory-to-motor pairs, plus separate compact reference sheets. '
                'All data cells round-trip against their hashed CSV inputs; body IDs preserved as text, counts numeric, filters/frozen headers enabled. '
                'Uses the existing four-hop structural scope; no new analysis or biological selection.\n')
    with (ROOT/'logs/run_manifest.jsonl').open('a') as f:
        f.write(json.dumps(dict(timestamp=stamp.isoformat(),experiment='BROAD_NETWORK_EXCEL_EXPORT',run=str(out.relative_to(ROOT)),
            manifest_sha256=digest(out/'manifest.json'),workbook_sha256=export_manifest['workbook_sha256'],all_data_cells_verified=True))+'\n')
    print(json.dumps(dict(workbook=str(output),size_mb=round(output.stat().st_size/1024/1024,2),
        sheets=len(SHEETS)+3,verified_rows=sum(v['rows'] for v in schemas.values())),indent=2))


if __name__=='__main__':
    main()
