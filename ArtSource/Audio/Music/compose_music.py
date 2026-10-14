"""Original RecordShop arrangements; no downloaded audio, samples or song references.
Rebuild with Python/NumPy/SciPy and FFmpeg. Stereo 48kHz, PCM16, target -18 LUFS.
"""
from pathlib import Path
import json, math, subprocess, wave
import numpy as np
from scipy.signal import butter,sosfilt
SR=48000;ROOT=Path.cwd();OUT=ROOT/'ArtSource/Audio/Music';EV=ROOT/'Saved/Finalization/ArtAudio';rng=np.random.default_rng(20261014)
def filt(x,f,kind='lowpass'):return sosfilt(butter(2,f,kind,fs=SR,output='sos'),x)
def env(t,d,a=.008,r=.1):return np.minimum(1,t/a)*np.minimum(1,np.maximum(0,(d-t)/r))
def tone(note,d,kind):
 t=np.arange(int(d*SR))/SR;f=440*2**((note-69)/12)
 if kind=='piano':
  x=np.zeros_like(t)
  for k in range(1,10):
   fk=f*k*math.sqrt(1+.000045*k*k);x+=(np.sin(2*np.pi*fk*t)+.3*np.sin(2*np.pi*fk*1.0007*t))/(k**1.75)*np.exp(-t*(.9+k*.43))
  x+=filt(rng.normal(size=len(t)),2100)*.018*np.exp(-t*35)
 elif kind=='ep':
  x=np.sin(2*np.pi*f*t+1.7*np.exp(-t*3)*np.sin(2*np.pi*f*2*t))*np.exp(-t*1.2)+.22*np.sin(2*np.pi*f*3*t)*np.exp(-t*5);x*=1+.055*np.sin(2*np.pi*4.2*t)
 elif kind=='bass':
  x=(np.sin(2*np.pi*f*t)+.31*np.sin(2*np.pi*f*2*t)+.13*np.sin(2*np.pi*f*3*t))*np.exp(-t*2)+filt(rng.normal(size=len(t)),1100)*.035*np.exp(-t*45)
 elif kind=='rock':
  x=np.zeros_like(t)
  for k in range(1,min(25,int(16000/f))):x+=np.sin(2*np.pi*f*k*t+.04*np.sin(2*np.pi*.7*t))/k
  x=filt(np.tanh(x*1.6)*np.exp(-t*.7),3400)
 else:raise ValueError(kind)
 return x*env(t,d)
def drum(kind):
 d={'kick':.36,'snare':.26,'brush':.3,'hat':.095,'ride':.42,'open':.28}[kind];t=np.arange(int(d*SR))/SR;n=rng.normal(size=len(t))
 if kind=='kick':x=np.sin(2*np.pi*(48*t+65*.026*(1-np.exp(-t/.026))))*np.exp(-t*15)+filt(n,1800)*.06*np.exp(-t*100)
 elif kind in ('snare','brush'):
  x=filt(filt(n,900,'highpass')*np.exp(-t*(18 if kind=='snare' else 10)),6500 if kind=='snare' else 3900)+.35*np.sin(2*np.pi*185*t)*np.exp(-t*30)
  if kind=='brush':x*=.5
 else:
  x=filt(n,6300,'highpass')*.5
  for f in [3420,4870,6190,8230]:x+=.045*np.sin(2*np.pi*f*t)
  x*=np.exp(-t*{'hat':65,'ride':12,'open':18}[kind])
 return x*env(t,d,.001,.025)
def write(path,x):
 with wave.open(str(path),'wb') as f:f.setnchannels(2);f.setsampwidth(2);f.setframerate(SR);f.writeframes((np.clip(x,-.9999,.9999)*32767).astype('<i2').tobytes())
