'use client';

import React, { useState } from 'react';
import HomeButton from '../components/HomeButton';
import { codePatterns } from '../../../constant/qaConstants';

// Custom component to render text and code blocks
const TextCodeRenderer = ({ content }: { content: string }) => {
  // First try to split by markdown code blocks
  let blocks = content.split(/(```[\s\S]*?```)/g);
  
  // If no markdown blocks found, try to detect code patterns
  if (blocks.length === 1 && !blocks[0].includes('```')) {
    // Use imported codePatterns to split text into code and text blocks
    const text = blocks[0];
    const newBlocks: string[] = [];
    let lastIndex = 0;
    
    // Find all code matches
    const matches: Array<{start: number, end: number, text: string}> = [];
    
    codePatterns.forEach(pattern => {
      let match;
      while ((match = pattern.exec(text)) !== null) {
        matches.push({
          start: match.index,
          end: match.index + match[0].length,
          text: match[0]
        });
      }
    });
    
    // Sort matches by start position
    matches.sort((a, b) => a.start - b.start);
    
    // Merge overlapping matches
    const mergedMatches: Array<{start: number, end: number, text: string}> = [];
    for (const match of matches) {
      if (mergedMatches.length === 0 || match.start > mergedMatches[mergedMatches.length - 1].end) {
        mergedMatches.push(match);
      } else {
        // Extend the last match
        mergedMatches[mergedMatches.length - 1].end = Math.max(
          mergedMatches[mergedMatches.length - 1].end,
          match.end
        );
        mergedMatches[mergedMatches.length - 1].text = text.substring(
          mergedMatches[mergedMatches.length - 1].start,
          mergedMatches[mergedMatches.length - 1].end
        );
      }
    }
    
    // Build blocks from text and code
    for (const match of mergedMatches) {
      // Add text before code
      if (match.start > lastIndex) {
        const textBlock = text.substring(lastIndex, match.start).trim();
        if (textBlock) {
          newBlocks.push(textBlock);
        }
      }
      
      // Add code block
      newBlocks.push(`\`\`\`\n${match.text}\n\`\`\``);
      lastIndex = match.end;
    }
    
    // Add remaining text
    if (lastIndex < text.length) {
      const remainingText = text.substring(lastIndex).trim();
      if (remainingText) {
        newBlocks.push(remainingText);
      }
    }
    
    blocks = newBlocks;
  }
  
  return (
    <div className="space-y-4">
      {blocks.map((block, index) => {
        if (block.startsWith('```') && block.endsWith('```')) {
          // This is a code block
          const codeContent = block.slice(3, -3);
          const lines = codeContent.split('\n');
          const language = lines[0].trim() || 'text';
          const actualCode = lines.slice(1).join('\n');
          
          return (
            <div key={index} className="bg-gray-100 dark:bg-gray-800 rounded-lg p-4 border border-gray-200 dark:border-gray-700">
              <div className="text-xs text-gray-500 mb-2 font-mono bg-gray-200 dark:bg-gray-700 px-2 py-1 rounded inline-block">
                {language}
              </div>
              <pre className="text-sm overflow-x-auto">
                <code className="font-mono text-gray-800 dark:text-gray-200">{actualCode}</code>
              </pre>
            </div>
          );
        } else {
          // This is text content
          return (
            <div key={index} className="text-gray-800 dark:text-gray-200 leading-relaxed whitespace-pre-wrap">
              {block}
            </div>
          );
        }
      })}
    </div>
  );
};

// Main component for the AskQA page
export default function AskQA() {
  // State for the user's question input
  const [question, setQuestion] = useState('');
  // State for the user's code input
  const [code, setCode] = useState('');
  // State for the response from the backend
  const [response, setResponse] = useState<string>('');
  // State to indicate if the request is loading
  const [isLoading, setIsLoading] = useState(false);

  // Handles form submission to send question/code to backend
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setResponse('');

    try {
      // Send POST request to the local API proxy for AskQA
      const res = await fetch('/api/ask-qa', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ question, code }),
      });

      if (!res.ok) {
        throw new Error('Network response was not ok');
      }

      // Debug: Check what we're actually getting
      const contentType = res.headers.get('content-type');
      console.log('Content-Type:', contentType);
      
      // Parse the response and clean up code block markers
      const data = await res.json();
      const raw = data.response || data.message || '';
      const cleaned = raw.replace(/```/g, "'''");  // retain newline structure
      setResponse(cleaned);
    } catch (error) {
      // Handle errors gracefully
      console.error('Error:', error);
      setResponse('An error occurred while processing your request.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="container mx-auto px-4 py-8">
      {/* Home navigation button */}
      <HomeButton />
      <h1 className="text-2xl font-bold mb-6">Developer Q&A</h1>
      
      {/* Form for user to submit question and code */}
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

        {/* Submit button, shows loading state if request is in progress */}
        <button
          type="submit"
          disabled={isLoading}
          className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
        >
          {isLoading ? 'Processing...' : 'Ask Question'}
        </button>
      </form>

      {/* Display the response from the backend, if available */}
      {response && (
        <div className="mt-8 p-4 border rounded-md dark:border-gray-700">
          <h2 className="text-xl font-semibold mb-4">Response</h2>
          <TextCodeRenderer content={response} />
        </div>
      )}
    </div>
  );
}