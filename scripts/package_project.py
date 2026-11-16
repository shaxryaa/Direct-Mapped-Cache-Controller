#!/usr/bin/env python3
"""Package the maintained project and current report export for submission."""
from pathlib import Path
import os
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def main():
    source = ROOT/'docs/REPORT.md'
    pdf = ROOT/'output/pdf/Cache_Controller_Report.pdf'
    if not pdf.exists() or pdf.stat().st_mtime < source.stat().st_mtime:
        raise SystemExit('The PDF is missing or older than docs/REPORT.md. Run scripts/build_report.py first.')
    files = [ROOT/'README.md', ROOT/'Makefile', ROOT/'.gitignore', ROOT/'.gitattributes', ROOT/'requirements-artifacts.txt']
    for directory in ('rtl', 'tb', 'scripts', 'traces', 'results', 'docs',
                      'output/pdf', 'output/presentation', 'output/video', '.github'):
        files.extend(p for p in (ROOT/directory).rglob('*')
                     if p.is_file() and '__pycache__' not in p.parts and not p.is_symlink())
    for filename in ('cache_synth.v','cache_ice40_netlist.v','cache_ice40.asc'):
        netlist=ROOT/'build'/filename
        if netlist.is_file(): files.append(netlist)
    destination = ROOT/'output/Cache_Controller_Project.zip'
    destination.parent.mkdir(parents=True, exist_ok=True)
    # Replace the archive only after the new ZIP passes its integrity check.
    handle, temporary = tempfile.mkstemp(prefix='cache-project-', suffix='.zip',
                                         dir=destination.parent)
    os.close(handle)
    try:
        with zipfile.ZipFile(temporary, 'w', zipfile.ZIP_DEFLATED) as archive:
            for file in sorted(set(files)):
                archive.write(file, 'Cache_Controller_Project/' + str(file.relative_to(ROOT)))
        with zipfile.ZipFile(temporary) as archive:
            if archive.testzip() is not None:
                raise RuntimeError('Archive integrity check failed')
            count = len(archive.namelist())
        os.replace(temporary, destination)
    finally:
        Path(temporary).unlink(missing_ok=True)
    print(f'{destination}\n{count} files, {destination.stat().st_size:,} bytes')


if __name__ == '__main__':
    main()
