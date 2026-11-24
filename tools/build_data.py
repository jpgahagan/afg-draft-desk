import csv, json, re, os
B=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def norm(s):
    s=s.lower().replace('.','').replace("'",'').strip()
    s=re.sub(r'^saint ','st ',s)
    for suf in [' city and borough',' census area',' municipality',' borough',' county',' parish',' city']:
        if s.endswith(suf): s=s[:-len(suf)]
    return re.sub(r'\s+',' ',s).strip()
cty={}; st={}; us=None
for l in open(os.path.join(B,'data/saipe_est24all.txt'),encoding='latin-1'):
    sf,cf,pct,inc,name,pa=l[0:2],l[3:6].strip(),l[34:38].strip(),l[133:139].strip(),l[193:238].strip(),l[239:241]
    rec={'pov':float(pct) if pct not in ('','.') else None,'inc':int(inc) if inc.isdigit() else None,'name':name}
    if sf=='00': us=rec
    elif cf=='0': st[pa]=rec
    else: cty[pa+'|'+norm(name)]=rec
fips={}
for r in csv.DictReader(open(os.path.join(B,'data/co-est2024-alldata.csv'),encoding='latin-1')):
    if r['SUMLEV']!='050': continue
    # map state name to postal via saipe states
    pass
stname2pa={v['name']:k for k,v in st.items()}
for r in csv.DictReader(open(os.path.join(B,'data/co-est2024-alldata.csv'),encoding='latin-1')):
    if r['SUMLEV']!='050': continue
    pa=stname2pa.get(r['STNAME']); k=f"{pa}|{norm(r['CTYNAME'])}"
    if k in cty: cty[k]['pop']=int(r['POPESTIMATE2024'])
rows=list(csv.reader(open(os.path.join(B,'data/nfdr_national.csv'),encoding='utf-8-sig',errors='replace')))
h=[x.strip() for x in rows[0]]; I={k:i for i,k in enumerate(h)}
def g(r,k): return r[I[k]].strip() if I[k]<len(r) else ''
def n(x):
    try: return int(float(x))
    except: return 0
depts=[]; miss=0
for r in rows[1:]:
    if len(r)<10: continue
    pa=g(r,'HQ state'); co=g(r,'County')
    k=f"{pa}|{norm(co)}"
    if k not in cty: miss+=1
    depts.append([g(r,'FDID'),g(r,'Fire dept name'),g(r,'HQ city'),pa,co,g(r,'Dept Type'),n(g(r,'Number Of Stations')),n(g(r,'Active Firefighters - Career')),n(g(r,'Active Firefighters - Volunteer')),n(g(r,'Active Firefighters - Paid per Call')),k if k in cty else ''])
json.dump({'us':us,'states':st,'counties':cty},open(os.path.join(B,'data/econ.json'),'w'))
json.dump(depts,open(os.path.join(B,'data/depts.json'),'w'))
print(len(depts),'depts; county unmatched',miss,'; counties',len(cty),'; with pop',sum(1 for v in cty.values() if 'pop' in v)); print(us)
