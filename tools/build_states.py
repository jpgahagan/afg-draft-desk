import re, json, os, html
B=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
s=open(os.path.join(B,'public/index.html')).read()
arr=re.search(r'var G=(\[.*?\]\]);',s,re.S).group(1)
G=json.loads(arr)
head=s[:s.index('</head>')]
style=re.search(r'<style>.*?</style>',s,re.S).group(0)
fonts="\n".join(re.findall(r'<link[^>]+>',head))
MON=['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
def fmt(d):
    if d=='rolling':return 'Rolling'
    if d=='tbd':return 'Date to confirm'
    y,m,dd=d.split('-');return f"{MON[int(m)-1]} {int(dd)}, {y}"
SITE='https://backdraft.pplx.app'
TRACK0="<script>try{var v=Math.random().toString(36).slice(2);fetch('/port/5001/api/event',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({kind:'view',src:'SLUG',page:location.pathname,vid:v})}).catch(function(){})}catch(e){}</script>"
states=sorted(set(g[1] for g in G))
os.makedirs(os.path.join(B,'public/states'),exist_ok=True)
urls=[SITE+'/']
for st in states:
    slug=st.lower().replace(' ','-')
    TRACK=TRACK0.replace('SLUG','state_'+slug)
    rows="".join(f'<tr><td class="due">{fmt(g[0])}</td><td><a href="{html.escape(g[4])}" target="_blank" rel="noopener">{html.escape(g[2])}</a></td><td>{html.escape(g[3])}</td></tr>' for g in G if g[1]==st)
    n=sum(1 for g in G if g[1]==st)
    title=f"{st} Fire Department Grant Deadlines 2026–27 | Backdraft Grants"
    desc=f"{n} current {st} grant program{'s' if n>1 else ''} for volunteer and rural fire departments, with deadlines and official links, plus help with federal AFG narratives."
    page=f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<script>if(location.hostname==='afgdrafts.pplx.app')location.replace('https://backdraft.pplx.app'+location.pathname+location.search+location.hash);</script><title>{title}</title><meta name="description" content="{desc}"><link rel="canonical" href="{SITE}/states/{slug}.html">
{fonts}
{style}</head><body>
<header class="wrap" style="padding:20px 0"><a href="/?src=state_{slug}" style="font-weight:700;text-decoration:none;color:inherit">Backdraft Grants</a></header>
<main class="wrap">
<section><h1 style="font-size:clamp(30px,5vw,46px);line-height:1.1;margin:10px 0 14px">{st} fire department grant deadlines, 2026–27</h1>
<p class="muted">Grant programs open to volunteer and rural fire departments in {st}, checked on each agency's official page on November 24, 2026. Confirm dates on the official page before applying.</p>
<table class="gt"><thead><tr><th>Due</th><th>Program</th><th>Amount and match</th></tr></thead><tbody>{rows}</tbody></table></section>
<section><h2>The federal grant most {st} departments also apply for</h2>
<p>The Assistance to Firefighters Grant (AFG) from FEMA is the largest federal grant for fire departments. In the FY2025 round FEMA received 8,426 applications for about 1,800 awards, and the four written narratives carry much of the score.</p>
<p>Backdraft Grants drafts all four AFG narratives from your department's own figures for a flat $249. Reserving holds a spot for the FY2026 window and costs nothing today.</p>
<p><a class="btn" href="/?src=state_{slug}#reserve">Reserve an AFG draft, pay nothing today</a></p>
<p class="note"><a href="/?src=state_{slug}#state">See deadlines for all states</a></p></section>
</main>
<footer class="wrap note" style="padding:30px 0">Run by Joseph Gahagan, 1390 Chain Bridge Rd #10140, McLean, VA 22101. Not affiliated with FEMA or any state agency.</footer>
<div class="stk on"><span class="stk-t">Free grant draft for your department</span><a class="btn" href="/?src=state_{slug}#draft">Start my free draft</a></div>
{TRACK}
</body></html>'''
    open(os.path.join(B,f'public/states/{slug}.html'),'w').write(page)
    urls.append(f"{SITE}/states/{slug}.html")
open(os.path.join(B,'public/sitemap.xml'),'w').write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'+"".join(f"<url><loc>{u}</loc><lastmod>2026-11-24</lastmod></url>\n" for u in urls)+'</urlset>\n')
open(os.path.join(B,'public/robots.txt'),'w').write(f"User-agent: *\nAllow: /\nSitemap: {SITE}/sitemap.xml\n")
links=" · ".join(f'<a href="/states/{x.lower().replace(" ","-")}.html">{x}</a>' for x in states)
p2=os.path.join(B,'public/index.html');t=open(p2).read()
t=re.sub(r'  <p class="note" id="stlinks"[^>]*>.*?</p>\n',' ',t,flags=re.S).replace('</tbody></table>\n \n','</tbody></table>\n')
t=t.replace('</tbody></table>\n','</tbody></table>\n  <p class="note" id="stlinks" style="margin-top:12px">State pages: '+links+'</p>\n',1)
open(p2,'w').write(t)
print(len(urls))
