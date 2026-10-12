"""Bounded AST interpreter for a declared subset of Python. Never exec/eval generated code.

This is not a full CPython judge or an official LeetCode submission. Unsupported syntax
has its own outcome. A separate process supplies a wall-clock limit as defense in depth.
"""
import ast
import copy
import json
import operator
import subprocess
import sys

class Unsupported(Exception): pass
class BudgetExceeded(Exception): pass
class ReturnValue(Exception):
    def __init__(self, value): self.value = value
class BreakLoop(Exception): pass
class ContinueLoop(Exception): pass

BIN = {ast.Add:operator.add, ast.Sub:operator.sub, ast.Mult:operator.mul,
       ast.Div:operator.truediv, ast.FloorDiv:operator.floordiv, ast.Mod:operator.mod}
CMP = {ast.Eq:operator.eq, ast.NotEq:operator.ne, ast.Lt:operator.lt,
       ast.LtE:operator.le, ast.Gt:operator.gt, ast.GtE:operator.ge,
       ast.In:lambda a,b:a in b, ast.NotIn:lambda a,b:a not in b,
       ast.Is:operator.is_, ast.IsNot:operator.is_not}
FUNCTIONS = dict(len=len,sum=sum,min=min,max=max,abs=abs,sorted=sorted,range=range,
                 enumerate=enumerate,list=list,tuple=tuple,set=set,dict=dict,all=all,
                 any=any,reversed=reversed,zip=zip,int=int,str=str,bool=bool)
METHODS = {list: {'append','pop','reverse','sort','count','index','insert','extend'},
           dict: {'get','keys','values','items','pop'}, set: {'add','discard'},
           str: {'lower','upper','count','isdigit','isalnum','isalpha','strip','split','join'}}

def clean_code(code):
    code = code.strip()
    if code.startswith('```'):
        parts = code.split('\n',1)
        code = parts[1] if len(parts)>1 else ''
        code = code.rsplit('```',1)[0]
    return code.strip() + '\n'

