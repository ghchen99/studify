'use client';

import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import remarkMath from 'remark-math';
import rehypeKatex from 'rehype-katex';

import 'katex/dist/katex.min.css';

export default function MarkdownRenderer({ content }: { content: string }) {
  return (
    <div className="prose prose-blue max-w-none">
      <ReactMarkdown
        remarkPlugins={[remarkGfm, remarkMath]}
        rehypePlugins={[rehypeKatex]}
        components={{
          ul: ({ children }) => (
            <ul className="list-disc pl-6 mb-4 marker:text-gray-500">
              {children}
            </ul>
          ),
          ol: ({ children }) => (
            <ol className="list-decimal pl-6 mb-4 marker:text-gray-500">
              {children}
            </ol>
          ),
          li: ({ children }) => (
            <li className="mb-1 leading-relaxed">
              {children}
            </li>
          ),
          h1: ({ children }) => (
            <h1 className="text-3xl font-bold mt-6 mb-4">{children}</h1>
          ),
          h2: ({ children }) => (
            <h2 className="text-2xl font-semibold mt-6 mb-3">{children}</h2>
          ),
          h3: ({ children }) => (
            <h3 className="text-xl font-semibold mt-5 mb-2">{children}</h3>
          ),
          p: ({ children }) => (
            <p className="leading-relaxed mb-4">{children}</p>
          ),
          table: ({ children }) => (
            <table className="border-collapse border border-gray-300 my-4">
              {children}
            </table>
          ),
          th: ({ children }) => (
            <th className="border border-gray-300 px-3 py-2 bg-gray-100">
              {children}
            </th>
          ),
          td: ({ children }) => (
            <td className="border border-gray-300 px-3 py-2">
              {children}
            </td>
          ),
          code: ({ children }) => (
            <code className="bg-gray-100 px-1 py-0.5 rounded text-sm">
              {children}
            </code>
          ),
          pre: ({ children }) => (
            <pre className="bg-gray-900 text-gray-100 p-4 rounded-lg overflow-x-auto mb-4">
              {children}
            </pre>
          ),
        }}
      >
        {content}
      </ReactMarkdown>
    </div>
  );
}
