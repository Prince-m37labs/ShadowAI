'use client';

import { useState } from 'react';

export default function DevQAChatPage() {
  const [question, setQuestion] = useState('');
  const [answer, setAnswer] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [copied, setCopied] = useState(false);

  const handleSubmit = async () => {
    setLoading(true);
    setError('');
    setAnswer('');
    setCopied(false);
    try {
      const res = await fetch('http://localhost:8000/ask-qa', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question }),
      });
      if (!res.ok) throw new Error('Claude API error');
      const data = await res.json();
      setAnswer(data.answer);
    } catch (e) {
      setError((e as Error).message || 'Unknown error');
    }
    setLoading(false);
  };

  const handleCopy = () => {
    if (answer) {
      navigator.clipboard.writeText(answer);
      setCopied(true);
      setTimeout(() => setCopied(false), 1200);
    }
  };

  const handleReset = () => {
    setQuestion('');
    setAnswer('');
    setError('');
    setCopied(false);
  };

  return (
    <div className="min-h-screen w-full bg-gradient-to-br from-[#232946] via-[#313866] to-[#a7c7e7] flex items-center justify-center py-12">
      <div className="max-w-2xl w-full p-8 bg-gradient-to-br from-[#232946] to-[#393e6e] rounded-2xl shadow-2xl border border-[#232946] animate-fade-in">
        <h1 className="text-3xl font-extrabold mb-6 text-[#f6f7fb] tracking-tight flex items-center gap-2">
          <span className="animate-bounce">💬</span> Ask Anything (Dev QA)
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
                Thinking…
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
              <span className="animate-bounce">🤖</span> Claude's Answer
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
            <pre className="bg-[#181a2a] text-[#a7e7c7] p-4 rounded-lg overflow-x-auto whitespace-pre-wrap text-base font-mono border border-[#232946] transition-all duration-300 animate-fade-in">
              {answer}
            </pre>
          </div>
        )}
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