"""Behavior tests on small cyclic graphs, independent of biological hypotheses."""
import importlib.util,unittest,collections
from pathlib import Path
spec=importlib.util.spec_from_file_location('trace',Path(__file__).with_name('07_trace_structural_paths.py'))
trace=importlib.util.module_from_spec(spec);spec.loader.exec_module(trace)

class StructuralSearchTests(unittest.TestCase):
    def test_cycles_bound_and_multiple_targets(self):
        adj={1:[2,3],2:[1,3,4],3:[2,4],4:[5],5:[]}
        targets={4,5};reverse=collections.defaultdict(list)
        for a,bs in adj.items():
            for b in bs:reverse[b].append(a)
        distance={t:0 for t in targets};queue=collections.deque(targets)
        while queue:
            b=queue.popleft()
            for a in reverse[b]:
                if a not in distance:distance[a]=distance[b]+1;queue.append(a)
        def brute(path,bound):
            result={path} if len(path)>1 and path[-1] in targets else set()
            if len(path)-1<bound:
                for b in adj[path[-1]]:
                    if b not in path:result|=brute(path+(b,),bound)
            return result
        for bound in range(1,6):
            found=set(trace.simple_paths(adj,[1],targets,distance,bound))
            self.assertEqual(found,brute((1,),bound))
            self.assertTrue(all(len(p)==len(set(p)) for p in found))
    def test_combined_sources_are_exact_union(self):
        adj={1:[3],2:[3,4],3:[4],4:[]};d={1:2,2:1,3:1,4:0}
        a=set(trace.simple_paths(adj,[1],[4],d,4));b=set(trace.simple_paths(adj,[2],[4],d,4))
        self.assertEqual(set(trace.simple_paths(adj,[1,2],[4],d,4)),a|b)
    def test_unreachable_and_one_synapse_edges(self):
        self.assertEqual(list(trace.simple_paths({1:[2],2:[]},[1],[3],{3:0},4)),[])
        self.assertEqual(list(trace.simple_paths({1:[2]},[1],[2],{1:1,2:0},1)),[(1,2)])
    def test_scc_and_annotation_groups(self):
        spec=importlib.util.spec_from_file_location('exporter',Path(__file__).with_name('09_export_structural_checkpoint.py'))
        exporter=importlib.util.module_from_spec(spec);spec.loader.exec_module(exporter)
        lab,sizes=exporter.scc([1,2,3],[(1,2),(2,3)])
        self.assertEqual(len(set(lab.values())),3)
        lab,sizes=exporter.scc([1,2,3],[(1,2),(2,1),(2,3)])
        self.assertEqual(lab[1],lab[2]);self.assertNotEqual(lab[2],lab[3])
        self.assertEqual(exporter.classification('cb_sensory','X'),'sensory')
        self.assertEqual(exporter.classification('vnc_motor','X'),'motor')
        self.assertEqual(exporter.classification('cb_sensory_tbc','X'),'uncertain_annotated_class')
        self.assertEqual(exporter.classification(None,''),'unclassified')

if __name__=='__main__':unittest.main()
