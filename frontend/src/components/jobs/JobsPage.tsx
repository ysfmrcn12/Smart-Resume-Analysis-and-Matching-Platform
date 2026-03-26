"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import CreateJobForm from "./CreateJobForm";
import type { JobPosting } from "@/lib/api/types";
import type { JobCreateInput } from "@/lib/api/types";
import { createJob, deleteJob, getJobs } from "@/lib/api/jobs";

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
  const [fillingMock, setFillingMock] = useState(false);

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

  const rowCountLabel = useMemo(() => `${jobs.length} job${jobs.length === 1 ? "" : "s"}`, [jobs.length]);

  const mockJobs: JobCreateInput[] = useMemo(
    () => [
      {
        title: "Frontend Engineer (React)",
        description:
          "Build accessible UI components, improve performance, and collaborate with design and backend teams.",
        requirements: "React, TypeScript, accessibility, performance tuning",
        company: "Acme Labs",
        location: "Remote",
      },
      {
        title: "Backend Engineer (Python/Flask)",
        description:
          "Design REST APIs, process uploaded documents, and maintain reliable data pipelines.",
        requirements: "Python, Flask, SQLAlchemy, PostgreSQL, testing",
        company: "Smart Resume Co.",
        location: "New York, NY",
      },
      {
        title: "Data/ML Engineer",
        description:
          "Develop ranking and matching models, iterate on features, and evaluate candidate-job compatibility.",
        requirements: "NLP, embeddings, model evaluation, production ML basics",
        company: "Talent Signals",
        location: "Hybrid",
      },
    ],
    []
  );

  async function fillMockData() {
    if (fillingMock) return;
    const ok = window.confirm("Create mock job postings now? This may create duplicates.");
    if (!ok) return;

    setError(null);
    setFillingMock(true);
    try {
      // Create sequentially for simpler debugging and to reduce backend burst load.
      for (const job of mockJobs) {
        await createJob(job);
      }
      await refresh();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to create mock jobs.");
    } finally {
      setFillingMock(false);
    }
  }

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-2xl font-semibold text-zinc-900">Jobs</h1>
        <p className="mt-1 text-sm text-zinc-600">{rowCountLabel}</p>
      </div>

      <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
        <CreateJobForm onCreated={refresh} />
        <div className="sm:pt-7">
          <button
            type="button"
            onClick={() => void fillMockData()}
            disabled={fillingMock}
            className="inline-flex w-full items-center justify-center rounded-lg bg-zinc-100 px-4 py-2 text-sm font-semibold text-zinc-900 hover:bg-zinc-200 disabled:cursor-not-allowed disabled:opacity-60 sm:w-auto"
          >
            {fillingMock ? "Filling..." : "Fill mock data"}
          </button>
        </div>
      </div>

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
                        <button
                          type="button"
                          onClick={async () => {
                            const ok = window.confirm(`Delete job "${job.title}"?`);
                            if (!ok) return;
                            await deleteJob(job.id);
                            await refresh();
                          }}
                          className="rounded-md bg-red-600 px-3 py-1 text-xs font-semibold text-white hover:bg-red-700"
                        >
                          Delete
                        </button>
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

