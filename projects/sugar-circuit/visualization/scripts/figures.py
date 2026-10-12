"""Deterministic, publication-resolution structural display derivatives."""
import collections
import json
import math
import xml.etree.ElementTree as ET
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Patch
from matplotlib.path import Path as DrawPath
from model import PALETTE, SENSORY, MOTORS, PAPER, CANDIDATES, ALIASES, CONDITIONS, width

INK = '#182D3C'
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 12, 'svg.fonttype': 'none',
                     'pdf.fonttype': 42, 'savefig.facecolor': 'white'})


def save(fig, out, name, tooltips=None):
    paths = []
    for ext in ['svg', 'pdf', 'png']:
        p = out / (name + '.' + ext)
        fig.savefig(p, dpi=320)
        paths.append(p)
    plt.close(fig)
    if tooltips:
        p = paths[0]
        tree = ET.parse(p)
        ns = 'http://www.w3.org/2000/svg'
        ET.register_namespace('', ns)
        for elem in tree.iter():
            if elem.get('id') in tooltips:
                title = ET.Element('{' + ns + '}title')
                title.text = tooltips[elem.get('id')]
                elem.insert(0, title)
        tree.write(p, encoding='utf-8', xml_declaration=True)
    return paths


def header(fig, label, title, subtitle):
    fig.text(.035, .965, label, weight='bold', color=INK, size=12)
    fig.text(.035, .935, title, weight='bold', color=INK, size=23)
    fig.text(.035, .907, subtitle, color='#435465', size=12)


