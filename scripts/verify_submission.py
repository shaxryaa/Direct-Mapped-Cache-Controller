#!/usr/bin/env python3
"""Check consistency of submission artifacts against raw experiment results."""
import csv
import hashlib
import json
from pathlib import Path
import re
import subprocess

R=Path(__file__).resolve().parents[1]
def read_json(path): return json.loads((R/path).read_text())
def main():
    source=(R/'docs/REPORT.md').read_text()
    for section in ['Abstract','Literature Review','Proposed Solution','Individual Contributions','References']:
        assert section in source,section
    members=read_json('docs/team.json')['members'] if (R/'docs/team.json').exists() else [
        {'name':name.strip(),'roll':roll} for name,roll in re.findall(r'^\| ([^|]+) \| (\d{10}) \|',source,re.M)]
    assert len(members)==2
    for member in members:
        assert member['name'] in source and member['roll'] in source
    references=set(re.findall(r'^\[(\d+)\]',source,re.M))
    assert set(re.findall(r'\[(\d+)\]',source))==references=={'1','2','3','4'}
    assert 'All requested checks passed.' in (R/'results/run.log').read_text()
    cache=sum(r['requests'] for path in ['results/summary.json','results/summary_512_32.json'] for r in read_json(path))
    baseline=sum(r['requests'] for r in read_json('results/baseline_comparison.json'))
    fpga=read_json('results/fpga_summary.json')
    waveform=read_json('results/waveform_verification.json')
    assert cache==9252 and baseline==4626 and fpga['netlist_verified_transactions']==4626
    assert waveform['result']=='PASS' and waveform['checked_response_handshakes']==18
    for trace in sorted((R/'traces').glob('*.trace')):
        def rows(suffix):
            with (R/'results'/f'{trace.stem}{suffix}.csv').open() as f:return list(csv.DictReader(f))
        assert rows('')==rows('_fpga')
    assert fpga['estimated_post_route_fmax_mhz']>=fpga['target_mhz']
    assert fpga['utilization']['ICESTORM_LC']['used']==610
    assert fpga['utilization']['ICESTORM_RAM']['used']==4
    video=R/'output/video/Cache_Controller_Demo.mp4'
    probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(video)]))
    seconds=float(probe['format']['duration'])
    assert seconds<300 and any(s['codec_type']=='audio' for s in probe['streams'])
    assert abs(seconds-read_json('results/video_verification.json')['duration_seconds'])<.01
    assert (R/'output/pdf/Cache_Controller_Report.pdf').stat().st_mtime>=(R/'docs/REPORT.md').stat().st_mtime
    from pypdf import PdfReader
    reader=PdfReader(R/'output/pdf/Cache_Controller_Report.pdf')
    assert len(reader.pages)==4
    assert all(abs(float(page.mediabox.width)-612)<.1 and abs(float(page.mediabox.height)-792)<.1 for page in reader.pages)
    pdf_text='\n'.join(p.extract_text() for p in reader.pages)
    assert all(member['name'] in pdf_text for member in members)
    assert '<!--' not in pdf_text and '**' not in pdf_text
    # Both body columns have text on each page; title may span the page.
    for page in reader.pages:
        positions=[]
        page.extract_text(visitor_text=lambda text,cm,tm,font,size: positions.append((tm[4]*cm[0]+tm[5]*cm[2]+cm[4],text.strip())) if text.strip() else None)
        assert any(x<300 for x,text in positions) and any(x>300 for x,text in positions)
    artifacts=['output/pdf/Cache_Controller_Report.pdf','output/presentation/Direct_Mapped_Cache_Slides.pptx',
               'output/video/Cache_Controller_Demo.mp4','output/video/Cache_Controller_Demo.vtt']
    fingerprints={path:hashlib.sha256((R/path).read_bytes()).hexdigest() for path in artifacts}
    result=dict(status='PASS',report_pages=4,report_page_format='Letter, IEEE conference-style two-column',
        checked_trace_transactions=cache+baseline+fpga['netlist_verified_transactions'],
        checked_vcd_response_handshakes=18,video_seconds=seconds,video_has_audio=True,
        actual_members=[m['name'] for m in members],reference_fpga=fpga,artifact_sha256=fingerprints,
        external_actions=['Faculty confirmation of two-member group against five-member wording',
            'Course form submission: URL not provided','Student live demonstration'])
    (R/'results/submission_verification.json').write_text(json.dumps(result,indent=2)+'\n')
    print('PASS: 4-page IEEE-style report; 18,504 transactions; 18 VCD handshakes; reference FPGA timing; video under 5 minutes.')

if __name__=='__main__':main()
