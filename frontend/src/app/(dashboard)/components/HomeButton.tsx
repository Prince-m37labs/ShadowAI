'use client';

import Link from 'next/link';

export default function HomeButton() {
  return (
    <Link href="/">
      <button className="fixed top-6 left-6 z-50  to-[#a7c7e7] text-[#232946] px-3 py-3 rounded-lg shadow-lg font-bold text-sm flex items-center gap-2 transition-all duration-300 hover:scale-105 hover:shadow-xl hover:from-[#a7c7e7] hover:to-[#f4acb7] group">
        <span className="text-2xl group-hover:animate-bounce">🏠</span>
        
      </button>
    </Link>
  );
} 