# Cloudflare Overview

## What is Cloudflare?
Cloudflare is an edge network and security platform that accelerates and protects websites, applications, APIs, and other Internet properties. It runs on a global network with hundreds of data centers spanning more than 300 cities worldwide.

## Cloudflare Infrastructure

### Global edge network
- Cloudflare operates a globally distributed edge network in over 300 cities.
- Traffic is routed to the nearest Cloudflare location for lower latency and faster response times.
- Each edge location can cache content, apply security rules, and run edge code.

### Edge services
Cloudflare provides services at the edge, including:
- DDoS protection
- WAF (Web Application Firewall)
- SSL/TLS termination
- Load balancing
- Rate limiting
- IP reputation and bot management

## Caching and HTTP headers
Caching is one of Cloudflare's core benefits. It can cache responses at the edge and reduce load on origin servers.

### Browser cache vs CDN cache
- **Browser cache** stores resources in the user's browser.
  - Controlled by headers such as `Cache-Control`, `Expires`, and `ETag`.
  - Helps repeat visits load faster by avoiding network requests.
- **CDN cache** stores resources at Cloudflare edge locations.
  - Controlled by Cloudflare settings and response headers like `Cache-Control` and `Surrogate-Control`.
  - Reduces origin hits and serves content from the nearest edge location.

### Typical cache headers
- `Cache-Control: max-age=3600, public` — browser can cache for one hour.
- `Cache-Control: no-store` — prevent browser caching.
- `Cache-Control: s-maxage=3600` — instructs shared caches (CDN) to cache for one hour.
- `ETag` — validates resources and enables conditional requests.
- `Expires` — older HTTP header for explicit expiration times.

### Configuring Cloudflare cache
- Use the Cloudflare dashboard to set cache levels and edge TTL.
- Configure page rules or Cache Rules to customize caching per path.
- Use `Cache-Control` headers from your origin to control browser and edge cache behavior.
- Cache static content (images, CSS, JavaScript) aggressively at the edge.
- Use `Cache-Control: no-cache` or `no-store` for sensitive or dynamic content.

## Cloudflare Workers

### What are Workers?
Cloudflare Workers are serverless functions that run at the edge. They execute JavaScript or WebAssembly in response to HTTP requests and can modify request/response traffic, implement APIs, or serve full applications.

### Worker capabilities
- Rewrite URLs and route requests.
- Add custom headers and security logic.
- Fetch data from origin or external services.
- Cache responses at Cloudflare edge locations.
- Serve applications, APIs, and static content directly from the edge.

### Common Worker use cases
- Building APIs and microservices on the edge.
- Implementing authentication or access control.
- Managing A/B testing and redirects.
- Working with durable storage like Workers KV and R2.
- Customizing caching logic per request.

## Cloudflare Pages

### What is Pages?
Cloudflare Pages is a JAMstack hosting platform for static sites and frontend web apps.
- Deploy sites directly from GitHub or GitLab repositories.
- Automatically build, preview, and publish sites.
- Provide global CDN delivery for static assets.

### Pages features
- Automatic build pipelines for frameworks like React, Vue, Hugo, and more.
- Preview deployments for pull requests.
- Custom domains and SSL support.
- Integration with Workers for dynamic behavior.

### When to use Pages
- Hosting static sites, documentation, blogs, or frontend apps.
- Serving content directly from a globally distributed CDN.
- Using serverless Workers to add custom logic or APIs.

## Cloudflare R2

### What is R2?
Cloudflare R2 is object storage designed to work with Workers and the edge.
- Stores files, images, and other binary objects.
- Integrates with Workers through R2 bindings.
- Avoids egress fees for Cloudflare Workers access.

### R2 use cases
- Storing uploaded files and images.
- Building edge-first media delivery.
- Persisting user-generated content from Workers.

## Putting it all together
A Cloudflare-native application often uses:
- **Pages** for static frontend hosting
- **Workers** for edge logic and dynamic behavior
- **R2** for persistent file storage
- **Cache rules** and headers to control browser and edge caching
- **Global edge network** to deliver content fast from 300+ cities

This combination allows applications to run close to users, reduce origin load, and scale without managing traditional server infrastructure.
