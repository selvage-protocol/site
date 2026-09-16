import * as React from "react";
import { renderToStaticMarkup } from "react-dom/server";
import { Button, type ButtonProps } from "../components/ui/button";

let failures = 0;

function check(condition: boolean, label: string, detail?: string): void {
  if (condition) {
    console.log(`ok: ${label}`);
  } else {
    failures += 1;
    console.error(`FAIL: ${label}${detail === undefined ? "" : ` (${detail})`}`);
  }
}

// Button element: handlers, disabled/type and accessibility attributes reach the DOM.
const onClick = (): void => {};
const buttonElement = (
  <Button type="button" disabled onClick={onClick} aria-label="Join" id="join">
    Join the session
  </Button>
);
const buttonHtml = renderToStaticMarkup(buttonElement);
check(buttonHtml.startsWith("<button"), "renders a button without href", buttonHtml);
check(buttonHtml.includes('type="button"'), "type reaches the button", buttonHtml);
const defaultTypeHtml = renderToStaticMarkup(<Button>Default type</Button>);
check(
  defaultTypeHtml.includes('type="button"'),
  "button defaults to type button without a caller value",
  defaultTypeHtml,
);
const submitHtml = renderToStaticMarkup(<Button type="submit">Submit</Button>);
check(
  submitHtml.includes('type="submit"'),
  "an explicit button type is preserved",
  submitHtml,
);
check(
  buttonHtml.includes("disabled"),
  "disabled reaches the button",
  buttonHtml,
);
check(
  buttonHtml.includes('aria-label="Join"'),
  "aria-label reaches the button",
  buttonHtml,
);
check(buttonHtml.includes("Join the session"), "children reach the button", buttonHtml);
check(
  (Button({ type: "button", onClick, children: "x" } as ButtonProps) as React.JSX.Element)
    .props.onClick === onClick,
  "onClick reaches the button element",
);

// Anchor element: href wins, link attributes reach the DOM, styling preserved.
const anchorHtml = renderToStaticMarkup(
  <Button
    href="https://github.com/selvage-protocol/specification"
    target="_blank"
    rel="noreferrer"
    aria-label="Read the spec"
    variant="secondary"
    size="lg"
  >
    Read the spec
  </Button>,
);
check(anchorHtml.startsWith("<a "), "renders an anchor with href", anchorHtml);
check(
  anchorHtml.includes('href="https://github.com/selvage-protocol/specification"'),
  "href reaches the anchor",
  anchorHtml,
);
check(anchorHtml.includes('target="_blank"'), "target reaches the anchor", anchorHtml);
check(anchorHtml.includes('rel="noreferrer"'), "rel reaches the anchor", anchorHtml);
check(
  anchorHtml.includes('aria-label="Read the spec"'),
  "aria-label reaches the anchor",
  anchorHtml,
);
check(
  anchorHtml.includes("bg-mauve/15") && anchorHtml.includes("px-6"),
  "variant/size styling preserved on the anchor",
  anchorHtml,
);

if (failures > 0) {
  console.error(`${failures} check(s) failed`);
  process.exit(1);
}
console.log("button props reach the DOM");
