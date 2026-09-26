/** The published image the page hands a reader, on the tag the release publishes: a
    command that names a version goes stale as soon as the page's copy of it does, and
    the reader who pastes it is owed a tag that resolves. It and the demo speak one wire
    version, `selvage/2`. */
const IMAGE = "ghcr.io/selvage-protocol/selvaged:latest";

/** The one command the page hands a reader, in both places it appears. */
export const COMMAND = `docker run --rm -p 127.0.0.1:8080:8080 ${IMAGE}`;

/** The demo instance: the origin a guest opens, and the address an editor hosts on. */
export const DEMO = "selvage-demo.dontblameme.dev";
