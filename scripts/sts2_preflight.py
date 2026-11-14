#!/usr/bin/env python3
"""Offline .NET class/method name audit for the upstream sts2-ios port.
No game files, binaries, or proprietary assets are included.
Usage: python3 scripts/sts2_preflight.py path/to/sts2.dll path/to/manifest.json
Name matches do NOT establish method signature, NativeAOT, or iOS compatibility.
"""
import hashlib
import json
import pathlib
import struct
import sys

class MetadataError(ValueError):
    pass

def parse_cli(data: bytes) -> dict[str, set[str]]:
    def u16(p):
        return struct.unpack_from('<H', data, p)[0]
    def u32(p):
        return struct.unpack_from('<I', data, p)[0]
    pe=u32(0x3c)
    if data[pe:pe+4] != bytes((80,69,0,0)):
        raise MetadataError('Not a PE image')
    coff=pe+4
    nsec=u16(coff+2)
    optsz=u16(coff+16)
    opt=coff+20
    magic=u16(opt)
    if magic not in (0x10b,0x20b):
        raise MetadataError('Unexpected PE optional header')
    directories=opt+(112 if magic==0x20b else 96)
    sections=opt+optsz
    sec=[]
    for i in range(nsec):
        p=sections+i*40
        vsize,vrva,rsize,rpos=struct.unpack_from('<IIII',data,p+8)
        sec.append((vrva,max(vsize,rsize),rpos))
    def rvaoff(rva):
        for va,size,off in sec:
            if va <= rva < va+size:
                return off+rva-va
        raise MetadataError('Missing PE section for RVA')
    cli_rva=u32(directories+14*8)
    if not cli_rva:
        raise MetadataError('Not a .NET assembly')
    cli=rvaoff(cli_rva)
    md=rvaoff(u32(cli+8))
    if data[md:md+4] != b'BSJB':
        raise MetadataError('Missing CLI metadata signature')
    vlen=u32(md+12)
    p=(md+16+vlen+3)&~3
    nstreams=u16(p+2)
    p+=4
    streams={}
    for _ in range(nstreams):
        off,size=struct.unpack_from('<II',data,p)
        p+=8
        q=data.index(0,p)
        name=data[p:q].decode('ascii')
        p=(q+4)&~3
        streams[name]=(md+off,size)
    if '#Strings' not in streams:
        raise MetadataError('Missing string heap')
    st=streams['#Strings'][0]
    def string(idx):
        if not idx:
            return ''
        pos=st+idx
        return data[pos:data.index(0,pos)].decode('utf8','replace')
    tbl=streams.get('#~') or streams.get('#-')
    if tbl is None:
        raise MetadataError('Missing table stream')
    p=tbl[0]
    heaps=data[p+6]
    valid=struct.unpack_from('<Q',data,p+8)[0]
    p+=24
    rc={}
    for i in range(64):
        if valid&(1<<i):
            rc[i]=u32(p)
            p+=4
    si=4 if heaps&1 else 2
    gi=4 if heaps&2 else 2
    bi=4 if heaps&4 else 2
    def ti(table):
        return 4 if rc.get(table,0)>=65536 else 2
    def ci(tables,bits):
        return 4 if max((rc.get(t,0) for t in tables),default=0)>=(1<<(16-bits)) else 2
    sizes={
        0:2+si+gi*3,
        1:ci([0,26,35,1],2)+si*2,
        2:4+si*2+ci([2,1,27],2)+ti(4)+ti(6),
        3:ti(4),
        4:2+si+bi,
        5:ti(6),
        6:4+2+2+si+bi+ti(8)
    }
    offsets={}
    pos=p
    for i in range(7):
        if valid&(1<<i):
            offsets[i]=pos
            pos+=rc[i]*sizes[i]
    def readindex(at,size):
        return u16(at) if size==2 else u32(at)
    types=[]
    for i in range(rc.get(2,0)):
        a=offsets[2]+i*sizes[2]
        name=string(readindex(a+4,si))
        namespace=string(readindex(a+4+si,si))
        start=readindex(a+4+2*si+ci([2,1,27],2)+ti(4),ti(6))
        types.append(((namespace+'.' if namespace else '')+name,start))
    names=[]
    for i in range(rc.get(6,0)):
        a=offsets[6]+i*sizes[6]
        names.append(string(readindex(a+8,si)))
    out={}
    for i,(name,start) in enumerate(types):
        end=types[i+1][1] if i+1<len(types) else len(names)+1
        out[name]=set(names[max(0,start-1):max(0,end-1)])
    return out

def main():
    if len(sys.argv)!=3:
        print(__doc__)
        return 2
    dll=pathlib.Path(sys.argv[1])
    manifest=pathlib.Path(sys.argv[2])
    blob=dll.read_bytes()
    methods=parse_cli(blob)
    targets=[(x['targetType'],x['targetMethod']) for x in json.loads(manifest.read_text())['patches']]
    missing_types=[]
    missing_methods=[]
    matched=[]
    for typ,meth in targets:
        if typ not in methods:
            missing_types.append(f'{typ}::{meth}')
        elif meth not in methods[typ]:
            missing_methods.append(f'{typ}::{meth}')
        else:
            matched.append(f'{typ}::{meth}')
    result={
        'assembly':dll.name,
        'bytes':len(blob),
        'sha256':hashlib.sha256(blob).hexdigest(),
        'type_definitions':len(methods),
        'total_hook_checks':len(targets),
        'hook_names_found':len(matched),
        'missing_types':missing_types,
        'missing_methods':missing_methods,
        'verdict':'INCOMPATIBLE_HOOK_NAMES' if missing_types or missing_methods else 'HOOK_NAMES_PRESENT_ONLY_SIGNATURES_UNVERIFIED'
    }
    print(json.dumps(result,indent=2))
    return 1 if missing_types or missing_methods else 0

if __name__=='__main__':
    sys.exit(main())
