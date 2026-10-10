#!/usr/bin/env python3
"""Healer tree kernel Oppo A14 (4.19).

Dump git Oppo mengubah symlink vendor menjadi FILE TEKS kecil berisi
path relatif, dan banyak `source "..."` Kconfig menunjuk file yang tidak
diterbitkan. Healer dua-pass:
  pass1: file <200B berisi path relatif murni -> ganti direktori berisi
         Kconfig + Makefile kosong (89 entri di tree a38_a18).
  pass2: setiap `source` yang masih hilang (resolve relatif-dir dan
         relatif-root) -> touch file stub. Idempoten.
"""
import os, re, sys

os.chdir(sys.argv[1] if len(sys.argv) > 1 else '.')

n1 = 0
for dp, dn, fn in os.walk('.'):
    for f in fn:
        p = os.path.join(dp, f)
        try:
            if os.path.getsize(p) >= 200: continue
            c = open(p, errors='ignore').read().strip()
        except Exception: continue
        if re.fullmatch(r'(\.\./)+[a-zA-Z0-9_][a-zA-Z0-9_/.-]*|vendor/[a-zA-Z0-9_/.-]*', c or ''):
            os.remove(p); os.makedirs(p, exist_ok=True)
            open(os.path.join(p, 'Kconfig'), 'a').close()
            open(os.path.join(p, 'Makefile'), 'a').close()
            n1 += 1
print("pass1 placeholder->dir:", n1)

def ensure_file(t):
    d = os.path.dirname(t) or '.'
    if os.path.exists(d) and not os.path.isdir(d):
        if os.path.getsize(d) < 256: os.remove(d)
        else: return False
    os.makedirs(d, exist_ok=True)
    if os.path.isdir(t): return False
    open(t, 'a').close(); return True

for it in range(40):
    todo = set()
    for dp, dn, fn in os.walk('.'):
        for f in fn:
            if f != 'Kconfig': continue
            k = os.path.join(dp, f)
            try: txt = open(k, errors='ignore').read()
            except Exception: continue
            for m in re.finditer(r'^\s*source\s+"([^"]+)"', txt, re.M):
                p = m.group(1)
                if p.startswith('$('): continue
                for c in (os.path.normpath(os.path.join(dp, p)), os.path.normpath(p)):
                    if not os.path.isfile(c): todo.add(c)
    if not todo:
        print("pass2 CONVERGED iter", it); break
    for t in todo: ensure_file(t)
else:
    print("PERINGATAN: pass2 tidak konvergen; sisa:", len(todo))
