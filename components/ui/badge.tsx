import * as React from "react";
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/lib/utils";

const badgeVariants = cva("inline-flex items-center whitespace-nowrap", {
  variants: {
    variant: {
      // A mono caps chip: the one label that is a status rather than a value.
      default:
        "gap-2 rounded-full border border-mauve/60 bg-mauve/10 px-3 py-1 font-mono text-[10px] font-medium uppercase tracking-[0.1em] text-mauve sm:text-[11px] sm:tracking-[0.14em]",
      outline:
        "gap-2 rounded-full border border-surface0 px-3 py-1 font-mono text-[10px] font-medium uppercase tracking-[0.1em] text-subtext sm:text-[11px] sm:tracking-[0.14em]",
      // A pill: a state beside a card's own name, in the word the project uses for
      // it rather than in caps.
      pill: "rounded-full px-2 py-[3px] text-xs",
    },
  },
  defaultVariants: {
    variant: "default",
  },
});

export interface BadgeProps
  extends React.HTMLAttributes<HTMLSpanElement>,
    VariantProps<typeof badgeVariants> {}

function Badge({ className, variant, ...props }: BadgeProps) {
  return (
    <span className={cn(badgeVariants({ variant }), className)} {...props} />
  );
}

export { Badge, badgeVariants };
