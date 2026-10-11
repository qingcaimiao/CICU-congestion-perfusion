# -*- coding: utf-8 -*-
"""从 Crossref 抓取全作者名单 + 期刊缩写，生成 MDPI/JCM 格式参考文献（并再次核验 DOI）"""
import urllib.request, urllib.parse, json, ssl, time, re

ctx = ssl.create_default_context(); ctx.check_hostname = False; ctx.verify_mode = ssl.CERT_NONE
UA = {'User-Agent': 'mdpirefs/1.0 (mailto:refs@example.org)'}

# 稿件引用顺序（1..28）：doi 或特殊标记
REFS = [
    ('10.1161/CIR.0b013e31826890b0', None),
    ('10.1016/j.jacc.2016.04.036', None),
    ('10.1001/jama.287.5.628', None),
    ('10.1161/CIRCULATIONAHA.119.039920', None),
    ('10.1161/CIRCHEARTFAILURE.121.008403', None),
    ('10.1001/jama.2026.0446', None),
    ('10.1007/s00134-014-3326-4', None),
    ('10.1001/jama.2019.0071', None),
    ('10.1186/s13089-020-00163-w', None),
    ('10.1513/AnnalsATS.201511-737OC', None),
    ('10.3390/medicina62071422', None),
    ('10.2459/JCM.0000000000001907', None),
    ('10.1093/eschf/xvag226', None),
    ('10.1093/eurjcn/zvae181', None),
    ('10.1038/s41597-022-01899-x', None),
    ('10.1038/sdata.2018.178', None),
    ('10.1136/bmj-2023-078378', None),
    ('10.64898/2026.09.29.26364303', None),
    ('10.1093/ehjdh/ztae098', None),
    ('10.3389/fcvm.2025.1694001', None),
    ('10.1093/ehjacc/zuae037', None),
    ('10.3390/jcm15186957', None),
    ('10.1093/eurjcn/zvaf075', None),
    ('10.1093/eurheartj/ehu065', None),
    ('10.1186/s13054-015-1085-4', None),
    ('10.1093/ehjdh/ztaf002', None),
    ('10.1038/s41598-026-46063-2', None),
    ('10.5281/zenodo.22674523', 'DataCite'),
]

def cr(doi):
    u = 'https://api.crossref.org/works/' + urllib.parse.quote(doi)
    with urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=50, context=ctx) as r:
        return json.loads(r.read().decode('utf-8', 'ignore'))['message']

def dc(doi):
    u = 'https://api.datacite.org/dois/' + urllib.parse.quote(doi)
    with urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=50, context=ctx) as r:
        return json.loads(r.read().decode('utf-8', 'ignore'))['data']['attributes']

def initials(given):
    """'Alistair E. W.' -> 'A.E.W.'"""
    parts = re.split(r'[\s\-]+', (given or '').strip())
    return ''.join(p[0].upper() + '.' for p in parts if p)

def authors_mdpi(author_list):
    out = []
    for a in author_list:
        fam = (a.get('family') or '').strip()
        giv = (a.get('given') or '').strip()
        if fam and giv:
            out.append('%s, %s' % (fam, initials(giv)))
        elif fam:
            out.append(fam)
        elif a.get('name'):
            out.append(a['name'])
    return out

def fmt_pages(m):
    p = m.get('page'); art = m.get('article-number')
    if p: return p.replace('-', '\u2013')
    if art: return art
    return None

lines = []
report = []
for i, (doi, kind) in enumerate(REFS, 1):
    try:
        if kind == 'DataCite':
            a = dc(doi)
            ttl = (a.get('titles') or [{}])[0].get('title', '')
            year = (a.get('publicationYear') or '')
            publisher = a.get('publisher', 'Zenodo')
            au = [{'family': c.get('name', '').split(',')[0].strip(),
                   'given': (c.get('name', '').split(',')[1].strip() if ',' in c.get('name', '') else '')}
                  for c in (a.get('creators') or [])]
            au_s = authors_mdpi(au)
            # DataCite 元数据只登记部分作者；补全作者名单（来自存档描述）
            full = 'Hao, Y.; Qin, L.; Zhang, Q.; Chen, S.; Li, P.; Wan, J.; Ye, H.'
            s = '%s %s (v1.2.1) [Data set]. %s, %s. https://doi.org/%s' % (full, ttl, publisher, year, doi)
            lines.append('%d. %s' % (i, s))
            report.append(('OK-DataCite', doi, ttl[:70]))
        else:
            m = cr(doi)
            au = authors_mdpi(m.get('author') or [])
            au_s = '; '.join(au[:10]) + (', et al.' if len(au) > 10 else '')
            ttl = (m.get('title') or [''])[0]
            ttl = re.sub(r'\s+', ' ', ttl).strip()
            jrn = (m.get('short-container-title') or m.get('container-title') or [''])[0]
            jrn = jrn.strip()
            yr = m.get('issued', {}).get('date-parts', [[None]])[0][0]
            vol = m.get('volume')
            pg = fmt_pages(m)
            bits = ['%s %s.' % (au_s, ttl)]
            tail = '%s %s' % (jrn, yr)
            if vol:
                tail += ', %s' % vol
            if pg:
                tail += ', %s' % pg
            tail += '.'
            s = '%s %s https://doi.org/%s' % (bits[0], tail, doi)
            lines.append('%d. %s' % (i, s))
            report.append(('OK', doi, '%s | %s | vol %s | p %s | yr %s | authors %d' % (jrn[:38], ttl[:44], vol, pg, yr, len(au))))
    except Exception as e:
        lines.append('%d. [FAILED] doi:%s (%s)' % (i, doi, str(e)[:60]))
        report.append(('FAIL', doi, str(e)[:90]))
    time.sleep(0.35)

print('==== 核验报告 ====')
for st, doi, info in report:
    print('%-12s %-42s %s' % (st, doi, info))
print()
print('==== MDPI 格式参考文献 ====')
for l in lines:
    print(l)
json.dump(lines, open('mdpi_refs.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('\nsaved -> mdpi_refs.json')
