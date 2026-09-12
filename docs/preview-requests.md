# Preview browser requests

Browser-to-server calls: the preview runs in an opaque-origin sandbox. Use
plain `fetch()` with relative URLs under the page's `<base href>` (the
`requestJson` helper does this) and no `credentials` option. ES module
scripts work. Do not add CORS, `Cross-Origin-Resource-Policy`, or preflight
handling to the Flask app: the platform's preview proxy already sets those
headers, and app-side copies cannot fix a request the platform rejected. If
the preview reports "Failed to fetch" while the same route works with
`curl`, that is platform routing, not the app; say so and stop rather than
adding headers. Forms that submit through JavaScript must call
`event.preventDefault()` in a `submit` handler so a slow or failed script
does not fall back to a full-page form post.

