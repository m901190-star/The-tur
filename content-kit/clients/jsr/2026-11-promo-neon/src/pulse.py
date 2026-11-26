import numpy as np, wave, sys
SR=48000; T=float(sys.argv[2]); N=int(T*SR); out=np.zeros(N); end=float(sys.argv[3])
t=np.arange(int(.35*SR))/SR; kick=np.sin(2*np.pi*52*t*(1+2*np.exp(-t*30)))*np.exp(-t*9)
tk=np.arange(int(.03*SR))/SR; tick=np.random.default_rng(1).standard_normal(len(tk))*np.exp(-tk*200)*.15
b=1.0
while b<end-.1:
    i=int(b*SR); n=min(len(kick),N-i); out[i:i+n]+=kick[:n]*.55
    for h in (0.25,):
        j=int((b+h)*SR); m=min(len(tick),N-j); out[j:j+m]+=tick[:m]
    b+=0.5
out=np.tanh(out)
s=np.stack([out,out],1); w=wave.open(sys.argv[1],'wb'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((s*.7*32767).astype('<i2').tobytes()); w.close()
