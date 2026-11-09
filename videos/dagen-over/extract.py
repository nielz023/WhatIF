import re,sys
L=open('script_days_left.md').read().split('\n')
shot_re=re.compile(r"^(?:- )?\*\*(\d+[a-z0-9-]*[a-z0-9]?) · ")
lab=re.compile(r"(?:\*\*([A-ZËÈ][A-ZËÈ' ]+?)(?: \(([^)]*)\))?:\*\*|\*\*([A-ZËÈ][A-ZËÈ' ]+?)\*\* \(([^)]*)\)\*\*:\*\*| · (VO):\*\*)")
ROL={'VO':'Verteller','JONGEN':'Jongen','OPA':'Opa','VRIEND':'Vriend','DIRECTEUR':'Directeur','BROERTJE':'Broertje','OMA':'Oma','PESTKOP':'Pestkop','PAPA':'Papa','NIEUWSLEZERES':'Nieuwslezeres','MAMA':'Mama','DOKTER':'Dokter','MAN':'ManPak','CONCIËRGE':'Concierge'}
out=[];shot=None
for i,l in enumerate(L):
    if l.startswith('# Bijlagen'): break
    m=shot_re.match(l)
    if m: shot=m.group(1)
    ms=list(lab.finditer(l))
    for k,m in enumerate(ms):
        who=m.group(1) or m.group(3) or m.group(5)
        if who not in ROL: continue
        seg=l[m.end(): ms[k+1].start() if k+1<len(ms) else len(l)]
        qs=re.findall(r'"([^"]+)"',seg)
        if qs: out.append((shot,ROL[who],' '.join(qs),i+1))
    if 'Ma\'am, quick question' in l: out.append((shot,'Vriend',"Ma'am, quick question about the, uh... the thing.",i+1))
n={};rows=[]
for shot,rol,t,ln in out:
    sc=re.match(r'\d+',shot).group(); n[sc]=n.get(sc,0)+1
    rows.append(f"K{int(sc):02d}-{n[sc]:02d}\t{shot}\t{rol}\t{t}")
open('vo/regels.tsv','w').write('\n'.join(rows)+'\n')
print(len(rows))
