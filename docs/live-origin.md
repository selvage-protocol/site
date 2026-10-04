# The live origin

The page is live and public at **https://selvage.dontblameme.dev**, served by Vercel with the three
response headers. That origin is the page's home. `selvageprotocol.com` is **not registered**, and
registering it is not being pursued: nothing here is waiting on a domain.

What that decides:

- **One origin, named once.** [`app/layout.tsx`](../app/layout.tsx) holds it in `LIVE_ORIGIN` and
  nothing else in the page names a host. `metadataBase` resolves the file conventions' paths against
  it, so `og:image` and `twitter:image` read a URL that resolves,
  `https://selvage.dontblameme.dev/opengraph-image.png`, instead of the `http://localhost:3000/…` a
  local or preview build published while the layout had no `metadataBase` at all. `check-csp.py`'s
  `DEFAULT_ORIGIN` names the same origin.
- **`rel="canonical"` and `og:url` name that origin too.** Both are written from the same constant,
  so the document carries `<link rel="canonical" href="https://selvage.dontblameme.dev"/>` and the
  matching `og:url`, and a card unfurled from a branch preview names the same URL and image as
  production. Moving the page to another origin is one constant, and the two tags follow it.
- **The title, description and `og:title`/`og:description` are the page's own words, in the longer
  form a crawler and a card unfurl want.** The title is the project's name in front of the hero's
  own sentence; the description is the same account at more length — one Rust binary you host holds
  the room and an invite link is the whole permission, four clients on the same file, no account
  and no third party's cloud holding the room — with the specification clause after it. It has to
  agree with the lede, and it does: the lede is the shorter statement of the same two claims.
