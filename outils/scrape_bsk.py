#!/usr/bin/env python3
"""Lit la page BSK de Julien avec Playwright et met à jour annonces.json. N'écrit rien si la lecture échoue."""
import json,re,sys,os
from playwright.sync_api import sync_playwright
R=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
URL='https://bskimmobilier.com/julien-sabatier-7852/biens'
JS=r"""()=>{const res={};document.querySelectorAll('a[href*="/bien/"]').forEach(a=>{const id=(a.href.match(/\/(\d+)\?/)||[])[1];if(!id||res[id])return;let c=a;while(c.parentElement&&new Set([...c.parentElement.querySelectorAll('a[href*="/bien/"]')].map(x=>x.href)).size==1)c=c.parentElement;const im=c.querySelector('img[src*="cloudfront"],img[data-src*="cloudfront"]');res[id]={url:a.href,text:c.innerText.replace(/\s+/g,' '),img:im?(im.currentSrc||im.src||im.dataset.src):''}});return res}"""
def main():
    with sync_playwright() as p:
        b=p.chromium.launch();pg=b.new_page(viewport={'width':1300,'height':900})
        pg.goto(URL,wait_until='networkidle',timeout=60000)
        for _ in range(25):
            pg.mouse.wheel(0,1200);pg.wait_for_timeout(400)
        d=pg.evaluate(JS);b.close()
    if len(d)<10:sys.exit('lecture insuffisante: %d annonces'%len(d))
    old={a['id']:a for a in json.load(open(R+'/annonces.json',encoding='utf-8'))}
    out=[]
    for i,v in d.items():
        i=int(i);t=v['text']
        m=re.search(r'/bien/([^/]+)/([^/]+)/',v['url']);com_slug,ty=m.group(1),m.group(2)
        st=(re.findall(r'Sous offre|Sous compromis|À saisir|Nouveauté|Investisseur|Coup de coeur',t) or [''])[0]
        pr=re.search(r'(\d[\d\s  ]*)\s*€',t)
        prix=int(re.sub(r'\D','',pr.group(1))) if pr else old.get(i,{}).get('prix')
        if i in old: a=dict(old[i]);a.update(statut=st,prix=prix,url=v['url'])
        else:
            sm=re.search(r'(\d[\d\s]*)\s*m²',t)
            a=dict(id=i,commune=com_slug.replace('-',' ').title().replace(' Sur ','-sur-'),cp='',type=ty.split('-de-')[0].capitalize(),surface=int(re.sub(r'\D','',sm.group(1))) if sm else 0,pieces=None,chambres=None,terrain=None,prix=prix,statut=st,url=v['url'],img='')
        if v['img'] and 'default/ad.png' not in v['img']:a['img']=v['img']
        if not a.get('prix') or not a.get('img'):continue
        out.append(a)
    if len(out)<10:sys.exit('trop peu d\'annonces valides')
    json.dump(out,open(R+'/annonces.json','w',encoding='utf-8'),ensure_ascii=False,indent=1);print(len(out),'annonces')
main()
