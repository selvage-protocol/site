import { Box, Code, Globe, Terminal, type LucideIcon } from "lucide-react";
import { DEMO } from "@/lib/selvage";

/* One entry per client, and every surface the page draws a client on derives from this list:
   the repository grid's row, the chips in *Clients share one protocol*, and the install route in
   the terminal. A client added here appears on all three; nothing else about it is written
   out a second time.

   `id` is what keys the three together. Each surface carries it in a `data-client` attribute
   (or, for the install routes, in the panel's own id), which is what lets the claim check read
   the surfaces against each other without a list of client names of its own.

   The grid's row names the repository the client lives in, and a client whose repository is a
   plan rather than something a reader can open carries the `planned` status: the row marks it
   and links nothing, because there is nothing at the other end of the link. */

/** The glyphs a route's prompt gutter draws: the shell's, Neovim's command line's, and the
    browser's address bar's. */
type Prompt = "$" | ":" | "›";

declare const afterPrompt: unique symbol;
/** A command as it reads after its prompt. Only `command` makes one. */
type CommandText = string & { readonly [afterPrompt]: true };

/** One line of an install route, as the terminal draws it. */
export type InstallLine =
  | { prompt: Prompt; text: CommandText; comment?: never }
  | {
      prompt?: never;
      text: string;
      /** A note about the command rather than the command, in the terminal's dim tone. */
      comment?: boolean;
    };

/* The gutter draws the prompt and the text is what follows it, so a text that begins with its
   own prompt reads doubled (`::`). The two are literals, and a text that starts with its prompt,
   or that is not a literal and so cannot be read, is `never` and fails the typecheck: a prompted
   line cannot be written any other way, because `CommandText` comes from nowhere else. */
function command<P extends Prompt, T extends string>(
  prompt: P,
  text: string extends T ? never : T extends `${P}${string}` ? never : T,
): InstallLine {
  return { prompt, text: text as string as CommandText };
}

/** A client the page offers, or writes down as a plan. */
export type Client = {
  id: string;
  /** The repository the client lives in, and the name the grid's row shows. */
  repository: string;
  /** What the grid's row says the client is. */
  description: string;
  Icon: LucideIcon;
  status: "available" | "planned";
  /** The label the client wears as a chip, and as its install route's tab. */
  chip: string;
  /** The route a reader installs it by. A plan has none, and so has no tab. */
  install?: {
    lines: InstallLine[];
    /** What the route's copy control puts on the clipboard. */
    copy: string;
    /** What the copy announces: the tab it came from is not something a listener sees. */
    announce: string;
    note: string;
  };
};

export function repositoryUrl(repository: string) {
  return `https://github.com/selvage-protocol/${repository}`;
}

const NEOVIM_COMMAND = "SelvageHost ws://127.0.0.1:8080";
const NEOVIM_PLUGIN_LINE = "{ 'selvage-protocol/nvim_client', build = 'npm ci' }";

export const CLIENTS: Client[] = [
  {
    id: "vscode",
    repository: "vscode_client",
    description: "VS Code extension",
    Icon: Code,
    status: "available",
    chip: "VS Code",
    install: {
      lines: [
        command("$", "code --install-extension selvage-protocol.selvage"),
        { text: "# then run  Selvage: Host a session — this opens the room", comment: true },
      ],
      copy: "code --install-extension selvage-protocol.selvage",
      announce: "VS Code command",
      note: "Published on the VS Code Marketplace and on Open VSX.",
    },
  },
  {
    id: "nvim",
    repository: "nvim_client",
    description: "Neovim plugin",
    Icon: Terminal,
    status: "available",
    chip: "Neovim",
    install: {
      lines: [
        { text: "-- lazy.nvim: add this line to your spec", comment: true },
        { text: NEOVIM_PLUGIN_LINE },
        command(":", NEOVIM_COMMAND),
      ],
      copy: NEOVIM_PLUGIN_LINE,
      announce: "Neovim plugin line",
      note: "Works with any plugin manager; the spec above is the lazy.nvim form.",
    },
  },
  {
    id: "web",
    repository: "web_client",
    description: "The browser page",
    Icon: Globe,
    status: "available",
    chip: "Browser",
    install: {
      lines: [
        { text: `# point an editor at wss://${DEMO}`, comment: true },
        command("›", DEMO),
        { text: "# the invite a host sends opens in the page", comment: true },
      ],
      copy: DEMO,
      announce: "Browser address",
      note: "Guests need nothing installed.",
    },
  },
  {
    id: "jetbrains",
    repository: "jetbrains_client",
    description: "JetBrains IDEs",
    Icon: Box,
    status: "planned",
    chip: "JetBrains",
  },
];

/** How many clients the chips figure names before it rolls the rest into its last chip. The
    list is open, and the figure is a fixed-height band between two other drawings: a cap is
    what keeps it the same shape at four clients and at ten. */
export const CHIP_LIMIT = 4;
