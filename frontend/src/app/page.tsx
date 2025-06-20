'use client';

import Link from 'next/link';
import { useEffect } from 'react';
import { HOME_FEATURES } from '../constant/homeConstants';

export default function Home() {
  useEffect(() => {
    if (typeof window === 'undefined') return;
    // Use imported HOME_FEATURES for the typewriter animation
    const features = HOME_FEATURES;
    let idx = 0;
    let char = 0;
    let currentLine = 0;
    let timeoutId: ReturnType<typeof setTimeout>;
    const container = document.getElementById('typewriter-multiline');
    if (!container) return;
    container.innerHTML = '';
    function typeLine(lineIdx: number) {
      if (!container) return;
      // Create or get the span for this line
      let lineSpan = container.querySelector(`span[data-line="${lineIdx}"]`) as HTMLSpanElement;
      if (!lineSpan) {
        lineSpan = document.createElement('span');
        lineSpan.setAttribute('data-line', String(lineIdx));
        container.appendChild(lineSpan);
      }
      let text = features[lineIdx];
      let typed = lineSpan.textContent || '';
      if (typed.length < text.length) {
        lineSpan.textContent = text.slice(0, typed.length + 1);
        timeoutId = setTimeout(() => typeLine(lineIdx), 55); // slower typing
      } else {
        lineSpan.classList.add('filled');
        if (lineIdx + 1 < features.length) {
          timeoutId = setTimeout(() => typeLine(lineIdx + 1), 600);
        } else {
          // After all lines, pause, then reset
          timeoutId = setTimeout(() => {
            container.innerHTML = '';
            setTimeout(() => typeLine(0), 800);
          }, 1800);
        }
      }
    }
    typeLine(0);
    return () => clearTimeout(timeoutId);
  }, []);

  return (
    <div className="min-h-screen w-full bg-gradient-to-br from-[#232946] via-[#313866] to-[#a7c7e7] flex flex-col items-center justify-center py-16 animate-fade-in relative overflow-hidden">
      {/* AI Features Typing Animation - multiline, left-aligned, more space before ShadowAI */}
      <div className="absolute top-8 left-0 w-full flex flex-col items-start pl-10 pointer-events-none z-0">
        <div id="typewriter-multiline" className="flex flex-col items-start gap-0.5"></div>
      </div>
      <div className="max-w-3xl w-full p-10 mt-32 bg-gradient-to-br from-[#232946] to-[#393e6e] rounded-3xl shadow-2xl border border-[#232946] flex flex-col items-center gap-8 animate-fade-in">
        <h1 className="text-4xl md:text-5xl font-extrabold text-[#f6f7fb] tracking-tight flex items-center gap-4 hover:animate-move-on-hover ">
          <span className="text-5xl md:text-6xl animate-bounce-slow">🚀</span>
          Welcome to <span className="text-[#f4acb7] animate-gradient">ShadowAI</span>
          
        </h1>
        <p className="text-lg md:text-xl text-[#a7adc6] text-center max-w-2xl animate-fade-in">
          {/*<span className="mr-2 animate-bounce">🤖</span>*/}
          Your all in one AI-powered developer assistant for code refactoring, documentation, security, GitOps, and more.
        </p>
        <div className="flex flex-wrap gap-6 justify-center mt-4 animate-fade-in">
          <Link href="/refactor">
            <div className="group bg-gradient-to-br from-[#f4acb7] to-[#a7c7e7] text-[#232946] px-6 py-4 rounded-xl shadow-lg font-bold text-lg flex items-center gap-2 transition cursor-pointer hover:animate-move-on-hover">
              <span className="text-2xl group-hover:animate-bounce">🛠️</span> Refactor
            </div>
          </Link>
          <Link href="/devqa">
            <div className="group bg-gradient-to-br from-[#a7e7c7] to-[#f4acb7] text-[#232946] px-6 py-4 rounded-xl shadow-lg font-bold text-lg flex items-center gap-2 transition cursor-pointer hover:animate-move-on-hover">
              <span className="text-2xl group-hover:animate-bounce">💬</span> Ask Anything
            </div>
          </Link>
          <Link href="/gitops">
            <div className="group bg-gradient-to-br from-[#f4acb7] to-[#393e6e] text-[#232946] px-6 py-4 rounded-xl shadow-lg font-bold text-lg flex items-center gap-2 transition cursor-pointer hover:animate-move-on-hover">
              <span className="text-2xl group-hover:animate-bounce">🔀</span> GitOps
            </div>
          </Link>
          <Link href="/screen-assist">
            <div className="group bg-gradient-to-br from-[#a7c7e7] to-[#393e6e] text-[#232946] px-6 py-4 rounded-xl shadow-lg font-bold text-lg flex items-center gap-2 transition cursor-pointer hover:animate-move-on-hover">
              <span className="text-2xl group-hover:animate-bounce">🖼️</span> Screen Assist
            </div>
          </Link>
        </div>
        <div className="mt-8 flex flex-col items-center gap-2 animate-fade-in">
          <span className="text-[#a7adc6] text-lg flex items-center gap-2 group hover:animate-move-on-hover">
            <span className="animate-spin-slow">🌐</span> Built with Next.js, FastAPI, Claude, and MongoDB
          </span>
          <span className="text-[#a7adc6] text-base flex items-center gap-2 group hover:animate-move-on-hover">
            <span>✨</span> Designed for productivity and joy
          </span>
        </div>
      </div>
      <footer className="w-full flex justify-center items-center py-6 mt-10 text-xs text-[#232946] font-mono select-none z-10">
        <span>&copy; {new Date().getFullYear()} M37 labs. All rights reserved. | ShadowAI is a developer assistant project by Master Prince. For more info, contact: prince@m37labs.com</span>
      </footer>
    </div>
  );
}