def paper_diagram(model, out, relation):
    nodes = {n['body_id']: n for n in model['nodes']}
    disp = {}
    ids = {}
    for n in nodes.values():
        if n['type'] not in SENSORY + PAPER + MOTORS:
            continue
        k = n['type'] + ':' + n['side'] if n['type'] in SENSORY else n['body_id']
        ids[n['body_id']] = k
        if k not in disp:
            disp[k] = dict(n, members=[])
        disp[k]['members'].append(n['body_id'])
    edges = {}
    for e in model['edges']:
        if not e['paper_associated']:
            continue
        a, b = e['source'], e['target']
        same = nodes[a]['side'] == nodes[b]['side']
        if (relation == 'same_side') != same:
            continue
        pair = ids[a], ids[b]
        if pair not in edges:
            edges[pair] = dict(raw_synapse_count=0, members=[])
        edges[pair]['raw_synapse_count'] += e['raw_synapse_count']
        edges[pair]['members'].append(e)
    fig, ax = plt.subplots(figsize=(26, 16))
    fig.subplots_adjust(left=.035, right=.98, top=.86, bottom=.15)
    title = 'Figure 1 · Tastekin Figure 6 counterparts · ' + ('same-side endpoints' if relation == 'same_side' else 'opposite-side endpoints')
    header(fig, 'PAPER-ASSOCIATED', title,
           'male-cns:v1.0 · current raw weights · mapped motif subset · computational replication remains BLOCKED')
    ax.set(xlim=(0, 26), ylim=(-.4, 10.9)); ax.axis('off')
    ax.axvline(13, color='#D9DFE4', ls='--', lw=1)
    ax.text(6.2, 10.55, 'LEFT CNS', ha='center', weight='bold', size=17, color=INK)
    ax.text(19.8, 10.55, 'RIGHT CNS', ha='center', weight='bold', size=17, color=INK)
    layer_types = [SENSORY, ['GNG042', 'ANXXX462a'], ['GNG585'],
                   ['GNG015', 'GNG108', 'GNG120', 'GNG472'], MOTORS]
    ys = [9.3, 7.0, 4.9, 2.9, .65]
    pos = {}; boxes = {}; tips = {}
    for li, types in enumerate(layer_types):
        for side, lo, hi in [('L', .1, 12.6), ('R', 13.4, 25.9)]:
            ns = sorted([(k, n) for k, n in disp.items() if n['type'] in types and n['side'] == side],
                        key=lambda item: (types.index(item[1]['type']), int(item[1]['body_id'])))
            for j, (k, n) in enumerate(ns):
                x = lo + (hi-lo) * (j+.5) / len(ns); y = ys[li]
                # Reserve the left branch lane for Quasimodo→GNG015. A long arrow
                # must never be hidden by an unrelated intervening neuron box.
                if li == 1: x = lo + (1.50 if n['type']=='GNG042' else 8.4)
                if li == 2: x = lo + (5.6 + 4.1*j if len(ns)>1 else 8.4)
                w = min(3.0 if li==1 else 3.35, (hi-lo) / len(ns) - .13)
                h = 1.86 if li == 0 else .78
                pos[k] = (x, y); boxes[k] = (w, h)
    maxw = max(e['raw_synapse_count'] for e in edges.values())
    # Draw edges first so endpoints are occluded by opaque node boxes.
    for i, ((a, b), e) in enumerate(sorted(edges.items())):
        x, y = pos[a]; xx, yy = pos[b]
        style=dict(arrowstyle='-|>', mutation_scale=15, linewidth=width(e['raw_synapse_count'], maxw),
                   color='#5C6D79', alpha=.67,zorder=1)
        if y-yy > 3:
            top=y-boxes[a][1]/2; bottom=yy+boxes[b][1]/2; rail=top-(.26 if xx>=x else .43)
            sign=1 if xx>x else -1
            path=DrawPath([(x,top),(x,rail),(x+sign*.08,rail),(xx-sign*.08,rail),
                           (xx,rail),(xx,rail-.18),(xx,bottom)],
                          [DrawPath.MOVETO,DrawPath.CURVE3,DrawPath.CURVE3,DrawPath.LINETO,
                           DrawPath.CURVE3,DrawPath.CURVE3,DrawPath.LINETO])
            arrow=FancyArrowPatch(path=path,**style)
        else:
            top=y-boxes[a][1]/2; bottom=yy+boxes[b][1]/2; middle=(top+bottom)/2
            # Monotone vertical Bezier stays entirely in the inter-layer gap;
            # circular arcs over long cross-side spans can pass through boxes.
            path=DrawPath([(x,top),(x,middle),(xx,middle),(xx,bottom)],
                          [DrawPath.MOVETO,DrawPath.CURVE4,DrawPath.CURVE4,DrawPath.CURVE4])
            arrow=FancyArrowPatch(path=path,**style)
        gid = 'edge_' + str(i); arrow.set_gid(gid); ax.add_patch(arrow)
        tips[gid] = json.dumps(e, ensure_ascii=False)
        # All exact values remain on SVG hover and in the body-edge table.
        if len(edges) <= 35:
            ax.text((x+xx)/2, (y+yy)/2, str(e['raw_synapse_count']), size=10,
                    ha='center', color=INK, bbox=dict(facecolor='white', edgecolor='none', pad=.4), zorder=2)
    for k, n in disp.items():
        x, y = pos[k]; w, h = boxes[k]
        box = FancyBboxPatch((x-w/2, y-h/2), w, h, boxstyle='round,pad=0.025',
                             facecolor=n['color'], edgecolor=INK, lw=1.1, zorder=3)
        box.set_gid('node_' + k.replace(':', '_')); ax.add_patch(box)
        tips[box.get_gid()] = json.dumps(n, ensure_ascii=False)
        title = n['type'] + (('\n' + n['display_alias']) if n['display_alias'] else '')
        if n['type'] in SENSORY:
            members = n['members']
            bodylines = '\n'.join(' · '.join(members[i:i+2]) for i in range(0, len(members), 2))
            title += f' · {len(members)} bodies\n' + bodylines
            size = 11
        else:
            title += '\n' + n['body_id']; size = 12
        ax.text(x, y, title, va='center', ha='center', size=size,
                color='white' if n['role'] == 'premotor' else INK, zorder=4)
    fig.legend(handles=[Patch(facecolor=PALETTE[k], label=label) for k, label in
                        [('LB3b','LB3b'),('LB3c','LB3c'),('sensory','Other LB3'),('second_order','Second-order'),
                         ('higher_order','Higher-order'),('premotor','Premotor'),('motor','Motor')]],
               loc='lower center', bbox_to_anchor=(.5,.103), ncol=7, frameon=False, fontsize=12)
    fig.text(.035,.089, 'Puddle: UNRESOLVED — no body mapping and no replacement node. MN6: verified target; no mapped named motif drawn here.', size=12, color=INK)
    fig.text(.035,.064, 'Sensory cards pool bodies only within subtype and side; arrows from these cards sum their listed raw body edges. All other nodes are individual bodies.', size=12)
    fig.text(.035,.042, 'Width = 0.7 + 4.3 √(raw count / panel maximum). Exact counts and member edges: SVG hover and data tables. No physiological sign.', size=12)
    fig.text(.035,.020, 'Same/opposite refers to soma/root labels, not localized midline crossings. Eight paper/current pooled discrepancies persist; this is not a selected sugar pathway.', size=12)
    name = 'figure1_paper_' + relation
    return save(fig, out, name, tips), dict(id=name, label='PAPER-ASSOCIATED',
        question='Which verified current v1.0 bodies instantiate the mapped Figure 6 motifs?',
        node_rule='All 77 LB3 inputs, 15 verified named counterpart bodies and 10 motors. Sensory display cards group subtype+side, with all member IDs retained.',
        edge_rule='Union of frozen paper_associated_paths.csv edges; split by same/opposite endpoint side; sum only sensory-card outgoing counts.',
        sources=['nodes.csv','raw_edges.csv','paper_associated_paths.csv','paper_motif_comparison.csv'],
        layout='Layered sensory → second-order → higher-order / premotor → body-level motors; left/right columns.',
        filters=relation + '; no weight threshold; no guessed Puddle edges; MN6 retained as an unconnected target in this motif subset',
        width='0.7 + 4.3*sqrt(raw_count/panel_max); sensory counts are explicit sums',
        limitations='Not strict replication; eight source discrepancies; sensory aggregation; diagram layers follow paper motifs, not general functional classification; all body pairs available in graph/HTML.')


