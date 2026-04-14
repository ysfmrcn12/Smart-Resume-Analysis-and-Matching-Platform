import Link from "next/link";

export default function NavBar() {
  return (
    <header className="border-b border-zinc-200 bg-white/80 backdrop-blur">
      <div className="mx-auto flex max-w-5xl items-center justify-between px-4 py-3">
        <Link href="/jobs" className="text-lg font-semibold text-zinc-900">
          SMARP
        </Link>
        <nav className="flex items-center gap-4 text-sm text-zinc-700">
          <Link href="/jobs" className="hover:text-zinc-900">
            Jobs
          </Link>
        </nav>
      </div>
    </header>
  );
}

