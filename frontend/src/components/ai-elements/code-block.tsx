import React, { useState } from 'react';
import SyntaxHighlighter from 'react-syntax-highlighter';
import { atomDark } from 'react-syntax-highlighter/dist/esm/styles/prism';
import { Check as LucideCheck, Copy as LucideCopy } from 'lucide-react';

// --- CodeBlockCopyButton Component ---
export interface CodeBlockCopyButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  onCopy?: () => void;
  onCopyError?: (error: Error) => void;
  timeout?: number;
  children?: React.ReactNode;
  className?: string;
  codeToCopy?: string;
}

export const CodeBlockCopyButton = ({
  className,
  onCopy,
  onCopyError,
  timeout = 2000,
  children,
  codeToCopy,
  ...props
}: CodeBlockCopyButtonProps) => {
  const [isCopied, setIsCopied] = useState(false);

  const handleCopy: React.MouseEventHandler<HTMLButtonElement> = async () => {
    if (!navigator.clipboard || !codeToCopy) {
      if (onCopyError) onCopyError(new Error('Clipboard API not available or no code to copy'));
      return;
    }
    try {
      await navigator.clipboard.writeText(codeToCopy);
      setIsCopied(true);
      if (onCopy) onCopy();
      setTimeout(() => {
        setIsCopied(false);
      }, timeout);
    } catch (err: any) {
      if (onCopyError) onCopyError(err);
    }
  };

  return (
    <button
      className={`inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 hover:bg-accent hover:text-accent-foreground h-9 px-3 rounded-md ${className}`}
      onClick={handleCopy}
      {...props}
    >
      {isCopied ? <LucideCheck className="h-4 w-4" /> : <LucideCopy className="h-4 w-4" />}
      {children}
    </button>
  );
};

// --- CodeBlock Component ---
interface CodeBlockProps {
  code: string;
  language: string;
  showLineNumbers?: boolean;
  children?: React.ReactNode;
  className?: string;
}

export const CodeBlock = ({
  code,
  language,
  showLineNumbers = false,
  children,
  className,
}: CodeBlockProps) => {
  return (
    <div className={`relative ${className}`}>
      <SyntaxHighlighter
        language={language}
        style={atomDark}
        showLineNumbers={showLineNumbers}
        customStyle={{ padding: '1rem', borderRadius: '0.5rem', overflowX: 'auto' }}
      >
        {code}
      </SyntaxHighlighter>
      <div className="absolute top-2 right-2 flex gap-2">
        {React.Children.map(children, child => {
          if (React.isValidElement(child) && child.type === CodeBlockCopyButton) {
            return React.cloneElement(child as React.ReactElement<CodeBlockCopyButtonProps>, { codeToCopy: code });
          }
          return child;
        })}
      </div>
    </div>
  );
};
