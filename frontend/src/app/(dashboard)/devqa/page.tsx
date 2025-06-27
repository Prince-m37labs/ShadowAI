'use client';

import { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { tomorrow } from 'react-syntax-highlighter/dist/esm/styles/prism';
import type { HTMLAttributes } from 'react';
import HomeButton from '../components/HomeButton';
// Remove the import of DEVQA_ENDPOINT and define it as a constant
const DEVQA_ENDPOINT = '/api/ask-qa';

interface CodeComponentProps extends HTMLAttributes<HTMLElement> {
  inline?: boolean;
}

export default function DevQAChatPage() {
  // State for the user's question input
  const [question, setQuestion] = useState('');
  // State for the answer from the backend
  const [answer, setAnswer] = useState('');
  // State to indicate if the request is loading
  const [loading, setLoading] = useState(false);
  // State for error messages
  const [error, setError] = useState('');
  // State to indicate if the answer was copied
  const [copied, setCopied] = useState(false);

  // Handles form submission to send question to backend
  const handleSubmit = async () => {
    if (!question.trim()) return;
    
    setLoading(true);
    setError('');
    setAnswer('');
    setCopied(false);
    
    try {
      console.log('Sending request to backend...');
      // Send POST request to the DevQA backend endpoint
      const res = await fetch(DEVQA_ENDPOINT, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: question.trim() }),
      });
      
      console.log('Response status:', res.status);
      
      if (!res.ok) {
        const errorData = await res.json();
        throw new Error(errorData.error || 'Failed to get response');
      }

      // Handle non-streaming response
      const data = await res.json();
      const cleaned = (data.response || '')
        .replace(/'''(\w+)?/g, '```$1')  // convert '''python back to ```python
        .replace(/'''/g, '```');         // convert all other ''' back to ```
      setAnswer(cleaned);
    } catch (e) {
      // Handle errors gracefully
      const errorMessage = e instanceof Error ? e.message : 'An unknown error occurred';
      console.error('DevQA Error:', e);
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  // Handles copying the answer to clipboard
  const handleCopy = () => {
    if (answer) {
      navigator.clipboard.writeText(answer);
      setCopied(true);
      setTimeout(() => setCopied(false), 1200);
    }
  };

  // Handles resetting the form
  const handleReset = () => {
    setQuestion('');
    setAnswer('');
    setError('');
    setCopied(false);
  };

  return (
    <div className="min-h-screen w-full bg-gradient-to-br from-[#232946] via-[#313866] to-[#a7c7e7] flex items-center justify-center py-12">
      <HomeButton />
      <div className="max-w-2xl w-full p-8 bg-gradient-to-br from-[#232946] to-[#393e6e] rounded-2xl shadow-2xl border border-[#232946] animate-fade-in">
        <h1 className="text-3xl font-extrabold mb-6 text-[#f6f7fb] tracking-tight flex items-center gap-2">
          <span className="animate">💬</span> Ask Anything (Dev QA)
        </h1>
        <textarea
          className="w-full border border-[#393e6e] rounded-lg p-3 bg-[#232946] text-[#f6f7fb] font-mono text-base transition min-h-[100px] focus:outline-none focus:ring-2 focus:ring-[#f4acb7] placeholder:text-[#f4acb7]/60"
          rows={5}
          placeholder="Ask any developer question... 🤔"
          value={question}
          onChange={e => setQuestion(e.target.value)}
        />
        <div className="flex gap-3 mt-5">
          <button
            className="px-5 py-2 bg-gradient-to-r from-[#f4acb7] to-[#a7c7e7] text-[#232946] font-bold rounded-lg shadow-lg hover:from-[#a7c7e7] hover:to-[#f4acb7] transition disabled:opacity-60 flex items-center gap-2"
            onClick={handleSubmit}
            disabled={loading || !question.trim()}
          >
            {loading ? (
              <span className="flex items-center gap-2 animate-pulse">
                <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24"><circle className="opacity-25" cx="12" cy="12" r="10" stroke="#f4acb7" strokeWidth="4" fill="none" /><path className="opacity-75" fill="#f4acb7" d="M4 12a8 8 0 018-8v8z" /></svg>
                Thinking&hellip;
              </span>
            ) : (
              <>
                <span className="animate-wiggle">🚀</span> Ask
              </>
            )}
          </button>
          <button
            className="px-5 py-2 bg-[#232946] text-[#a7adc6] font-semibold rounded-lg border border-[#393e6e] hover:bg-[#393e6e] transition"
            onClick={handleReset}
            disabled={loading && !question && !answer}
          >
            <span className="mr-1">♻️</span>Reset
          </button>
        </div>
        {error && (
          <div className="mt-5 text-[#ffb4b4] bg-[#393e6e] border border-[#ffb4b4]/30 rounded-lg p-3 font-medium flex items-center gap-2 animate-shake">
            <span>❌</span> {error}
          </div>
        )}
        {answer && (
          <div className="mt-8 bg-gradient-to-br from-[#393e6e] to-[#232946] p-5 rounded-xl border border-[#393e6e] relative shadow-lg animate-fade-in">
            <h2 className="font-semibold mb-3 text-[#a7adc6] flex items-center gap-2">
              <span className="animate-bounce">🤖</span> Claude&apos;s Answer
            </h2>
            <button
              className={`absolute top-5 right-5 px-3 py-1 text-xs font-semibold rounded transition flex items-center gap-1 ${copied ? 'bg-[#a7e7c7] text-[#232946]' : 'bg-[#f4acb7] text-[#232946] hover:bg-[#a7c7e7]'}`}
              onClick={handleCopy}
              title="Copy to clipboard"
            >
              {copied ? (
                <>
                  <span className="animate-pulse">✅</span> Copied
                </>
              ) : (
                <>
                  <span>📋</span> Copy
                </>
              )}
            </button>
            <div className="prose prose-invert max-w-none">
              <ReactMarkdown
                components={{
                  code: ({ inline, className, children, ...props }: CodeComponentProps) => {
                    const match = /language-(\w+)/.exec(className || '');
                    if (!inline) {
                      return (
                        <SyntaxHighlighter
                          language={match ? match[1] : undefined}
                          style={tomorrow}
                          PreTag="div"
                          customStyle={{
                            fontFamily:
                              "var(--font-geist-mono), 'Fira Mono', 'Menlo', 'Monaco', 'Consolas', 'Liberation Mono', 'Courier New', monospace",
                            borderRadius: '0.5rem',
                            padding: '1rem',
                            fontSize: '0.9rem'
                          }}
                        >
                          {String(children).replace(/\n$/, '')}
                        </SyntaxHighlighter>
                      );
                    }
                    return (
                      <code
                        className={className}
                        style={{
                          fontFamily:
                            "var(--font-geist-mono), 'Fira Mono', 'Menlo', 'Monaco', 'Consolas', 'Liberation Mono', 'Courier New', monospace",
                          backgroundColor: '#2d2d2d',
                          padding: '0.2em 0.4em',
                          borderRadius: '0.3em',
                          fontSize: '0.9em'
                        }}
                        {...props}
                      >
                        {children}
                      </code>
                    );
                  }
                }}
              >
                {answer}
              </ReactMarkdown>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}