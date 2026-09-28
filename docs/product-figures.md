# The product figures

The page shows the product instead of describing it, without an image, a dependency or a third-party
request: [`components/room-window.tsx`](../components/room-window.tsx) draws the hero's window and
[`components/room-visuals.tsx`](../components/room-visuals.tsx) the four smaller figures, all of
them from inline markup styled by [`style.css`](../style.css). The hero figure is the whole window
at once: the host's folder down the side, the file the room has open, the line one of them is
typing, and the invite link that put them there. Two carets travel inside that text — a 2 px bar in
the peer's colour at a column between two characters of the line, the peer's name in the window's
own gutter lane on that line, and a quarter-alpha fill behind what one of them holds — and each card
in *See it working* carries one smaller drawing of the thing it claims, the middle one with three
carets in it.

Seven rules hold it together:

- **The invite draws a link that works.** The strip in the window's footer and the chip *See
  working* carries both read `?room=k7m2&token=4f9c#k=…`: the query the page takes and the fragment
  the keys travel in, the shape `PROTOCOL.md` §5.1 fixes. They used to stop at the query, which is
  the link shape that cannot seal a room; the chip teaches the shape the clients hand a guest. The
  chip is one row, and the sample is one line: the fragment used to break under the query at a
  `<wbr>`, which made the chip a two-row block, and the `invite link` label is gone because with it
  the chip holds the query or the fragment on one row, not both, in a card 345 px wide. Nothing is
  lost either way: the lead above the card's chip names the link, and the window's own footer
  carries the same one.
- **It is an illustration, and it says so.** The drawings are `aria-hidden` and the card beside each
  one is the sentence it illustrates; the window's side and its code pane are hidden the same way,
  and its invite is a sample rather than a control: nothing in it copies anything. Each code sample
  is a short function against the client crate's own API, with the `use` line left out, and each
  peer's caret is drawn where the browser client draws it (`renderCursors` in
  `web_client/src/browser/editor.ts`): a 2 px bar at the caret's own range, a badge in the left
  gutter on the line the caret is on, and a fill behind the characters the peer holds. A name is
  never written into the text of a line: inside Rust it would read as syntax, which is a claim about
  the source that is not true — so it stays in the lane beside the line number, where that client's
  glyph-margin badge goes.
- **The open file is named twice, and nothing marks it.** The file the room has open is written in
  the guest's tree and in the window's own sidebar, both times in the figure's text colour (`--fg`).
  The tree used to carry a dot beside the name, the drawings' only shape that was not a peer's, and
  the two readings a small filled shape invites — "this file is open" and "this peer is here" — are
  not the same claim, so the name in the figure's own colour carries it alone.
- **The sample is coloured the way the editor colours it.** The token colours are the browser
  client's own `selvage-mocha` theme (`defineTheme` in `web_client/src/browser/main.ts`): comment
  `#868ca2`, keyword `#cba6f7`, function `#89b4fa`, string `#a6e3a1`, number `#fab387`, type
  `#f9e2af`, on the sample's ground and in the body colour `#cdd6f4` otherwise. Punctuation has no
  rule in that theme, so it keeps the body colour here too. The samples are fixed and short, so each
  token is a span written by hand in `components/room-visuals.tsx` — no highlighter, no dependency,
  no parser.
- **Every figure is one band.** The grid is `repeat(auto-fit, minmax(min(100%, 250px), 1fr))`, so
  the four cards are four columns at the shell's width, two or three in between, and one under 390
  px; each card is a column of the drawing's band and the sentence, and the band is a fixed `8rem`
  high — enough for the tallest drawing — so the four leads sit at one height in cards the grid has
  already made equal. A band wider than its drawing centres it, and the code sample's own four lines
  at 12 px on a 22 px line-height do not move with the font, because both numbers are set.
- **The drawings are `aria-hidden`; the cards' own sentences are not.** A screen reader hears the
  sentence that describes the room, not the code in it.
- **No inline `style`, no `<style>`, no font from a third party, no external image.** The policy in
  `vercel.json` refuses the first two outright and admits this origin's fonts alone through
  `font-src 'self'` (see [the Content-Security-Policy](content-security-policy.md)). Every colour in
  a figure is a class in `style.css` or a theme token, which is also what lets
  `scripts/check-contrast.py` measure the figure and the glass card it draws on.
