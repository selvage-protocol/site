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

/** The name the server answers to on the network the two containers share. */
const SERVER_HOST = "selvaged";

/** The one command the page hands a reader, built from the images above so the command and the
    tags inside it are one string. Only the page container is published, on this machine's
    loopback; the server has no port on it, and the address the page is given names the server
    on the network the two share. */
export const COMMAND =
  `docker network create selvage` +
  ` && docker run -d --rm --name ${SERVER_HOST} --network selvage ${SERVER_IMAGE}` +
  ` && docker run --rm --network selvage -p 127.0.0.1:8080:8080` +
  ` -e SELVAGE_SERVER=http://${SERVER_HOST}:8080 ${PAGE_IMAGE}`;

/** The demo instance: the origin a guest opens, and the address an editor hosts on. */
export const DEMO = "selvage-demo.dontblameme.dev";
