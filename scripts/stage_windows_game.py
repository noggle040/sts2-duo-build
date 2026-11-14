#!/usr/bin/env python3
"""Stage an owned Windows STS2 install for upstream's macOS-style folder layout.
Creates symlinks, never converts Windows native code, and never builds an IPA.
Requires a private filesystem; do not upload the staged assets to this public repo.
"""
import argparse
import json
from pathlib import Path
from sts2_preflight import parse_cli, MetadataError

p=argparse.ArgumentParser(description=__doc__)
p.add_argument('windows_game_root',help='Folder with SlayTheSpire2.exe and SlayTheSpire2.pck')
p.add_argument('staging_root',help='New empty directory for staged symlinks')
a=p.parse_args()
root=Path(a.windows_game_root).expanduser().resolve()
stage=Path(a.staging_root).expanduser().resolve()
source=root/'data_sts2_windows_x86_64'
pck=root/'SlayTheSpire2.pck'
if not source.is_dir() or not (source/'sts2.dll').is_file() or not pck.is_file():
    p.error('Missing data_sts2_windows_x86_64/sts2.dll or SlayTheSpire2.pck')
if stage.exists() and any(stage.iterdir()):
    p.error('Refusing to overwrite nonempty stage directory')
resources=stage/'Resources'
target=resources/'data_sts2_macos_arm64'
target.mkdir(parents=True,exist_ok=True)
managed=[]
skipped=[]
for file in sorted(source.glob('*.dll')):
    try:
        parse_cli(file.read_bytes())
    except (MetadataError, ValueError, KeyError, IndexError, OverflowError):
        skipped.append(file.name)
        continue
    (target/file.name).symlink_to(file)
    managed.append(file.name)
for name in ('sts2.deps.json','sts2.runtimeconfig.json'):
    if (source/name).is_file():
        (target/name).symlink_to(source/name)
(resources/'Slay the Spire 2.pck').symlink_to(pck)
print(json.dumps({
    'STS2_GAME_APP':str(resources),
    'managed_assemblies':len(managed),
    'excluded_windows_native_dlls':skipped,
    'warning':'Compatibility shim only; iOS libraries, AOT, signing and device testing still required.'
},indent=2))
