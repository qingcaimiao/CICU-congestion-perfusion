# -*- coding: utf-8 -*-
"""最终参考文献表：逐条取 Crossref 权威元数据（作者/卷/页），并补验 pLOS 一篇"""
import urllib.request, urllib.parse, json, ssl, time
ctx=ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
UA={'User-Agent':'refcheck/2.0 (mailto:refs@example.org)'}
def crossref(doi):
    try:
        with urllib.request.urlopen(urllib.request.Request('https://api.crossref.org/works/'+urllib.parse.quote(doi),headers=UA),timeout=45,context=ctx) as r:
            return json.loads(r.read().decode('utf-8','ignore'))['message']
    except Exception as e: return {'err':str(e)[:70]}
def epmc_doi(doi):
    u='https://www.ebi.ac.uk/europepmc/webservices/rest/search?'+urllib.parse.urlencode({'query':'DOI:"%s"'%doi,'format':'json','pageSize':1,'resultType':'core'})
    try:
        with urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=45,context=ctx) as r:
            d=json.loads(r.read().decode('utf-8','ignore'))
        res=(d.get('resultList',{}) or {}).get('result',[])
        return res[0] if res else None
    except Exception as e: return None
def fmt(doi):
    m=crossref(doi); e=epmc_doi(doi)
    if m.get('err') and not e: return doi, 'NOT FOUND', ''
    au=m.get('author') or []
    names=[]
    for a in au[:6]:
        fam=a.get('family',''); giv=''.join([x[0] for x in (a.get('given') or '').replace('-',' ').split() if x])
        if fam: names.append('%s %s'%(fam,giv))
    astr=', '.join(names)+(' et al.' if len(au)>6 else '')
    title=(m.get('title') or [e.get('title') if e else ''])[0].rstrip('.')
    jrn=(m.get('container-title') or [''])[0] or ((e.get('journalInfo',{}) or {}).get('journal',{}) or {}).get('title','')
    yr=(m.get('issued',{}).get('date-parts',[[None]])[0][0]) or (e.get('pubYear') if e else None)
    vol=m.get('volume') or ''; pg=m.get('page') or ''
    pmid=(e or {}).get('pmid','')
    cite='%s. %s. %s. %s;%s:%s. doi:%s%s' % (astr, title, jrn, yr, vol, pg, doi, (' PMID:%s'%pmid) if pmid else '')
    return doi, cite, title
DOIS=[
 ('MIMIC-IV','10.1038/s41597-022-01899-x'),
 ('eICU','10.1038/sdata.2018.178'),
 ('Nohria 2002','10.1001/jama.287.5.628'),
 ('Circ 2019 PE congestion','10.1161/circulationaha.119.039920'),
 ('CircHF 2021 PE trends','10.1161/circheartfailure.121.008403'),
 ('JAMA 2026 volume overload','10.1001/jama.2026.0446'),
 ('Medicina 2026 C-P','10.3390/medicina62071422'),
 ('HELP-HF 2026','10.2459/jcm.0000000000001907'),
 ('ESC HF 2026','10.1093/eschf/xvag226'),
 ('CRT ICM 2014','10.1007/s00134-014-3326-4'),
 ('ANDROMEDA JAMA 2019','10.1001/jama.2019.0071'),
 ('VExUS USJ 2020','10.1186/s13089-020-00163-w'),
 ('Gao 2025','10.3389/fcvm.2025.1694001'),
 ('Hu 2024','10.1093/ehjacc/zuae037'),
 ('Bohm 2025','10.1093/ehjdh/ztaf002'),
 ('PADS 2026','10.3390/jcm15186957'),
 ('CICU ML score','10.1093/ehjdh/ztae098'),
 ('CRT preprint','10.64898/2026.09.29.26364303'),
 ('CCM evolution 2012','10.1161/cir.0b013e31826890b0'),
 ('CCM future 2016','10.1016/j.jacc.2016.04.036'),
 ('Diuretic response 2014','10.1093/eurheartj/ehu065'),
 ('Fluid balance 2015','10.1186/s13054-015-1085-4'),
 ('TRIPOD+AI 2024','10.1136/bmj-2023-078378'),
 ('pLOS HF EJCN 2025','10.1093/eurjcn/zvaf075'),
]
out={}
for lab,doi in DOIS:
    _,cite,title=fmt(doi)
    out[lab]={'doi':doi,'title':title,'citation':cite}
    print('[%s]\n  %s\n' % (lab, cite))
    time.sleep(0.35)
json.dump(out, open('D:/桌面/workbuddyzuopin/CPxiangmu/03_结果/refs_final.json','w'), ensure_ascii=False, indent=1)
print('saved -> refs_final.json  (n=%d)'%len(out))
