"use client";

import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";

type UserRole = "hr" | "applicant";

type LoginCopy = {
  heading: string;
  subtitle: string;
  cta: string;
};

const COPY_BY_ROLE: Record<UserRole, LoginCopy> = {
  hr: {
    heading: "Human Resource Login",
    subtitle: "Manage job postings, review candidates, and inspect scoring breakdowns.",
    cta: "Login as HR",
  },
  applicant: {
    heading: "Applicant Login",
    subtitle: "Browse opportunities and submit your CV for AI-powered matching.",
    cta: "Login as Applicant",
  },
};

export default function LoginPage() {
  const router = useRouter();
  const [role, setRole] = useState<UserRole>("hr");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);

  const copy = COPY_BY_ROLE[role];

  function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);

    if (!email.trim() || !password.trim()) {
      setError("Email and password are required.");
      return;
    }

    // UI-only role persistence for role-specific views.
    window.localStorage.setItem("sramp_user_role", role);
    router.push(`/jobs?role=${role}`);
  }

  return (
    <div className="mx-auto flex w-full max-w-3xl flex-col gap-6 rounded-2xl border border-zinc-200 bg-white p-6 shadow-sm">
      <div>
        <h1 className="text-2xl font-bold text-zinc-900">SRAMP Login</h1>
        <p className="mt-2 text-sm text-zinc-600">
          Sign in as a Human Resource user or as an Applicant.
        </p>
      </div>

      <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
        <button
          type="button"
          onClick={() => setRole("hr")}
          className={`rounded-lg border px-4 py-3 text-left text-sm font-semibold transition-colors ${
            role === "hr"
              ? "border-blue-600 bg-blue-50 text-blue-800"
              : "border-zinc-200 bg-white text-zinc-700 hover:bg-zinc-50"
          }`}
        >
          Human Resource
        </button>
        <button
          type="button"
          onClick={() => setRole("applicant")}
          className={`rounded-lg border px-4 py-3 text-left text-sm font-semibold transition-colors ${
            role === "applicant"
              ? "border-emerald-600 bg-emerald-50 text-emerald-800"
              : "border-zinc-200 bg-white text-zinc-700 hover:bg-zinc-50"
          }`}
        >
          Applicant
        </button>
      </div>

      <form onSubmit={onSubmit} className="flex flex-col gap-4 rounded-xl border border-zinc-200 p-5">
        <div>
          <h2 className="text-lg font-semibold text-zinc-900">{copy.heading}</h2>
          <p className="mt-1 text-sm text-zinc-600">{copy.subtitle}</p>
        </div>

        <label className="flex flex-col gap-1 text-sm">
          <span className="font-medium text-zinc-700">Email</span>
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="rounded-md border border-zinc-300 px-3 py-2 text-zinc-900 outline-none focus:border-zinc-500 focus:ring-1 focus:ring-zinc-500"
            placeholder={role === "hr" ? "hr@company.com" : "applicant@email.com"}
            autoComplete="email"
          />
        </label>

        <label className="flex flex-col gap-1 text-sm">
          <span className="font-medium text-zinc-700">Password</span>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="rounded-md border border-zinc-300 px-3 py-2 text-zinc-900 outline-none focus:border-zinc-500 focus:ring-1 focus:ring-zinc-500"
            placeholder="••••••••"
            autoComplete="current-password"
          />
        </label>

        {error ? <div className="rounded-md bg-red-50 px-3 py-2 text-sm text-red-700">{error}</div> : null}

        <button
          type="submit"
          className="rounded-md bg-zinc-900 px-4 py-2 text-sm font-semibold text-white hover:bg-zinc-800"
        >
          {copy.cta}
        </button>
      </form>
    </div>
  );
}
