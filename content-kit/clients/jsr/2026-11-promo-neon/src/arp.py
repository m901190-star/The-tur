import numpy as np, wave, sys
SR=48000; T=float(sys.argv[2]); end=float(sys.argv[3]); N=int(T*SR); out=np.zeros((N,2))
E=[329.63,392.0,493.88,659.25]; notes=[0,2,1,3,0,2,1,2]  # E minor arpeggio, 16ths @120bpm
def pluck(f,d=.22):
    n=int(d*SR); t=np.arange(n)/SR
    s=(np.sin(2*np.pi*f*t)+.4*np.sin(2*np.pi*2*f*t)+.15*np.sign(np.sin(2*np.pi*f*t)))*np.exp(-t*16)
    return s*np.minimum(1,t/.003)
k=0; t=3.6  # start when the phone enters
while t<end-.05:
    f=E[notes[k%8]]*(1 if (k//16)%2==0 else 0.8909)  # alternate Em / C-ish colour
    s=pluck(f); i=int(t*SR); n=min(len(s),N-i); pan=.35 if k%2 else -.35
    g=.22*min(1,(t-3.6)/1.5)
    out[i:i+n,0]+=s[:n]*g*(1-pan); out[i:i+n,1]+=s[:n]*g*(1+pan); k+=1; t+=.125
# simple echo
d=int(.375*SR); out[d:]+=out[:-d]*.3
out=np.tanh(out)
w=wave.open(sys.argv[1],'wb'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((out*.8*32767).astype('<i2').tobytes()); w.close()
