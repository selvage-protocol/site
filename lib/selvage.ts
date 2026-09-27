/** The tag the project publishes the images under: a command that names a version goes stale as
    soon as the page's copy of it does, and the reader who pastes it is owed a tag that
    resolves. */
const IMAGE_TAG = "latest";

/** The two images the page hands a reader. The server is the room, and it serves no page; the
    page image is the browser client, and it relays the session protocol's two endpoints to the
    server named beside it, so a reader who wants the browser editor needs both. They and the
    demo speak one wire version, `selvage/2`. */
const SERVER_IMAGE = `ghcr.io/selvage-protocol/selvaged:${IMAGE_TAG}`;
const PAGE_IMAGE = `ghcr.io/selvage-protocol/selvage-web:${IMAGE_TAG}`;

/** The name the server answers to on the network the two containers share, and the name its
    container runs under so that a reader has something to stop. */
const SERVER_HOST = "selvaged";

/** The name the page container runs under, for the same reason. */
const PAGE_CONTAINER = "selvage-web";

/** The one command that stops and removes both containers: the run below clears a pair left by a
    previous paste with it, and the card prints it as the teardown, so the two cannot drift
    apart. */
const REMOVE_CONTAINERS = `docker rm -f ${SERVER_HOST} ${PAGE_CONTAINER}`;

/** The one command the page hands a reader, built from the images above so the command and the
    tags inside it are one string. Only the page container is published, on this machine's
    loopback; the server has no port on it, and the address the page is given names the server
    on the network the two share.

    Pasting it twice leaves a working pair rather than an error: the network is created only when
    it is missing, and the run clears the two names first, which is what a `docker run --name`
    refuses to do on its own. Both containers run detached, so neither one is left behind by the
    other being stopped. */
export const COMMAND =
  `docker network create selvage 2>/dev/null || true` +
  `; ${REMOVE_CONTAINERS} 2>/dev/null` +
  `; docker run -d --rm --name ${SERVER_HOST} --network selvage ${SERVER_IMAGE}` +
  ` && docker run -d --rm --name ${PAGE_CONTAINER} --network selvage` +
  ` -p 127.0.0.1:8080:8080 -e SELVAGE_SERVER=http://${SERVER_HOST}:8080 ${PAGE_IMAGE}`;

/** What the card prints beside the command to end the run, as the same string the command above
    clears a previous pair with. */
export const TEARDOWN = REMOVE_CONTAINERS;

/** The demo instance: the origin a guest opens, and the address an editor hosts on. */
export const DEMO = "selvage-demo.dontblameme.dev";
