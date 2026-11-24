// Backdraft Grants pass-through: serves https://backdraftgrants.com from the
// Perplexity-hosted origin while keeping backdraftgrants.com in the address bar.
const ORIGIN = 'backdraft.pplx.app';
const APEX = 'backdraftgrants.com';

export default {
  async fetch(request) {
    const url = new URL(request.url);

    // One canonical host: send www and plain http to https://backdraftgrants.com
    if (url.hostname !== APEX || url.protocol !== 'https:') {
      url.hostname = APEX;
      url.protocol = 'https:';
      return Response.redirect(url.toString(), 301);
    }

    const upstream = new URL(url.pathname + url.search, 'https://' + ORIGIN);
    const headers = new Headers(request.headers);
    headers.delete('host');
    headers.set('x-forwarded-host', APEX);

    const resp = await fetch(upstream.toString(), {
      method: request.method,
      headers,
      body: ['GET', 'HEAD'].includes(request.method) ? undefined : request.body,
      redirect: 'manual',
    });

    const out = new Headers(resp.headers);
    const loc = out.get('location');
    if (loc) out.set('location', loc.split('https://' + ORIGIN).join('https://' + APEX));
    out.delete('content-length');

    const type = out.get('content-type') || '';
    if (/text\/html|xml|text\/plain|javascript/.test(type)) {
      const body = (await resp.text()).split('https://' + ORIGIN).join('https://' + APEX);
      return new Response(body, { status: resp.status, headers: out });
    }
    return new Response(resp.body, { status: resp.status, headers: out });
  },
};
