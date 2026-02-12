import React from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
// You can choose different styles (e.g., atomDark, dracula, vsDark)
import { oneDark } from 'react-syntax-highlighter/dist/esm/styles/prism';

interface ChatResponseProps {
  content: string;
}

const ChatResponse: React.FC<ChatResponseProps> = ({ content }) => {
  return (
    <div className="markdown-container p-0 leading-relaxed">
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        components={{
          // Customizing the "code" tag
          code({ node, inline, className, children, ...props }: any) {
            const match = /language-(\w+)/.exec(className || '');
            
            return !inline && match ? (
              <div className="rounded-md overflow-hidden my-4">
                <div className="bg-gray-800 text-gray-400 text-xs px-4 py-1 flex justify-between uppercase">
                  <span>{match[1]}</span>
                </div>
                <SyntaxHighlighter
                  {...props}
                  style={oneDark}
                  language={match[1]}
                  PreTag="div"
                  customStyle={{ margin: 0 }}
                >
                  {String(children).replace(/\n$/, '')}
                </SyntaxHighlighter>
              </div>
            ) : (
              // This is for inline code like `const x = 1`
              <code className="bg-gray-200 dark:bg-gray-700 rounded px-1 py-0.5 font-mono text-sm" {...props}>
                {children}
              </code>
            );
          },
          // Ensuring bold text stands out
          strong: ({ children }) => <strong className="font-bold text-gray-900 dark:text-white">{children}</strong>,
          // Making links safe and styled
          a: ({ href, children }) => (
            <a href={href} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">
              {children}
            </a>
          ),
        }}
      >
        {content}
      </ReactMarkdown>
    </div>
  );
};

export default ChatResponse;