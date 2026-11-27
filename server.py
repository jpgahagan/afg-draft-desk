import os, sqlite3, json, re, time, secrets, hmac, csv
from flask import Flask, request, jsonify, send_from_directory

BASE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(BASE, "data.db")
KEYF = os.path.join(BASE, "admin_key.txt")
ADMIN_KEY = os.environ.get("ADMIN_KEY") or (open(KEYF).read().strip() if os.path.exists(KEYF) else secrets.token_urlsafe(24))
app = Flask(__name__, static_folder=os.path.join(BASE, "public"), static_url_path="")

def db():
    c = sqlite3.connect(DB)
    c.execute("""CREATE TABLE IF NOT EXISTS events(id INTEGER PRIMARY KEY, ts REAL, kind TEXT, src TEXT, page TEXT, vid TEXT)""")
    c.execute("""CREATE TABLE IF NOT EXISTS reservations(id INTEGER PRIMARY KEY, ts REAL, org TEXT, email TEXT, state TEXT, orgtype TEXT, plan TEXT, note TEXT, src TEXT, vid TEXT)""")
    c.execute("""CREATE TABLE IF NOT EXISTS pipeline(
        id INTEGER PRIMARY KEY, dept TEXT, state TEXT, town TEXT, email TEXT, phone TEXT,
        fdid TEXT, draft_url TEXT, emailed INTEGER DEFAULT 0, emailed_at TEXT DEFAULT '',
        called INTEGER DEFAULT 0, called_at TEXT DEFAULT '', outcome TEXT DEFAULT 'Not started',
        owner TEXT DEFAULT 'Hayes', notes TEXT DEFAULT '', updated_at REAL)""")
    return c

def authed():
    return hmac.compare_digest(request.headers.get("X-Admin-Key", ""), ADMIN_KEY)

INTERNAL_SRCS = {"qa", "t", "internal", "self", "admin"}
INTERNAL_EMAILS = {
    "zzqa@example.com", "joe.gahagan@gmail.com", "qa-legal@example.com",
    "hello@backdraftgrants.com", "joseph@solcompas.com", "hello@wagl.com",
    "hayes@gahaganllc.com", "hayes@loringenergy.com", "joegahagan@clearplanconsulting.com"
}
BOT_UA = re.compile(r"bot|crawler|spider|headless|curl|wget|python|urllib|go-http|lighthouse|pingdom|uptime|slurp|facebookexternalhit|preview", re.I)

def is_internal_email(email):
    e = (email or "").strip().lower()
    return (e in INTERNAL_EMAILS) or e.endswith("@gahaganllc.com") or e.endswith("@backdraftgrants.com") or e.endswith("@example.com")

@app.route("/api/event", methods=["POST", "OPTIONS"])
def event():
    if request.method == "OPTIONS": return ("", 204)
    d = request.get_json(silent=True) or {}
    kind = str(d.get("kind", ""))[:32]
    if kind not in ("view", "reserve_click", "list_click", "faq_open", "draft_made", "draft_copy", "form_start", "example_write", "sticky_click", "cta_inline", "cta_nav", "resume", "flow_done"):
        return jsonify(ok=False), 400
    src = str(d.get("src", ""))[:64]
    ua = request.headers.get("User-Agent", "")
    if src.lower() in INTERNAL_SRCS or d.get("internal") or BOT_UA.search(ua):
        return jsonify(ok=True, ignored=True)
    c = db(); c.execute("INSERT INTO events(ts,kind,src,page,vid) VALUES(?,?,?,?,?)",
        (time.time(), kind, src, str(d.get("page", ""))[:64], str(d.get("vid", ""))[:40])); c.commit()
    return jsonify(ok=True)

EMAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

@app.route("/api/reserve", methods=["POST", "OPTIONS"])
def reserve():
    if request.method == "OPTIONS": return ("", 204)
    d = request.get_json(silent=True) or {}
    email = str(d.get("email", "")).strip()[:120]
    org = str(d.get("org", "")).strip()[:160]
    if not EMAIL.match(email) or not org:
        return jsonify(ok=False, error="Please add your organization name and a valid email."), 400
    if d.get("website"):  # honeypot
        return jsonify(ok=True)
    c = db()
    if c.execute("SELECT 1 FROM reservations WHERE lower(email)=lower(?)", (email,)).fetchone():
        return jsonify(ok=True, duplicate=True)
    c.execute("INSERT INTO reservations(ts,org,email,state,orgtype,plan,note,src,vid) VALUES(?,?,?,?,?,?,?,?,?)",
        (time.time(), org, email, str(d.get("state", ""))[:40], str(d.get("orgtype", ""))[:60],
         str(d.get("plan", ""))[:20], str(d.get("note", ""))[:600], str(d.get("src", ""))[:64], str(d.get("vid", ""))[:40]))
    c.commit()
    return jsonify(ok=True)

