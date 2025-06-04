'use client';

import { useState } from 'react';

export default function GitOpsPage() {
  const [instruction, setInstruction] = useState('');
  const [gitCommand, setGitCommand] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setGitCommand('');
    try {
      const res = await fetch('http://localhost:8000/gitops', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ instruction }),
      });
      const data = await res.json();
      setGitCommand(data.git_command || data.content || 'No command returned.');
    } catch (err) {
      setGitCommand('Error fetching git command.');
    }
    setLoading(false);
  };

  return (
    <div className="max-w-xl mx-auto p-6">
      <h1 className="text-2xl font-bold mb-4">GitOps via Claude</h1>
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block font-medium mb-1">Describe your git task</label>
          <input
            className="w-full border rounded p-2"
            type="text"
            value={instruction}
            onChange={e => setInstruction(e.target.value)}
            placeholder='e.g. "Create a new branch for the release"'
            required
          />
        </div>
        <button
          type="submit"
          className="bg-blue-600 text-white px-4 py-2 rounded"
          disabled={loading}
        >
          {loading ? 'Generating...' : 'Generate Git Command'}
        </button>
      </form>
      <div className="mt-6">
        <h2 className="font-semibold mb-2">AI-Generated Git Command:</h2>
        <pre className="bg-gray-900 text-green-200 border rounded p-4 min-h-[48px] whitespace-pre-wrap">
          {loading ? 'Loading...' : gitCommand}
        </pre>
      </div>
    </div>
  );
}