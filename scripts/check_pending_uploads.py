#!/usr/bin/env python3
"""Compare the prepared submission files with origin/main, without committing."""
import hashlib
from pathlib import Path
import subprocess

R=Path(__file__).resolve().parents[1]

def git(*args):
    return subprocess.check_output(['git',*args],cwd=R)

def main():
    remote=git('rev-parse','origin/main').decode().strip()
    tree={}
    for record in git('ls-tree','-r','-z','origin/main').split(b'\0'):
        if not record: continue
        meta,name=record.split(b'\t',1)
        tree[name.decode()]=meta.split()[2].decode()
    files=[R/name for name in ['README.md','Makefile','.gitignore','.gitattributes','requirements-artifacts.txt']]
    for folder in ['rtl','tb','scripts','traces','results','docs','output/pdf','output/presentation','output/video','.github']:
        files.extend(p for p in (R/folder).rglob('*') if p.is_file() and '__pycache__' not in p.parts and not p.is_symlink())
    files.append(R/'output/Cache_Controller_Project.zip')
    new=[];changed=[]
    for file in sorted(set(files)):
        relative=str(file.relative_to(R))
        if relative=='docs/PENDING_UPLOADS.md' or not file.exists(): continue
        data=file.read_bytes()
        digest=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
        if relative not in tree: new.append(relative)
        elif tree[relative]!=digest: changed.append(relative)
    deleted=[p for p in tree if not (R/p).exists() and p.startswith(('docs/','rtl/','tb/','scripts/'))]
    lines=['# Latest repository review and pending uploads','',
        f'Reviewed `origin/main` at `{remote}`. No new commits or pushes were made.','',
        '## What Lakshay committed','',
        '`6ac3947` updates only `docs/REPORT.md`: both authors, IEEE sections, modular architecture, baseline results, FPGA resources/Fmax, contributions and references.',
        'It does not upload the corresponding RTL modules, baseline/FPGA scripts and evidence, diagrams, regenerated PDF or demo video.','',
        '## Completed locally in this review','',
        '- Used Lakshay\'s report as the source, retaining his wording and tables.',
        '- Added architecture, FSM and actual-waveform figures and exported the matching IEEE-style PDF.',
        '- Re-ran RTL/cache/baseline verification and the reference FPGA/netlist flow.',
        '- Checked the existing 4:18 demonstration, captions, members and artifact consistency.',
        '- Refreshed the submission archive and this upload inventory.',
        '- Preserved the deletion of CONTRIBUTIONS.md, team.json and DEMO_AND_VIVA.md.','',
        '## Upload priorities','',
        '1. Updated modular `rtl/`, `tb/`, and reproduction scripts with current `results/` evidence.',
        '2. Report source, matching PDF, `docs/assets/` diagrams and current PPTX.',
        '3. MP4, captions and transcript under `output/video/` and `docs/VIDEO_SCRIPT.md`.',
        '4. README, submission checklist, optional CI workflow and complete ZIP.',
        '5. Preserve the intentional file deletions listed below.','',
        'The original `.git` history, `build/` caches, and extracted `output/Cache_Controller_Project/` folder do not need uploading. The ZIP is the refreshed complete package.','',
        '## New files not present in origin/main','']
    lines += [f'- `{p}`' for p in new]
    lines += ['', '## Existing files with prepared changes','']+[f'- `{p}`' for p in changed]
    lines += ['', '## Intentional deletions to preserve','']+[f'- `{p}`' for p in deleted]
    lines += ['', '## External actions still needed','',
        '- A group member must review and commit/upload these prepared files; no assistant commit or push will be made.',
        '- Obtain faculty confirmation of the actual two-member group against the five-member wording.',
        '- Submit the repository/video links in the course form (its URL has not been provided).',
        '- Deliver the live presentation; no physical FPGA board was supplied.','']
    (R/'docs/PENDING_UPLOADS.md').write_text('\n'.join(lines))
    print(f'Remote {remote[:7]}: {len(new)} new files and {len(changed)} changed files prepared locally; {len(deleted)} intentional tracked deletions.')

if __name__=='__main__':main()