def candidate_comparison(model, out):
    fig, axes = plt.subplots(3, 2, figsize=(20, 15))
    fig.subplots_adjust(left=.04, right=.975, top=.865, bottom=.135, hspace=.30, wspace=.10)
    header(fig, 'CANDIDATE', 'Figure 3 · Six independent candidate comparisons',
           'male-cns:v1.0 · direct raw input/output summaries · no single pathway or algorithm-selected membership is asserted')
    node_map = {n['body_id']: n for n in model['nodes']}
    for ax, t in zip(axes.flat, CANDIDATES):
        ax.axis('off')
        ns = sorted([n for n in model['nodes'] if n['type'] == t], key=lambda n:n['side'])
        name = (ALIASES[t] + ' / ' if t in ALIASES else '') + t
        ax.text(0,1,name, transform=ax.transAxes, size=19, weight='bold', color=INK)
        badges = ' + '.join(ns[0]['evidence'])
        ax.text(1,1,badges,transform=ax.transAxes,ha='right',size=14,weight='bold',
                bbox=dict(facecolor='white',edgecolor=INK,boxstyle='round,pad=.3'))
        ax.text(0,.85, 'Fill: ' + ns[0]['role'].replace('_',' ') + '  |  outlined because requested for comparison',
                transform=ax.transAxes, size=11, color='#526574')
        cells=[]
        for n in ns:
            v=n['body_id']; weights=[]
            for source in ['LB3b','LB3c']:
                weights.append(sum(e['raw_synapse_count'] for e in model['edges'] if e['target']==v and node_map[e['source']]['type']==source))
            for target in MOTORS:
                weights.append(sum(e['raw_synapse_count'] for e in model['edges'] if e['source']==v and node_map[e['target']]['type']==target))
            cells.append([n['side']+' · '+v]+weights)
        table=ax.table(cellText=cells, colLabels=['Side · body','LB3b →','LB3c →','→ MN4a','→ MN6','→ MN8','→ MN9'],
                       cellLoc='center',bbox=[0,.35,1,.39],colWidths=[.22]+[.13]*6)
        table.auto_set_font_size(False);table.set_fontsize(12)
        for (row,col),cell in table.get_celld().items():
            cell.set_edgecolor('#CFD8DF')
            if row==0:cell.set_facecolor('#EDF2F5')
            elif col==0:cell.set_facecolor(ns[row-1]['color']);cell.set_text_props(color='white' if ns[row-1]['role']=='premotor' else INK)
        support = ('P: '+('S16A / S19 labels' if t=='DNg67' else 'S16A label' if t=='GNG232' else 'S19 label')+'; selected membership unverified.'
                   if t in ['GNG232','DNg67','DNge080'] else 'P: mapped Figure 6 motif counterpart.' if 'P' in ns[0]['evidence'] else 'P: paper presence unverified; not an absence claim.')
        ax.text(0,.20,'Counts pool sensory/motor partners across both sides; body detail in explorer.\n'+support,transform=ax.transAxes,size=11)
        ax.text(0,.035,('E: selected in validated result(s)' if any('E' in n['evidence'] for n in ns) else 'E: not assessed')+
                '    D: unverified    X: unverified',transform=ax.transAxes,size=12,color='#526574')
    fig.text(.04,.091,'P = paper-selected/support (here: inspected paper-associated support); R = raw MaleCNS structure; E = effective selection; D = dynamic/Shiu; X = experimental.',size=12)
    fig.text(.04,.064,'An annotation synonym beginning “Shiu 2022” does not earn a D badge. No body-mapped dynamic or experimental evidence has been ingested.',size=12)
    fig.text(.04,.037,'Unknown biological order stays gray. Candidate interest changes outlines/badges, never role fill. Zero means no direct record in this scoped view.',size=12)
    return save(fig,out,'figure3_candidate_comparison'),dict(id='figure3_candidate_comparison',label='CANDIDATE',
        question='Why are these six types included, and what are their direct raw sensory/motor connections?',
        node_rule='Exactly six user-requested candidate types; 12 individual bodies with preserved sides.',
        edge_rule='Direct LB3b/LB3c→candidate and candidate→four motor types; table sums across endpoint type bodies.',
        sources=['nodes.csv','raw_edges.csv','paper/supplement/supplemental_information.pdf pp17,20',
                 'results/method_recovery/20261006T214639Z/audit_snapshot_final/logs/claim_ledger.csv C061'],layout='Six separate cards with two body rows each; no candidate-to-candidate pathway drawing.',
        filters='Only requested comparison types and direct sensory/motor boundaries; no effective, Shiu or experimental badges without evidence.',
        width='Not applicable: exact raw counts in tables, no drawn edges.',
        limitations='Raw counts are not normalized strengths; order for GNG021/GNG232/DNg67/DNge080 remains unknown; no dynamic validation implied by aliases.')


