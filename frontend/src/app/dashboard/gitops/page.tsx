'use client';

import { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';
import type { HTMLAttributes } from 'react';

interface CodeComponentProps extends HTMLAttributes<HTMLElement> {
  inline?: boolean;
}

export default function GitOpsPage() {
  const [task, setTask] = useState('');
  const [command, setCommand] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [copied, setCopied] = useState(false);

  const handleSubmit = async () => {
    if (!task.trim()) return;
    
    setLoading(true);
    setError('');
    setCommand('');
    setCopied(false);
    
    try {
      const res = await fetch('http://localhost:8000/gitops', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ instruction: task.trim() }),
      });
      
      const data = await res.json();
      
      if (!res.ok) {
        throw new Error(data.detail || data.error || 'Failed to get response');
      }
      
      if (data.error) {
        throw new Error(data.error);
      }
      
      if (data.warnings && data.warnings.length > 0) {
        setError(data.warnings.join('\n'));
      }
      
      setCommand(data.command || data.summary || data.suggestions?.join('\n') || 'No command generated.');
    } catch (e) {
      const errorMessage = e instanceof Error ? e.message : 'An unknown error occurred';
      setError(errorMessage);
      console.error('GitOps Error:', e);
    } finally {
      setLoading(false);
    }
  };

  const handleCopy = () => {
    if (command) {
      navigator.clipboard.writeText(command);
      setCopied(true);
      setTimeout(() => setCopied(false), 1200);
    }
  };

  const handleReset = () => {
    setTask('');
    setCommand('');
    setError('');
    setCopied(false);
  };

  return (
    <div className="min-h-screen w-full bg-gradient-to-br from-[#232946] via-[#313866] to-[#a7c7e7] flex items-center justify-center py-12">
      <div className="max-w-2xl w-full p-10 bg-gradient-to-br from-[#232946] to-[#393e6e] rounded-2xl shadow-2xl border border-[#232946] animate-fade-in text-center">
        <h1 className="text-4xl font-extrabold mb-6 text-[#f6f7fb] tracking-tight flex items-center gap-3 justify-center animate">
          <span className="animate">🔀</span> GitOps via Claude <span className="animate">🌳</span>
        </h1>
        <label className="block font-semibold mb-2 text-[#a7adc6] text-left">Describe your git task</label>
        <input
          className="w-full border border-[#393e6e] rounded-lg p-3 bg-[#232946] text-[#f6f7fb] font-mono text-base transition focus:outline-none focus:ring-2 focus:ring-[#f4acb7] placeholder:text-[#f4acb7]/60 mb-4"
          placeholder='e.g. "Create a new branch for the release"'
          value={task}
          onChange={e => setTask(e.target.value)}
        />
        <div className="flex gap-3 mb-6">
          <button
            className="px-6 py-2 bg-gradient-to-r from-[#f4acb7] to-[#a7c7e7] text-[#232946] font-bold rounded-lg shadow-lg hover:from-[#a7c7e7] hover:to-[#f4acb7] transition flex items-center gap-2 disabled:opacity-60"
            onClick={handleSubmit}
            disabled={loading || !task.trim()}
          >
            {loading ? (
              <span className="flex items-center gap-2 animate-pulse">
                <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24"><circle className="opacity-25" cx="12" cy="12" r="10" stroke="#f4acb7" strokeWidth="4" fill="none" /><path className="opacity-75" fill="#f4acb7" d="M4 12a8 8 0 018-8v8z" /></svg>
                Generating…
              </span>
            ) : (
              <>
                <span className="animate-wiggle">🚀</span> Generate Git Command
              </>
            )}
          </button>
          <button
            className="px-6 py-2 bg-[#232946] text-[#a7adc6] font-semibold rounded-lg border border-[#393e6e] hover:bg-[#393e6e] transition"
            onClick={handleReset}
            disabled={loading && !task && !command}
          >
            <span className="mr-1">♻️</span>Reset
          </button>
        </div>
        {error && (
          <div className="mt-2 text-[#ffb4b4] bg-[#393e6e] border border-[#ffb4b4]/30 rounded-lg p-3 font-medium flex items-center gap-2 animate-shake">
            <span>❌</span> {error}
          </div>
        )}
        <div className="mt-8 text-left">
          <h2 className="font-semibold mb-2 text-[#a7adc6] flex items-center gap-2">
            <span className="animate">🤖</span> AI-Generated Git Command:
          </h2>
          <div className="relative">
            <button
              className={`absolute top-2 right-2 px-3 py-1 text-xs font-semibold rounded transition flex items-center gap-1 ${copied ? 'bg-[#a7e7c7] text-[#232946]' : 'bg-[#f4acb7] text-[#232946] hover:bg-[#a7c7e7]'}`}
              onClick={handleCopy}
              title="Copy to clipboard"
              disabled={!command}
            >
              {copied ? (
                <span className="animate-pulse">✅ Copied</span>
              ) : (
                <>
                  <span>📋</span> Copy
                </>
              )}
            </button>
            <div className="prose prose-invert max-w-none min-h-[48px]">
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
                {command}
              </ReactMarkdown>
            </div>
          </div>
        </div>
        <style jsx global>{`
          @keyframes fade-in {
            0% { opacity: 0; transform: translateY(16px); }
            100% { opacity: 1; transform: none; }
          }
          .animate-fade-in { animation: fade-in 0.7s cubic-bezier(.4,0,.2,1) both; }
          @keyframes wiggle {
            0%, 100% { transform: rotate(-3deg); }
            50% { transform: rotate(3deg); }
          }
          .animate-wiggle { animation: wiggle 0.7s infinite; display: inline-block; }
          @keyframes bounce-slow {
            0%, 100% { transform: translateY(0); }
            50% { transform: translateY(-12px); }
          }
          .animate-bounce-slow { animation: bounce-slow 2.2s infinite; display: inline-block; }
          @keyframes spin-slow {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
          }
          .animate-spin-slow { animation: spin-slow 6s linear infinite; display: inline-block; }
          @keyframes shake {
            0%, 100% { transform: translateX(0); }
            20%, 60% { transform: translateX(-6px); }
            40%, 80% { transform: translateX(6px); }
          }
          .animate-shake { animation: shake 0.5s; }
        `}</style>
      </div>
    </div>
  );
}
