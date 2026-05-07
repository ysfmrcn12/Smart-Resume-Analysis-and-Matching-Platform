import Link from "next/link";
import Image from "next/image";

export default function NavBar() {
  return (
    <header
      className="border-b border-zinc-200"
      style={{
        background: "linear-gradient(to bottom, rgb(21, 78, 139), rgb(48, 169, 113))",
      }}
    >
      <div className="mx-auto flex max-w-5xl items-center justify-between px-4 py-3">
        <Link href="/jobs" className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-full bg-white shadow-sm">
            <Image
              src="/sramp.png"
              alt="SRAMP"
              width={32}
              height={32}
              className="object-contain"
            />
          </div>
          <span className="text-lg font-semibold text-white">SRAMP</span>
        </Link>
        <nav className="flex items-center gap-4 text-sm text-white">
          <Link href="/login" className="hover:text-zinc-100">
            Login
          </Link>
          <Link href="/jobs" className="hover:text-zinc-100">
            Jobs
          </Link>
        </nav>
      </div>
    </header>
  );
}

