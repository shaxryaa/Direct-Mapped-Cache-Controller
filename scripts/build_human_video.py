#!/usr/bin/env python3
"""Build a local human-narrated review video without replacing the submission.
Run with build/analysis-env/bin/python. Transcripts with word timestamps must
exist in build/human_video (generated locally with faster-whisper).
"""
from pathlib import Path
import json, subprocess, textwrap, csv
from PIL import Image, ImageDraw, ImageFont
R=Path(__file__).resolve().parents[1]
B=R/'build/human_video'; O=R/'output/video/human_review'; O.mkdir(parents=True,exist_ok=True)
FONT='/System/Library/Fonts/Supplemental/Arial.ttf'
BOLD='/System/Library/Fonts/Supplemental/Arial Bold.ttf'
MONO='/System/Library/Fonts/Menlo.ttc'
INK='#152f49'; TEAL='#087f8c'
def run(args): subprocess.run(args,check=True)
def txt(d,xy,s,size=28,bold=False,color=INK):
    d.multiline_text(xy,s,font=ImageFont.truetype(BOLD if bold else FONT,size),fill=color,spacing=12)
def frame(title,speaker):
    im=Image.new('RGB',(1280,720),'#f8fafc');d=ImageDraw.Draw(im)
    txt(d,(55,28),title,36,True);d.line((55,85,1225,85),fill='#c6d5df',width=2)
    txt(d,(55,665),speaker,21,True,TEAL)
    txt(d,(690,668),'Direct-Mapped Cache Controller | MCA Project',19)
    return im,d
