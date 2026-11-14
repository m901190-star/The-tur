import numpy as np, wave
SR=48000; T=51.2; N=int(T*SR); out=np.zeros((N,2)); rng=np.random.default_rng(9)
C={'p1':5.0,'p2':12.6,'p3':22.4,'p4':32.2,'p5':38.6,'end':44.2}; O=1.0
def add(s,t,g,pan=0):
    i=int(t*SR); n=min(len(s),N-i)
    if n>0: out[i:i+n,0]+=s[:n]*g*(1-pan*.5); out[i:i+n,1]+=s[:n]*g*(1+pan*.5)
def whoosh(d=.6):
    n=int(d*SR); x=rng.standard_normal(n); t=np.linspace(0,1,n); env=np.sin(np.pi*t)**2; y=np.zeros(n); lp=0
    for k in range(n): lp+=(.02+.2*env[k])*(x[k]-lp); y[k]=lp
    return (y-np.convolve(y,np.ones(40)/40,'same'))*env*3
def chime(f,d=1.6):
    n=int(d*SR); t=np.arange(n)/SR; return (np.sin(2*np.pi*f*t)+.3*np.sin(2*np.pi*2*f*t))*np.exp(-t*3)*.25
def tick(f=2600):
    n=int(.08*SR); t=np.arange(n)/SR; return np.sin(2*np.pi*f*t)*np.exp(-t*70)*.25
def thud():
    n=int(.8*SR); t=np.arange(n)/SR; return (np.sin(2*np.pi*70*t*(1+np.exp(-t*25)))*np.exp(-t*7)+rng.standard_normal(n)*np.exp(-t*40)*.3)*.8
add(chime(1318.5),.06,.5); add(whoosh(.45),.78,.4)
add(chime(987.8),O+2.1,.45); add(chime(1318.5),O+2.15,.25)
for k in ['p1','p2','p3','p4','p5']: add(whoosh(),O+C[k]-.35,.5,.3)
def rowticks(at,nxt,n,first):
    step=min(.62,(nxt-at-3.2)/n)
    for i in range(n): add(tick(2200+i*90),O+at+first+i*step,.5)
rowticks(C['p1'],C['p2'],6,.9); rowticks(C['p2'],C['p3'],9,.5); rowticks(C['p3'],C['p4'],9,.9)
add(thud(),O+C['p5']+3.05,.9)
add(whoosh(.5),O+C['end']-.4,.5); add(chime(659.25,2.4),O+C['end']+.2,.7); add(chime(987.8,2.4),O+C['end']+.25,.4); add(chime(1318.5,2.4),O+C['end']+.3,.25)
out=np.tanh(out)*.8
w=wave.open('sfx.wav','wb'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((out*32767).astype('<i2').tobytes()); w.close()
