'use client';

import { useState } from 'react';

export default function DevQAPage() {
  const [context, setContext] = useState('');
  const [question, setQuestion] = useState('');
  const [response, setResponse] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setResponse('');
    try {
      const res = await fetch('http://localhost:8000/claude-qa', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ context, question }),
      });
      const data = await res.json();
      console.log(data); // 🌟 Log the response structure
      // Support both { answer: ... } and { content: ... }
      setResponse(data.answer || data.content || 'No answer received.');
    } catch (err) {
      setResponse('Error fetching response.');
    }
    setLoading(false);
  };

  return (
    <div className="max-w-2xl mx-auto p-6">
      <h1 className="text-2xl font-bold mb-4">Claude Dev QA</h1>
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block font-medium mb-1">Context</label>
          <textarea
            className="w-full border rounded p-2"
            rows={5}
            value={context}
            onChange={e => setContext(e.target.value)}
            placeholder="Paste code or context here..."
            required
          />
        </div>
        <div>
          <label className="block font-medium mb-1">Question</label>
          <input
            className="w-full border rounded p-2"
            type="text"
            value={question}
            onChange={e => setQuestion(e.target.value)}
            placeholder="Ask a question about the context..."
            required
          />
        </div>
        <button
          type="submit"
          className="bg-blue-600 text-white px-4 py-2 rounded"
          disabled={loading}
        >
          {loading ? 'Asking...' : 'Ask Claude'}
        </button>
      </form>
      <div className="mt-6">
        <h2 className="font-semibold mb-2">Claude's Response:</h2>
        {/* 🌟 Use <pre> to preserve formatting */}
        <pre className="bg-gray-100 border rounded p-4 min-h-[48px] whitespace-pre-wrap">
          {loading ? 'Loading...' : response}
        </pre>
      </div>
    </div>
  );
}