class Interpreter:
    def __init__(self, code):
        if len(code)>16000: raise BudgetExceeded('Source limit')
        tree = ast.parse(clean_code(code))
        if len(tree.body)!=1 or not isinstance(tree.body[0],ast.FunctionDef):
            raise Unsupported('Exactly one function, solve, is supported')
        self.fn = tree.body[0]
        f = self.fn
        if f.name!='solve' or f.decorator_list or f.returns or f.args.defaults or f.args.kwonlyargs or f.args.vararg or f.args.kwarg or f.args.posonlyargs:
            raise Unsupported('Use a plain solve function without annotations or defaults')
        if any(a.annotation for a in f.args.args): raise Unsupported('Annotations unsupported')
        allowed = (ast.Module,ast.FunctionDef,ast.arguments,ast.arg,ast.Return,ast.Assign,ast.AugAssign,
                   ast.Expr,ast.If,ast.For,ast.While,ast.Break,ast.Continue,ast.Pass,
                   ast.Name,ast.Constant,ast.List,ast.Tuple,ast.Set,ast.Dict,ast.Subscript,
                   ast.Slice,ast.BinOp,ast.UnaryOp,ast.BoolOp,ast.Compare,ast.IfExp,ast.Call,
                   ast.Attribute,ast.ListComp,ast.SetComp,ast.DictComp,ast.GeneratorExp,ast.comprehension,
                   ast.Load,ast.Store,ast.keyword,ast.operator,ast.unaryop,ast.boolop,ast.cmpop)
        for node in ast.walk(tree):
            if not isinstance(node,allowed): raise Unsupported(type(node).__name__)
            if isinstance(node,ast.Name) and node.id.startswith('_'): raise Unsupported('Private names unsupported')
            if isinstance(node,ast.Attribute) and node.attr.startswith('_'): raise Unsupported('Private attributes unsupported')
        self.budget=30000

    def tick(self):
        self.budget-=1
        if self.budget<0: raise BudgetExceeded('Instruction limit')

    def bound(self,v):
        if isinstance(v,(str,list,tuple,set,dict,range)) and len(v)>10000:
            raise BudgetExceeded('Collection limit')
        if isinstance(v,int) and v.bit_length()>4096: raise BudgetExceeded('Integer limit')
        return v

    def binary(self,op,a,b):
        if type(op) not in BIN: raise Unsupported(type(op).__name__)
        if isinstance(op,ast.Mult):
            if isinstance(a,(list,tuple,str)) and isinstance(b,int) and len(a)*max(0,b)>10000: raise BudgetExceeded('Repeat limit')
            if isinstance(b,(list,tuple,str)) and isinstance(a,int) and len(b)*max(0,a)>10000: raise BudgetExceeded('Repeat limit')
        if isinstance(op,ast.Mod) and isinstance(a,str): raise Unsupported('String formatting')
        return self.bound(BIN[type(op)](a,b))

    def expression(self,n,e):
        self.tick()
        if isinstance(n,ast.Constant): return self.bound(n.value)
        if isinstance(n,ast.Name): return e[n.id]
        if isinstance(n,(ast.List,ast.Tuple,ast.Set)):
            return {ast.List:list,ast.Tuple:tuple,ast.Set:set}[type(n)](self.expression(x,e) for x in n.elts)
        if isinstance(n,ast.Dict): return {self.expression(k,e):self.expression(v,e) for k,v in zip(n.keys,n.values)}
        if isinstance(n,ast.Subscript): return self.expression(n.value,e)[self.expression(n.slice,e)]
        if isinstance(n,ast.Slice): return slice(*(self.expression(x,e) if x else None for x in (n.lower,n.upper,n.step)))
        if isinstance(n,ast.BinOp): return self.binary(n.op,self.expression(n.left,e),self.expression(n.right,e))
        if isinstance(n,ast.UnaryOp):
            ops={ast.Not:operator.not_,ast.USub:operator.neg,ast.UAdd:operator.pos}
            if type(n.op) not in ops: raise Unsupported(type(n.op).__name__)
            return ops[type(n.op)](self.expression(n.operand,e))
        if isinstance(n,ast.BoolOp):
            for v in n.values:
                x=self.expression(v,e)
                if isinstance(n.op,ast.And) and not x: return x
                if isinstance(n.op,ast.Or) and x: return x
            return x
        if isinstance(n,ast.Compare):
            a=self.expression(n.left,e)
            for op,r in zip(n.ops,n.comparators):
                b=self.expression(r,e)
                if type(op) not in CMP: raise Unsupported(type(op).__name__)
                if not CMP[type(op)](a,b): return False
                a=b
            return True
        if isinstance(n,ast.IfExp): return self.expression(n.body if self.expression(n.test,e) else n.orelse,e)
        if isinstance(n,(ast.ListComp,ast.SetComp,ast.GeneratorExp,ast.DictComp)):
            values=[]
            def loop(level,env):
                if level==len(n.generators):
                    values.append((self.expression(n.key,env),self.expression(n.value,env)) if isinstance(n,ast.DictComp) else self.expression(n.elt,env))
                    self.bound(values); return
                g=n.generators[level]
                if g.is_async: raise Unsupported('async')
                for value in self.expression(g.iter,env):
                    self.tick(); inner=env.copy();self.assign(g.target,value,inner)
                    if all(self.expression(c,inner) for c in g.ifs): loop(level+1,inner)
            loop(0,e.copy())
            return dict(values) if isinstance(n,ast.DictComp) else set(values) if isinstance(n,ast.SetComp) else values
        if isinstance(n,ast.Call):
            args=[self.expression(a,e) for a in n.args]
            if any(k.arg is None for k in n.keywords): raise Unsupported('Keyword expansion')
            kw={k.arg:self.expression(k.value,e) for k in n.keywords}
            if isinstance(n.func,ast.Name) and n.func.id in FUNCTIONS:
                f=FUNCTIONS[n.func.id]; value=f(*args,**kw)
                if n.func.id in ('enumerate','reversed','zip'): value=list(value)
                return self.bound(value)
            if isinstance(n.func,ast.Attribute):
                obj=self.expression(n.func.value,e); name=n.func.attr
                if name not in METHODS.get(type(obj),set()): raise Unsupported('Method '+name)
                value=getattr(obj,name)(*args,**kw); self.bound(obj)
                if name in ('keys','values','items'): value=list(value)
                return self.bound(value)
            raise Unsupported('Function call')
        raise Unsupported(type(n).__name__)

    def assign(self,n,v,e):
        if isinstance(n,ast.Name): e[n.id]=v
        elif isinstance(n,(ast.Tuple,ast.List)):
            if len(n.elts)!=len(v): raise ValueError('Unpack length')
            for a,b in zip(n.elts,v): self.assign(a,b,e)
        elif isinstance(n,ast.Subscript):
            obj=self.expression(n.value,e);obj[self.expression(n.slice,e)]=v;self.bound(obj)
        else: raise Unsupported('Assignment target')

    def statements(self,nodes,e):
        for n in nodes:
            self.tick()
            if isinstance(n,ast.Return): raise ReturnValue(self.expression(n.value,e) if n.value else None)
            elif isinstance(n,ast.Assign):
                value=self.expression(n.value,e)
                for target in n.targets: self.assign(target,value,e)
            elif isinstance(n,ast.AugAssign): self.assign(n.target,self.binary(n.op,self.expression(n.target,e),self.expression(n.value,e)),e)
            elif isinstance(n,ast.Expr): self.expression(n.value,e)
            elif isinstance(n,ast.If): self.statements(n.body if self.expression(n.test,e) else n.orelse,e)
            elif isinstance(n,(ast.For,ast.While)):
                broke=False
                iterator=iter(self.expression(n.iter,e)) if isinstance(n,ast.For) else None
                while True:
                    self.tick()
                    if iterator is not None:
                        try: value=next(iterator)
                        except StopIteration: break
                        self.assign(n.target,value,e)
                    elif not self.expression(n.test,e): break
                    try: self.statements(n.body,e)
                    except BreakLoop: broke=True;break
                    except ContinueLoop: continue
                if not broke:self.statements(n.orelse,e)
            elif isinstance(n,ast.Break): raise BreakLoop()
            elif isinstance(n,ast.Continue): raise ContinueLoop()
            elif isinstance(n,ast.Pass): pass
            else: raise Unsupported(type(n).__name__)

    def run(self,args):
        if len(args)!=len(self.fn.args.args): raise TypeError('Argument count')
        self.budget=30000
        e={a.arg:copy.deepcopy(v) for a,v in zip(self.fn.args.args,args)}
        try:self.statements(self.fn.body,e)
        except ReturnValue as r:return r.value
        return None

