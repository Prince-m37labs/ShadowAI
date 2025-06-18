'use client';

import { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';
import type { HTMLAttributes } from 'react';
import HomeButton from '../dashboard/components/HomeButton';

interface CodeComponentProps extends HTMLAttributes<HTMLElement> {
  inline?: boolean;
}

const PROMPT_TEMPLATES = [
  "Explain this code in simple terms.",
  "What does this function do?",
  "Summarize the logic of the following code.",
  "Convert this code into TypeScript.",
];

export default function PromptExplorerPage() {
  const [selectedPrompt, setSelectedPrompt] = useState(PROMPT_TEMPLATES[0]);
  const [prompt, setPrompt] = useState(PROMPT_TEMPLATES[0]);
  const [response, setResponse] = useState('');
  const [loading, setLoading] = useState(false);

  const handleTemplateChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    setSelectedPrompt(e.target.value);
    setPrompt(e.target.value);
  };

  const handleRunPrompt = async () => {
    setLoading(true);
    setResponse('');
    try {
      // Use the ask-qa endpoint instead of claude-qa
      const res = await fetch('http://localhost:8000/ask-qa', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: prompt, code: '' }),
      });
      
      if (!res.ok) {
        throw new Error('Failed to get response');
      }

      // Handle streaming response
      const reader = res.body?.getReader();
      if (!reader) {
        throw new Error('No reader available');
      }

      let fullText = '';
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = new TextDecoder().decode(value);
        const lines = chunk.split('\n');
        
        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = line.slice(6);
            // Handle error messages
            if (data.startsWith('[ERROR]')) {
              console.error('Streaming error:', data);
              throw new Error('An error occurred during streaming.');
            }
            // Add the text content directly
            fullText += data;
            setResponse(fullText);
          }
        }
      }
    } catch (err) {
      setResponse('Error fetching response.');
    }
    setLoading(false);
  };

  return (
    <div className="max-w-2xl mx-auto p-6">
      <HomeButton />
      <h1 className="text-2xl font-bold mb-4">Prompt Explorer</h1>
      <div className="mb-4">
        <label className="block font-medium mb-1">Choose a prompt template</label>
        <select
          className="w-full border rounded p-2"
          value={selectedPrompt}
          onChange={handleTemplateChange}
        >
          {PROMPT_TEMPLATES.map((tpl, idx) => (
            <option key={idx} value={tpl}>
              {tpl}
            </option>
          ))}
        </select>
      </div>
      <div className="mb-4">
        <label className="block font-medium mb-1">Edit your prompt</label>
        <textarea
          className="w-full border rounded p-2"
          rows={4}
          value={prompt}
          onChange={e => setPrompt(e.target.value)}
        />
      </div>
      <button
        className="bg-blue-600 text-white px-4 py-2 rounded"
        onClick={handleRunPrompt}
        disabled={loading}
      >
        {loading ? 'Running...' : 'Run Prompt'}
      </button>
      <div className="mt-6">
        <h2 className="font-semibold mb-2">Claude's Response:</h2>
        <div className="prose prose-invert max-w-none">
          <ReactMarkdown
            components={{
              code: ({ inline, className, children, ...props }: CodeComponentProps) => {
                const match = /language-(\w+)/.exec(className || '');
                return !inline && match ? (
                  <SyntaxHighlighter
                    style={vscDarkPlus as any}
                    language={match[1]}
                    PreTag="div"
                    {...props}
                  >
                    {String(children).replace(/\n$/, '')}
                  </SyntaxHighlighter>
                ) : (
                  <code className={className} {...props}>
                    {children}
                  </code>
                );
              }
            }}
          >
            {loading ? 'Loading...' : response}
          </ReactMarkdown>
        </div>
      </div>
    </div>
  );
}