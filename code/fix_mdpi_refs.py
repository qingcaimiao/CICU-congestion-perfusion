# -*- coding: utf-8 -*-
"""修正并定稿 MDPI 参考文献：期刊缩写、作者粘连、版本号重复、Gao 年份"""
import urllib.request, urllib.parse, json, ssl, re, time

ctx = ssl.create_default_context(); ctx.check_hostname = False; ctx.verify_mode = ssl.CERT_NONE
UA = {'User-Agent': 'refs/2.0 (mailto:a@b.org)'}

# --- 核查 Gao 年份与 ref18 类型 ---
def epmc(q):
    u = 'https://www.ebi.ac.uk/europepmc/webservices/rest/search?' + urllib.parse.urlencode(
        {'query': q, 'format': 'json', 'pageSize': 2, 'resultType': 'core'})
    with urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=50, context=ctx) as r:
        return json.loads(r.read().decode('utf-8', 'ignore'))

d = epmc('DOI:"10.3389/fcvm.2025.1694001"')
for x in (d.get('resultList', {}) or {}).get('result', []):
    j = (x.get('journalInfo', {}) or {})
    print('GAO ->', 'pubYear:', x.get('pubYear'), '| firstPublicationDate:', x.get('firstPublicationDate'),
          '| journalIssue:', (j.get('journal', {}) or {}).get('title'), '| volume:', j.get('volume'),
          '| yearOfPublication:', j.get('yearOfPublication'), '| printPubDate:', j.get('printPublicationDate'))

with urllib.request.urlopen(urllib.request.Request(
        'https://api.crossref.org/works/' + urllib.parse.quote('10.64898/2026.09.29.26364303'), headers=UA),
        timeout=50, context=ctx) as r:
    m = json.loads(r.read().decode('utf-8', 'ignore'))['message']
print('REF18 type:', m.get('type'), '| container:', m.get('container-title'),
      '| institution:', m.get('institution'), '| publisher:', m.get('publisher'),
      '| issued:', m.get('issued'), '| posted:', m.get('posted'))

# --- 期刊缩写映射 ---
ABBR = {
    'Journal of the American College of Cardiology': 'J. Am. Coll. Cardiol.',
    'Annals of the American Thoracic Society': 'Ann. Am. Thorac. Soc.',
    'Journal of Cardiovascular Medicine': 'J. Cardiovasc. Med.',
    'European Journal of Cardiovascular Nursing': 'Eur. J. Cardiovasc. Nurs.',
    'European Heart Journal': 'Eur. Heart J.',
    'European Heart Journal - Digital Health': 'Eur. Heart J. Digit. Health',
    'European Heart Journal: Acute Cardiovascular Care': 'Eur. Heart J. Acute Cardiovasc. Care',
    'Intensive Care Med': 'Intensive Care Med.',
    'Ultrasound J': 'Ultrasound J.',
    'ESC Heart Failure': 'ESC Heart Fail.',
    'Sci Data': 'Sci. Data',
    'Crit Care': 'Crit. Care',
    'Sci Rep': 'Sci. Rep.',
    'Circ: Heart Failure': 'Circ. Heart Fail.',
    'Front. Cardiovasc. Med.': 'Front. Cardiovasc. Med.',
    'J. Clin. Med.': 'J. Clin. Med.',
    'Circulation': 'Circulation',
    'JAMA': 'JAMA',
    'BMJ': 'BMJ',
    'Medicina': 'Medicina',
}

lines = json.load(open('mdpi_refs.json', encoding='utf-8'))
fixed = []
for l in lines:
    n = int(re.match(r'(\d+)\.', l).group(1))
    s = l
    # 期刊缩写
    for full, ab in ABBR.items():
        if full != ab:
            s = re.sub(r'(?<=\.\s)' + re.escape(full) + r'(?= \d{4})', ab, s)
    # Ref 25 工作组粘连
    if n == 25:
        s = s.replace('Xi, X.M.; The Beijing Acute Kidney Injury Trial (BAKIT) Workgroup Fluid',
                      'Xi, X.M.; The Beijing Acute Kidney Injury Trial (BAKIT) Workgroup. Fluid')
    # Ref 28 重复版本号
    if n == 28:
        s = s.replace('(v1.2.1) (v1.2.1)', '(v1.2.1)')
    # Ref 18 预印本补服务器
    if n == 18:
        s = s.replace('A Methodological Analysis.  2026.',
                      'A Methodological Analysis. Preprints 2026.')
        s = s.rstrip() + ' (preprint; not peer reviewed)'
    # Ref 20 Gao 年份按 DOI/卷期统一为 2025
    if n == 20:
        s = s.replace('Front. Cardiovasc. Med. 2026,', 'Front. Cardiovasc. Med. 2025,')
    fixed.append(s)

print()
print('==== 定稿 MDPI 参考文献 ====')
for l in fixed:
    print(l)
json.dump(fixed, open('mdpi_refs_final.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('\nsaved -> mdpi_refs_final.json | count', len(fixed))
