import * as React from "react";
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/lib/utils";

const buttonVariants = cva(
  "inline-flex items-center justify-center gap-2 whitespace-nowrap rounded-lg text-sm font-semibold transition duration-150 ease-out motion-safe:active:translate-y-0 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-mauve disabled:pointer-events-none disabled:opacity-50 [&_svg]:size-4 [&_svg]:shrink-0",
  {
    variants: {
      variant: {
        default: "bg-mauve text-[color:var(--color-base)] hover:bg-mauve-hi",
        secondary:
          "bg-mauve/15 text-mauve hover:bg-mauve/20 border border-mauve/60 hover:border-mauve",
        outline:
          "border border-surface1 bg-mantle text-text hover:border-overlay1",
        ghost: "text-subtext hover:text-text hover:bg-surface0/60",
      },
      size: {
        default: "h-10 px-5",
        sm: "h-[34px] px-3.5 text-sm",
        lg: "h-11 px-6 text-[15px]",
        hero: "h-12 px-5 text-[16px]",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
    },
  },
);

type ButtonStyleProps = VariantProps<typeof buttonVariants>;

export type ButtonAsButtonProps =
  React.ButtonHTMLAttributes<HTMLButtonElement> &
    ButtonStyleProps & {
      href?: undefined;
    };

export type ButtonAsAnchorProps =
  React.AnchorHTMLAttributes<HTMLAnchorElement> &
    ButtonStyleProps & {
      href: string;
    };

export type ButtonProps = ButtonAsButtonProps | ButtonAsAnchorProps;

function Button({
  className,
  variant,
  size,
  href,
  children,
  ...rest
}: ButtonProps) {
  const classes = cn(buttonVariants({ variant, size, className }));
  if (href !== undefined) {
    return (
      <a
        href={href}
        className={classes}
        {...(rest as React.AnchorHTMLAttributes<HTMLAnchorElement>)}
      >
        {children}
      </a>
    );
  }
  return (
    <button
      className={classes}
      {...(rest as React.ButtonHTMLAttributes<HTMLButtonElement>)}
      type={(rest as React.ButtonHTMLAttributes<HTMLButtonElement>).type ?? "button"}
    >
      {children}
    </button>
  );
}

export { Button, buttonVariants };
