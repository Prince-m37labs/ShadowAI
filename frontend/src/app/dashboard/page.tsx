'use client';

import { useEffect, useState } from 'react';
import ModuleCard from './components/ModuleCard';

export default function DashboardPage() {
  const [modules, setModules] = useState([]);

  useEffect(() => {
    fetch('http://localhost:8000/modules')
      .then(res => res.json())
      .then(data => setModules(data));
  }, []);

  return (
    <main className="p-6">
      <h1 className="text-2xl font-bold mb-4">Dashboard</h1>
      <div className="grid gap-4 sm:grid-cols-2 md:grid-cols-3">
        {modules.map((mod: any, index: number) => (
          <ModuleCard
            key={index}
            title={mod.title}
            description={mod.description}
            status={mod.status}
          />
        ))}
      </div>
    </main>
  );
}