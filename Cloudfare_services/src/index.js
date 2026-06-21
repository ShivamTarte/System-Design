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
      const obj = await env.IMAGES.get(key, { type: 'arrayBuffer' });
      if (!obj) return new Response('Not Found', { status: 404 });

      // Try to get metadata for content-type
      const meta = await env.IMAGES.get(key, { type: 'json', onlyIf: { match: 'none' } }).catch(() => null);

      const headers = new Headers();
      // Use the object's httpMetadata if present
      const info = await env.IMAGES.get(key, { onlyIf: { match: 'none' } }).catch(() => null);

      // It's safe to set a default content-type
      headers.set('Content-Type', 'application/octet-stream');
      headers.set('Cache-Control', 's-maxage=3600, max-age=0');

      return new Response(obj, { status: 200, headers });
    } catch (err) {
      console.error('Serve from R2 failed:', err);
      return new Response('Internal error', { status: 500 });
    }
  }

  return new Response('Not Found', { status: 404 });
}