def sugar_panels(model, out):
    fig, axes=plt.subplots(2,2,figsize=(18,12))
    fig.subplots_adjust(left=.045,right=.965,top=.845,bottom=.12,hspace=.27,wspace=.12)
    header(fig,'SUGAR-RESTRICTED EFFECTIVE-CONNECTIVITY','Figure 2 · Validated sugar-circuit display slots',
           'A · LB3b     B · LB3c     C · LB3b + LB3c     D · overlap / difference')
    selected=model['selected_results']; conditions=selected.get('conditions',{})
    for i,(ax,title) in enumerate(zip(axes.flat,['A · LB3b','B · LB3c','C · LB3b + LB3c','D · overlap / difference'])):
        ax.set_facecolor('#F4F7F9');ax.set_xticks([]);ax.set_yticks([])
        for sp in ax.spines.values():sp.set_color('#D6E0E7')
        ax.text(.055,.88,title,transform=ax.transAxes,size=19,weight='bold',color=INK)
        if not conditions:
            ax.text(.055,.58,'BLOCKED — VALIDATED RESULTS REQUIRED',transform=ax.transAxes,size=13,weight='bold')
            ax.text(.055,.38,'No algorithm-selected intermediates or edges populated.\nNo raw path union is substituted for selected membership.',transform=ax.transAxes,size=13,linespacing=1.7)
        elif i<3:
            result=conditions[CONDITIONS[i]]
            ax.text(.055,.59,f"{len(result['node_ids'])} validated bodies · {len(result['edges'])} edges",transform=ax.transAxes,size=16)
            ax.text(.055,.35,'Open the switchable HTML graph for body-level membership,\nraw/score width modes, and complete score provenance.',transform=ax.transAxes,size=13)
        else:
            a=set(conditions['lb3b_only']['node_ids']);b=set(conditions['lb3c_only']['node_ids']);c=set(conditions['lb3b_lb3c_combined']['node_ids'])
            ax.text(.055,.6,f'Shared: {len(a&b)}   A only: {len(a-b)}   B only: {len(b-a)}',transform=ax.transAxes,size=15)
            ax.text(.055,.38,f'Combined-only: {len(c-(a|b))}\nComputed from validated condition memberships, not assumed union.',transform=ax.transAxes,size=13)
    fig.text(.045,.070,'The exact Tastekin algorithm is not implemented here. This framework only consumes independently validated, provenance-bearing result files.',size=12)
    fig.text(.045,.041,'Current LB3b/LB3c identity is verified; their retained downstream membership remains unpopulated until that analysis is complete.',size=12)
    return save(fig,out,'figure2_sugar_panels'),dict(id='figure2_sugar_panels',label='SUGAR-RESTRICTED EFFECTIVE-CONNECTIVITY',
        question='Which bodies and edges are retained independently for LB3b, LB3c and combined inputs?',
        node_rule='Only explicitly listed membership from validated selected-result contract; currently none.',
        edge_rule='Only validated selected-result edges with separately preserved raw counts and effective scores; currently none.',
        sources=['selected_results contract; currently absent'],layout='Four switchable HTML panels; matching four-panel static status sheet.',
        filters='No raw search memberships used. Overlap/difference derives from the independent validated sets.',
        width='HTML supports separate raw sqrt and effective-score sqrt modes; no score fallback.',
        limitations='BLOCKED pending validated Tastekin effective-connectivity results. Status sheet is not a circuit result.')


def render_all(model,out):
    records=[]
    for func,arg in [(paper_diagram,'same_side'),(paper_diagram,'opposite_side'),(sugar_panels,None),(candidate_comparison,None)]:
        files,record=func(model,out,arg) if arg else func(model,out)
        record['files']=[str(p) for p in files];records.append(record)
    return records
