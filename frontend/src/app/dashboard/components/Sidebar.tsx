// app/_components/Sidebar.tsx
import Link from "next/link";

const links = [
  { href: "/refactor", label: "🛠 Refactor Code" },
  { href: "/explorer", label: "🔍 Prompt Explorer" },
  { href: "/devqa", label: "🤖 Claude Dev QA" },
  { href: "/gitops", label: "🧬 GitOps" },
];

export default function Sidebar() {
  return (
    <aside className="w-64 h-screen bg-gray-100 p-4">
      <nav className="flex flex-col space-y-2">
        <Link href="/dashboard">🏠 Dashboard</Link>
        {links.map((link) => (
          <Link key={link.href} href={link.href}>
            {link.label}
          </Link>
        ))}
      </nav>
    </aside>
  );
}