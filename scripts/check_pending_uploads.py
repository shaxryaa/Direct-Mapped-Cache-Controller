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
    lines=['# Repository comparison and remaining actions','',
        f'Compared local submission files with `origin/main` at `{remote}`.',
        'This is a snapshot of the last fetched remote branch, not a live GitHub status check.',
        'The inventory excludes this generated document itself. No commit or push is performed by this script.','',
        f'New files: {len(new)}. Changed files: {len(changed)}. Deleted files: {len(deleted)}.','',
        '## New files','']
    lines += [f'- `{p}`' for p in new] or ['None.']
    lines += ['', '## Changed files',''] + ([f'- `{p}`' for p in changed] or ['None.'])
    lines += ['', '## Deleted files',''] + ([f'- `{p}`' for p in deleted] or ['None.'])
    lines += ['', '## External actions still needed','',
        '- Obtain faculty confirmation of the actual two-member group against the five-member wording.',
        '- Submit the repository/video links in the course form (its URL has not been provided).',
        '- Deliver the live presentation; no physical FPGA board was supplied.',
        '- Use a verified GitHub email for future commits if profile attribution is required.','']
    (R/'docs/PENDING_UPLOADS.md').write_text('\n'.join(lines))
    print(f'Remote {remote[:7]}: {len(new)} new files and {len(changed)} changed files prepared locally; {len(deleted)} intentional tracked deletions.')

if __name__=='__main__':main()
