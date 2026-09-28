# The page

The landing page for **Selvage** (the project) and the **Selvage Session Protocol** (the protocol it
publishes). A Next.js App Router project with one route (`/`) and the framework's not-found route
beside it ([`app/not-found.tsx`](../app/not-found.tsx), styled from the same stylesheet): the page
component carries the prose, the product figures live in two components of their own, the global
stylesheet carries the styling, and the browser downloads nothing beyond the prerendered page, the
stylesheet, the two fonts, the images, and the framework runtime with the four client components
(the bar, the hero's room window, the terminal, and the demo's copy control) and their dependencies.
The page runs no analytics and makes no third-party request: the two fonts it loads are served from
this origin, and the glyph files are one of the things it holds to its budget here.
