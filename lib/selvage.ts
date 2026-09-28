/** The two images the page hands a reader, pinned as the card prints them: the repository each one
    is published under, with no tag. Docker reads a bare repository as `:latest`, which is the tag
    the release publishes, and the tag the registry is asked about has one home in
    `scripts/check-claims.py` (`PUBLISHED_IMAGE_TAG`), so the card prints the short string and the
    two cannot drift apart.

    The server is the room, and it serves no page; the page image is the browser client, and it
    relays the session protocol's two endpoints to the server named beside it, so a reader who
    wants the browser editor needs both. They and the demo speak one wire version, `selvage/2`. */
const SERVER_IMAGE = "ghcr.io/selvage-protocol/selvaged";
const PAGE_IMAGE = "ghcr.io/selvage-protocol/selvage-web";

/** The name the server answers to on the network the two containers share, and the name its
    container runs under so that a reader has something to stop. */
const SERVER_HOST = "selvaged";

/** The name the page container runs under, for the same reason. */
const PAGE_CONTAINER = "selvage-web";

/** The network the two containers share, which is how the page reaches the server by name
    rather than over this machine's loopback. */
const NETWORK = "selvage";

/** The address the page container relays to, the address the card tells a reader to open, and the
    mapping the page container publishes the second one on. The first two are one fact in two
    forms and the third is that same address as docker writes it, so they are named together: the
    check reads the pair back out of the rendered card. Only the page container is published, and
    on this machine's loopback rather than on every interface the host has: a page that hands a
    stranger a command should not put their room on the network. */
const SERVER_ADDRESS = `http://${SERVER_HOST}:8080`;
const PUBLISHED_AT = "127.0.0.1:8080:8080";
export const OPEN_AT = "http://127.0.0.1:8080/";

/** The commands the card hands a reader, in the order they are run: the network the two
    containers share, the server that holds the room, and the page that reaches it. Each is one
    line in a block of its own, so a reader who selects one does not take the next with it.

    They are three steps and not one because that is what the three do, and each is short enough
    to read. Pasting a line twice is docker's error to report — the card is the happy path — and a
    reader who is done stops the pair with `docker stop` or `docker rm -f`, which the card does
    not spell out. */
export const RUN_STEPS: readonly { label: string; command: string }[] = [
  {
    label: "Create the network",
    command: `docker network create ${NETWORK}`,
  },
  {
    label: "Start the reference server",
    command: `docker run -d --rm --name ${SERVER_HOST} --network ${NETWORK} ${SERVER_IMAGE}`,
  },
  {
    label: "Start the web client",
    command:
      `docker run -d --rm --name ${PAGE_CONTAINER} --network ${NETWORK}` +
      ` -p ${PUBLISHED_AT} -e SELVAGE_SERVER=${SERVER_ADDRESS} ${PAGE_IMAGE}`,
  },
];

/** The demo instance: the origin a guest opens, and the address an editor hosts on. */
export const DEMO = "selvage-demo.dontblameme.dev";
