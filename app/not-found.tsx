/** The framework's default 404 document carries a `<style>` element and four `style` attributes,
    and the policy in `vercel.json` refuses both: a reader who mistyped an address got a page the
    site's own header said was not there, in the browser's colours. This one is styled from
    `style.css` alone, so the policy refuses nothing the site serves. */
export default function NotFound() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center px-5 text-center">
      <h1 className="text-[1.5rem] font-semibold tracking-[-0.02em] text-text">
        Nothing at this address
      </h1>
      <p className="mt-4 max-w-[35rem] text-[1.0625rem] leading-[1.7] text-subtext">
        This site has one page:{" "}
        <a href="/" className="text-mauve underline underline-offset-4">
          the landing page
        </a>
        .
      </p>
    </main>
  );
}
