#!/usr/bin/env python3
"""Read-only structural audit for a Skyline Edge APK (Python stdlib only)."""
import argparse, json, re, shutil, struct, subprocess, tempfile, zipfile
from pathlib import Path

def u32(data, off): return struct.unpack_from("<I", data, off)[0]
def uleb(data, off):
    value = shift = 0
    while True:
        byte = data[off]; off += 1; value |= (byte & 127) << shift
        if byte < 128: return value, off
        shift += 7
        if shift > 35: raise ValueError("Invalid ULEB128")

def parse_dex(data):
    if data[:4] != b"dex\n": raise ValueError("Invalid DEX header")
    ss, so, ts, to = u32(data,56),u32(data,60),u32(data,64),u32(data,68)
    ps, po, ms, mo = u32(data,72),u32(data,76),u32(data,88),u32(data,92)
    cs, co = u32(data,96),u32(data,100)
    strings=[]
    for i in range(ss):
        off=u32(data,so+4*i); _,off=uleb(data,off); end=data.index(b"\0",off)
        strings.append(data[off:end].decode("utf-8","replace"))
    types=[strings[u32(data,to+4*i)] for i in range(ts)]
    protos=[]
    for i in range(ps):
        _,ret,param_off=struct.unpack_from("<III",data,po+12*i); args=[]
        if param_off:
            count=u32(data,param_off)
            args=[types[struct.unpack_from("<H",data,param_off+4+2*j)[0]] for j in range(count)]
        protos.append((types[ret],args))
    methods=[]
    for i in range(ms):
        ci,pi,ni=struct.unpack_from("<HHI",data,mo+8*i)
        methods.append((types[ci],strings[ni],protos[pi]))
    classes=[]; natives=[]
    for i in range(cs):
        ci,_,_,_,_,_,data_off,_=struct.unpack_from("<IIIIIIII",data,co+32*i)
        desc=types[ci]
        if not desc.startswith("Lemu/skyline/"): continue
        classes.append(desc)
        if not data_off: continue
        off=data_off
        for _ in range(2): _,off=uleb(data,off) # static and instance fields
        direct,off=uleb(data,off); virtual,off=uleb(data,off)
        for count in (direct,virtual):
            idx=0
            for _ in range(count):
                diff,off=uleb(data,off); flags,off=uleb(data,off); _,off=uleb(data,off); idx+=diff
                if idx>=len(methods): continue
                owner,name,(ret,args)=methods[idx]
                if owner==desc and flags&0x100:
                    natives.append(f"{owner}->{name}({''.join(args)}){ret}")
    return {"dex_version":data[4:7].decode("ascii","replace"),"dex_bytes":len(data),
      "string_ids":ss,"type_ids":ts,"method_ids":ms,"class_defs":cs,
      "skyline_class_count":len(classes),"skyline_classes":sorted(classes),
      "skyline_native_methods":sorted(set(natives))}

def inspect_elf(blob):
    out={"present":bool(blob),"bytes":len(blob)}
    if not blob:return out
    readelf=shutil.which("readelf")
    if not readelf:out["note"]="readelf unavailable";return out
    with tempfile.NamedTemporaryFile(suffix=".so") as f:
        f.write(blob);f.flush();p=f.name
        h=subprocess.run([readelf,"-h",p],text=True,capture_output=True,check=True).stdout
        d=subprocess.run([readelf,"-d",p],text=True,capture_output=True,check=True).stdout
        s=subprocess.run([readelf,"-Ws",p],text=True,capture_output=True,check=True).stdout
        n=subprocess.run([readelf,"-n",p],text=True,capture_output=True).stdout
    out["elf64_aarch64"]="ELF64" in h and "AArch64" in h
    out["needed_libraries"]=sorted(set(re.findall(r"Shared library: \[(.*?)\]",d)))
    out["jni_exports"]=sorted(set(re.findall(r"\b(Java_[A-Za-z0-9_]+)",s)))
    out["jni_export_count"]=len(out["jni_exports"])
    out["build_id"]=next(iter(re.findall(r"Build ID: ([0-9a-f]+)",n)),None)
    return out

def audit(apk):
    with zipfile.ZipFile(apk) as z:
        names=set(z.namelist()); dex=z.read("classes.dex")
        so=z.read("lib/arm64-v8a/libskyline.so") if "lib/arm64-v8a/libskyline.so" in names else b""
        return {"apk":Path(apk).name,"apk_bytes":Path(apk).stat().st_size,
          "classes_dex":parse_dex(dex),"libskyline_so":inspect_elf(so),
          "arm64_libraries":sorted(x for x in names if x.startswith("lib/arm64-v8a/") and x.endswith(".so")),
          "zip_entry_count":len(names)}

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument("apk",type=Path);p.add_argument("--output",type=Path);a=p.parse_args()
    report=json.dumps(audit(a.apk),ensure_ascii=False,indent=2)+"\n"
    if a.output:a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(report,encoding="utf-8")
    print(report,end="")
if __name__=="__main__":main()
