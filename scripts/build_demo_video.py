#!/usr/bin/env python3
"""Create a <=5 minute narrated walkthrough using actual project evidence.

macOS say supplies synthetic narration. Requires Pillow, Matplotlib and FFmpeg.
The result presents recorded simulation evidence; it is not a live screen capture.
"""
from pathlib import Path
import csv
import json
import subprocess
import textwrap

from PIL import Image, ImageDraw, ImageFont
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

R=Path(__file__).resolve().parents[1]
B=R/'build/video';B.mkdir(parents=True,exist_ok=True)
O=R/'output/video';O.mkdir(parents=True,exist_ok=True)
font='/System/Library/Fonts/Supplemental/Arial.ttf'
bold='/System/Library/Fonts/Supplemental/Arial Bold.ttf'
mono='/System/Library/Fonts/Menlo.ttc'
ink='#152f49';teal='#087f8c'
fpga=json.loads((R/'results/fpga_summary.json').read_text())
scenes=[
('Project idea and group members', 'A direct-mapped cache controller stores recently used memory blocks to reduce repeated access latency. This prototype uses one kilobyte of cache data and sixteen-byte blocks. The actual group members are Shaurya Sharma, roll number 2401010439, and Lakshay Saharan, roll number 2401020034. Shaurya handles implementation and analysis. Lakshay handles the report, slides and video. This walkthrough uses synthetic narration and actual recorded simulation evidence.', 'team'),
('System architecture', 'The cache sits between a CPU request interface and backing memory. The address decoder separates a twenty-two-bit tag, six-bit index and four-bit offset. Metadata stores tags and valid bits. The comparator checks for a hit. Data RAM holds four words per line. Requests and responses use valid and ready handshakes. The controller supports one outstanding CPU request.', 'architecture'),
('Synthesizable modular Verilog', 'This is the actual Verilog implementation. The top module instantiates the decoder, metadata storage, tag comparator and data RAM. The data RAM has synchronous read and write ports, so the FPGA flow can infer block memories. A word is read when the CPU request is accepted, then LOOKUP uses that registered word. The dedicated test memory is excluded from cache synthesis.', 'rtl'),
('Seven-state controller', 'IDLE accepts a request and LOOKUP checks the line. A read hit prepares a response. A read miss alternates REFILL REQUEST and REFILL WAIT until all four words arrive, then installs the tag and valid bit. Writes use write-through with no-write-allocate. A write hit updates cache and memory; a write miss updates memory only. The response waits until the CPU accepts it.', 'fsm'),
('Actual verification output', 'These PASS lines come from the executed testbench. Eight workloads run on two cache configurations. Independent Verilog and Python scoreboards check hit decisions and data. The testbench also checks backing memory and stable outputs during stalls. Reset tests cover invalidation and aborted transactions. Including the no-cache baseline and FPGA primitive netlist, eighteen thousand five hundred and four trace transactions passed.', 'logs'),
('Waveform verification', 'This waveform comes directly from the simulator V C D file. The first read misses and causes four memory responses before the CPU response becomes valid. Later accesses to other words in the same block hit. CPU response backpressure keeps the result stable until ready. A separate checker samples every directed-trace response handshake and confirms that all eighteen match the checked result C S V.', 'waveform'),
('Directed requests and returned data', 'Here are actual requests from the directed trace. The first read at address zero misses. Reads at four, eight and twelve hit because the whole block was refilled. Address hexadecimal four hundred maps to the same line with a different tag, causing a conflict. Later writes and reads verify write-through and no-write-allocate behavior. Every returned word and hit flag matches the independent model.', 'transactions'),
('Measured hit rates and baseline', 'Sequential reads achieve seventy-five percent hits. Repeated reads over a small working set achieve ninety-six point eight eight percent. Alternating conflicting addresses achieve zero percent. The no-cache comparison is important: repeated reads are about one point eight three times faster, but sequential and conflict accesses are slower with this cache. A miss fetches four serial words while an uncached read fetches only one.', 'metrics'),
('Reference FPGA results', f'The reference implementation targets a Lattice ice forty H X eight K, C T two fifty-six device. It uses six hundred and ten logic cells and four block memories. The post-route internal maximum frequency estimate is {fpga["estimated_post_route_fmax_mhz"]:.2f} megahertz, meeting the requested twenty-five megahertz target. IO pins are placed automatically, without external delay constraints. These are tool estimates, not measurements from a physical board.', 'fpga'),
('Reproduction and submission', 'The repository contains the modular source code, testbenches, traces, waveform, raw results, IEEE-format report and this demonstration video. Run python three scripts slash run dot py to reproduce functional verification. Run scripts slash run underscore F P G A dot py for reference synthesis and timing. The actual group has two members, so the five-member rubric requirement needs faculty confirmation. A live presentation remains the group members responsibility.', 'finish'),
]

