'use client';

import React from 'react';

interface ModuleCardProps {
  title: string;
  description: string;
  status?: 'active' | 'inactive' | 'coming-soon';
}

const statusColor = {
  active: 'bg-green-100 text-green-700',
  inactive: 'bg-gray-100 text-gray-600',
  'coming-soon': 'bg-yellow-100 text-yellow-700',
};

const ModuleCard: React.FC<ModuleCardProps> = ({ title, description, status = 'active' }) => {
  return (
    <div className="p-4 border rounded-lg shadow-sm hover:shadow-md transition duration-200 bg-white dark:bg-neutral-900">
      <div className="flex justify-between items-center mb-2">
        <h2 className="text-lg font-semibold">{title}</h2>
        <span className={`text-xs px-2 py-1 rounded ${statusColor[status]}`}>
          {status.replace('-', ' ')}
        </span>
      </div>
      <p className="text-sm text-gray-600 dark:text-gray-300">{description}</p>
    </div>
  );
};

export default ModuleCard;