'use client';

import React, { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import { StreamingResponse } from '../components/StreamingResponse';
import HomeButton from '../components/HomeButton';

export default function AskQA() {
  const [question, setQuestion] = useState('');
  const [code, setCode] = useState('');
  const [response, setResponse] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isStreaming, setIsStreaming] = useState(false);
  const [streamUrl, setStreamUrl] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setIsStreaming(true);
    setResponse('');

    try {
      const res = await fetch('http://localhost:8000/ask-qa', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ question, code }),
      });

      if (!res.ok) {
        throw new Error('Network response was not ok');
      }

      // Set up streaming
      const reader = res.body?.getReader();
      if (!reader) {
        throw new Error('No reader available');
      }

      let fullText = '';
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = new TextDecoder().decode(value);
        console.log('Received chunk:', chunk); // Debug log
        const lines = chunk.split('\n');
        
        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = line.slice(6);
            console.log('Processing data line:', data); // Debug log
            // Handle error messages
            if (data.startsWith('[ERROR]')) {
              console.error('Streaming error:', data);
              setResponse('An error occurred during streaming.');
              break;
            }
            // Add the text content directly
            fullText += data;
            console.log('Updated fullText:', fullText); // Debug log
            setResponse(fullText);
          }
        }
      }

      setIsStreaming(false);
    } catch (error) {
      console.error('Error:', error);
      setResponse('An error occurred while processing your request.');
      setIsStreaming(false);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <HomeButton />
      <h1 className="text-2xl font-bold mb-6">Developer Q&A</h1>
      
      <form onSubmit={handleSubmit} className="space-y-4 mb-8">
        <div>
          <label htmlFor="question" className="block text-sm font-medium mb-2">
            Your Question
          </label>
          <textarea
            id="question"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            className="w-full p-2 border rounded-md dark:bg-gray-800 dark:border-gray-700"
            rows={3}
            placeholder="Ask a question about your code..."
            required
          />
        </div>

        <div>
          <label htmlFor="code" className="block text-sm font-medium mb-2">
            Code (optional)
          </label>
          <textarea
            id="code"
            value={code}
            onChange={(e) => setCode(e.target.value)}
            className="w-full p-2 border rounded-md font-mono text-sm dark:bg-gray-800 dark:border-gray-700"
            rows={10}
            placeholder="Paste your code here..."
          />
        </div>

        <button
          type="submit"
          disabled={isLoading}
          className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
        >
          {isLoading ? 'Processing...' : 'Ask Question'}
        </button>
      </form>

      {response && (
        <div className="mt-8 p-4 border rounded-md dark:border-gray-700">
          <h2 className="text-xl font-semibold mb-4">Response</h2>
          <div className="prose prose-sm max-w-none dark:prose-invert">
            <ReactMarkdown>{response}</ReactMarkdown>
          </div>
          {isStreaming && (
            <div className="mt-2 text-sm text-gray-500">
              <span className="animate-pulse">●</span> Streaming...
            </div>
          )}
        </div>
      )}
    </div>
  );
} 