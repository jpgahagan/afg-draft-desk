import re, json, os, html, datetime

B = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
s = open(os.path.join(B, 'public/index.html')).read()
arr = re.search(r'var G=(\[.*?\]\]);', s, re.S).group(1)
G = json.loads(arr)
head = s[:s.index('</head>')]
style = re.search(r'<style>.*?</style>', s, re.S).group(0)
# Never copy index.html's canonical link into child pages!
fonts = "\n".join(x for x in re.findall(r'<link[^>]+>', head) if 'canonical' not in x.lower())

TODAY = datetime.date.today().isoformat()
MON = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
def fmt(d):
    if d == 'rolling': return 'Rolling'
    if d == 'tbd': return 'Date to confirm'
    y, m, dd = d.split('-')
    return f"{MON[int(m)-1]} {int(dd)}, {y}"

SITE = 'https://backdraftgrants.com'
CF_REDIRECT = "<script>if(/\\.pplx\\.app$/.test(location.hostname))fetch('https://backdraftgrants.com/__cf',{cache:'no-store',redirect:'error'}).then(function(r){return r.text()}).then(function(t){if(t.trim()==='backdraft-cf')location.replace('https://backdraftgrants.com'+location.pathname+location.search+location.hash)}).catch(function(){});</script>"
TRACK0 = "<script>try{if(!localStorage.getItem('bdg_admin_key')){var v=Math.random().toString(36).slice(2);fetch('/port/5001/api/event',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({kind:'view',src:'SLUG',page:location.pathname,vid:v})}).catch(function(){})}}catch(e){}</script>"

GUIDES_NAV = (
    '<nav class="footlinks" aria-label="Grant guides" style="margin-bottom:10px">'
    f'<a href="{SITE}/guides/afg-grant-narrative-template.html">AFG Narrative Template</a>'
    f'<a href="{SITE}/guides/afg-2026-deadline-checklist.html">AFG 2026–27 Deadlines &amp; Checklist</a>'
    f'<a href="{SITE}/guides/fire-department-equipment-grants.html">Turnout Gear, SCBA &amp; Truck Grants</a>'
    f'<a href="{SITE}/guides/safer-grant-narrative-guide.html">SAFER Grant Guide</a>'
    f'<a href="{SITE}/guides/volunteer-fire-department-grants.html">All 50 State Fire Grants</a>'
    '</nav>'
)

FOOT = (
    '<footer class="wrap note sitefoot" style="padding-top:30px;padding-bottom:30px">'
    + GUIDES_NAV +
    '<nav class="footlinks" aria-label="Legal and contact">'
    f'<a href="{SITE}/privacy.html">Privacy Policy</a><a href="{SITE}/terms.html">Terms of Service</a>'
    f'<a href="{SITE}/terms.html#disclaimer">Grant disclaimer</a><a href="mailto:hello@backdraftgrants.com">hello@backdraftgrants.com</a></nav>'
    '<p style="margin:10px 0 0">Backdraft Grants is run by Joseph Gahagan, 1390 Chain Bridge Rd #10140, McLean, VA 22101. '
    'Independent service. Not affiliated with FEMA, the U.S. Fire Administration or any state agency. Grant funding is never guaranteed.</p></footer>'
)

FOOTCSS = (
    '<style>.footlinks{display:flex;flex-wrap:wrap;gap:8px 20px}.footlinks a{color:inherit;text-decoration:underline;text-underline-offset:2px}'
    '.legal{max-width:780px;padding-bottom:20px}.legal h1{font:800 clamp(30px,5vw,46px)/1.1 "Archivo",sans-serif;margin:24px 0 6px}'
    '.legal h2{font-size:clamp(21px,2.4vw,26px);margin:34px 0 10px}.legal h3{font-size:17px;margin:20px 0 6px}'
    '.legal li{margin:6px 0}.legal ul,.legal ol{padding-left:22px}.legal .legal-key{margin:26px 0}.legal .legal-key ul{margin-bottom:0}'
    '.legal p,.legal li{font-size:16px;line-height:1.6}.skip{position:absolute;left:-9999px}.skip:focus{left:12px;top:12px;background:#fff;padding:8px 12px;z-index:9}'
    '.stgrid{display:grid;grid-template-columns:repeat(auto-fill,minmax(175px,1fr));gap:8px 14px;margin:18px 0}'
    '.stgrid a{display:block;padding:8px 10px;background:#fff;border:1px solid var(--line);border-radius:8px;text-decoration:none;color:var(--ink);font-size:15px}'
    '.stgrid a:hover{border-color:var(--accent);color:var(--accent)}'
    '.gbox{background:#fff;border:1px solid var(--line);border-left:4px solid var(--accent);border-radius:10px;padding:18px 20px;margin:20px 0}</style>'
)

