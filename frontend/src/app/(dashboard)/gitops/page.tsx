'use client';

import { useState, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { tomorrow } from 'react-syntax-highlighter/dist/esm/styles/prism';
import type { HTMLAttributes } from 'react';
import HomeButton from '../components/HomeButton';

interface CodeComponentProps extends HTMLAttributes<HTMLElement> {
  inline?: boolean;
}

interface GitScenario {
  [key: string]: string;
}

export default function GitOpsPage() {
  const [task, setTask] = useState('');
  const [command, setCommand] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [copied, setCopied] = useState(false);
  const [scenarios, setScenarios] = useState<GitScenario>({});
  const [selectedScenario, setSelectedScenario] = useState('');
  const [steps, setSteps] = useState<string[]>([]);
  const [beginnerExplanation, setBeginnerExplanation] = useState('');
  const [errorMessage, setErrorMessage] = useState('');
  const [explainTerms, setExplainTerms] = useState(false);

  useEffect(() => {
    // Fetch available scenarios from our own API proxy
    fetch('/api/git-scenarios')
      .then(res => res.json())
      .then(data => setScenarios(data.scenarios))
      .catch(err => console.error('Failed to fetch scenarios:', err));
  }, []);

  // Handles form submission to send task/scenario to backend
  const handleSubmit = async () => {
    if (!task.trim() && !selectedScenario) return;
    
    setLoading(true);
    setError('');
    setCommand('');
    setCopied(false);
    setSteps([]);
    setBeginnerExplanation('');
    // Note: Do not reset errorMessage here, it's part of the input
    
    try {
      const requestBody: Record<string, unknown> = {};
      
      if (selectedScenario) {
        requestBody.scenario_type = selectedScenario;
        if (errorMessage) {
          requestBody.error_message = errorMessage;
        }
      } else {
        requestBody.instruction = task.trim();
      }

      // Add explain_terms to request
      requestBody.explain_terms = explainTerms;

      // Send POST request to our own API proxy
      const res = await fetch('/api/gitops', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(requestBody),
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
      
      if (data.command) {
        setCommand(data.command);
      } else if (data.summary) {
        setCommand(data.summary);
      } else if (data.suggestions && data.suggestions.length > 0) {
        setCommand(data.suggestions.join('\n'));
      } else {
        setCommand('No command generated.');
      }

      if (data.steps && data.steps.length > 0) {
        setSteps(data.steps);
      }
      if (data.beginner_explanation) {
        setBeginnerExplanation(data.beginner_explanation);
      }
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
    setSelectedScenario('');
    setSteps([]);
    setBeginnerExplanation('');
    setErrorMessage('');
    setExplainTerms(false);
  };

  return (
    <div className="min-h-screen w-full bg-gradient-to-br from-[#232946] via-[#313866] to-[#a7c7e7] flex items-center justify-center py-12">
      <HomeButton />
      <div className="max-w-2xl w-full p-10 bg-gradient-to-br from-[#232946] to-[#393e6e] rounded-2xl shadow-2xl border border-[#232946] animate-fade-in text-center">
        <h1 className="text-4xl font-extrabold mb-6 text-[#f6f7fb] tracking-tight flex items-center gap-3 justify-center animate">
          <span className="animate">🔀</span> GitOps via Claude <span className="animate">🌳</span>
        </h1>

        {/* Interactive Scenarios Section */}
        <div className="mb-6">
          <label className="block font-semibold mb-2 text-[#a7adc6] text-left">Common Git Scenarios</label>
          <div className="grid grid-cols-2 gap-2">
            {Object.entries(scenarios).map(([key, value]) => (
              <button
                key={key}
                className={`p-3 text-left rounded-lg border transition ${
                  selectedScenario === key
                    ? 'bg-[#f4acb7] text-[#232946] border-[#f4acb7]'
                    : 'bg-[#232946] text-[#f6f7fb] border-[#393e6e] hover:border-[#f4acb7]'
                }`}
                onClick={() => setSelectedScenario(key)}
              >
                {value}
              </button>
            ))}
          </div>
        </div>

        {/* Error Message Input (shown when error scenario is selected) */}
        {selectedScenario === 'error' && (
          <div className="mb-4">
            <label className="block font-semibold mb-2 text-[#a7adc6] text-left">Error Message</label>
            <textarea
              className="w-full border border-[#393e6e] rounded-lg p-3 bg-[#232946] text-[#f6f7fb] font-mono text-base transition focus:outline-none focus:ring-2 focus:ring-[#f4acb7] placeholder:text-[#f4acb7]/60"
              placeholder="Paste your Git error message here..."
              value={errorMessage}
              onChange={e => setErrorMessage(e.target.value)}
              rows={3}
            />
          </div>
        )}

        {/* Custom Task Input */}
        <div className="mb-6">
          <label className="block font-semibold mb-2 text-[#a7adc6] text-left">Or describe your git task</label>
        <input
            className="w-full border border-[#393e6e] rounded-lg p-3 bg-[#232946] text-[#f6f7fb] font-mono text-base transition focus:outline-none focus:ring-2 focus:ring-[#f4acb7] placeholder:text-[#f4acb7]/60"
          placeholder='e.g. "Create a new branch for the release"'
          value={task}
          onChange={e => setTask(e.target.value)}
        />
        </div>

        {/* Explain Terms Toggle */}
        <div className="mb-6 flex items-center justify-start">
          <label className="relative inline-flex items-center cursor-pointer">
            <input
              type="checkbox"
              className="sr-only peer"
              checked={explainTerms}
              onChange={(e) => setExplainTerms(e.target.checked)}
            />
            <div className="w-11 h-6 bg-[#393e6e] peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-[#f4acb7]/20 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-[#f4acb7]"></div>
            <span className="ml-3 text-[#a7adc6] font-medium">Explain technical terms</span>
          </label>
        </div>

        <div className="flex gap-3 mb-6">
          <button
            className="px-6 py-2 bg-gradient-to-r from-[#f4acb7] to-[#a7c7e7] text-[#232946] font-bold rounded-lg shadow-lg hover:from-[#a7c7e7] hover:to-[#f4acb7] transition flex items-center gap-2 disabled:opacity-60"
            onClick={handleSubmit}
            disabled={loading || (!task.trim() && !selectedScenario)}
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

        {/* Step-by-Step Instructions */}
        {steps.length > 0 && (
          <div className="mt-8 text-left">
            <h2 className="font-semibold mb-2 text-[#a7adc6] flex items-center gap-2">
              <span className="animate">📝</span> Step-by-Step Instructions:
            </h2>
            <div className="space-y-2">
              {steps.map((step, index) => (
                <div key={index} className="bg-[#232946] p-3 rounded-lg border border-[#393e6e]">
                  <ReactMarkdown>{step}</ReactMarkdown>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Beginner Explanation */}
        {beginnerExplanation && (
          <div className="mt-8 text-left">
            <h2 className="font-semibold mb-2 text-[#a7adc6] flex items-center gap-2">
              <span className="animate">🎓</span> For Beginners:
            </h2>
            <div className="bg-[#232946] p-3 rounded-lg border border-[#393e6e]">
              <ReactMarkdown>{beginnerExplanation}</ReactMarkdown>
            </div>
          </div>
        )}

        {/* Command Output */}
        {command && (
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
                {command}
              </ReactMarkdown>
            </div>
          </div>
        </div>
        )}
      </div>
    </div>
  );
}
