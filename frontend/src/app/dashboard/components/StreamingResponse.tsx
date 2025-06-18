'use client';

import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';

interface StreamingResponseProps {
  text: string;
  isStreaming?: boolean;
  onStreamComplete?: () => void;
  streamUrl?: string;
  streamData?: any;
}

export const StreamingResponse: React.FC<StreamingResponseProps> = ({
  text,
  isStreaming = true,
  onStreamComplete,
  streamUrl,
  streamData
}) => {
  const [displayedText, setDisplayedText] = useState('');
  const [currentIndex, setCurrentIndex] = useState(0);

  useEffect(() => {
    if (streamUrl && streamData) {
      const eventSource = new EventSource(streamUrl);
      let fullText = '';

      eventSource.onmessage = (event) => {
        try {
          if (event.data && !event.data.startsWith('[ERROR]')) {
            fullText += event.data;
            setDisplayedText(fullText);
          } else if (event.data.startsWith('[ERROR]')) {
            console.error('Streaming error:', event.data);
            onStreamComplete?.();
          }
        } catch (error) {
          console.error('Error parsing SSE data:', error);
        }
      };

      eventSource.onerror = (error) => {
        console.error('SSE Error:', error);
        eventSource.close();
        onStreamComplete?.();
      };

      return () => {
        eventSource.close();
      };
    } else if (!isStreaming) {
      setDisplayedText(text);
      onStreamComplete?.();
      return;
    } else if (currentIndex < text.length) {
      const timeout = setTimeout(() => {
        setDisplayedText(prev => prev + text[currentIndex]);
        setCurrentIndex(prev => prev + 1);
      }, 20); // Adjust speed here (lower = faster)

      return () => clearTimeout(timeout);
    } else {
      onStreamComplete?.();
    }
  }, [currentIndex, text, isStreaming, onStreamComplete, streamUrl, streamData]);

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="prose prose-sm max-w-none dark:prose-invert"
    >
      {displayedText.split('\n').map((line, index) => (
        <React.Fragment key={index}>
          {line}
          <br />
        </React.Fragment>
      ))}
    </motion.div>
  );
}; 