def og_tags(title, desc, url, kind='article', keywords=''):
    t = html.escape(title, quote=True)
    d = html.escape(desc, quote=True)
    kw = f'<meta name="keywords" content="{html.escape(keywords, quote=True)}">' if keywords else ''
    return (
        kw
        + '<meta name="robots" content="index, follow, max-snippet:-1, max-image-preview:large, max-video-preview:-1">'
        + '<meta name="author" content="Backdraft Grants">'
        + '<meta name="theme-color" content="#a3271c">'
        + f'<meta property="og:type" content="{kind}">'
        + '<meta property="og:locale" content="en_US">'
        + '<meta property="og:site_name" content="Backdraft Grants">'
        + f'<meta property="og:title" content="{t}">'
        + f'<meta property="og:description" content="{d}">'
        + f'<meta property="og:url" content="{url}">'
        + f'<meta property="og:image" content="{SITE}/og-card.png">'
        + '<meta property="og:image:width" content="1200">'
        + '<meta property="og:image:height" content="630">'
        + f'<meta property="article:modified_time" content="{TODAY}">'
        + '<meta name="twitter:card" content="summary_large_image">'
        + f'<meta name="twitter:title" content="{t}">'
        + f'<meta name="twitter:description" content="{d}">'
        + f'<meta name="twitter:image" content="{SITE}/og-card.png">'
    )

states = sorted(set(g[1] for g in G))
os.makedirs(os.path.join(B, 'public/states'), exist_ok=True)
os.makedirs(os.path.join(B, 'public/guides'), exist_ok=True)

sitemap_entries = [(SITE + '/', '1.0', 'weekly')]

