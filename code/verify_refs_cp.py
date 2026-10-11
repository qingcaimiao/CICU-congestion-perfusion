# -*- coding: utf-8 -*-
"""参考文献双源核验：Europe PMC 命中 + Crossref 反查 DOI。
任何一条若两边不一致/查不到，一律标记为不可引用。"""
import urllib.request, urllib.parse, json, ssl, time, sys, os
ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
UA = {'User-Agent':'refcheck/2.0 (mailto:refs@example.org)'}

def epmc_by_doi(doi):
    u='https://www.ebi.ac.uk/europepmc/webservices/rest/search?'+urllib.parse.urlencode(
        {'query':'DOI:"%s"'%doi,'format':'json','pageSize':1,'resultType':'core'})
    try:
        with urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=45,context=ctx) as r:
            d=json.loads(r.read().decode('utf-8','ignore'))
        res=(d.get('resultList',{}) or {}).get('result',[])
        if not res: return None
        x=res[0]; j=(x.get('journalInfo',{}) or {}).get('journal',{}) or {}
        return {'title':x.get('title'),'journal':j.get('title'),'year':x.get('pubYear'),
                'authors':x.get('authorString'),'doi':x.get('doi'),'pmid':x.get('pmid')}
    except Exception as e:
        return {'err':str(e)[:60]}

def epmc_search(q):
    u='https://www.ebi.ac.uk/europepmc/webservices/rest/search?'+urllib.parse.urlencode(
        {'query':q,'format':'json','pageSize':3,'resultType':'core','sort':'CITED desc'})
    try:
        with urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=45,context=ctx) as r:
            d=json.loads(r.read().decode('utf-8','ignore'))
        out=[]
        for x in (d.get('resultList',{}) or {}).get('result',[]):
            j=(x.get('journalInfo',{}) or {}).get('journal',{}) or {}
            out.append({'title':x.get('title'),'journal':j.get('title'),'year':x.get('pubYear'),
                        'authors':x.get('authorString'),'doi':x.get('doi'),'pmid':x.get('pmid')})
        return out
    except Exception as e:
        return [{'err':str(e)[:60]}]

def crossref(doi):
    try:
        with urllib.request.urlopen(urllib.request.Request('https://api.crossref.org/works/'+urllib.parse.quote(doi),headers=UA),timeout=45,context=ctx) as r:
            m=json.loads(r.read().decode('utf-8','ignore'))['message']
        au=m.get('author') or []
        first = ('%s %s'%(au[0].get('family',''), au[0].get('given',''))).strip() if au else ''
        return {'title':(m.get('title') or [''])[0],'journal':(m.get('container-title') or [''])[0],
                'year':(m.get('issued',{}).get('date-parts',[[None]])[0][0]),'first_author':first,
                'volume':m.get('volume'),'page':m.get('page'),'doi':m.get('DOI')}
    except Exception as e:
        return {'err':str(e)[:60]}

