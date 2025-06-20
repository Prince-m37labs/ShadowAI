interface ModuleCardProps {
  title: string;
  description: string;
  status: string;
}

export default function ModuleCard({ title, description, status }: ModuleCardProps) {
  return (
    <div className="p-4 border rounded-lg shadow-sm">
      <h2 className="text-lg font-semibold">{title}</h2>
      <p className="text-gray-600 mt-2">{description}</p>
      <span className={`inline-block mt-2 px-2 py-1 text-sm rounded ${
        status === 'active' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
      }`}>
        {status}
      </span>
    </div>
  );
} 