# 1. Build all 50 state grant deadline pages
for idx, st in enumerate(states):
    slug = st.lower().replace(' ', '-')
    url = f"{SITE}/states/{slug}.html"
    TRACK = TRACK0.replace('SLUG', 'state_' + slug)
    st_grants = [g for g in G if g[1] == st]
    rows = "".join(
        f'<tr><td class="due">{fmt(g[0])}</td><td><a href="{html.escape(g[4])}" target="_blank" rel="noopener">{html.escape(g[2])}</a></td><td>{html.escape(g[3])}</td></tr>'
        for g in st_grants
    )
    n = len(st_grants)
    prog_names = ", ".join(g[2] for g in st_grants[:4])
    title = f"{st} Volunteer Fire Department Grants & Deadlines (2026–27) | Backdraft Grants"
    desc = f"{n} current {st} fire department grant program{'s' if n > 1 else ''} for turnout gear, SCBA, radios, and rural fire equipment, with 2026–27 deadlines, official links, and free FEMA AFG narrative drafts."
    st_keywords = f"{st} volunteer fire department grants, {st} fire department grants 2026 2027, {st} rural fire grants, {prog_names}, FEMA AFG grant {st}, turnout gear grant, SCBA grant"
    # Nearby alphabetical states for crawlable internal linking
    neighbors = [states[(idx - 2) % len(states)], states[(idx - 1) % len(states)], states[(idx + 1) % len(states)], states[(idx + 2) % len(states)]]
    neighbor_links = " · ".join(f'<a href="{SITE}/states/{x.lower().replace(" ", "-")}.html">{html.escape(x)}</a>' for x in neighbors)

    ld = {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "BreadcrumbList",
                "itemListElement": [
                    {"@type": "ListItem", "position": 1, "name": "Backdraft Grants", "item": SITE + "/"},
                    {"@type": "ListItem", "position": 2, "name": "All 50 State Fire Grants", "item": SITE + "/guides/volunteer-fire-department-grants.html"},
                    {"@type": "ListItem", "position": 3, "name": f"{st} Fire Department Grants", "item": url},
                ],
            },
            {
                "@type": "WebPage",
                "name": title,
                "description": desc,
                "url": url,
                "dateModified": TODAY,
                "publisher": {"@type": "Organization", "name": "Backdraft Grants", "url": SITE},
            },
            {
                "@type": "FAQPage",
                "mainEntity": [
                    {
                        "@type": "Question",
                        "name": f"What fire department grants are available in {st} for 2026–27?",
                        "acceptedAnswer": {
                            "@type": "Answer",
                            "text": f"Volunteer and rural fire departments in {st} can apply to {n} tracked state grant program{'s' if n > 1 else ''} plus federal FEMA AFG, SAFER, and FP&S grants.",
                        },
                    },
                    {
                        "@type": "Question",
                        "name": f"Can {st} volunteer fire departments apply for FEMA AFG grants?",
                        "acceptedAnswer": {
                            "@type": "Answer",
                            "text": f"Yes. Eligible volunteer, combination, and career fire departments in {st} can apply for FEMA Assistance to Firefighters Grants (AFG) through FEMA GO with an active SAM.gov registration and UEI.",
                        },
                    },
                ],
            },
        ],
    }

    page = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
{CF_REDIRECT}<title>{html.escape(title)}</title><meta name="description" content="{html.escape(desc, quote=True)}"><link rel="canonical" href="{url}">
{og_tags(title, desc, url, 'article', st_keywords)}
<script type="application/ld+json">{json.dumps(ld, separators=(',', ':'))}</script>
{fonts}
{style}{FOOTCSS}</head><body>
<header class="wrap" style="padding:20px 0;display:flex;justify-content:space-between;align-items:center;gap:12px"><a href="{SITE}/?src=state_{slug}" style="font-weight:700;text-decoration:none;color:inherit">Backdraft Grants</a><a class="navcta" href="{SITE}/?src=state_{slug}#draft">Start free AFG draft</a></header>
<main class="wrap">
<p class="note" style="margin:0 0 8px"><a href="{SITE}/">Home</a> / <a href="{SITE}/guides/volunteer-fire-department-grants.html">All 50 State Fire Grants</a> / {html.escape(st)}</p>
<section style="padding-top:12px"><h1 style="font-size:clamp(30px,5vw,46px);line-height:1.1;margin:10px 0 14px">{html.escape(st)} fire department grant deadlines, 2026–27</h1>
<p class="muted">Grant programs open to volunteer and rural fire departments in {html.escape(st)}, verified against official agency pages. Always confirm current dates on the official link before applying.</p>
<table class="gt"><thead><tr><th>Due</th><th>Program</th><th>Amount and match</th></tr></thead><tbody>{rows}</tbody></table></section>
<section><h2>Federal FEMA grants {html.escape(st)} fire departments also apply for</h2>
<p>The Assistance to Firefighters Grant (AFG) from FEMA is the largest federal equipment and training grant for fire departments. In the FY 2025 cycle, FEMA received 8,426 AFG applications for approximately 1,800 awards ($291.6M), and the four written narratives drive peer-review scoring.</p>
<p>Backdraft Grants generates a free prefilled draft for any U.S. fire department in the USFA registry, or finishes all four AFG narratives for a flat $249 ($795 for a full FEMA GO application package). Reserving holds a spot for the FY 2026 window and costs nothing today.</p>
<p class="cta-row"><a class="btn" href="{SITE}/?src=state_{slug}#draft">Generate a free {html.escape(st)} AFG draft</a><a class="btn ghost" href="{SITE}/?src=state_{slug}#reserve">Reserve FY 2026 spot ($0 today)</a></p>
<p class="note" style="margin-top:18px">Helpful guides: <a href="{SITE}/guides/afg-grant-narrative-template.html">AFG Narrative Template</a> · <a href="{SITE}/guides/afg-2026-deadline-checklist.html">AFG 2026–27 Checklist</a> · <a href="{SITE}/guides/safer-grant-narrative-guide.html">SAFER Grant Guide</a></p>
<p class="note">Other states: {neighbor_links} · <a href="{SITE}/guides/volunteer-fire-department-grants.html">View all 50 states</a></p></section>
</main>
{FOOT}
<div class="stk on"><span class="stk-t">Free grant draft for your department</span><a class="btn" href="{SITE}/?src=state_{slug}#draft">Start my free draft</a></div>
{TRACK}
</body></html>'''
    open(os.path.join(B, f'public/states/{slug}.html'), 'w').write(page)
    sitemap_entries.append((url, '0.8', 'weekly'))

# 2. Build 5 high-intent SEO guide pages in /guides/
def build_guide(slug, title, desc, h1_text, body_html, faqs, keywords=''):
    url = f"{SITE}/guides/{slug}.html"
    TRACK = TRACK0.replace('SLUG', 'guide_' + slug)
    ld = {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "BreadcrumbList",
                "itemListElement": [
                    {"@type": "ListItem", "position": 1, "name": "Backdraft Grants", "item": SITE + "/"},
                    {"@type": "ListItem", "position": 2, "name": h1_text, "item": url},
                ],
            },
            {
                "@type": "Article",
                "headline": h1_text,
                "description": desc,
                "url": url,
                "datePublished": TODAY,
                "dateModified": TODAY,
                "author": {"@type": "Organization", "name": "Backdraft Grants", "url": SITE},
                "publisher": {"@type": "Organization", "name": "Backdraft Grants", "url": SITE},
            },
            {
                "@type": "FAQPage",
                "mainEntity": [
                    {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}}
                    for q, a in faqs
                ],
            },
        ],
    }
    page = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
{CF_REDIRECT}<title>{html.escape(title)} | Backdraft Grants</title><meta name="description" content="{html.escape(desc, quote=True)}"><link rel="canonical" href="{url}">
{og_tags(title + ' | Backdraft Grants', desc, url, 'article', keywords)}
<script type="application/ld+json">{json.dumps(ld, separators=(',', ':'))}</script>
{fonts}
{style}{FOOTCSS}</head><body>
<a class="skip" href="#main">Skip to content</a>
<header class="wrap legal" style="padding-top:20px;padding-bottom:0;display:flex;justify-content:space-between;align-items:center;gap:12px"><a href="{SITE}/" style="font-weight:700;text-decoration:none;color:inherit">Backdraft Grants</a><a class="navcta" href="{SITE}/#draft">Start free draft</a></header>
<main class="wrap legal" id="main">
<p class="note" style="margin:14px 0 0"><a href="{SITE}/">Home</a> / Guides</p>
<h1>{html.escape(h1_text)}</h1>
{body_html}
<div class="gbox">
  <h3 style="margin-top:0">Skip the blank page</h3>
  <p style="margin:6px 0 14px">Pick your fire department from the USFA national registry and get a free prefilled FEMA AFG, SAFER, or FP&amp;S narrative draft in 60 seconds. No account or credit card required.</p>
  <p class="cta-row" style="margin:0"><a class="btn" href="{SITE}/?src=guide_{slug}#draft">Generate my free draft</a><a class="btn ghost" href="{SITE}/?src=guide_{slug}#reserve">Reserve FY 2026 spot ($249 / $795)</a></p>
</div>
</main>
{FOOT}
{TRACK}
</body></html>'''
    open(os.path.join(B, f'public/guides/{slug}.html'), 'w').write(page)
    sitemap_entries.append((url, '0.9', 'weekly'))

