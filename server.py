import os, sqlite3, json, re, time, secrets, hmac
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
    return c

@app.route("/api/event", methods=["POST", "OPTIONS"])
def event():
    if request.method == "OPTIONS": return ("", 204)
    d = request.get_json(silent=True) or {}
    kind = str(d.get("kind", ""))[:32]
    if kind not in ("view", "reserve_click", "list_click", "faq_open"):
        return jsonify(ok=False), 400
    c = db(); c.execute("INSERT INTO events(ts,kind,src,page,vid) VALUES(?,?,?,?,?)",
        (time.time(), kind, str(d.get("src", ""))[:64], str(d.get("page", ""))[:64], str(d.get("vid", ""))[:40])); c.commit()
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

@app.route("/api/stats")
def stats():
    if not hmac.compare_digest(request.headers.get("X-Admin-Key", ""), ADMIN_KEY): return jsonify(error="forbidden"), 403
    c = db()
    ev = c.execute("SELECT kind, src, COUNT(*), COUNT(DISTINCT vid) FROM events GROUP BY kind, src").fetchall()
    rs = c.execute("SELECT ts, org, email, state, orgtype, plan, src FROM reservations ORDER BY ts").fetchall()
    return jsonify(events=[dict(kind=a, src=b, n=n, uniq=u) for a, b, n, u in ev],
                   reservations=[dict(ts=a, org=b, email=e, state=s, orgtype=t, plan=p, src=x) for a, b, e, s, t, p, x in rs])

@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")

if __name__ == "__main__":
    db()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5001)))
