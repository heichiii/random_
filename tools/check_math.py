"""Independent checks of selected new numerical and symbolic conclusions (stdlib only)."""
from fractions import Fraction as F
from math import sin,cos,pi,exp,comb
from pathlib import Path
import json
checks=[]
def check(name,ok):
    checks.append({'check':name,'passed':bool(ok)})
    assert ok,name
def stationary(p,v):
    return all(sum(v[i]*p[i][j] for i in range(len(v)))==v[j] for j in range(len(v)))
P=[[F(1,2),F(1,4),F(1,4)],[F(2,3),0,F(1,3)],[F(3,5),F(2,5),0]]
route=[2,1,2,0,2,0,2,1];v=F(1)
for i,j in zip(route,route[1:]):v*=P[i][j]
check('5.1 path and two-step endpoint',v==F(3,2500) and sum(P[1][k]*P[k][2] for k in range(3))==F(1,6))
P8=[[0,F(1,2),F(1,2),0],[F(1,3),0,0,F(2,3)],[F(1,2),0,0,F(1,2)],[0,F(3,4),F(1,4),0]]
check('5.8 closed-class invariant vector',stationary(P8,[F(x,46) for x in [9,15,8,14]]))
P12=[[F(1,2),F(1,2),0],[F(1,3),F(1,9),F(5,9)],[F(1,6),F(2,3),F(1,6)]]
check('5.12 sales invariant vector',stationary(P12,[F(x,23) for x in [8,9,6]]))
for p in [F(1,10),F(1,2),F(4,5)]:
 q=1-p; z=q*q+p*q+p*p
 check(f'5.9 invariant vector p={p}',stationary([[q,p,0],[q,0,p],[0,q,p]],[q*q/z,p*q/z,p*p/z]))
for a in range(1,8):
 mat=[[F(0) for _ in range(a+1)] for _ in range(a+1)]
 for i in range(a+1):
  mat[i][i]=F(2*i*(a-i),a*a)
  if i<a:mat[i][i+1]=F((a-i)**2,a*a)
  if i:mat[i][i-1]=F(i*i,a*a)
 probs=[F(comb(a,i)**2,comb(2*a,a)) for i in range(a+1)]
 check(f'5.13 exchange invariant, a={a}',sum(probs)==1 and stationary(mat,probs))
N=360000
count1=sum(sin(2*pi*(j+.5)/N)<=.5 and sin(4*pi*(j+.5)/N)<=.5 for j in range(N))
count2=sum(sin(4*pi*(j+.5)/N)<=.5 and sin(6*pi*(j+.5)/N)<=.5 for j in range(N))
check('4.2 joint event counterexample',abs(count1/N-11/24)<1e-5 and abs(count2/N-4/9)<1e-5)
def simpson(f,a,b,n=12000):
 h=(b-a)/n
 return h*(f(a)+f(b)+sum((4 if i%2 else 2)*f(a+i*h) for i in range(1,n)))/3
for alpha,beta in [(1.,2.),(2.,1.),(1.,1.)]:
 for tau in [-2.,0.,1.]:
  calc=exp(-alpha*tau)/(alpha+beta) if tau>=0 else exp(alpha*tau)*(-tau+1/(2*alpha)) if alpha==beta else (exp(beta*tau)-exp(alpha*tau))/(alpha-beta)+exp(beta*tau)/(alpha+beta)
  f=lambda u:exp(-beta*u-alpha*abs(tau+u))
  numeric=simpson(f,0,40) if tau>=0 else simpson(f,0,-tau)+simpson(f,-tau,40)
  check(f'4.11 correlation direction alpha={alpha} beta={beta} tau={tau}',abs(calc-numeric)<1e-8)
for w in [0.,.1,1.,3.]:
 numeric=2*simpson(lambda t:(1-t)*cos(w*t),0,1)
 check(f'4.8 spectrum omega={w}',abs(numeric-(1 if w==0 else 2*(1-cos(w))/w**2))<1e-9)
for n,m in [(1,2),(3,8),(8,3)]:
 coeff=[(F(1,n) if i<n else 0)-(F(1,m) if i<m else 0) for i in range(max(n,m))]
 check(f'3.3 shared-average error n={n} m={m}',sum(c*c for c in coeff)==F(1,n)+F(1,m)-F(2,max(n,m)))
Path('tmp/math-check.json').write_text(json.dumps(checks,ensure_ascii=False,indent=2),encoding='utf-8')
print(f'{len(checks)} independent mathematical checks passed.')
