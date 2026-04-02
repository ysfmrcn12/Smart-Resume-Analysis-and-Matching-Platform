"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import type { Application, JobPosting } from "@/lib/api/types";
import { deleteJob, getJob } from "@/lib/api/jobs";
import { listApplications, rankApplications } from "@/lib/api/applications";
import UploadResumeForm from "./UploadResumeForm";

function formatDate(value: string | null) {
  if (!value) return "";
  const d = new Date(value);
  if (Number.isNaN(d.getTime())) return "";
  return d.toLocaleString();
}

function scoreLabel(score: number) {
  const s = Number(score);
  if (Number.isNaN(s)) return { text: "—", className: "bg-zinc-100 text-zinc-700" };
  // Backend returns percent values (0..100).
  if (s >= 80) return { text: s.toFixed(2), className: "bg-green-50 text-green-800" };
  if (s >= 50) return { text: s.toFixed(2), className: "bg-yellow-50 text-yellow-900" };
  return { text: s.toFixed(2), className: "bg-red-50 text-red-800" };
}

export default function JobDetailsPage({ jobId }: { jobId: number }) {
  const router = useRouter();

  const [job, setJob] = useState<JobPosting | null>(null);
  const [applications, setApplications] = useState<Application[]>([]);

  const [loading, setLoading] = useState(true);
  const [loadingApps, setLoadingApps] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [rankedMode, setRankedMode] = useState(false);
  const [applyOpen, setApplyOpen] = useState(false);

  const refreshJobAndApplications = useCallback(async () => {
    setError(null);
    setLoading(true);
    try {
      const [jobRes, appsRes] = await Promise.all([getJob(jobId), listApplications(jobId)]);
      setJob(jobRes);
      setApplications(appsRes);
      setRankedMode(false);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load job.");
    } finally {
      setLoading(false);
    }
  }, [jobId]);

  useEffect(() => {
    void refreshJobAndApplications();
  }, [refreshJobAndApplications]);

  const applicantCountLabel = useMemo(() => {
    return `${applications.length} applicant${applications.length === 1 ? "" : "s"}`;
  }, [applications.length]);

  async function refreshApplicationsOnly() {
    setLoadingApps(true);
    setError(null);
    try {
      const appsRes = await listApplications(jobId);
      setApplications(appsRes);
      setRankedMode(false);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load applications.");
    } finally {
      setLoadingApps(false);
    }
  }

  async function onRank() {
    setError(null);
    setLoadingApps(true);
    try {
      const ranked = await rankApplications(jobId);
      setApplications(ranked);
      setRankedMode(true);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Ranking failed.");
    } finally {
      setLoadingApps(false);
    }
  }

  if (loading) {
    return <div className="py-6 text-sm text-zinc-600">Loading job...</div>;
  }

  if (error || !job) {
    return (
      <div className="flex flex-col gap-3 py-6">
        <Link href="/jobs" className="text-sm font-semibold text-zinc-700 hover:underline">
          Back to jobs
        </Link>
        {error ? <div className="rounded bg-red-50 p-3 text-sm text-red-700">{error}</div> : null}
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-start justify-between gap-4">
        <div>
          <Link
            href="/jobs"
            className="text-sm font-semibold text-zinc-700 hover:underline"
          >
            Back to jobs
          </Link>
          <h1 className="mt-2 text-2xl font-semibold text-zinc-900">{job.title}</h1>
          <p className="mt-1 whitespace-pre-wrap text-sm text-zinc-700">
            {job.description}
          </p>
          {job.requirements ? (
            <div className="mt-3 rounded-lg border border-zinc-200 bg-white p-3">
              <div className="text-sm font-semibold text-zinc-900">Requirements</div>
              <div className="mt-1 whitespace-pre-wrap text-sm text-zinc-700">
                {job.requirements}
              </div>
            </div>
          ) : null}
        </div>

        <div className="flex flex-col items-end gap-2">
          <button
            type="button"
            onClick={() => setApplyOpen(true)}
            className="rounded-md bg-zinc-900 px-3 py-2 text-sm font-semibold text-white hover:bg-zinc-800"
          >
            apply for this job
          </button>
          <button
            type="button"
            onClick={async () => {
              const ok = window.confirm(`Delete job "${job.title}"? This cannot be undone.`);
              if (!ok) return;
              await deleteJob(job.id);
              router.push("/jobs");
            }}
            className="rounded-md bg-red-600 px-3 py-2 text-sm font-semibold text-white hover:bg-red-700"
          >
            Delete Job
          </button>
        </div>
      </div>

      {applyOpen ? (
        <div className="flex flex-col gap-4">
          <UploadResumeForm
            jobId={jobId}
            onUploaded={async () => {
              await refreshApplicationsOnly();
              setApplyOpen(false);
            }}
          />
        </div>
      ) : null}

      <section className="rounded-xl border border-zinc-200 bg-white p-4 shadow-sm">
        <div className="mb-3 flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h2 className="text-base font-semibold text-zinc-900">
              Applications
            </h2>
            <p className="text-sm text-zinc-600">{applicantCountLabel}</p>
          </div>

          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={() => void refreshApplicationsOnly()}
              disabled={loadingApps}
              className="rounded-md border border-zinc-200 bg-white px-3 py-2 text-sm font-semibold text-zinc-900 hover:bg-zinc-50 disabled:cursor-not-allowed disabled:opacity-60"
            >
              Refresh
            </button>
            <button
              type="button"
              onClick={() => void onRank()}
              disabled={loadingApps}
              className="rounded-md bg-zinc-900 px-3 py-2 text-sm font-semibold text-white hover:bg-zinc-800 disabled:cursor-not-allowed disabled:opacity-60"
            >
              {loadingApps ? "Working..." : "Rank Applicants"}
            </button>
          </div>
        </div>

        {rankedMode ? (
          <div className="mb-3 rounded bg-blue-50 p-2 text-sm text-blue-800">
            Showing ranked results.
          </div>
        ) : null}

        {error ? <div className="mb-3 rounded bg-red-50 p-2 text-sm text-red-700">{error}</div> : null}

        {loadingApps ? (
          <div className="py-6 text-sm text-zinc-600">Loading applications...</div>
        ) : applications.length === 0 ? (
          <div className="py-6 text-sm text-zinc-600">No applications yet.</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full border-separate border-spacing-0">
              <thead>
                <tr className="text-left text-xs font-medium text-zinc-600">
                  <th className="border-b border-zinc-200 py-2 pr-3">Candidate</th>
                  <th className="border-b border-zinc-200 py-2 pr-3">Email</th>
                  <th className="border-b border-zinc-200 py-2 pr-3">Score</th>
                  <th className="border-b border-zinc-200 py-2 pr-3">File</th>
                  <th className="border-b border-zinc-200 py-2 pr-3">Uploaded</th>
                </tr>
              </thead>
              <tbody>
                {applications.map((a) => {
                  const badge = scoreLabel(a.compatibility_score);
                  return (
                    <tr key={a.id} className="align-top">
                      <td className="border-b border-zinc-100 py-3 pr-3">
                        <div className="text-sm font-semibold text-zinc-900">
                          {a.candidate_name || "Unknown"}
                        </div>
                      </td>
                      <td className="border-b border-zinc-100 py-3 pr-3 text-sm text-zinc-700">
                        {a.candidate_email || "—"}
                      </td>
                      <td className="border-b border-zinc-100 py-3 pr-3">
                        <span
                          className={`inline-flex items-center rounded-full px-2 py-1 text-xs font-semibold ${badge.className}`}
                        >
                          {badge.text}
                        </span>
                      </td>
                      <td className="border-b border-zinc-100 py-3 pr-3 text-sm text-zinc-700">
                        {a.resume_filename || "—"}
                      </td>
                      <td className="border-b border-zinc-100 py-3 pr-3 text-sm text-zinc-700">
                        {formatDate(a.created_at)}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </div>
  );
}

