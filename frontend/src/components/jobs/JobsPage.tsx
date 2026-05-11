"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import CreateJobForm from "./CreateJobForm";
import type { JobPosting } from "@/lib/api/types";
import { deleteJob, getJobs } from "@/lib/api/jobs";

function formatDate(value: string | null) {
  if (!value) return "";
  const d = new Date(value);
  if (Number.isNaN(d.getTime())) return "";
  return d.toLocaleString();
}

export default function JobsPage() {
  const [jobs, setJobs] = useState<JobPosting[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [createModalOpen, setCreateModalOpen] = useState(false);
  const [storedRole, setStoredRole] = useState<"hr" | "applicant">("hr");
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [currentUserId, setCurrentUserId] = useState<string | null>(null);

  const role = storedRole;
  const isHrView = isLoggedIn && role === "hr";

  async function refresh() {
    setError(null);
    setLoading(true);
    try {
      const data = await getJobs();
      setJobs(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load jobs.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void refresh();
  }, []);

  useEffect(() => {
    const savedRole = window.localStorage.getItem("sramp_user_role");
    if (savedRole === "applicant" || savedRole === "hr") {
      setStoredRole(savedRole);
    }
    setIsLoggedIn(!!window.localStorage.getItem("sramp_user_id"));
    setCurrentUserId(window.localStorage.getItem("sramp_user_id"));
  }, []);

  useEffect(() => {
    if (!createModalOpen) return;

    const handleEsc = (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        setCreateModalOpen(false);
      }
    };

    document.addEventListener("keydown", handleEsc);
    return () => document.removeEventListener("keydown", handleEsc);
  }, [createModalOpen]);

  const rowCountLabel = useMemo(() => `${jobs.length} job${jobs.length === 1 ? "" : "s"}`, [jobs.length]);

  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold text-zinc-900">
            {isHrView ? "Jobs" : "Open Positions"}
          </h1>
          <p className="mt-1 text-sm text-zinc-600">{rowCountLabel}</p>
        </div>
        {isHrView ? (
          <button
            type="button"
            onClick={() => setCreateModalOpen(true)}
            className="rounded-lg bg-zinc-900 px-4 py-2 text-sm font-semibold text-white hover:bg-zinc-800"
          >
            Create Job
          </button>
        ) : null}
      </div>

      {createModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
          <div className="relative max-h-[90vh] w-full max-w-2xl overflow-y-auto rounded-lg bg-white shadow-lg">
            <button
              onClick={() => setCreateModalOpen(false)}
              className="sticky top-3 right-3 z-10 rounded-md p-1 text-zinc-500 hover:bg-zinc-100 hover:text-zinc-700"
            >
              <span className="text-xl">×</span>
            </button>
            <div className="p-6">
              <CreateJobForm
                onCreated={async () => {
                  await refresh();
                  setCreateModalOpen(false);
                }}
              />
            </div>
          </div>
        </div>
      )}

      <section className="rounded-xl border border-zinc-200 bg-white p-4 shadow-sm">
        {error ? <div className="mb-3 rounded bg-red-50 p-2 text-sm text-red-700">{error}</div> : null}

        {loading ? (
          <div className="py-6 text-sm text-zinc-600">Loading jobs...</div>
        ) : jobs.length === 0 ? (
          <div className="py-6 text-sm text-zinc-600">No jobs yet.</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full border-separate border-spacing-0">
              <thead>
                <tr className="text-left text-xs font-medium text-zinc-600">
                  <th className="border-b border-zinc-200 py-2 pr-3">Title</th>
                  <th className="border-b border-zinc-200 py-2 pr-3">Company</th>
                  <th className="border-b border-zinc-200 py-2 pr-3">Location</th>
                  <th className="border-b border-zinc-200 py-2 pr-3">Created</th>
                  <th className="border-b border-zinc-200 py-2">Actions</th>
                </tr>
              </thead>
              <tbody>
                {jobs.map((job) => (
                  <tr key={job.id} className="align-top">
                    <td className="border-b border-zinc-100 py-3 pr-3">
                      <Link
                      href={`/jobs/${job.id}`}
                        className="font-medium text-zinc-900 hover:underline"
                      >
                        {job.title}
                      </Link>
                    </td>
                    <td className="border-b border-zinc-100 py-3 pr-3 text-sm text-zinc-700">
                      {job.company}
                    </td>
                    <td className="border-b border-zinc-100 py-3 pr-3 text-sm text-zinc-700">
                      {job.location}
                    </td>
                    <td className="border-b border-zinc-100 py-3 pr-3 text-sm text-zinc-700">
                      {formatDate(job.created_at)}
                    </td>
                    <td className="border-b border-zinc-100 py-3">
                      <div className="flex items-center gap-2">
                        <Link
                        href={`/jobs/${job.id}`}
                          className="rounded-md border border-zinc-200 bg-white px-3 py-1 text-xs font-semibold text-zinc-900 hover:bg-zinc-50"
                        >
                          View
                        </Link>
                        {isHrView && String((job as any).user_id) === String(currentUserId) ? (
                          <button
                            type="button"
                            onClick={async () => {
                              const ok = window.confirm(`Delete job "${job.title}"?`);
                              if (!ok) return;
                              await deleteJob(job.id, currentUserId!);
                              await refresh();
                            }}
                            className="rounded-md bg-red-600 px-3 py-1 text-xs font-semibold text-white hover:bg-red-700"
                          >
                            Delete
                          </button>
                        ) : null}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </div>
  );
}
