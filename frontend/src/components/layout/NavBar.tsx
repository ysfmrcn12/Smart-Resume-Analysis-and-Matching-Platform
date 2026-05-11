"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import Image from "next/image";

export default function NavBar() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [userRole, setUserRole] = useState<string | null>(null);
  const [userName, setUserName] = useState<string | null>(null);

  useEffect(() => {
    const checkAuth = () => {
      setIsLoggedIn(!!window.localStorage.getItem("sramp_user_id"));
      setUserRole(window.localStorage.getItem("sramp_user_role"));
      setUserName(window.localStorage.getItem("sramp_user_name"));
    };
    
    checkAuth();

    window.addEventListener("auth-change", checkAuth);
    return () => window.removeEventListener("auth-change", checkAuth);
  }, []);

  const handleLogout = () => {
    window.localStorage.removeItem("sramp_user_id");
    window.localStorage.removeItem("sramp_user_role");
    window.localStorage.removeItem("sramp_user_name");
    window.dispatchEvent(new Event("auth-change"));
  };

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
          {!isLoggedIn ? (
            <Link href="/login" className="hover:text-zinc-100 font-medium">
              Login
            </Link>
          ) : (
            <div className="flex items-center gap-4">
              <Link href="/profile" className="text-zinc-100 opacity-90 hover:underline">
                {userName ? `Hello, ${userName}` : "Profile"}
              </Link>
              <button onClick={handleLogout} className="hover:text-zinc-100 font-medium">
                Logout
              </button>
            </div>
          )}
          <Link href="/jobs" className="hover:text-zinc-100">
            Jobs
          </Link>
        </nav>
      </div>
    </header>
  );
}
