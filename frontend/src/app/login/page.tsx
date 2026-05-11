"use client";

import { FormEvent, useState, useEffect } from "react";
import { useRouter } from "next/navigation";

type UserRole = "hr" | "applicant";

export default function LoginPage() {
  const router = useRouter();
  const [isSignUp, setIsSignUp] = useState(false);
  const [role, setRole] = useState<UserRole>("applicant");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [name, setName] = useState("");
  const [company, setCompany] = useState("");
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const id = window.localStorage.getItem("sramp_user_id");
    if (id) {
      router.push("/profile");
    }
  }, [router]);

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);

    if (!email.trim() || !password.trim()) {
      setError("Email and password are required.");
      return;
    }

    if (isSignUp && !name.trim()) {
      setError("Name is required for sign up.");
      return;
    }

    if (isSignUp && password !== confirmPassword) {
      setError("Passwords do not match.");
      return;
    }

    try {
      const endpoint = isSignUp ? "/api/auth/signup" : "/api/auth/login";
      const payload = isSignUp ? { email, password, role, name, company } : { email, password };

      const res = await fetch(`http://localhost:5000${endpoint}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      const data = await res.json();

      if (!res.ok) {
        setError(data.error || "Something went wrong.");
        return;
      }

      // Persist logged in user state
      window.localStorage.setItem("sramp_user_role", data.user.role);
      window.localStorage.setItem("sramp_user_id", data.user.id);
      window.localStorage.setItem("sramp_user_name", data.user.name || "");
      
      window.dispatchEvent(new Event("auth-change"));

      router.push(`/jobs`);
    } catch (err) {
      setError("Failed to connect to the server.");
    }
  }

  return (
    <div className="mx-auto flex w-full max-w-xl flex-col gap-6 rounded-2xl border border-zinc-200 bg-white p-6 shadow-sm">
      <div>
        <h1 className="text-2xl font-bold text-zinc-900">
          {isSignUp ? "Create an Account" : "Welcome Back"}
        </h1>
        <p className="mt-2 text-sm text-zinc-600">
          {isSignUp 
            ? "Sign up to start applying for jobs or managing candidates." 
            : "Sign in to your SRAMP account."}
        </p>
      </div>

      <form onSubmit={onSubmit} className="flex flex-col gap-4 rounded-xl border border-zinc-200 p-5">
        {isSignUp && (
          <>
            <label className="flex flex-col gap-1 text-sm">
              <span className="font-medium text-zinc-700">Full Name</span>
              <input
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                className="rounded-md border border-zinc-300 px-3 py-2 text-zinc-900 outline-none focus:border-zinc-500 focus:ring-1 focus:ring-zinc-500"
                placeholder="John Doe"
              />
            </label>

            <label className="flex flex-col gap-1 text-sm">
              <span className="font-medium text-zinc-700">I am a...</span>
              <select
                value={role}
                onChange={(e) => setRole(e.target.value as UserRole)}
                className="rounded-md border border-zinc-300 px-3 py-2 text-zinc-900 outline-none focus:border-zinc-500 focus:ring-1 focus:ring-zinc-500 bg-white"
              >
                <option value="applicant">Applicant</option>
                <option value="hr">Human Resource (HR)</option>
              </select>
            </label>

            {role === "hr" && (
              <label className="flex flex-col gap-1 text-sm">
                <span className="font-medium text-zinc-700">Company Name</span>
                <input
                  type="text"
                  value={company}
                  onChange={(e) => setCompany(e.target.value)}
                  className="rounded-md border border-zinc-300 px-3 py-2 text-zinc-900 outline-none focus:border-zinc-500 focus:ring-1 focus:ring-zinc-500"
                  placeholder="Acme Corp"
                />
              </label>
            )}
          </>
        )}

        <label className="flex flex-col gap-1 text-sm">
          <span className="font-medium text-zinc-700">Email</span>
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="rounded-md border border-zinc-300 px-3 py-2 text-zinc-900 outline-none focus:border-zinc-500 focus:ring-1 focus:ring-zinc-500"
            placeholder="you@example.com"
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

        {isSignUp && (
          <label className="flex flex-col gap-1 text-sm">
            <span className="font-medium text-zinc-700">Confirm Password</span>
            <input
              type="password"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              className="rounded-md border border-zinc-300 px-3 py-2 text-zinc-900 outline-none focus:border-zinc-500 focus:ring-1 focus:ring-zinc-500"
              placeholder="••••••••"
            />
          </label>
        )}

        {error ? <div className="rounded-md bg-red-50 px-3 py-2 text-sm text-red-700">{error}</div> : null}

        <button
          type="submit"
          className="rounded-md bg-zinc-900 px-4 py-2 text-sm font-semibold text-white hover:bg-zinc-800"
        >
          {isSignUp ? "Sign Up" : "Login"}
        </button>

        <div className="mt-2 text-center text-sm text-zinc-600">
          {isSignUp ? "Already have an account?" : "Don't have an account?"}{" "}
          <button
            type="button"
            onClick={() => {
              setIsSignUp(!isSignUp);
              setError(null);
            }}
            className="font-semibold text-zinc-900 underline outline-none hover:text-zinc-700 focus:text-zinc-700"
          >
            {isSignUp ? "Login here" : "Sign up here"}
          </button>
        </div>
      </form>
    </div>
  );
}
