import numpy as np, json, sys, subprocess
SR=48000; C=json.load(open(sys.argv[1])); T=C['total']+1.0+0.5; N=int(T*SR); out=np.zeros((N,2))
rng=np.random.default_rng(3)
def add(sig,t,g=1.0,pan=0):
    i=int(t*SR); n=min(len(sig),N-i)
    if n<=0: return
    out[i:i+n,0]+=sig[:n]*g*(1-pan*.5); out[i:i+n,1]+=sig[:n]*g*(1+pan*.5)
def whoosh(d=.55):
    n=int(d*SR); x=rng.standard_normal(n); t=np.linspace(0,1,n); env=np.sin(np.pi*t)**2
    # sweeping bandpass via cumulative one-pole with changing coeff
    y=np.zeros(n); a=0; lp=0
    for k in range(n):
        c=.02+.25*env[k]; lp+=c*(x[k]-lp); y[k]=lp
    hp=y-np.convolve(y,np.ones(40)/40,'same'); return hp*env*3.2
def hit(d=1.6,f=48):
    n=int(d*SR); t=np.arange(n)/SR; s=np.sin(2*np.pi*f*t*(1+1.5*np.exp(-t*18)))*np.exp(-t*3.2)
    s+=rng.standard_normal(n)*np.exp(-t*30)*.35; return s*.9
def pop(f=900):
    n=int(.12*SR); t=np.arange(n)/SR; return np.sin(2*np.pi*f*t*(1-t*3))*np.exp(-t*40)*.5
def tick():
    n=int(.06*SR); t=np.arange(n)/SR; return (np.sin(2*np.pi*2400*t)+.5*np.sin(2*np.pi*3600*t))*np.exp(-t*90)*.22
def riser(d=1.0):
    n=int(d*SR); t=np.arange(n)/SR; env=(t/d)**2; return (rng.standard_normal(n)*.25+np.sin(2*np.pi*(200+600*(t/d)**2)*t)*.2)*env
O=1.0
add(pop(700),.06,.8); add(whoosh(.4),.78,.7)
for k in ['p1','p2','p3','p4','p5']: add(whoosh(),O+C[k]-.3,.8, pan=.3)
p1=O+C['p1']
for i,dt in enumerate([.55,1.05,1.5,1.95]): add(pop(1200),p1+dt+.1,.6); add(tick(),p1+dt+.12,.8)
add(tick(),O+C['p2']+.7,1.0); add(pop(500),O+C['p2']+.7,.5)
add(hit(1.0,60),O+C['p3']+.95,.45)
add(riser(.9),O+C['end']-.9,.6); add(hit(2.2,42),O+C['end'],1.0); add(whoosh(.5),O+C['end']-.4,.6)
out=np.tanh(out*.9)*.8
import wave
w=wave.open(sys.argv[2],'wb'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((out*32767).astype('<i2').tobytes()); w.close()
