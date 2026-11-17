#!/usr/bin/env python3
"""Réécrit uniquement les blocs <section id="biens"> à partir de annonces.json."""
import json,re,html,os
R=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
A=json.load(open(os.path.join(R,'annonces.json'),encoding='utf-8'))
SLUG={'Rouillé':'rouille','Lusignan':'lusignan','Saint-Sauvant':'saint-sauvant','Curzay-sur-Vonne':'curzay-sur-vonne','Jazeneuil':'jazeneuil','Sanxay':'sanxay','Pamproux':'pamproux','Ménigoute':'menigoute'}
def eur(n):return f"{n:,}".replace(',',' ')+' €'
def titre(a):
    t=a['type']
    if a['surface'] and t!='Terrain':
        s=f"{t} de {a['surface']} m²"
    elif t=='Terrain': s=f"Terrain de {a['surface']:,} m²".replace(',',' ')
    else: s=t
    return s
def detail(a):
    d=[]
    if a.get('pieces'):d.append(f"{a['pieces']} pièces")
    if a.get('chambres'):d.append(f"{a['chambres']} ch.")
    if a.get('terrain') and a['type']!='Terrain':d.append(f"terrain {a['terrain']}")
    return ' · '.join(d)
FAINT={'Sous offre','Sous compromis'}
def card(a):
    st=a['statut']; dim=st in FAINT
    badge=f'<span style="position:absolute;top:12px;left:12px;background:{"#1E3A5F" if dim else "#C9A84C"};color:{"#fff" if dim else "#1E3A5F"};font-size:12px;font-weight:600;padding:4px 10px;border-radius:999px">{html.escape(st)}</span>' if st else ''
    de=detail(a)
    return (f'<article style="background:#F7F4EC;border-radius:10px;overflow:hidden;display:flex;flex-direction:column{";opacity:.8" if dim else ""}">'
     f'<div style="position:relative"><img src="{a["img"]}" alt="{html.escape(titre(a))} à {html.escape(a["commune"])}" loading="lazy" referrerpolicy="no-referrer" onerror="this.onerror=null;this.src=\'assets/banniere.jpg\'" style="width:100%;height:210px;object-fit:cover;display:block">{badge}</div>'
     f'<div style="padding:20px;display:flex;flex-direction:column;gap:8px"><span style="font-size:12px;letter-spacing:.1em;text-transform:uppercase;color:#8A6D1F;font-weight:600">{html.escape(a["commune"])}</span>'
     f'<h3 style="font-size:22px">{html.escape(titre(a))}</h3>'
     +(f'<span style="font-size:14px;color:#555">{de}</span>' if de else '')+
     f'<span style="font-size:24px;font-weight:600">{eur(a["prix"])}</span>'
     f'<a href="{a["url"]}" target="_blank" rel="noopener" style="font-weight:600">Voir l\'annonce sur BSK</a></div></article>')
def tri(L):return sorted(L,key=lambda a:(a['statut'] in FAINT,))
GRID='<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:28px">'
def section(title,L,empty=None):
    if L: body=''.join(card(a) for a in tri(L))
    else: body=empty
    return (f'<section id="biens" style="background:#fff;padding:56px 48px"><div style="max-width:1280px;margin:0 auto;display:flex;flex-direction:column;gap:28px"><h2 style="font-size:34px">{title}</h2>{GRID}{body}</div></div></section>')
def patch(path,new):
    s=open(path,encoding='utf-8').read()
    n,k=re.subn(r'<section id="biens".*?</section>',lambda m:new,s,count=1,flags=re.S)
    assert k==1,path
    open(path,'w',encoding='utf-8').write(n)
idx=section('Mes biens à vendre',A).replace('<h2 style="font-size:34px">Mes biens à vendre</h2>','<div style="display:flex;flex-wrap:wrap;justify-content:space-between;align-items:flex-end;gap:16px"><div><h2 style="font-size:38px">Mes biens à vendre</h2><p style="margin:8px 0 0;color:#4A5C73;font-size:16px">Annonces synchronisées avec ma page BSK. Chaque fiche renvoie vers l\'annonce complète.</p></div><a href="https://bskimmobilier.com/julien-sabatier-7852/biens" style="font-weight:600;border-bottom:2px solid #C9A84C;padding-bottom:2px">Tous mes biens sur BSK</a></div>')
patch(os.path.join(R,'index.html'),idx)
for com,sl in SLUG.items():
    p=os.path.join(R,sl+'.html')
    if not os.path.exists(p):continue
    L=[a for a in A if a['commune']==com]
    wa=f'https://wa.me/33630389267?text='+f'Bonjour Julien, je cherche un bien à {com}'.replace(' ','%20')
    empty=f'<div style="background:#F7F4EC;border-radius:10px;padding:28px;grid-column:1/-1"><h3 style="font-size:22px">Pas de bien affiché à {com} pour le moment</h3><p style="margin:10px 0 16px">Dites-moi ce que vous cherchez, je vous préviens dès qu\'un bien correspond.</p><a href="{wa}" style="font-weight:600">Me contacter sur WhatsApp</a></div>'
    patch(p,section(f'Mes biens à {com}',L,empty))
print('ok')
