"""Check source coverage, local links, and selected math independently of the renderer."""
from pathlib import Path
from fractions import Fraction as F
from html.parser import HTMLParser
from urllib.parse import unquote
from math import gcd
import ast,json,re
ROOT=Path(__file__).resolve().parents[1]
checks=[]
def check(name,ok):
    checks.append({'name':name,'passed':bool(ok)})
    if not ok:raise AssertionError(name)
class H(HTMLParser):
    def __init__(self):super().__init__();self.ids=[];self.links=[]
    def handle_starttag(self,t,attrs):
        a=dict(attrs)
        if 'id' in a:self.ids.append(a['id'])
        for k in ['href','src']:
            if k in a:self.links.append(a[k])
def stationary(p,v):
    return sum(v)==1 and all(x>=0 for x in v) and all(sum(v[i]*p[i][j] for i in range(len(v)))==v[j] for j in range(len(v)))
def squared(p):return [[sum(p[i][k]*p[k][j] for k in range(len(p))) for j in range(len(p))] for i in range(len(p))]

pages={}
for p in list(ROOT.glob('chapter*/index.html'))+list((ROOT/'lecture').rglob('*.html'))+[ROOT/'index.html']:
    q=H();q.feed(p.read_text(encoding='utf-8'));pages[p.resolve()]=q
for p,q in pages.items():
    check(f'Unique ids: {p.relative_to(ROOT)}',len(q.ids)==len(set(q.ids)))
    for link in q.links:
        if link.startswith(('https:','http:','data:')):continue
        rel,_,frag=link.partition('#');target=(p.parent/unquote(rel)).resolve() if rel else p
        if not target.exists():raise AssertionError((p,link))
        if frag and target in pages and unquote(frag) not in pages[target].ids:raise AssertionError((p,link))
check('All HTML local files and anchors exist',True)
for n,total in enumerate([122,78,26,121],1):
    meta=json.loads((ROOT/f'lecture/lecture{n}/coverage.json').read_text(encoding='utf-8'));covered=set()
    for item in meta['coverage']:
        for part in item['slides'].split('、'):
            v=part.split('—');covered.update(range(int(v[0]),int(v[-1])+1))
    check(f'PPT{n}: all {total} slide numbers mapped',covered==set(range(1,total+1)))

# All eight finite classification matrices are independently classified from graph edges.
tree=ast.parse((ROOT/'tools/lecture4_content.py').read_text(encoding='utf-8'))
node=next(x for x in ast.walk(tree) if isinstance(x,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='classification' for t in x.targets))
data=eval(compile(ast.Expression(node.value),'<authored classification data>','eval'),{'__builtins__':{},'list':list,'range':range})
expected=[{(0,1,2):1},{(1,2):1,(4,):1},{(1,3,5):1},{(0,):1,(1,2):2,(3,4,5):1},{(0,1,2,3):3},{(0,1):1,(2,3):1},{(0,1,2,3):2},{(1,2,3,4,5,6,7,8):4}]
for item,want in zip(data,expected):
    k,_,_,states,rows,_,_=item;N=len(states);edges=[{states.index(j) for j,p in row} for row in rows]
    reach=[[int(i==j or j in edges[i]) for j in range(N)] for i in range(N)]
    for m in range(N):
        for i in range(N):
            for j in range(N):reach[i][j]|=reach[i][m] and reach[m][j]
    unseen=set(range(N));closed={}
    while unseen:
        i=min(unseen);cl={j for j in range(N) if reach[i][j] and reach[j][i]};unseen-=cl
        if not all(edges[j]<=cl for j in cl):continue
        dist={i:0};queue=[i]
        for u in queue:
            for v in edges[u]:
                if v not in dist:dist[v]=dist[u]+1;queue.append(v)
        period=0
        for u in cl:
            for v in edges[u]:period=gcd(period,abs(dist[u]+1-dist[v]))
        closed[tuple(sorted(states[j] for j in cl))]=period
    check(f'5.3.{k}: closed classes and periods',closed==want)
    for row in rows:
        if not any(p=='*' for j,p in row):check(f'5.3.{k}: numerical row sum {rows.index(row)}',sum(F(p) for j,p in row)==1)

