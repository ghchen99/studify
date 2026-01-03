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
          strong: ({ children }) => (
            <strong className="font-semibold text-gray-900">{children}</strong>
          ),
          b: ({ children }) => (
            <b className="font-semibold text-gray-900">{children}</b>
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
          code: (props: any) => {
            const { inline, children } = props;
            if (inline) {
              return (
                <code className="bg-gray-100 px-1 py-0.5 rounded text-sm text-gray-800">
                  {children}
                </code>
              );
            }

            // When not inline, let the `pre` renderer handle block code.
            return <code className="text-sky-200">{children}</code>;
          },
          pre: (props: any) => {
            // `props.children` is typically a <code> element whose props.children is the raw code string
            const codeElement = Array.isArray(props.children) ? props.children[0] : props.children;
            const raw = String(codeElement?.props?.children || '');
            const codeText = raw.replace(/\n$/, '');

            const lines = codeText.split('\n');
            let prevWasPrompt = false;

            const rendered = lines.map((line: string, idx: number) => {
              const promptMatch = line.match(/^(\s*)(>>> |\.\.\. )(.*)$/);
              if (promptMatch) {
                prevWasPrompt = true;
                return (
                  <div key={idx} className="whitespace-pre">
                    <span className="text-green-300 font-semibold">{promptMatch[2]}</span>
                    <span className="text-sky-200">{promptMatch[3]}</span>
                  </div>
                );
              } else {
                if (prevWasPrompt && line.trim() !== '') {
                  prevWasPrompt = false;
                  return (
                    <div key={idx} className="whitespace-pre text-amber-200">{line}</div>
                  );
                }
                prevWasPrompt = false;
                return (
                  <div key={idx} className="whitespace-pre text-sky-200">{line}</div>
                );
              }
            });

            return (
              <pre className="bg-gray-900 p-4 rounded-lg overflow-x-auto mb-4">
                <code className="">{rendered}</code>
              </pre>
            );
          },
        }}
      >
        {content}
      </ReactMarkdown>
    </div>
  );
}