# Guide 1: AFG Grant Narrative Template & Example
build_guide(
    'afg-grant-narrative-template',
    'FEMA AFG Grant Narrative Template & Scoring Guide (2026–27)',
    'Free FEMA Assistance to Firefighters Grant (AFG) narrative template covering all four peer-reviewed sections: Financial Need, Project Description, Cost Benefit, and Statement of Effect.',
    'FEMA AFG Grant Narrative Template & Scoring Guide (2026–27)',
    '''<p class="muted">Updated November 2026 · Built for volunteer, combination, and rural U.S. fire departments preparing for the FY 2026 FEMA AFG window.</p>
<p>Every FEMA Assistance to Firefighters Grant (AFG) application that clears the initial automated prescore is evaluated by a peer-review panel of fire service professionals. Those reviewers score four written narrative sections, each carrying 25% of your peer-review score. Strong narratives rely on concrete department numbers rather than generic statements.</p>
<h2>1. Financial Need (25% of Peer-Review Score)</h2>
<p>Peer reviewers want to see why your department cannot fund this request from its normal operating budget without outside help.</p>
<ul>
  <li><strong>Operating budget and revenue sources:</strong> State your annual operating budget, tax base or municipal appropriation, and reliance on fundraising or donations.</li>
  <li><strong>Community demographics:</strong> Include service area population, median household income, and poverty rate from U.S. Census ACS data (our free tool prefills these automatically).</li>
  <li><strong>Prior attempts to fund:</strong> Note deferred capital purchases, reserve balances already committed to apparatus or station repairs, and why the 5% or 10% local match is manageable while the full purchase is not.</li>
</ul>
<h2>2. Project Description and Budget (25% of Peer-Review Score)</h2>
<p>Spell out exactly what you are requesting, why existing gear or training falls short, and how your cost estimate was built.</p>
<ul>
  <li><strong>Current inventory age and compliance:</strong> List the age of current SCBA, turnout gear (NFPA 1851 10-year retirement rule), radios, or hose, and cite failed tests or out-of-service units.</li>
  <li><strong>Itemized vendor quotes:</strong> Show exact unit counts, unit costs, total project cost, federal share, and local cost-share match.</li>
  <li><strong>Implementation timeline:</strong> Give realistic milestones from award notification through procurement, delivery, acceptance testing, and firefighter training.</li>
</ul>
<h2>3. Cost Benefit (25% of Peer-Review Score)</h2>
<p>Explain how the requested funding delivers the greatest risk reduction per federal dollar spent.</p>
<ul>
  <li><strong>Call volume and protected population:</strong> Connect the request to annual call counts, mutual-aid responses, and critical infrastructure (schools, nursing homes, highways, industrial hazards).</li>
  <li><strong>Service life and maintenance savings:</strong> Show expected 10–15 year equipment life, elimination of recurring repair costs, and interoperability with neighboring departments.</li>
</ul>
<h2>4. Statement of Effect on Daily Operations (25% of Peer-Review Score)</h2>
<p>Describe the measurable operational improvement on day one after deployment.</p>
<ul>
  <li><strong>Firefighter safety and NFPA compliance:</strong> Explain how new PPE, SCBA, or training directly reduces injury, cancer exposure, or cardiac risk.</li>
  <li><strong>Response readiness:</strong> State how the award eliminates delays, improves mutual-aid interoperability, or protects volunteers responding from rural stations.</li>
</ul>''',
    [
        ('What are the four FEMA AFG narrative sections?', 'The four peer-reviewed AFG narrative sections are Financial Need (25%), Project Description and Budget (25%), Cost Benefit (25%), and Statement of Effect on Daily Operations (25%).'),
        ('How long should each FEMA AFG narrative section be?', 'Each section should be concise, factual, and free of filler—typically 300 to 600 words backed by exact department call counts, equipment ages, NFPA standards, and vendor quotes.'),
    ],
)