p=[[F(3,4),F(1,4),0],[F(1,4),F(1,2),F(1,4)],[0,F(3,4),F(1,4)]];p2=squared(p)
check('5.2.7 joint 5/48 and absolute 11/24',F(1,3)*p2[0][1]==F(5,48) and sum(p2[i][1] for i in range(3))/3==F(11,24))
for p in [F(1,3),F(1,2),F(2,3)]:
    q=1-p;r=q/p;c=5;u=[(r**j-r**c)/(1-r**c) if r!=1 else 1-F(j,c) for j in range(c+1)]
    check(f'5.2.4 ruin recurrence p={p}',u[0]==1 and u[-1]==0 and all(u[j]==p*u[j+1]+q*u[j-1] for j in range(1,c)))
p=F(9,10);q=1-p
check('5.2.8 return after flips',p*p+q*q==F(82,100) and 3*q*p*p+q**3==F(244,1000))
p=[[F(1,2),F(2,5),F(1,10)],[F(3,10),F(2,5),F(3,10)],[F(1,5),F(3,10),F(1,2)]]
check('5.4.2 invariant vector',stationary(p,[F(21,62),F(23,62),F(18,62)]))
p=[[F(1,3),F(2,3),0,0,0],[F(1,3),0,F(2,3),0,0],[0,F(1,3),0,F(2,3),0],[0,0,F(1,3),0,F(2,3)],[0,0,0,F(1,3),F(2,3)]]
check('5.4.3 invariant vector',stationary(p,[F(v,31) for v in [1,2,4,8,16]]))
check('5.4.4 first closed class',stationary([[F(1,2),F(1,2),0],[0,F(2,3),F(1,3)],[F(1,3),0,F(2,3)]],[F(2,8),F(3,8),F(3,8)]))
check('5.4 exchange supplement',stationary([[0,1,0,0],[F(1,9),F(4,9),F(4,9),0],[0,F(4,9),F(4,9),F(1,9)],[0,0,1,0]],[F(v,20) for v in [1,9,9,1]]))
check('5.4 sales supplement',stationary([[F(1,2),F(1,2),0],[F(1,3),F(1,9),F(5,9)],[F(1,6),F(2,3),F(1,6)]],[F(v,23) for v in [8,9,6]]))
values=[1,1,1,1,1,1,-1,-1,0,0,0,0,1,1,0,0,0,-1,-1,-1,-1,-1,-1,-1,1,1,0,-1,-1,-1,-1,0,0,-1,-1,-1,0,0,-1,-1];states=[-1,0,1];counts=[[0]*3 for _ in states]
for i,j in zip(values,values[1:]):counts[states.index(i)][states.index(j)]+=1
check('Stock supplement 40 values and 39 adjacent pairs',len(values)==40 and counts==[[13,3,1],[4,7,1],[1,2,7]])
p=[[F(v,sum(row)) for v in row] for row in counts]
check('Stock supplement two-step row',squared(p)[0]==[F(1877,2890),F(1443,5780),F(583,5780)])
probs=[F(1,6),F(1,3),F(1,3),F(1,6)];mean=sum(i*p for i,p in zip(range(1,5),probs));second=sum(i*i*p for i,p in zip(range(1,5),probs))
check('Poisson immigration example moments',mean==F(5,2) and second==F(43,6) and 10*second==F(215,3))
for n in [1,2,5]:
    mean=F(n,2);variance=sum((F(i)-mean)**2 for i in range(n+1))/(n+1)
    check(f'Discrete uniform table n={n}',variance==F(n*(n+2),12))
check('Two-time Gaussian determinant',all((1+s*s)*(1+t*t)-(1+s*t)**2==(s-t)**2 for s,t in [(0,1),(1,3),(2,2)]))
dest=ROOT/'lecture/内容核对.json';dest.write_text(json.dumps(checks,ensure_ascii=False,indent=2),encoding='utf-8')
print(f'{len(checks)} source, structure and independent math checks passed.')
