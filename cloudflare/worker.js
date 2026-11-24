// Backdraft Grants pass-through for backdraftgrants.com
// Deployed as Cloudflare Worker "backdraft-grants", route *backdraftgrants.com/*
const ORIGIN = 'backdraft.pplx.app';
const APEX = 'backdraftgrants.com';
const KEEP = ['accept', 'accept-language', 'content-type', 'cookie', 'user-agent', 'x-admin-key', 'if-none-match', 'if-modified-since'];
export default {
  async fetch(request) {
    const url = new URL(request.url);
    if (!url.hostname.endsWith('.workers.dev') && (url.hostname !== APEX || url.protocol !== 'https:')) {
      url.hostname = APEX;
      url.protocol = 'https:';
      return Response.redirect(url.toString(), 301);
    }
    if (url.pathname === '/__cf') {
      // Loop guard: pplx.app pages redirect here only if this answer arrives straight from the Worker.
      return new Response('backdraft-cf', { headers: { 'access-control-allow-origin': '*', 'cache-control': 'no-store', 'content-type': 'text/plain' } });
    }
    const upstream = 'https://' + ORIGIN + url.pathname + url.search;
    const headers = new Headers();
    for (const k of KEEP) { const v = request.headers.get(k); if (v) headers.set(k, v); }
    let resp;
    try {
      resp = await fetch(upstream, {
        method: request.method,
        headers,
        body: ['GET', 'HEAD'].includes(request.method) ? undefined : await request.arrayBuffer(),
        redirect: 'manual',
      });
    } catch (e) {
      return new Response('Upstream error: ' + e.message, { status: 502 });
    }
    const out = new Headers(resp.headers);
    const loc = out.get('location');
    if (loc) out.set('location', loc.split('https://' + ORIGIN).join('https://' + APEX));
    out.delete('content-length');
    out.delete('content-encoding');
    const type = out.get('content-type') || '';
    if (/text\/html|xml|text\/plain|javascript/.test(type)) {
      const body = (await resp.text()).split('https://' + ORIGIN).join('https://' + APEX);
      return new Response(body, { status: resp.status, headers: out });
    }
    return new Response(resp.body, { status: resp.status, headers: out });
  },
};
