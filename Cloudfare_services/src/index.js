export default {
  async fetch(request) {
    const url = new URL(request.url);
    
    // Log incoming request
    console.log(`[${new Date().toISOString()}] ${request.method} ${url.pathname}`);
    
    // Get the response from the static files or API
    const response = await getAssetFromKV(request);
    
    // Add cache headers for images - Cloudflare cache only, no browser cache
    if (url.pathname.includes('/static/uploads/')) {
      response.headers.set('Cache-Control', 's-maxage=3600, max-age=0');
    }
    
    // Add CORS headers
    response.headers.set('Access-Control-Allow-Origin', '*');
    response.headers.set('X-Powered-By', 'Cloudflare');
    
    return response;
  },
};

async function getAssetFromKV(request) {
  const url = new URL(request.url);
  
  // Proxy API requests to backend
  if (url.pathname.startsWith('/upload') || 
      url.pathname.startsWith('/images') ||
      url.pathname.startsWith('/static/uploads/')) {
    // Forward to your backend server
    return fetch(new Request(
      `http://127.0.0.1:8000${url.pathname}${url.search}`,
      {
        method: request.method,
        headers: request.headers,
        body: request.body,
      }
    ));
  }
  
  return new Response('Not Found', { status: 404 });
}