# Guide 2: AFG 2026-27 Deadlines, Eligibility & FEMA GO Checklist
build_guide(
    'afg-2026-deadline-checklist',
    'FEMA AFG 2026–27 Deadlines, Eligibility & FEMA GO Checklist',
    'Step-by-step FEMA AFG 2026–27 readiness checklist: SAM.gov registration, UEI, FEMA GO AOR setup, local cost-share tiers (5%, 10%, 15%), and FY 2025 award benchmarks.',
    'FEMA AFG 2026–27 Deadlines, Eligibility & FEMA GO Checklist',
    '''<p class="muted">Updated November 2026 · Verified against FEMA Federal Register notices and SAM.gov Assistance Listings.</p>
<p>In the FY 2025 AFG cycle (closed June 22, 2026), FEMA received <strong>8,426 AFG applications</strong> competing for <strong>$291.6 million</strong> across roughly <strong>1,800 awards</strong> (averaging about $162,000 per award). Because FEMA AFG windows typically stay open for only 4 to 5 weeks, departments that wait until the Notice of Funding Opportunity (NOFO) drops often get locked out by SAM.gov or FEMA GO delays.</p>
<h2>Complete These 5 Steps Before the FY 2026 Window Opens</h2>
<ol>
  <li><strong>Verify your UEI and EIN:</strong> Confirm your Unique Entity Identifier (UEI) and IRS Employer Identification Number match your department's legal name.</li>
  <li><strong>Renew SAM.gov early:</strong> Maintain an active System for Award Management (SAM.gov) registration. Renewals can take 2 to 4 weeks if entity validation triggers review.</li>
  <li><strong>Confirm FEMA GO Authorized Organizational Representative (AOR):</strong> Log in at go.fema.gov and verify at least two officers have active access so a single departure does not lock your application.</li>
  <li><strong>Pull NFIRS / NERIS incident totals:</strong> Gather 3 years of incident counts (structure fires, EMS, hazmat, mutual aid) and verify your USFA National Fire Department Registry profile is current.</li>
  <li><strong>Collect written vendor quotes and lock local match approval:</strong> Get itemized quotes for requested equipment and confirm your town council, fire district board, or volunteer association can cover the required local match.</li>
</ol>
<h2>FEMA AFG Local Cost-Share Match Tiers</h2>
<table class="gt"><thead><tr><th>Jurisdiction Population Served</th><th>Required Local Match</th></tr></thead><tbody>
<tr><td>20,000 or fewer residents</td><td>5% of total federal award</td></tr>
<tr><td>20,001 to 1,000,000 residents</td><td>10% of total federal award</td></tr>
<tr><td>More than 1,000,000 residents</td><td>15% of total federal award</td></tr>
</tbody></table>
<p class="note">Nonaffiliated EMS organizations follow the same population-based match tiers. State Fire Training Academies have no cost-share requirement.</p>
<h2>Don't Miss State Fire Grants While Waiting for AFG</h2>
<p>Many states run volunteer fire assistance (VFA) and equipment grant cycles between December and March with far better award odds than federal AFG. Check your state's current deadlines in our <a href="''' + SITE + '''/guides/volunteer-fire-department-grants.html">All 50 State Fire Grants Directory</a>.</p>''',
    [
        ('How many applications does FEMA AFG receive each year?', 'In FY 2025, FEMA received 8,426 AFG applications for $291.6 million in funding, supporting approximately 1,800 awards.'),
        ('What is the cost-share match for small volunteer fire departments?', 'Departments serving 20,000 or fewer residents pay a 5% local cost-share match on FEMA AFG awards.'),
    ],
)

