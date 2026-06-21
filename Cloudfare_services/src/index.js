export default {
  async fetch(request, env) {
    const url = new URL(request.url);

    console.log(
      `[${new Date().toISOString()}] ${request.method} ${url.pathname}`
    );

    // List images for frontend gallery
    if (url.pathname === "/images") {
      return Response.json({
        images: [
          {
            filename: "Pikachu.webp",
            url: `${url.origin}/static/uploads/Pikachu.webp`,
          },
        ],
      });
    }

    // Upload disabled (no R2)
    if (url.pathname === "/upload") {
      return Response.json(
        {
          error:
            "Uploads disabled. Add images to public/static/uploads and redeploy.",
        },
        {
          status: 400,
        }
      );
    }

    // Everything else is served by Cloudflare Assets
    return env.ASSETS.fetch(request);
  },
};