LAUNCH_TS = 1795793000.0  # Nov 27, 2026 pre-outreach cutoff (excludes pre-launch self-tests/bots)

@app.route("/api/stats")
def stats():
    if not authed(): return jsonify(error="forbidden"), 403
    c = db()
    ev = c.execute("SELECT kind, src, COUNT(*), COUNT(DISTINCT vid) FROM events WHERE ts >= ? GROUP BY kind, src", (LAUNCH_TS,)).fetchall()
    ev = [(a, b, n, u) for a, b, n, u in ev if (b or "").lower() not in INTERNAL_SRCS]
    rs = c.execute("SELECT ts, org, email, state, orgtype, plan, src, note FROM reservations WHERE ts >= ? ORDER BY ts", (LAUNCH_TS,)).fetchall()
    rs = [r for r in rs if (r[6] or "").lower() not in INTERNAL_SRCS and not is_internal_email(r[2])]
    return jsonify(events=[dict(kind=a, src=b, n=n, uniq=u) for a, b, n, u in ev],
                   reservations=[dict(ts=a, org=b, email=e, state=s, orgtype=t, plan=p, src=x, note=nt) for a, b, e, s, t, p, x, nt in rs])

@app.route("/api/stats/reset-internal", methods=["POST", "OPTIONS"])
def stats_reset_internal():
    if request.method == "OPTIONS": return ("", 204)
    if not authed(): return jsonify(error="forbidden"), 403
    d = request.get_json(silent=True) or {}
    c = db()
    ev_deleted = 0
    if d.get("clear_prelaunch"):
        ev_deleted = c.execute("DELETE FROM events").rowcount
    else:
        ev_deleted = c.execute("DELETE FROM events WHERE lower(src) IN ('qa','t','internal','self','admin')").rowcount
    res_rows = c.execute("SELECT id, email, src FROM reservations").fetchall()
    res_deleted = 0
    for rid, em, sr in res_rows:
        if (sr or "").lower() in INTERNAL_SRCS or is_internal_email(em):
            c.execute("DELETE FROM reservations WHERE id=?", (rid,))
            res_deleted += 1
    c.commit()
    return jsonify(ok=True, events_deleted=ev_deleted, reservations_deleted=res_deleted)

PIPE_COLS = ("id","dept","state","town","email","phone","fdid","draft_url","emailed","emailed_at","called","called_at","outcome","owner","notes","updated_at")
OUTCOMES = ("Not started","Emailed","Left voicemail","Spoke - interested","Spoke - send info","Reserved","Not interested","Opted out")

