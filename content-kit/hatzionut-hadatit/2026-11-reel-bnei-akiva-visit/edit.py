"""Smotrich visit to Bnei Akiva Shabbat — summary reel.
Hook: v01 (his line + 'יברך כבודו'), then beat-cut montage on a Splice house loop (124 bpm), RZ logo end card."""
import os, subprocess, json
HERE = os.path.dirname(os.path.abspath(__file__))
KIT = os.path.abspath(os.path.join(HERE, '..', '..'))
LOGO = os.path.join(KIT, 'clients', 'hatzionut-hadatit', 'logo.png')
W, H, FPS = 1080, 1920, 30
BEAT = 60 / 124
SEG = 4 * BEAT            # one bar
HOOK = ('src/v01.mov', 0.0, 6.9)
MONTAGE = [  # (source, start, bars)
    ('src/v02.mov', 0.0, 1),
    ('src/v12.mov', 1.8, 1),
    ('src/v06.mov', 16.6, 1),
    ('src/v02.mov', 4.6, 1),
    ('src/p07.jpg', 0, 1),
    ('src/v04.mov', 10.0, 1),
    ('src/v05.mov', 49.5, 1),
    ('src/v12.mov', 8.8, 1),
    ('src/v06.mov', 40.2, 1),
    ('src/p04.jpg', 0, 1),
    ('src/v05.mov', 68.5, 1),
    ('src/v07.mov', 9.0, 1),
    ('src/p03.jpg', 0, 1),
    ('src/v02.mov', 11.0, 1),
    ('src/v05.mov', 83.0, 2),
]
END = 2.2
TMP = os.path.join(HERE, '_tmp'); os.makedirs(TMP, exist_ok=True)
GRADE = 'eq=contrast=1.06:saturation=1.12:brightness=0.01'

def run(cmd):
    subprocess.run(cmd, check=True)

def fit(zoom_from=1.0, zoom_to=1.06, dur=2.0):
    # cover-crop to 9:16 then slow push-in
    return (f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},"
            f"scale=iw*({zoom_from}+({zoom_to}-{zoom_from})*t/{dur}):-2:eval=frame,crop={W}:{H},"
            f"setsar=1,fps={FPS},{GRADE},format=yuv420p")

parts = []
# hook keeps its own audio
out = f'{TMP}/00.mp4'
run(['ffmpeg', '-v', 'error', '-y', '-ss', str(HOOK[1]), '-t', str(HOOK[2]), '-i', HOOK[0],
     '-vf', fit(1.0, 1.04, HOOK[2]), '-af', 'aresample=48000,highpass=f=80,afade=t=out:st=%.2f:d=0.25' % (HOOK[2] - 0.25),
     '-c:v', 'libx264', '-crf', '17', '-preset', 'medium', '-c:a', 'aac', '-ar', '48000', '-ac', '2', out])
parts.append(out)
for i, (src, st, bars) in enumerate(MONTAGE, 1):
    d = SEG * bars
    out = f'{TMP}/{i:02d}.mp4'
    if src.endswith('.jpg'):
        run(['ffmpeg', '-v', 'error', '-y', '-loop', '1', '-t', f'{d:.4f}', '-i', src,
             '-f', 'lavfi', '-t', f'{d:.4f}', '-i', 'anullsrc=r=48000:cl=stereo',
             '-vf', fit(1.0, 1.08, d), '-map', '0:v', '-map', '1:a',
             '-c:v', 'libx264', '-crf', '17', '-c:a', 'aac', '-shortest', out])
    else:
        run(['ffmpeg', '-v', 'error', '-y', '-ss', str(st), '-t', f'{d:.4f}', '-i', src,
             '-vf', fit(1.0, 1.06, d), '-af', 'aresample=48000,volume=0.18',
             '-c:v', 'libx264', '-crf', '17', '-c:a', 'aac', '-ar', '48000', '-ac', '2', out])
    parts.append(out)
# end card: RZ logo on deep teal
out = f'{TMP}/99.mp4'
run(['ffmpeg', '-v', 'error', '-y', '-f', 'lavfi', '-t', str(END), '-i', f'color=c=0x1c3436:s={W}x{H}:r={FPS}',
     '-loop', '1', '-t', str(END), '-i', LOGO, '-f', 'lavfi', '-t', str(END), '-i', 'anullsrc=r=48000:cl=stereo',
     '-filter_complex', f"[1]scale=640:-1,format=rgba,fade=t=in:st=0.15:d=0.5:alpha=1[l];[0][l]overlay=(W-w)/2:(H-h)/2-40,fade=t=in:st=0:d=0.2,fade=t=out:st={END-0.5}:d=0.5,format=yuv420p[v]",
     '-map', '[v]', '-map', '2:a', '-c:v', 'libx264', '-crf', '17', '-c:a', 'aac', '-shortest', out])
parts.append(out)

with open(f'{TMP}/list.txt', 'w') as f:
    for p in parts:
        f.write(f"file '{p}'\n")
run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', f'{TMP}/list.txt', '-c', 'copy', f'{TMP}/video.mp4'])

total = float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', f'{TMP}/video.mp4']))
hook_end = HOOK[2]
# music: downbeat lands on the first montage cut; starts 2 bars earlier, low under the hook
m_start = hook_end - 2 * SEG
music = os.path.join(HERE, 'music', 'house_124_Fm.wav')
fc = (f"[1:a]aloop=loop=-1:size=2e9,atrim=0:{total - m_start + 0.1},asetpts=N/SR/TB,"
      f"volume='if(lt(t,{2*SEG:.3f}),0.18+0.82*t/{2*SEG:.3f},1)':eval=frame,"
      f"afade=t=out:st={total - m_start - 1.6:.3f}:d=1.6,adelay={int(m_start*1000)}|{int(m_start*1000)},aresample=48000[m];"
      f"[0:a]aresample=48000[v];[v][m]amix=inputs=2:normalize=0:duration=first,loudnorm=I=-14:TP=-1.5:LRA=9[a]")
final = os.path.join(HERE, 'smotrich-bnei-akiva-summary.mp4')
run(['ffmpeg', '-v', 'error', '-y', '-i', f'{TMP}/video.mp4', '-stream_loop', '-1', '-i', music,
     '-filter_complex', fc, '-map', '0:v', '-map', '[a]', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-ar', '48000',
     '-movflags', '+faststart', '-t', f'{total:.3f}', final])
print('done', round(total, 2), 's ->', final)
