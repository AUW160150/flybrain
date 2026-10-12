import io
import json
from types import SimpleNamespace
from flycodes import server

class MemoryRequest:
    def __init__(self,request):self.request=io.BytesIO(request);self.output=io.BytesIO()
    def makefile(self,*args):return self.request
    def sendall(self,bytes):self.output.write(bytes)

def request(path,method='GET',host='127.0.0.1:5077',token=None,body=b'{}'):
    headers=f'{method} {path} HTTP/1.0\r\nHost: {host}\r\nContent-Length: {len(body)}\r\n'
    if token:headers+=f'X-Flycodes-Token: {token}\r\n'
    fake=MemoryRequest(headers.encode()+b'\r\n'+body)
    server.Handler(fake,('127.0.0.1',1000),SimpleNamespace(server_port=5077))
    head,data=fake.output.getvalue().split(b'\r\n\r\n',1)
    return int(head.split()[1]),data

def test_blocks_cross_origin_compute_requests():
    assert request('/api/train','POST')[0]==403
    assert request('/api/dashboard',host='attacker.example')[0]==403

def test_static_route_and_missing_resource():
    status,body=request('/')
    assert status==200 and b'connectome coding lab' in body
    assert request('/../../etc/passwd')[0]==404
    assert request('/docs/../../etc/passwd')[0]==404

def test_dashboard_and_unknown_job(monkeypatch):
    monkeypatch.setattr(server,'dashboard',lambda:{'run':None,'evaluations':{}})
    status,body=request('/api/dashboard')
    assert status==200 and json.loads(body)['token']==server.TOKEN
    assert request('/api/jobs/missing')[0]==404

def test_validated_action(monkeypatch):
    called=[]
    monkeypatch.setattr(server,'create_job',lambda a,v:called.append((a,v)) or {'status':'running'})
    status,body=request('/api/generate','POST',token=server.TOKEN,body=b'{"problem":"two-sum"}')
    assert status==202 and called==[('generate',{'problem':'two-sum'})]
    assert request('/api/delete','POST',token=server.TOKEN)[0]==400

def test_dashboard_identifies_current_api_without_changing_measured_data(monkeypatch):
    from flycodes import curriculum_dashboard
    marker=object()
    monkeypatch.setattr(curriculum_dashboard,'latest_v2',lambda:marker)
    monkeypatch.setattr(curriculum_dashboard,'dashboard_v2',lambda run:dict(protocol='curriculum-v2',run='recorded-run',evaluations={'fly':{'solved':0}}))
    result=server.dashboard()
    assert result['ui_api_version']==server.UI_API_VERSION
    assert result['protocol']=='curriculum-v2'
    assert result['evaluations']['fly']['solved']==0
