import React from 'react';
import { cva, type VariantProps } from 'class-variance-authority';
import { Loader2 } from 'lucide-react'; // Assuming Loader2 icon from lucide-react

// --- Input Component ---
export interface InputProps extends React.FormHTMLAttributes<HTMLFormElement> {
  children?: React.ReactNode;
  className?: string;
}

export const Input = ({ children, className, ...props }: InputProps) => {
  return (
    <form className={className} {...props}>
      {children}
    </form>
  );
};

// --- PromptInputTextarea Component ---
export interface PromptInputTextareaProps extends React.TextareaHTMLAttributes<HTMLTextAreaElement> {
  className?: string;
}

export const PromptInputTextarea = ({ className, ...props }: PromptInputTextareaProps) => {
  return (
    <textarea
      className={`min-h-[60px] w-full resize-none px-4 py-[1.3rem] focus-within:outline-none sm:text-sm ${className}`}
      {...props}
    />
  );
};

// --- PromptInputSubmit Component ---
const promptInputSubmitVariants = cva(
  'flex h-8 w-8 items-center justify-center rounded-full bg-black text-white transition-all hover:bg-black/80 dark:bg-white dark:text-black dark:hover:bg-white/80',
  {
    variants: {
      status: {
        ready: '',
        streaming: 'animate-spin',
      },
    },
    defaultVariants: {
      status: 'ready',
    },
  }
);

export interface PromptInputSubmitProps extends React.ButtonHTMLAttributes<HTMLButtonElement>, VariantProps<typeof promptInputSubmitVariants> {
  className?: string;
}

export const PromptInputSubmit = ({ className, status, ...props }: PromptInputSubmitProps) => {
  return (
    <button
      type="submit"
      className={promptInputSubmitVariants({ status, className })}
      disabled={status === 'streaming'}
      {...props}
    >
      {status === 'streaming' ? <Loader2 className="h-4 w-4" /> : '↵'}
    </button>
  );
};