# (标签, DOI 或 None, 检索式)
REFS = [
 ("MIMIC-IV", "10.1038/s41597-022-01899-x", None),
 ("eICU-CRD", "10.1038/sdata.2018.178", None),
 ("Nohria-Stevenson profiles", "10.1016/S0735-1097(02)82078-5", None),
 ("ANDROMEDA-SHOCK (CRT)", "10.1001/jama.2019.0071", None),
 ("TRIPOD+AI", "10.1136/bmj-2023-078378", None),
 ("Medicina 2026 congestion-perfusion", "10.3390/medicina62071422", None),
 ("HELP-HF congestion patterns", "10.2459/jcm.0000000000001907", None),
 ("ESC HF 2026 beyond warm and wet", "10.1093/eschf/xvag226", None),
 ("JAMA 2026 volume overload (Rational Clinical Exam)", "10.1001/jama.2026.0446", None),
 ("Gao 2025 CICU deterioration", "10.3389/fcvm.2025.1694001", None),
 ("Hu 2024 CShock", "10.1093/ehjacc/zuae037", None),
 ("Bohm 2025 STOP-SHOCK", "10.1093/ehjdh/ztaf002", None),
 ("PADS transportability", "10.3390/jcm15186957", None),
 ("CRT cross-database preprint", "10.64898/2026.09.29.26364303", None),
 ("CICU ML score (EHJ Digital Health)", None, 'TITLE:"machine learning score" AND TITLE:"cardiac intensive care"'),
 ("Heart failure pLOS model (EJCN 2025)", None, '"prolonged intensive care unit stay" AND "heart failure" AND "external validation"'),
 ("Nohria JAMA 2002 profiles", None, 'TITLE:"Medical management of advanced heart failure" AND AUTH:"Nohria"'),
 ("VExUS", None, 'TITLE:"venous excess ultrasound" OR TITLE:"VExUS"'),
 ("CRT septic shock review", None, 'TITLE:"capillary refill time" AND TITLE:"septic shock"'),
 ("CICU case mix / critical care cardiology", None, 'TITLE:"critical care cardiology" AND (TITLE:"organization" OR TITLE:"future" OR TITLE:"evolution")'),
 ("Diuretic response AHF", None, 'TITLE:"diuretic response" AND TITLE:"acute heart failure"'),
 ("Fluid balance ICU mortality", None, 'TITLE:"fluid balance" AND TITLE:"mortality" AND TITLE:"critically ill"'),
 ("Oedema prognosis heart failure", None, 'TITLE:"oedema" OR TITLE:"edema" AND TITLE:"heart failure" AND TITLE:"prognosis"'),
 ("Physical exam HF congestion", None, 'TITLE:"physical examination" AND TITLE:"heart failure" AND (TITLE:"congestion" OR TITLE:"prognosis")'),
]
out=[]
for label, doi, q in REFS:
    rec={'label':label}
    if doi:
        a=epmc_by_doi(doi); b=crossref(doi)
        rec['epmc']=a; rec['crossref']=b
        ok = bool(a and not a.get('err') and b and not b.get('err'))
        rec['status']='OK' if ok else 'CHECK'
    else:
        s=epmc_search(q) if q else []
        rec['epmc_candidates']=s[:3]
        if s and not s[0].get('err'):
            d0=s[0].get('doi'); b=crossref(d0) if d0 else {'err':'no doi'}
            rec['crossref']=b; rec['status']='OK' if (b and not b.get('err')) else 'CHECK'
        else:
            rec['status']='NOT FOUND'
    out.append(rec)
    print('='*98)
    print('[%s] %s' % (rec['status'], label))
    if doi:
        a=rec['epmc']; b=rec['crossref']
        print('  EPMC : %s | %s | %s | doi=%s' % ((a or {}).get('title','-')[:80] if a else '-', (a or {}).get('journal','-'), (a or {}).get('year','-'), (a or {}).get('doi','-')))
        print('  XREF : %s | %s | %s | doi=%s' % ((b or {}).get('title','-')[:80] if b else '-', (b or {}).get('journal','-'), (b or {}).get('year','-'), (b or {}).get('doi','-')))
        if a and b and not a.get('err') and not b.get('err'):
            t1=(a.get('title') or '').lower()[:45]; t2=(b.get('title') or '').lower()[:45]
            print('  title-match:', 'YES' if (t1[:30] in t2 or t2[:30] in t1) else '*** MISMATCH ***')
    else:
        for c in rec.get('epmc_candidates',[]):
            print('  EPMC : %s | %s | %s | doi=%s | pmid=%s' % ((c.get('title') or '')[:82], (c.get('journal') or '')[:26], c.get('year'), c.get('doi'), c.get('pmid')))
        b=rec.get('crossref') or {}
        print('  XREF : %s | %s | %s | doi=%s' % ((b.get('title') or '-')[:82], b.get('journal') or '-', b.get('year') or '-', b.get('doi') or '-'))
    time.sleep(0.4)
json.dump(out, open('D:/桌面/workbuddyzuopin/CPxiangmu/03_结果/refs_verified.json','w'), ensure_ascii=False, indent=1)
print('\nsaved -> refs_verified.json')
