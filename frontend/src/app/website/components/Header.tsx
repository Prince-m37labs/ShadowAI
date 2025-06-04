// app/_components/Header.tsx
import Link from "next/link";

export default function Header() {
  return (
    <header className="flex justify-between p-4 bg-gray-800 text-white">
      <Link href="/">Home</Link>
      <div className="space-x-4">
        <Link href="/login">Login</Link>
        <Link href="/dashboard">Dashboard</Link>
      </div>
    </header>
  );
}