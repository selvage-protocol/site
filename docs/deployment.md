# Deploying it

Vercel, connected to this repository over the GitHub integration, building the Next.js project:
[`vercel.json`](../vercel.json) carries `"framework": "nextjs"` so the dashboard does not have to,
plus the three response headers: the `Content-Security-Policy` ([its own
section](content-security-policy.md)), `X-Content-Type-Options: nosniff` and `Referrer-Policy: strict-origin-when-cross-origin`.
[`next.config.ts`](../next.config.ts) turns the framework's own `X-Powered-By: Next.js` banner off,
so the HTML response does not name the stack it was rendered by. There is nothing to configure
beyond connecting the repository.

Production deploys on `main`, at **https://selvage.dontblameme.dev**, and every branch and pull
request gets a preview URL. That is all Vercel is used for. It does not run the checks; the workflow
does, and those are the ones worth making required status checks under branch protection.

Two things about the host plan are the owner's call, not this page's. The page no longer advertises
anything, but should that change the plan question returns with it:

- Vercel's terms restrict the **Hobby** plan to personal, non-commercial use, and their Fair Use
  Guidelines count "advertising the sale of a product or service" as commercial. A page that
  advertised a future paid tier would sit on the commercial side of that line by their own
  definition, so Hobby may not be the right plan if that returns, even before anything is sold.
  [Fair Use Guidelines](https://vercel.com/docs/limits/fair-use-guidelines),
  [Terms](https://vercel.com/legal/terms).
- The Hobby terms also allow Hobby content to be used for model training. A paid plan turns that off
  by default.

## Releasing it

The page is not a released artefact: there is nothing to build or attach, no image and no registry,
no tag and no GitHub Release, and no release workflow. Vercel deploys it from `main` on every push
and reads no tag. The deployment does build — `next build`, on Vercel, from `main` — but that build
is the deployment and not a release.

`package.json`'s version is a private, unpublished manifest that no deployment consumes, so the
version assertion the other repositories' release workflows carry would have nothing to protect
here.
