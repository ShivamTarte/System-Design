export default {
  async fetch(request, env) {
    const url = new URL(request.url);

    // Log incoming request
    console.log(`[${new Date().toISOString()}] ${request.method} ${url.pathname}`);

    try {
      const response = await getAssetFromKV(request, env);

      // Add cache headers for images - Cloudflare cache only, no browser cache
      if (url.pathname.includes('/static/uploads/')) {
        response.headers.set('Cache-Control', 's-maxage=3600, max-age=0');
      }

      // Add CORS and metadata headers
      response.headers.set('Access-Control-Allow-Origin', '*');
      response.headers.set('X-Powered-By', 'Cloudflare');

      return response;
    } catch (err) {
      console.error('Worker error:', err);
      return new Response(JSON.stringify({ error: 'Worker error', detail: String(err) }), {
        status: 502,
        headers: { 'Content-Type': 'application/json; charset=utf-8', 'Access-Control-Allow-Origin': '*' },
      });
    }
  },
};

async function getAssetFromKV(request, env) {
  const url = new URL(request.url);

  if (!env?.IMAGES) {
    throw new Error('Missing R2 binding `IMAGES`. Create the R2 bucket and ensure `wrangler.toml` includes the binding.');
  }

  // Handle upload/listing/serve via R2 binding `env.IMAGES`
  if (url.pathname.startsWith('/upload')) {
    // POST /upload -> accept multipart/form-data and write to R2
    if (request.method !== 'POST') {
      return new Response(JSON.stringify({ error: 'Method not allowed' }), { status: 405, headers: { 'Content-Type': 'application/json' } });
    }

    try {
      const form = await request.formData();
      const file = form.get('image');
      if (!file) {
        return new Response(JSON.stringify({ error: 'No image provided' }), { status: 400, headers: { 'Content-Type': 'application/json' } });
      }

      const arrayBuffer = await file.arrayBuffer();
      const filename = file.name || `upload-${Date.now()}`;
      const safeName = filename.replace(/[^a-zA-Z0-9_.-]/g, '_');
      const key = `uploads/${Date.now()}-${safeName}`;

      await env.IMAGES.put(key, arrayBuffer, { httpMetadata: { contentType: file.type || 'application/octet-stream' } });

      const origin = new URL(request.url).origin;
      const urlPath = `${origin}/static/uploads/${encodeURIComponent(key)}`;

      return new Response(JSON.stringify({ filename, key, url: urlPath }), { status: 200, headers: { 'Content-Type': 'application/json' } });
    } catch (err) {
      console.error('Upload failed:', err);
      return new Response(JSON.stringify({ error: 'Upload failed', detail: String(err) }), { status: 500, headers: { 'Content-Type': 'application/json' } });
    }
  }

  if (url.pathname.startsWith('/images')) {
    // GET /images -> list images from R2
    if (request.method !== 'GET') {
      return new Response(JSON.stringify({ error: 'Method not allowed' }), { status: 405, headers: { 'Content-Type': 'application/json' } });
    }

    try {
      const list = await env.IMAGES.list({ prefix: 'uploads/' });
      const origin = new URL(request.url).origin;
      const images = (list.objects || []).map(obj => ({ filename: obj.key.split('/').pop(), url: `${origin}/static/uploads/${encodeURIComponent(obj.key)}` }));
      return new Response(JSON.stringify({ images }), { status: 200, headers: { 'Content-Type': 'application/json' } });
    } catch (err) {
      console.error('List images failed:', err);
      return new Response(JSON.stringify({ error: 'List failed', detail: String(err) }), { status: 500, headers: { 'Content-Type': 'application/json' } });
    }
  }

  if (url.pathname.startsWith('/static/uploads/')) {
    // GET /static/uploads/{key} -> return object from R2
    if (request.method !== 'GET' && request.method !== 'HEAD') {
      return new Response('Method not allowed', { status: 405 });
    }

    const key = decodeURIComponent(url.pathname.replace('/static/uploads/', ''));
    try {
      const obj = await env.IMAGES.get(key);
      if (!obj) return new Response('Not Found', { status: 404 });

      const buffer = await obj.arrayBuffer();
      const contentType = obj.httpMetadata?.contentType || 'application/octet-stream';
      const headers = new Headers({
        'Content-Type': contentType,
        'Cache-Control': 's-maxage=3600, max-age=0',
      });

      return new Response(buffer, { status: 200, headers });
    } catch (err) {
      console.error('Serve from R2 failed:', err);
      return new Response('Internal error', { status: 500 });
    }
  }

  return new Response('Not Found', { status: 404 });
}
