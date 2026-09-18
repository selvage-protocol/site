import * as React from "react";
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/lib/utils";

const badgeVariants = cva(
  "inline-flex items-center gap-2 whitespace-nowrap rounded-full border px-3 py-1 font-mono text-[10px] font-medium uppercase tracking-[0.1em] sm:text-[11px] sm:tracking-[0.14em]",
  {
    variants: {
      variant: {
        default: "border-mauve/60 bg-mauve/10 text-mauve",
        outline: "border-surface0 text-subtext",
      },
    },
    defaultVariants: {
      variant: "default",
    },
  },
);

export interface BadgeProps
  extends React.HTMLAttributes<HTMLSpanElement>,
    VariantProps<typeof badgeVariants> {}

function Badge({ className, variant, ...props }: BadgeProps) {
  return (
    <span className={cn(badgeVariants({ variant }), className)} {...props} />
  );
}

export { Badge, badgeVariants };