reports=[]
for number,bpm,bars in [(1,76,10),(2,96,12),(3,136,16)]:
 beat=60/bpm;duration=bars*4*beat+1.3;mix=np.zeros((int(duration*SR),2))
 def add(x,start,gain,pan=0):
  i=int(start*SR);n=min(len(x),len(mix)-i);angle=(pan+1)*np.pi/4
  if n>0:mix[i:i+n,0]+=x[:n]*gain*np.cos(angle);mix[i:i+n,1]+=x[:n]*gain*np.sin(angle)
 def note(n,start,length,gain,kind,pan=0):add(tone(n,length,kind),start,gain,pan)
 jazz=[(38,[53,57,60,64]),(43,[53,57,59,64]),(36,[52,55,59,62]),(45,[55,60,64,67]),(38,[53,57,60,64]),(43,[53,56,59,63]),(36,[52,55,59,62]),(40,[55,59,62,66]),(38,[53,57,60,64]),(36,[52,55,59,62])]
 soul=[(41,[57,60,64,67]),(40,[55,59,62,66]),(45,[55,60,64,71]),(43,[53,57,60,64]),(41,[57,60,64,67]),(43,[53,57,59,64])]
 rock=[(28,[52,59,64]),(31,[55,62,67]),(26,[50,57,62]),(33,[57,64,69])]
 for bar in range(bars):
  start=.08+bar*4*beat;root,chord=jazz[bar] if number==1 else soul[bar%6] if number==2 else rock[bar%4]
  if number==1:
   for off,length,gain in [(0,2.5,.17),(2.65,1.2,.11)]:
    for k,n in enumerate(chord):note(n,start+off*beat+k*.013,length*beat,gain,'piano',-.24+k*.13)
   for b,n in enumerate([root,root+7,root+12,root+(2 if bar%2 else 7)]):note(n,start+b*beat,.9*beat,.31,'bass',-.12)
   for b in range(4):
    add(drum('ride'),start+b*beat,.075,.38)
    if b in [1,3]:add(drum('brush'),start+b*beat,.16,-.25)
    if b in [0,2]:add(drum('kick'),start+b*beat,.09)
   if bar in [1,3,5,7]:
    for off,n in zip([.65,1.65,2,3.35],[chord[-1]+12,chord[-2]+12,chord[-1]+12,chord[1]+12]):note(n,start+off*beat,.55*beat,.075,'piano',.12)
  elif number==2:
   for off,length,gain in [(0,1.1,.14),(1.5,.8,.105),(2.75,1,.13)]:
    for k,n in enumerate(chord):note(n,start+off*beat+k*.009,length*beat,gain,'ep',-.3+k*.14)
   for off,n in zip([0,.75,1.5,2,2.75,3.5],[root,root,root+7,root+12,root+7,root+10]):note(n,start+off*beat,.55*beat,.28,'bass',-.06)
   for off in [0,1.75,2.5]:add(drum('kick'),start+off*beat,.23)
   for off in [1,3]:add(drum('snare'),start+off*beat,.115,-.12)
   for i in range(8):add(drum('hat'),start+i*.5*beat,.065 if i%2 else .085,.38)
   if bar>1:
    for off,n in zip([.5,1.25,2.5,3.25],[chord[2]+12,chord[3]+12,chord[2]+12,chord[1]+12]):note(n,start+off*beat,.45*beat,.055,'ep',.22)
  else:
   for i in range(8):
    for n in chord[:2]:note(n,start+i*.5*beat,.34*beat,.105,'rock',-.45 if i%2 else .45)
    note(root,start+i*.5*beat,.34*beat,.22,'bass')
   for off in [0,1.5,2,2.75]:add(drum('kick'),start+off*beat,.3)
   for off in [1,3]:add(drum('snare'),start+off*beat,.23,-.1)
   for i in range(8):add(drum('open' if i==7 else 'hat'),start+i*.5*beat,.1,.32)
   if bar>=4:
    for off,n in zip([0,.75,1.5,2.5,3],[chord[0]+12,chord[0]+15,chord[0]+19,chord[0]+15,chord[0]+12]):note(n,start+off*beat,.35*beat,.055,'rock',.12)
 dry=mix.copy();reflection=np.column_stack([filt(dry[:,1],4000),filt(dry[:,0],4000)])
 for delay,gain in [(.029,.13),(.047,.11),(.079,.09),(.113,.07),(.173,.055),(.239,.04),(.317,.03)]:
  n=int(delay*SR);mix[n:]+=reflection[:-n]*gain
 mix=np.column_stack([filt(mix[:,i],28,'highpass') for i in range(2)])
 n=int(.12*SR);mix[:n]*=np.linspace(0,1,n)[:,None];n=int(1.2*SR);mix[-n:]*=(np.cos(np.linspace(0,np.pi/2,n))**2)[:,None];mix*=.76/max(.001,np.max(np.abs(mix)))
 name=['RS001_Best','RS002_Good','RS003_Poor'][number-1];raw=EV/(name+'-mix.wav');dest=OUT/(name+'.wav');write(raw,mix)
 r=subprocess.run(['ffmpeg','-hide_banner','-y','-i',str(raw),'-af','loudnorm=I=-18:TP=-3:LRA=9:print_format=json','-ar','48000','-ac','2','-c:a','pcm_s16le',str(dest)],capture_output=True,text=True,check=True);(EV/(name+'-loudness.txt')).write_text(r.stderr)
 with wave.open(str(dest),'rb') as f:data=np.frombuffer(f.readframes(f.getnframes()),dtype='<i2').astype(float)/32768
 reports.append({'record':'RS00'+str(number),'bpm':bpm,'bars':bars,'duration':duration,'sample_rate':SR,'channels':2,'bits':16,'peak_dbfs':20*np.log10(np.max(np.abs(data))),'rms_dbfs':20*np.log10(np.sqrt(np.mean(data**2))),'file':str(dest),'original':True})
(EV/'music-metadata.json').write_text(json.dumps(reports,indent=2));print(json.dumps(reports,indent=2))