# Guide 3: SAFER Grant Narrative Guide
build_guide(
    'safer-grant-narrative-guide',
    'FEMA SAFER Grant Narrative Guide for Volunteer & Career Fire Departments (2026–27)',
    'How to structure a competitive FEMA SAFER grant narrative for Recruitment and Retention of Volunteer Firefighters or Hiring of Firefighters, including eligibility and scored criteria.',
    'FEMA SAFER Grant Narrative Guide (2026–27)',
    '''<p class="muted">Updated November 2026 · Covers both SAFER Hiring and Volunteer Recruitment &amp; Retention tracks.</p>
<p>FEMA's Staffing for Adequate Fire and Emergency Response (SAFER) grant program helps fire departments meet NFPA 1710 (career) and NFPA 1720 (volunteer) staffing standards. Roughly 2,000+ departments apply in a typical cycle, and volunteer fire departments often overlook the Recruitment and Retention (R&amp;R) activity.</p>
<h2>Two SAFER Funding Tracks</h2>
<ul>
  <li><strong>Recruitment and Retention of Volunteer Firefighters (R&amp;R):</strong> Open to volunteer and combination fire departments (plus national/state/local organizations representing volunteer firefighters). Funds turnout gear for new recruits, training tuition, NFPA 1582 physicals, marketing campaigns, length-of-service award programs (LOSAP), and recruitment coordinators.</li>
  <li><strong>Hiring of Firefighters:</strong> Funds salaries and benefits for newly hired full-time firefighters (typically over a 3-year period of performance) to increase front-line staffing toward NFPA 1710 compliance.</li>
</ul>
<h2>What SAFER Peer Reviewers Look For</h2>
<ul>
  <li><strong>Documented staffing gap:</strong> Quantify average volunteer turnout per alarm, daytime response gaps, missed calls, or mutual-aid reliance compared against NFPA 1720 or NFPA 1710 benchmarks.</li>
  <li><strong>Clear, measurable recruitment goals:</strong> Specify how many new firefighters you aim to recruit and certify to Firefighter I/II, and how you will measure retention over the grant period.</li>
  <li><strong>Sustainability after grant expiration:</strong> Explain how your department will maintain volunteer retention or sustain funded positions once federal funding ends.</li>
</ul>''',
    [
        ('Can all-volunteer fire departments apply for FEMA SAFER grants?', 'Yes. All-volunteer and mostly volunteer fire departments are eligible for the SAFER Recruitment and Retention of Volunteer Firefighters track.'),
        ('Does SAFER Recruitment and Retention require a local cost-share match?', 'Historically, FEMA SAFER grants have carried no local cost-share match, though applicants should always verify the current fiscal year Notice of Funding Opportunity (NOFO).'),
    ],
)

