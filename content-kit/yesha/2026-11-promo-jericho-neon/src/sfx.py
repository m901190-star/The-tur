import numpy as np, json, sys, wave
SR=48000; C=json.load(open(sys.argv[1])); T=C['total']+2.0; N=int(T*SR); out=np.zeros((N,2)); rng=np.random.default_rng(5)
def add(s,t,g,pan=0):
    i=int(t*SR); n=min(len(s),N-i); out[i:i+n,0]+=s[:n]*g*(1-pan*.5); out[i:i+n,1]+=s[:n]*g*(1+pan*.5)
def whoosh(d=.6):
    n=int(d*SR); x=rng.standard_normal(n); t=np.linspace(0,1,n); env=np.sin(np.pi*t)**2; y=np.zeros(n); lp=0
    for k in range(n): lp+=(.02+.2*env[k])*(x[k]-lp); y[k]=lp
    return (y-np.convolve(y,np.ones(40)/40,'same'))*env*3
def swell(d=1.2):
    n=int(d*SR); t=np.arange(n)/SR; e=(t/d)**2.5; return (rng.standard_normal(n)*.12)*e
def chime(f=1318.5):
    n=int(1.5*SR); t=np.arange(n)/SR; return (np.sin(2*np.pi*f*t)+.3*np.sin(2*np.pi*2*f*t))*np.exp(-t*3)*.25
O=1.0
add(chime(987.8),.08,.5); add(whoosh(.45),.8,.35)
for k in [x for x in ['p1','p2','p3','p4','p5','p6'] if x in C]: add(whoosh(),O+C[k]-.35,.45,.3)
add(chime(1318.5),O+C['p1']+1.3,.35)
add(swell(1.0),O+C['end']-1.0,.5); add(chime(659.25),O+C['end'],.6); add(chime(987.8),O+C['end']+.05,.35)
out=np.tanh(out)*.8
w=wave.open(sys.argv[2],'wb'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((out*32767).astype('<i2').tobytes()); w.close()