def drawtext(draw,xy,text,size=28,weight=False,fill=ink,width=None,spacing=10):
    f=ImageFont.truetype(bold if weight else font,size)
    if width:
        text='\n'.join(textwrap.fill(line,width=width) for line in text.split('\n'))
    draw.multiline_text(xy,text,font=f,fill=fill,spacing=spacing)

def base(title,n):
    im=Image.new('RGB',(1280,720),'#f8fafc');d=ImageDraw.Draw(im)
    drawtext(d,(55,35),title,40,True)
    d.line((55,102,1225,102),fill='#c6d5df',width=2)
    drawtext(d,(55,677),'Recorded prototype evidence / synthetic narration',19,fill='#4c6477')
    drawtext(d,(1170,677),f'{n+1:02d}',19)
    return im,d

def paste_image(im,path,box=(70,125,1140,520)):
    pic=Image.open(path).convert('RGB');pic.thumbnail((box[2],box[3]))
    im.paste(pic,(box[0]+(box[2]-pic.width)//2,box[1]+(box[3]-pic.height)//2))

def content(im,d,kind):
    if kind=='team':
        drawtext(d,(70,150),'Direct-mapped cache: 1 KB / 16-byte blocks',34,True,fill=teal)
        drawtext(d,(70,245),'Shaurya Sharma - 2401010439\nRTL, verification, analysis and synthesis',31,spacing=16)
        drawtext(d,(70,370),'Lakshay Saharan - 2401020034\nReport, slides and video',31,spacing=16)
        drawtext(d,(70,525),'Actual group: two members. Faculty confirmation needed for the five-member rubric.',24,width=85)
    elif kind in ('architecture','fsm','waveform'):
        paste_image(im,R/f'docs/assets/{kind}.png')
    elif kind=='rtl':
        source=(R/'rtl/direct_mapped_cache.v').read_text().splitlines()
        first=next(i for i,v in enumerate(source) if 'cache_address_decoder #' in v)
        lines=source[first:first+15]
        f=ImageFont.truetype(mono,19)
        display=[]
        for k,line in enumerate(lines):
            pieces=textwrap.wrap(line.strip(),width=88,break_long_words=False,break_on_hyphens=False) or ['']
            for n,piece in enumerate(pieces):
                display.append((f'{first+k+1:3d}  ' if n==0 else '     ')+piece)
        for j,line in enumerate(display[:18]):d.text((65,142+j*25),line,font=f,fill=ink)
        drawtext(d,(70,604),'rtl/direct_mapped_cache.v - actual source excerpt',23,fill=teal)
    elif kind=='logs':
        lines=[x for x in (R/'results/run.log').read_text().splitlines() if x.startswith('PASS')][:9]
        f=ImageFont.truetype(mono,19)
        for j,line in enumerate(lines):d.text((65,148+j*41),line,font=f,fill=ink)
        drawtext(d,(70,550),'18,504 verified transactions + dedicated reset checks',32,True,fill=teal)
        drawtext(d,(70,603),'Evidence: run.log, fpga_run.log and waveform_verification.json',23)
    elif kind=='transactions':
        with (R/'results/directed.csv').open() as f: rows=list(csv.DictReader(f))
        f=ImageFont.truetype(mono,25)
        d.text((70,142),' #   OP    BYTE ADDR    RETURN DATA   HIT   CYCLES',font=f,fill=teal)
        for j,row in enumerate(rows[:12]):
            d.text((70,185+j*35),f"{int(row['request']):2d}   {'WR' if row['op']=='1' else 'RD'}    {row['address']}     {row['data']}      {row['hit']}     {int(row['latency_cycles']):2d}",font=f,fill=ink)
    elif kind=='metrics':
        data=json.loads((R/'results/baseline_comparison.json').read_text())
        drawtext(d,(70,142),'Workload       Cache cycles    No-cache cycles    Speedup',28,True)
        for j,name in enumerate(['repeated','sequential','conflict','random']):
            row=next(v for v in data if v['workload']==name)
            f=ImageFont.truetype(mono,27)
            d.text((70,210+j*65),f"{name:12s}   {row['cache_response_cycles']:6.3f}          {row['baseline_response_cycles']:6.3f}        {row['response_speedup']:.3f}x",font=f,fill=ink)
        drawtext(d,(70,510),'Hit rates: repeated 96.88% / sequential 75% / conflict 0%',29,True,fill=teal)
        drawtext(d,(70,578),'A four-word serial refill can cost more than an uncached word read.',25,width=83)
    elif kind=='fpga':
        drawtext(d,(70,145),'Reference target: iCE40 HX8K / CT256 / seed 1',30,True)
        drawtext(d,(70,225),'610 / 7680 logic cells\n4 / 32 block RAMs\n206 / 206 IO cells',33,spacing=18)
        drawtext(d,(70,410),f'{fpga["estimated_post_route_fmax_mhz"]:.2f} MHz estimated internal Fmax',42,True,fill=teal)
        drawtext(d,(70,496),'25 MHz target met. Automatic IO placement.\nNo external IO-delay constraints or physical board test.',26,spacing=16)
    else:
        drawtext(d,(70,150),'github.com/shaxryaa/Direct-Mapped-Cache-Controller',31,True,fill=teal)
        drawtext(d,(70,250),'python3 scripts/run.py\npython3 scripts/run_fpga.py',31,spacing=22)
        drawtext(d,(70,395),'IEEE report / source / traces / waveforms / FPGA results / video',27,width=75)
        drawtext(d,(70,515),'Shaurya Sharma + Lakshay Saharan\nTwo actual members; live presentation remains to be delivered.',27,spacing=17)

def probe(path):
    return json.loads(subprocess.check_output(['ffprobe','-v','error','-show_format','-show_streams','-of','json',str(path)]))

clips=[];durations=[];vtt=['WEBVTT',''];transcript=['# Prototype video transcript','',
    'Synthetic narration over actual recorded prototype evidence. Actual group: Shaurya Sharma and Lakshay Saharan.','']
def stamp(seconds):
    ms=round(seconds*1000);h,ms=divmod(ms,3600000);m,ms=divmod(ms,60000);s,ms=divmod(ms,1000)
    return f'{h:02}:{m:02}:{s:02}.{ms:03}'
elapsed=0
for i,(title,narration,kind) in enumerate(scenes):
    im,d=base(title,i);content(im,d,kind);frame=B/f'{i:02}.png';im.save(frame)
    text=B/f'{i:02}.txt';text.write_text(narration)
    audio=B/f'{i:02}.aiff'
    subprocess.run(['say','-v','Samantha','-r','165','-f',str(text),'-o',str(audio)],check=True)
    duration=float(probe(audio)['format']['duration'])+.6
    clip=B/f'{i:02}.mp4'
    subprocess.run(['ffmpeg','-y','-v','error','-loop','1','-framerate','12','-i',str(frame),
        '-i',str(audio),'-t',str(round(duration,3)),'-vf','format=yuv420p','-c:v','libx264',
        '-preset','fast','-crf','22','-c:a','aac','-b:a','96k','-af','apad','-movflags','+faststart',str(clip)],check=True)
    clips.append(clip);durations.append(duration)
    # Sentence-sized captions timed proportionally to spoken word count.
    sentences=[s.strip()+'.' for s in narration.split('. ') if s.strip()]
    total=sum(len(s.split()) for s in sentences);at=elapsed
    for sentence in sentences:
        length=(duration-.6)*len(sentence.split())/total
        vtt.extend([f'{stamp(at)} --> {stamp(at+length)}',textwrap.fill(sentence,width=80),''])
        at+=length
    transcript += [f'## {stamp(elapsed)} - {title}',narration,'']
    elapsed+=duration
    print(f'{i+1}/{len(scenes)}: {title} ({duration:.1f}s)',flush=True)
if elapsed>=300:raise SystemExit(f'Video would exceed 5 minutes: {elapsed:.2f}s')
concat=B/'clips.txt';concat.write_text(''.join("file '"+str(p)+"'\n" for p in clips))
video=O/'Cache_Controller_Demo.mp4'
subprocess.run(['ffmpeg','-y','-v','error','-f','concat','-safe','0','-i',str(concat),
    '-c','copy','-movflags','+faststart',str(video)],check=True)
actual=probe(video);seconds=float(actual['format']['duration'])
assert seconds<300
assert any(s['codec_type']=='audio' for s in actual['streams'])
(O/'Cache_Controller_Demo.vtt').write_text('\n'.join(vtt))
(R/'docs/VIDEO_SCRIPT.md').write_text('\n'.join(transcript))
(R/'results/video_verification.json').write_text(json.dumps(dict(duration_seconds=seconds,
    maximum_allowed_seconds=300,under_limit=True,scene_count=len(scenes),
    has_audio=True,narration='macOS Samantha synthetic voice',
    source='Actual source files, checked simulation logs/CSVs, VCD plot and FPGA results; recorded-evidence walkthrough, not a live desktop recording.'),indent=2)+'\n')
print(f'PASS: video {seconds:.2f}s, audio present, under 300s. {video}')