# Guide 4b: Equipment-Specific Grants (Turnout Gear, SCBA, Radios, Fire Trucks)
build_guide(
    'fire-department-equipment-grants',
    'Grants for Fire Department Equipment: Turnout Gear, SCBA, Radios & Fire Trucks (2026–27)',
    'How volunteer and rural fire departments fund turnout gear, SCBA breathing apparatus, P25 radios, thermal cameras, and fire trucks through FEMA AFG and state fire grants.',
    'Grants for Fire Department Equipment: Turnout Gear, SCBA, Radios & Fire Trucks',
    '''<p class="muted">Updated November 2026 · Practical guide to the highest-priority equipment requests funded by FEMA AFG and state fire grants.</p>
<p>When fire chiefs search for grants, they are usually trying to replace expired turnout gear, aging SCBA cylinders, non-interoperable radios, or a 25-year-old engine. Knowing how FEMA peer reviewers rank each equipment category determines whether your application gets scored high enough for an award.</p>
<h2>1. Turnout Gear &amp; Personal Protective Equipment (PPE)</h2>
<ul>
  <li><strong>High priority under FEMA AFG:</strong> Replacing gear over 10 years old (past the NFPA 1851 mandatory retirement age), torn/contaminated ensembles, or providing first-time compliant sets for new volunteers consistently ranks among the highest-priority AFG Operations &amp; Safety requests.</li>
  <li><strong>What to document:</strong> Exact manufacture dates of every coat and pant set, number of active firefighters without a compliant primary set, and NFPA 1851 inspection failures.</li>
</ul>
<h2>2. Self-Contained Breathing Apparatus (SCBA)</h2>
<ul>
  <li><strong>High priority under FEMA AFG:</strong> Replacing SCBA units that do not meet current NFPA 1981 / 1982 standards or have expired cylinders (15-year service life) scores strongly when paired with firefighter safety and mutual-aid interoperability data.</li>
  <li><strong>What to document:</strong> Current SCBA brand/model, NFPA edition year, cylinder expiration dates, repair costs over the past 3 years, and whether neighboring mutual-aid departments use compatible packs.</li>
</ul>
<h2>3. Portable &amp; Mobile Radios (P25 Interoperability)</h2>
<ul>
  <li><strong>Strongest case:</strong> Replacing analog or unsupported radios with P25-compliant units that communicate directly with county dispatch and mutual-aid departments.</li>
  <li><strong>What to document:</strong> Dead zones, dropped transmissions, incompatible channels with neighboring districts, and written confirmation of county radio system requirements.</li>
</ul>
<h2>4. Fire Trucks &amp; Apparatus (Vehicle Acquisition)</h2>
<ul>
  <li><strong>Competitive but fundable:</strong> AFG Vehicle Acquisition prioritizes replacing front-line apparatus that is 20+ years old, lacks enclosed cabs or NFPA 1901 safety features, or has documented mechanical downtime.</li>
  <li><strong>Tip for rural departments:</strong> Also check USDA Rural Development Community Facilities grants/loans and state fire marshal apparatus programs listed in our <a href="''' + SITE + '''/guides/volunteer-fire-department-grants.html">All 50 State Fire Grants Directory</a>.</li>
</ul>''',
    [
        ('Can volunteer fire departments get grants for turnout gear and SCBA?', 'Yes. Replacing expired turnout gear (over 10 years old under NFPA 1851) and outdated SCBA units are among the highest-priority equipment requests under FEMA Assistance to Firefighters Grants (AFG) and state VFA programs.'),
        ('Can FEMA AFG pay for a fire truck?', 'Yes. The AFG Vehicle Acquisition activity funds pumpers, tankers/tenders, brush trucks, and aerial apparatus, prioritizing replacements for front-line trucks over 20 years old with documented safety or maintenance issues.'),
    ],
    'grants for turnout gear volunteer fire department, SCBA grant fire department, fire truck grant volunteer fire department, fire department radio grant, FEMA AFG equipment grant, PPE grant firefighters',
)

