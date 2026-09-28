# Privacy: controller and no collection

One thing is fixed, and one thing is gone.

**The controller.** The privacy notice names
[`selvage-protocol`](https://github.com/selvage-protocol), the GitHub organisation, as the
controller, and names the address to write to (`selvage@dontblameme.dev`) in a paragraph of its own.
Only the owner could fill that blank, and now it is filled.

The notice keeps two statements apart, because they are about two different things. The page's own
collection is nil, and that is what "collects no personal data of its own" scopes; the address is
where mail comes back, so the paragraph that carries it says that the controller receives the
sender's address and keeps it only to answer. A notice that invited mail without saying so would
have been the implied half again.

**The collection.** There is none. The waitlist form is removed (no form, no endpoint, no mailing
service, no processor), so the notice's collection, basis, retention and erasure paragraphs went
with it. What remains is the page-level statement the footer already carried: the page sets no
cookie, makes no third-party request, and sends nothing anywhere. If collection ever returns, the
notice grows back with it: controller, processor, purpose, basis and erasure path, before the form,
not after.

Two decisions taken here, stated so that they are not re-litigated silently:

- **No honeypot field.** Had a form stayed, a hidden field would only have worked because whatever
  received the submission discarded the ones that filled it, and each service spells that field its
  own way. Naming one service's convention before the service was chosen would have baked the
  provider in, exactly what the one-endpoint rule existed to avoid; so spam filtering would have
  been configured at the service, where it belongs. With no form there is no field to debate; the
  reasoning stays so a reintroduced form does not re-litigate it.
- **`form-action 'none'`.** The page renders no form, so a Form Action could only ever carry an
  injected one, and the directive is what refuses it. The waitlist form and its endpoint are gone,
  which is what made the directive free: naming an endpoint to keep a form working was the reason
  not to set it, and there is no endpoint to name.
