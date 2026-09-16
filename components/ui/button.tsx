import * as React from "react";
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/lib/utils";

const buttonVariants = cva(
  "inline-flex items-center justify-center gap-2 whitespace-nowrap rounded-lg text-sm font-semibold transition-colors focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-mauve disabled:pointer-events-none disabled:opacity-50 [&_svg]:size-4 [&_svg]:shrink-0",
  {
    variants: {
      variant: {
        default: "bg-mauve text-base hover:bg-text",
        secondary:
          "bg-mauve/15 text-mauve hover:bg-mauve/25 border border-mauve/30",
        ghost: "text-subtext hover:text-text hover:bg-surface0/60",
      },
      size: {
        default: "h-10 px-5",
        sm: "h-8 px-3 text-[13px]",
        lg: "h-11 px-6 text-[15px]",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
    },
  },
);

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
  href?: string;
}

function Button({ className, variant, size, href, children }: ButtonProps) {
  const classes = cn(buttonVariants({ variant, size, className }));
  if (href !== undefined) {
    return (
      <a href={href} className={classes}>
        {children}
      </a>
    );
  }
  return <button className={classes}>{children}</button>;
}

export { Button, buttonVariants };