@app.route("/api/pipeline", methods=["GET", "POST", "OPTIONS"])
def pipeline_list():
    if request.method == "OPTIONS": return ("", 204)
    if not authed(): return jsonify(error="forbidden"), 403
    c = db()
    if request.method == "GET":
        rows = c.execute("SELECT " + ",".join(PIPE_COLS) + " FROM pipeline ORDER BY id").fetchall()
        return jsonify(items=[dict(zip(PIPE_COLS, r)) for r in rows], outcomes=list(OUTCOMES))
    d = request.get_json(silent=True) or {}
    items = d.get("items") if isinstance(d.get("items"), list) else [d]
    added = 0
    now = time.time()
    for it in items:
        dept = str(it.get("dept", "")).strip()[:160]
        if not dept: continue
        state = str(it.get("state", "")).strip().upper()[:2]
        email = str(it.get("email", "")).strip()[:120]
        if email and c.execute("SELECT 1 FROM pipeline WHERE lower(email)=lower(?)", (email,)).fetchone():
            continue
        if not email and c.execute("SELECT 1 FROM pipeline WHERE lower(dept)=lower(?) AND state=?", (dept, state)).fetchone():
            continue
        outcome = str(it.get("outcome", "Not started")).strip()
        if outcome not in OUTCOMES: outcome = "Not started"
        c.execute("""INSERT INTO pipeline(dept,state,town,email,phone,fdid,draft_url,emailed,emailed_at,called,called_at,outcome,owner,notes,updated_at)
                     VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                  (dept, state, str(it.get("town","")).strip()[:80], email, str(it.get("phone","")).strip()[:40],
                   str(it.get("fdid","")).strip()[:16], str(it.get("draft_url","")).strip()[:300],
                   1 if it.get("emailed") else 0, str(it.get("emailed_at",""))[:32],
                   1 if it.get("called") else 0, str(it.get("called_at",""))[:32],
                   outcome, str(it.get("owner","Hayes")).strip()[:40] or "Hayes",
                   str(it.get("notes",""))[:1000], now))
        added += 1
    c.commit()
    rows = c.execute("SELECT " + ",".join(PIPE_COLS) + " FROM pipeline ORDER BY id").fetchall()
    return jsonify(ok=True, added=added, items=[dict(zip(PIPE_COLS, r)) for r in rows])

@app.route("/api/pipeline/<int:pid>", methods=["PATCH", "DELETE", "OPTIONS"])
def pipeline_item(pid):
    if request.method == "OPTIONS": return ("", 204)
    if not authed(): return jsonify(error="forbidden"), 403
    c = db()
    if request.method == "DELETE":
        c.execute("DELETE FROM pipeline WHERE id=?", (pid,)); c.commit()
        return jsonify(ok=True)
    d = request.get_json(silent=True) or {}
    sets, vals = [], []
    for k in ("dept","state","town","email","phone","fdid","draft_url","emailed_at","called_at","owner","notes"):
        if k in d:
            sets.append(f"{k}=?"); vals.append(str(d[k])[:1000])
    for k in ("emailed","called"):
        if k in d:
            sets.append(f"{k}=?"); vals.append(1 if d[k] else 0)
    if "outcome" in d and str(d["outcome"]) in OUTCOMES:
        sets.append("outcome=?"); vals.append(str(d["outcome"]))
    if not sets: return jsonify(ok=False, error="nothing to update"), 400
    sets.append("updated_at=?"); vals.append(time.time()); vals.append(pid)
    c.execute("UPDATE pipeline SET " + ",".join(sets) + " WHERE id=?", vals); c.commit()
    r = c.execute("SELECT " + ",".join(PIPE_COLS) + " FROM pipeline WHERE id=?", (pid,)).fetchone()
    if not r: return jsonify(ok=False, error="not found"), 404
    return jsonify(ok=True, item=dict(zip(PIPE_COLS, r)))

DEPTS = json.load(open(os.path.join(BASE, "data", "depts.json")))
ECON = json.load(open(os.path.join(BASE, "data", "econ.json")))
for _d in DEPTS: _d.append(_d[1].lower())
DEPT_PHONES = {}
_nfdr = os.path.join(BASE, "data", "nfdr_national.csv")
if os.path.exists(_nfdr):
    try:
        with open(_nfdr, newline="", encoding="utf-8", errors="ignore") as _f:
            for _r in csv.DictReader(_f):
                _k = (_r.get("FDID", "").strip(), _r.get("HQ state", "").strip().upper())
                _p = _r.get("HQ phone", "").strip()
                if _k[0] and _p: DEPT_PHONES[_k] = _p
    except Exception:
        pass

@app.route("/api/dept")
def dept_search():
    q = str(request.args.get("q", "")).strip().lower()[:80]
    st = str(request.args.get("st", "")).strip().upper()[:2]
    fd = str(request.args.get("fdid", "")).strip()[:12]
    if fd:
        hit = [d for d in DEPTS if d[0] == fd and (not st or d[3] == st)][:1]
        if hit:
            d = hit[0]; c = ECON["counties"].get(d[10]) if d[10] else None
            return jsonify(results=[dict(fdid=d[0], name=d[1], city=d[2], state=d[3], county=d[4], type=d[5], stations=d[6],
                        career=d[7], volunteer=d[8], ppc=d[9], phone=DEPT_PHONES.get((d[0], d[3]), ""), county_econ=c, state_econ=ECON["states"].get(d[3]))], us=ECON["us"])
    if len(q) < 2: return jsonify(results=[], us=ECON["us"], state_econ=ECON["states"].get(st) if st else None)
    words = q.split()
    out = []
    for d in DEPTS:
        if st and d[3] != st: continue
        hay = d[11] + " " + d[2].lower()
        if all(w in hay for w in words):
            out.append(d)
            if len(out) >= 25: break
    res = []
    for d in out:
        c = ECON["counties"].get(d[10]) if d[10] else None
        res.append(dict(fdid=d[0], name=d[1], city=d[2], state=d[3], county=d[4], type=d[5], stations=d[6],
                        career=d[7], volunteer=d[8], ppc=d[9], phone=DEPT_PHONES.get((d[0], d[3]), ""), county_econ=c, state_econ=ECON["states"].get(d[3])))
    return jsonify(results=res, us=ECON["us"], state_econ=ECON["states"].get(st) if st else None)

@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")

if __name__ == "__main__":
    db()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5001)))