# Guide 4: All 50 State Fire Grants Directory Hub
state_cards = "".join(
    f'<a href="{SITE}/states/{st.lower().replace(" ", "-")}.html"><strong>{html.escape(st)}</strong><br><span class="note">{sum(1 for g in G if g[1] == st)} program{"s" if sum(1 for g in G if g[1] == st) > 1 else ""}</span></a>'
    for st in states
)
build_guide(
    'volunteer-fire-department-grants',
    'Volunteer Fire Department Grants Directory: All 50 States (2026–27)',
    'Browse 2026–27 state fire department grant deadlines across all 50 U.S. states, plus federal FEMA AFG, SAFER, and FP&S grant guides for volunteer and rural fire departments.',
    'Volunteer Fire Department Grants Directory: All 50 States (2026–27)',
    f'''<p class="muted">Updated November 2026 · Covers state Volunteer Fire Assistance (VFA), forestry, and state fire marshal grant programs across all 50 states.</p>
<p>Roughly 85% of U.S. fire departments registered with the USFA are volunteer or mostly volunteer. While federal FEMA AFG, SAFER, and FP&amp;S grants offer the largest awards, state fire grants often have smaller applicant pools, faster turnarounds, and deadlines running throughout winter and spring. Select your state below to view verified 2026–27 deadlines and official agency links.</p>
<div class="stgrid">{state_cards}</div>
<h2>Federal Fire Department Grants</h2>
<ul>
  <li><a href="{SITE}/guides/afg-grant-narrative-template.html">FEMA AFG Grant Narrative Template &amp; Scoring Guide</a></li>
  <li><a href="{SITE}/guides/afg-2026-deadline-checklist.html">FEMA AFG 2026–27 Deadlines &amp; FEMA GO Checklist</a></li>
  <li><a href="{SITE}/guides/safer-grant-narrative-guide.html">FEMA SAFER Grant Narrative Guide (Hiring &amp; Volunteer R&amp;R)</a></li>
</ul>''',
    [
        ('Where can volunteer fire departments find state grants?', 'Every state administers federal-state Volunteer Fire Assistance (VFA) grants through its state forestry agency, plus many states offer dedicated fire marshal, emergency services, or rural equipment grants.'),
        ('Can a fire department apply for both state fire grants and FEMA AFG?', 'Yes. Departments frequently apply to state forestry or fire marshal grants for smaller equipment purchases while submitting separate federal AFG or SAFER applications through FEMA GO.'),
    ],
)

# 3. Rebuild privacy.html and terms.html without duplicate canonical tags
for name in ('privacy', 'terms'):
    src = open(os.path.join(B, 'tools/legal', name + '.html')).read()
    title = re.search(r'<!-- TITLE: (.*?) -->', src).group(1)
    desc = re.search(r'<!-- DESC: (.*?) -->', src).group(1)
    body = re.sub(r'<!-- (TITLE|DESC): .*? -->\n', '', src)
    url = f"{SITE}/{name}.html"
    page = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
{CF_REDIRECT}<title>{html.escape(title)} | Backdraft Grants</title><meta name="description" content="{html.escape(desc, quote=True)}"><link rel="canonical" href="{url}">
{og_tags(title + ' | Backdraft Grants', desc, url, 'website')}
{fonts}
{style}{FOOTCSS}</head><body>
<a class="skip" href="#main">Skip to content</a>
<header class="wrap legal" style="padding-top:20px;padding-bottom:0"><a href="{SITE}/" style="font-weight:700;text-decoration:none;color:inherit">Backdraft Grants</a></header>
<main class="wrap legal" id="main">
{body}</main>
{FOOT}
</body></html>'''
    open(os.path.join(B, 'public', name + '.html'), 'w').write(page)
    sitemap_entries.append((url, '0.3', 'monthly'))

# 4. Write sitemap.xml & robots.txt
sm_xml = (
    '<?xml version="1.0" encoding="UTF-8"?>\n'
    '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    + "".join(
        f'<url><loc>{u}</loc><lastmod>{TODAY}</lastmod><changefreq>{freq}</changefreq><priority>{prio}</priority></url>\n'
        for u, prio, freq in sitemap_entries
    )
    + '</urlset>\n'
)
open(os.path.join(B, 'public/sitemap.xml'), 'w').write(sm_xml)
open(os.path.join(B, 'public/robots.txt'), 'w').write(
    f"User-agent: *\nAllow: /\nDisallow: /admin.html\nSitemap: {SITE}/sitemap.xml\n"
)

# 5. Inject clean collapsible 50-state directory into public/index.html for full crawlability
all_state_links = " · ".join(
    f'<a href="/states/{x.lower().replace(" ", "-")}.html">{html.escape(x)}</a>'
    for x in states
)
state_dir_html = (
    '<!--STATE_DIR_START-->'
    '<details class="more" style="margin:0 0 12px"><summary style="font-size:14px">Browse fire grant deadlines by state (all 50 states)</summary>'
    f'<p style="margin:8px 0 0;line-height:1.8;font-size:14px">{all_state_links}</p>'
    '</details>'
    '<!--STATE_DIR_END-->'
)
p2 = os.path.join(B, 'public/index.html')
t = open(p2).read()
if '<!--STATE_DIR_START-->' in t:
    t = re.sub(r'<!--STATE_DIR_START-->.*?<!--STATE_DIR_END-->', state_dir_html, t, flags=re.S)
open(p2, 'w').write(t)

print(f"Built {len(states)} state pages, 4 guide pages, 2 legal pages. Total sitemap URLs: {len(sitemap_entries)}")
