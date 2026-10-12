"""Scientific boundary tests use synthetic records, never exported as circuit data."""
import copy
import json
import tempfile
import unittest
from pathlib import Path
from model import VIZ, DATASET, UUID, LABELS, CONDITIONS, load_selected, sha, width
from fetch_skeletons import parse_swc
from anatomy import validate_orientation


class SelectedContract(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(prefix='synthetic-test-',dir=VIZ/'data');self.folder=Path(self.temp.name)
        self.proof=self.folder/'analysis.json';self.proof.write_text(json.dumps(dict(status='PASS',dataset=DATASET,dataset_uuid=UUID,algorithm_version='test',fixture='SYNTHETIC TEST ONLY')))
        self.nodes={'1':{'type':'LB3b'},'2':{'type':'LB3c'},'3':{'type':'TEST_INTERMEDIATE'},'4':{'type':'MN6'}}
        self.raw={('1','3'):{'raw_synapse_count':9},('2','3'):{'raw_synapse_count':4},('3','4'):{'raw_synapse_count':7}}
        self.obj=dict(schema_version=1,dataset=DATASET,dataset_uuid=UUID,status='VALIDATED',scientific_label=LABELS[3],
                      algorithm_source='SYNTHETIC TEST ONLY',algorithm_version='test',method_source='test',selection_definition='test',
                      artifacts={'analysis.json':sha(self.proof)},validation_artifact='analysis.json',conditions={})
        for c,inputs in zip(CONDITIONS,[['1'],['2'],['1','2']]):
            self.obj['conditions'][c]=dict(status='VALIDATED',provenance='SYNTHETIC TEST ONLY',input_body_ids=inputs,node_ids=inputs+['3','4'],edges=[dict(source=v,target='3',raw_synapse_count=self.raw[v,'3']['raw_synapse_count'],effective_connectivity_score=.125,provenance='synthetic') for v in inputs])
    def tearDown(self):self.temp.cleanup()
    def load(self,obj):
        path=self.folder/'selected.json';path.write_text(json.dumps(obj));return load_selected(path,self.nodes,self.raw)
    def test_pending_is_empty(self):
        result=load_selected(None,self.nodes,self.raw);self.assertEqual(result['conditions'],{});self.assertEqual(result['selected_intermediates'],[])
    def test_raw_and_score_remain_distinct(self):
        r=self.load(self.obj)['conditions']['lb3b_only']['edges'][0]
        self.assertEqual(r['raw_synapse_count'],9);self.assertEqual(r['effective_connectivity_score'],.125)
    def test_failed_validation_cannot_be_promoted(self):
        proof=json.loads(self.proof.read_text());proof['status']='FAIL';self.proof.write_text(json.dumps(proof))
        self.obj['artifacts']['analysis.json']=sha(self.proof)
        with self.assertRaises(ValueError):self.load(self.obj)
    def test_rejects_scientific_boundary_violations(self):
        mutations=[lambda o:o.update(dataset='male-cns:v0.9'),lambda o:o.update(status='PENDING'),
                   lambda o:o.update(scientific_label='RAW STRUCTURAL'),lambda o:o.update(algorithm_version=''),
                   lambda o:o['conditions']['lb3b_only'].update(node_ids=['1','999']),
                   lambda o:o['conditions']['lb3b_only']['edges'][0].update(raw_synapse_count=8),
                   lambda o:o['conditions']['lb3b_only']['edges'][0].update(effective_connectivity_score=None),
                   lambda o:o['conditions']['lb3b_only']['edges'][0].update(effective_connectivity_score=float('nan')),
                   lambda o:o['conditions']['lb3b_only'].update(input_body_ids=['2']),
                   lambda o:o['artifacts'].update({'analysis.json':'invalid-hash'})]
        for mutation in mutations:
            obj=copy.deepcopy(self.obj);mutation(obj)
            with self.subTest(mutation=mutation),self.assertRaises((ValueError,KeyError)):self.load(obj)


class MorphologyBoundary(unittest.TestCase):
    def parse(self,text):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'synthetic.swc';p.write_text(text);return parse_swc(p)
    def test_disconnected_roots_are_not_healed(self):
        points,segments=self.parse('1 0 0 0 0 1 -1\n2 0 1 0 0 1 1\n3 0 100 0 0 1 -1\n4 0 101 0 0 1 3\n')
        self.assertEqual(len(points),4);self.assertEqual(len(segments),2)
        self.assertTrue(all(abs(a[0]-b[0])==1 for a,b in segments))
    def test_rejects_broken_or_invented_geometry(self):
        for text in ['<html>denied</html>','1 0 0 0 0 1 99','1 0 nan 0 0 1 -1','1 0 0 0 0 1 2\n2 0 1 0 0 1 1']:
            with self.subTest(text=text),self.assertRaises(ValueError):self.parse(text)
    def test_camera_orientation_needs_source_and_valid_matrix(self):
        self.assertIsNone(validate_orientation({'status':'UNVERIFIED'}))
        with self.assertRaises(ValueError):validate_orientation({'status':'VERIFIED'})
        with self.assertRaises(ValueError):validate_orientation(dict(status='VERIFIED',orientation_source='synthetic',raw_to_right_dorsal_anterior=[[1,0,0],[0,0,0],[0,0,1]]))


class WidthSemantics(unittest.TestCase):
    def test_square_root_scaling(self):
        self.assertAlmostEqual((width(4,100)-.7)/(width(1,100)-.7),2)
        self.assertEqual(width(100,100),5)
        with self.assertRaises(ValueError):width(-1,100)


if __name__=='__main__':unittest.main()
