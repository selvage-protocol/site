# The Content-Security-Policy

The header is [`vercel.json`](../vercel.json)'s, applied by Vercel:

```
default-src 'none'; script-src 'self' 'unsafe-inline'; script-src-attr 'none'; img-src 'self' data:; style-src 'self'; font-src 'self'; form-action 'none'; base-uri 'none'; frame-ancestors 'none'
```

It read without `script-src` until this was found, and that absence is the whole reason this section
exists. With `default-src 'none'` and nothing for scripts to fall back to, the page's own seven
chunks and all fifteen of its inline scripts were refused: `window.__next_f` stayed the string
`undefined`, the page never hydrated, and `SiteHeader`'s hide-on-scroll silently did nothing while
the [accessibility section](accessibility.md) read as if it worked. A policy that refuses the page
it ships with is not strict, it is broken, and nothing in the gate said so.

`script-src 'self' 'unsafe-inline'` is the smallest thing that is also true, and the route itself is
why it cannot be narrower. `'self'` is the seven chunks. `'unsafe-inline'` is the bootstrap and the
flight data Next writes into the HTML: a **nonce** would permit those instead, but a nonce has to be
fresh per request, which means dynamic rendering, and the page is a static prerender (`○ /`), so the
route would be traded for the directive. A committed **hash list** is worse than it looks: any prose
edit rewrites the flight payload the hashes are computed over, and a stale hash fails the same
silent way the missing directive did.

`script-src-attr 'none'` narrows that token to the elements the route actually needs. Without the
directive it covers an inline `on*` attribute on any element as well as an inline `<script>`, and
with it the two are decided separately: `script-src` carries the bootstrap, and every inline handler
attribute is refused. The page carries none, so it costs the page nothing.

`form-action 'none'` closes the one element kind `default-src 'none'` does not reach: a Form Action
has no fallback to `default-src`, so without the directive any `<form>` the page carried could
submit to any origin. The page renders no form and no user input into itself, so the directive
cannot break anything.

`font-src 'self'` is the one directive that does not exist for a script or an image: a font fetch
falls back to `default-src` like any other, so without it `default-src 'none'` refuses the two
families `next/font` self-hosts and a browser silently paints the fallback stack instead. `'self'`
is enough because the glyph files arrive from `/_next/static/media` on this origin, and no request
is ever made to a font host.

What the policy still refuses: every origin that is not this one, `eval`, an inline `on*` attribute,
a form submission, a `<base>` that would retarget the page's relative URLs, framing, every resource
kind the page does not name, and every font but this origin's. `data:` is allowed for `img-src`
alone.

Two pieces of evidence, with their limits:

- [`scripts/check-csp.py`](../scripts/check-csp.py) runs in the gate over the HTML the production
  server renders, and over the HTML its not-found route renders, because that route is a page the
  site serves and the policy has to permit it too. The framework's own 404 document is styled with a
  `<style>` element and four `style` attributes, all five of which `style-src 'self'` refuses;
  `app/not-found.tsx` is styled from `style.css` instead. The check takes the policy *from*
  `vercel.json`, not a copy of it, and decides every script, stylesheet, image and font against the
  directive that governs it, following the fallback chains a browser follows — a font fetch falls
  back to `default-src` like any other, and the `<link rel="preload" as="font">` the page carries is
  what names one that is coming. The policy as it read without `script-src` and the one as it read
  without `font-src` are both fixtures of its own, so it fails on the defect it was written for and
  on the quieter one a missing `font-src` is. It is a model of the policy, not a browser, and a
  source expression it does not model is an error rather than an assumption.
- A real Chromium run against the built page served with these exact headers, kept runnable as
  `scripts/check-csp-browser.mjs`: it applies the `headers` block out of `vercel.json` through a
  local proxy (`next start` does not apply it, only the host does) and asserts zero
  `securitypolicyviolation` events, `window.__next_f` an object, the header concealed (`translate: 0px -100%`)
  at `scrollY` 900 and back at 300, and no `X-Powered-By`. It is the only thing here that can see
  the fonts: both families have to be loaded and resolve, and the body's computed family has to be
  Geist rather than the stack under it, because a refused glyph file paints the fallback in the same
  layout and reads as a typographic choice. A violation naming a font is reported as what it is
  before the run fails on the count. It then requests a path no route claims and asserts the `404`
  it renders carries no violation either, which is the assertion that fails on the framework's own
  404 document. Point `VERCEL_JSON` at the policy as it read without `script-src`, or at the one as
  it read without `font-src`, and it fails, which is checked rather than assumed. It needs a browser
  the runner does not have, so it is not in the workflow: `npm run build && CHROMIUM=/path/to/chromium npm run check:csp-browser`.

Neither of them can see the deployed response headers. If Vercel stops applying the `headers` block,
or applies it to a path this policy was not written for, nothing in this repository notices.
