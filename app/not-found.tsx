/** The framework's default 404 document carries a `<style>` element and four `style` attributes,
    and the policy in `vercel.json` refuses both: a reader who mistyped an address got a page the
    site's own header said was not there, in the browser's colours. This one is styled from
    `style.css` alone, so the policy refuses nothing the site serves. */
export default function NotFound() {
  return (
    <main className="not-found">
      <h1>Nothing at this address</h1>
      <p>
        This site has one page:{" "}
        <a href="/" className="underline underline-offset-4">
          the landing page
        </a>
        .
      </p>
    </main>
  );
}