def evaluate_local(code,cases):
    try: machine=Interpreter(code)
    except SyntaxError as exc:return dict(status='syntax_error',passed=False,passed_cases=0,total_cases=len(cases),detail=str(exc))
    except (Unsupported,BudgetExceeded) as exc:return dict(status='unsupported',passed=False,passed_cases=0,total_cases=len(cases),detail=str(exc))
    outputs=[]
    for case in cases:
        try:
            actual=machine.run(case['args'])
            # bool and int are distinct result types for this contract.
            okay=type(actual) is type(case['expected']) and actual==case['expected']
            outputs.append(dict(passed=okay,actual=actual,expected=case['expected']))
        except Exception as exc:
            status='unsupported' if isinstance(exc,Unsupported) else 'budget_exceeded' if isinstance(exc,BudgetExceeded) else 'runtime_error'
            return dict(status=status,passed=False,passed_cases=sum(x['passed'] for x in outputs),total_cases=len(cases),detail=str(exc),cases=outputs)
    passed=all(x['passed'] for x in outputs)
    return dict(status='passed' if passed else 'wrong_answer',passed=passed,passed_cases=sum(x['passed'] for x in outputs),total_cases=len(cases),cases=outputs)

def judge(code,cases):
    try:
        process=subprocess.run([sys.executable,'-I',__file__],input=json.dumps(dict(code=code,cases=cases)),
                               text=True,capture_output=True,timeout=4,env={})
        if process.returncode: return dict(status='judge_error',passed=None,detail=process.stderr[:500])
        return json.loads(process.stdout)
    except subprocess.TimeoutExpired:return dict(status='timeout',passed=False,passed_cases=0,total_cases=len(cases))

if __name__=='__main__':
    import resource
    resource.setrlimit(resource.RLIMIT_CPU,(2,2))
    # macOS disallows this virtual address limit; instruction/collection/CPU/wall
    # limits still apply. Do not silently call that a memory sandbox.
    if sys.platform.startswith('linux'):
        resource.setrlimit(resource.RLIMIT_AS,(512*1024**2,512*1024**2))
    request=json.load(sys.stdin)
    print(json.dumps(evaluate_local(request['code'],request['cases'])))
