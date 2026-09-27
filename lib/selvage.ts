/** The published image the page hands a reader, pinned to the release `package.json`
    carries: a tag that does not exist is a command that fails rather than a sentence
    that lies. It and the demo speak one wire version, `selvage/2`. */
const IMAGE = "ghcr.io/selvage-protocol/selvaged:0.5.1";

/** The one `docker run` the page hands a reader, built from the image above so the command and
    the tag inside it are one string. */
export const COMMAND = `docker run --rm -p 127.0.0.1:8080:8080 ${IMAGE}`;

/** The demo instance: the origin a guest opens, and the address an editor hosts on. */
export const DEMO = "selvage-demo.dontblameme.dev";