def pic(im,p,box=(60,102,1160,530)):
    a=Image.open(p).convert('RGB');a.thumbnail((box[2],box[3]));im.paste(a,(box[0]+(box[2]-a.width)//2,box[1]+(box[3]-a.height)//2))
def make(kind,speaker):
    titles={'title':'Direct-Mapped Cache Controller','architecture':'System architecture','rtl':'Modular Verilog implementation','fsm':'Seven-state controller','code':'Refill, response and reset','logs':'Actual simulation evidence','trace':'Directed access trace','waveform':'Refill and response handshakes','baseline':'Measured latency against the baseline','report':'IEEE-style project report','files':'Project repository','closing':'Results and future improvements'}
    im,d=frame(titles.get(kind,kind),speaker)
    if kind.startswith('slide'):
        a=Image.open(R/f'build/slides/slide-{kind[5:]}.png').convert('RGB');a=a.resize((1152,648));a.thumbnail((1152,550));im.paste(a,((1280-a.width)//2,96))
        d.rectangle((0,0,1280,90),fill='#f8fafc')
        slide_titles={1:'Project idea and group members',2:'Cache organization',3:'Tag, index and offset',4:'Controller state transitions',5:'Write-through / no-write-allocate',6:'Verification evidence',7:'Measured hit rates',8:'Mean response latency',9:'Reference FPGA synthesis',10:'Results and future improvements'}
        txt(d,(55,28),slide_titles[int(kind[5:])],36,True)
    elif kind in ('architecture','fsm','waveform'):
        pic(im,R/f'docs/assets/{kind}.png')
    elif kind in ('rtl','code'):
        lines=(R/'rtl/direct_mapped_cache.v').read_text().splitlines(); start=50 if kind=='rtl' else 97
        fs=ImageFont.truetype(MONO,18)
        display=[]
        for n,line in enumerate(lines[start:start+16]):
            chunks=textwrap.wrap(line,105,replace_whitespace=False,drop_whitespace=False) or ['']
            display.extend([(f'{start+n+1:3} ' if j==0 else '    ')+c for j,c in enumerate(chunks)])
        for n,line in enumerate(display[:22]): d.text((58,109+n*24),line,font=fs,fill=INK)
    elif kind=='logs':
        ls=[l for l in (R/'results/run.log').read_text().splitlines() if l.startswith('PASS')][:9]
        for n,l in enumerate(ls): d.text((60,120+n*43),l,font=ImageFont.truetype(MONO,18),fill=INK)
        txt(d,(60,550),'18,504 checked transactions + separate reset tests',31,True,TEAL)
        txt(d,(60,604),'Source: results/run.log and results/fpga_run.log',23)
    elif kind=='trace':
        rows=list(csv.DictReader((R/'results/directed.csv').open()))
        f=ImageFont.truetype(MONO,25)
        d.text((70,120),' #   OP    BYTE ADDR    RETURN DATA   HIT  CYCLES',font=f,fill=TEAL)
        for n,row in enumerate(rows[:12]):d.text((70,167+n*35),f"{int(row['request']):2d}   {'WR' if row['op']=='1' else 'RD'}    {row['address']}     {row['data']}      {row['hit']}    {int(row['latency_cycles']):2d}",font=f,fill=INK)
    elif kind=='baseline':
        rows=json.loads((R/'results/baseline_comparison.json').read_text())
        txt(d,(60,130),'Workload       Cache cycles    No-cache cycles    Speedup',27,True)
        for n,name in enumerate(['repeated','sequential','conflict','random']):
            row=next(r for r in rows if r['workload']==name)
            d.text((60,205+n*70),f"{name:12s}   {row['cache_response_cycles']:6.3f}          {row['baseline_response_cycles']:6.3f}        {row['response_speedup']:.3f}x",font=ImageFont.truetype(MONO,27),fill=INK)
        txt(d,(60,530),'Serial four-word refills add miss latency.',30,True,TEAL)
        txt(d,(60,587),'Source: results/baseline_comparison.json',23)
    elif kind=='report':
        pic(im,B/'report-1.png',(70,100,530,540));pic(im,B/'report-3.png',(680,100,530,540))
    elif kind=='files':
        txt(d,(70,125),'github.com/shaxryaa/Direct-Mapped-Cache-Controller',30,True,TEAL)
        txt(d,(80,220),'rtl/                    Modular Verilog implementation\ntb/                     Testbenches and reference checks\ntraces/                 Access workloads\nresults/                Logs, measured results and FPGA estimates\ndocs/                   Report, architecture and figures\noutput/                 PDF report, presentation and video',27)
        txt(d,(80,565),'Reproduce: python3 scripts/run.py',28,True,TEAL)
    elif kind=='closing':
        txt(d,(70,145),'Locality improves repeated-access performance.',32,True,TEAL)
        txt(d,(70,230),'Conflict misses and serial refill can increase latency.\nNext steps: burst refill and a write buffer.',30)
        txt(d,(70,365),'Shaurya Sharma  |  Lakshay Saharan',30,True)
        txt(d,(70,443),'Thank you',44,True,TEAL)
        txt(d,(70,548),'github.com/shaxryaa/Direct-Mapped-Cache-Controller',29)
    dest=B/f'frame-{kind}-{speaker.split()[0]}.png';im.save(dest);return dest

def stamp(t):
    ms=round(t*1000);h,ms=divmod(ms,3600000);m,ms=divmod(ms,60000);s,ms=divmod(ms,1000)
    return f'{h:02}:{m:02}:{s:02}.{ms:03}'

def build():
    # The source manifest is reviewed against the local audio transcripts.
    manifest=json.loads((B/'edit_manifest.json').read_text())
    clips=[]; timeline=[]; captions=['WEBVTT',''];elapsed=0;chapters=[]
    for i,entry in enumerate(manifest):
        data=json.loads((B/entry['transcript']).read_text());src=Path(data['source'])
        start,end=entry['in'],entry['out'];duration=end-start
        audio=B/f'audio-{i:02}.wav'
        run(['ffmpeg','-y','-v','error','-ss',str(start),'-i',str(src),'-t',str(duration),'-af','highpass=f=70,loudnorm=I=-16:TP=-1.5:LRA=11,afade=t=in:d=0.025,afade=t=out:st='+str(duration-.04)+':d=0.04','-ar','48000','-ac','1',str(audio)])
        shots=entry['shots'];concat=B/f'shots-{i:02}.txt';items=[]
        for j,shot in enumerate(shots):
            at=shot['at'];nextat=shots[j+1]['at'] if j+1<len(shots) else duration
            p=make(shot['kind'],entry['speaker']);items.extend([f"file '{p}'",f'duration {nextat-at:.6f}'])
            timeline.append(dict(start=round(elapsed+at,3),end=round(elapsed+nextat,3),visual=shot['kind'],speaker=entry['speaker']))
        items.append(f"file '{p}'");concat.write_text('\n'.join(items)+'\n')
        clip=B/f'part-{i:02}.mp4'
        run(['ffmpeg','-y','-v','error','-f','concat','-safe','0','-i',str(concat),'-i',str(audio),'-t',str(duration),'-vf','fps=24,format=yuv420p','-c:v','libx264','-preset','fast','-crf','20','-c:a','aac','-b:a','160k','-movflags','+faststart',str(clip)])
        clips.append(clip);chapters.append((elapsed,elapsed+duration,entry['title']))
        # Captions use actual recognized word times, not proportional script timing.
        words=[w for segment in data['segments'] for w in segment['words'] if w['end']>start and w['start']<end]
        groups=[];group=[]
        for w in words:
            group.append(w)
            length=len(''.join(x['word'] for x in group))
            if (length>=70 or (w['word'].strip().endswith(('.', '?', '!')) and len(group)>=4)):
                groups.append(group);group=[]
        if group:
            if len(group)<3 and groups:groups[-1].extend(group)
            else:groups.append(group)
        for group in groups:
            a=max(0,group[0]['start']-start)+elapsed;b=min(duration,group[-1]['end']-start)+elapsed
            text=''.join(x['word'] for x in group).strip().replace('75.358','75.35')
            captions.extend([f'{stamp(a)} --> {stamp(b)}',textwrap.fill(text,64),''])
        elapsed+=duration
        print(f'Built {i+1}/{len(manifest)}: {entry["title"]} ({duration:.2f}s)',flush=True)
    (O/'Cache_Controller_Human_Review.vtt').write_text('\n'.join(captions))
    cat=B/'parts.txt';cat.write_text(''.join(f"file '{c}'\n" for c in clips))
    meta=B/'chapters.txt';meta.write_text(';FFMETADATA1\n'+''.join(f'[CHAPTER]\nTIMEBASE=1/1000\nSTART={round(a*1000)}\nEND={round(b*1000)}\ntitle={t}\n' for a,b,t in chapters))
    video=O/'Cache_Controller_Human_Review.mp4'
    run(['ffmpeg','-y','-v','error','-f','concat','-safe','0','-i',str(cat),'-i',str(O/'Cache_Controller_Human_Review.vtt'),'-map','0:v','-map','0:a','-map','1:0','-map_metadata','-1','-map_chapters','-1','-c:v','copy','-c:a','copy','-c:s','mov_text','-metadata:s:s:0','language=eng','-movflags','+faststart',str(video)])
    probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_format','-show_streams','-of','json',str(video)]))
    (O/'timeline.json').write_text(json.dumps(dict(duration=elapsed,scenes=timeline,sources=manifest),indent=2))
    (O/'verification.json').write_text(json.dumps(dict(duration_seconds=float(probe['format']['duration']),under_five_minutes=float(probe['format']['duration'])<300,streams=[dict(type=s['codec_type'],codec=s['codec_name']) for s in probe['streams']],narration='Original human recordings; no synthetic speech',audio_processing='70 Hz high-pass; per-section EBU loudness normalization; short edge fades',captions='Local ASR with word timestamps; review captions for recognition errors',status='Local preview awaiting user review; no push'),indent=2))
    (O/'REVIEW.md').write_text('# Human narration review\n\nLocal preview only. Original submission video and recordings are preserved.\n\n'+'\n'.join(f'- {stamp(a)[:-4]} — {title}' for a,b,title in chapters)+'\n\nCaptions are selectable and generated from the recordings with word timestamps. Please review recognition of names and technical terms.\n')
    print(video,flush=True)
if __name__=='__main__':build()
