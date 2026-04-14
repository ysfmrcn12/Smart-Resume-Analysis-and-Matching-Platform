"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import type { Application, JobPosting } from "@/lib/api/types";
import { deleteJob, getJob } from "@/lib/api/jobs";
import { listApplications, rankApplications } from "@/lib/api/applications";
import UploadResumeForm from "./UploadResumeForm";
import ResumeHighlightModal from "./ResumeHighlightModal";

function formatDate(value: string | null) {
  if (!value) return "";
  const d = new Date(value);
  if (Number.isNaN(d.getTime())) return "";
  return d.toLocaleString();
}

function scoreLabel(score: number) {
  const s = Number(score);
  if (Number.isNaN(s)) return { text: "—", className: "bg-zinc-100 text-zinc-700", raw: 0 };
  // Backend returns percent values (0..100).
  const rounded = Math.round(s);
  if (s >= 80) return { text: String(rounded), className: "bg-green-50 text-green-800", raw: s };
  if (s >= 50) return { text: String(rounded), className: "bg-yellow-50 text-yellow-900", raw: s };
  return { text: String(rounded), className: "bg-red-50 text-red-800", raw: s };
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
  const [highlightModalOpen, setHighlightModalOpen] = useState(false);
  const [selectedAppId, setSelectedAppId] = useState<number | null>(null);

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
      {/* Job Details Card */}
      <div className="rounded-xl border border-zinc-200 bg-white p-6 shadow-sm">
        <div className="mb-4">
          <Link
            href="/jobs"
            className="inline-flex items-center rounded-md border border-zinc-200 px-3 py-2 text-sm font-semibold text-zinc-700 hover:bg-zinc-50"
          >
            ← Back to jobs
          </Link>
        </div>

        <div className="flex items-start justify-between gap-6">
          <div className="flex-1">
            <h1 className="text-4xl font-bold text-zinc-900">{job.title}</h1>
            <p className="mt-3 whitespace-pre-wrap text-base text-zinc-700">
              {job.description}
            </p>
            {job.requirements && Array.isArray(job.requirements) && job.requirements.length > 0 ? (
              <div className="mt-4 rounded-lg border border-zinc-200 bg-zinc-50 p-4">
                <div className="text-sm font-semibold text-zinc-900">Requirements</div>
                <ul className="mt-2 list-inside list-disc space-y-1">
                  {job.requirements.map((req, i) => (
                    <li key={i} className="text-sm text-zinc-700">
                      {req}
                    </li>
                  ))}
                </ul>
              </div>
            ) : null}
          </div>

          <div className="flex flex-col gap-2">
            <button
              type="button"
              onClick={() => {
                const ok = window.confirm(`Delete job "${job.title}"? This cannot be undone.`);
                if (!ok) return;
                deleteJob(job.id).then(() => router.push("/jobs"));
              }}
              className="rounded-md bg-red-600 px-3 py-2 text-sm font-semibold text-white hover:bg-red-700"
            >
              Delete Job
            </button>
          </div>
        </div>

        <div className="mt-6 flex items-center justify-end">
          <button
            type="button"
            onClick={() => setApplyOpen(true)}
            className="rounded-lg bg-zinc-900 px-6 py-2 text-sm font-semibold text-white hover:bg-zinc-800"
          >
            Apply for this job
          </button>
        </div>
      </div>

      {/* Apply Modal */}
      {applyOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
          <div className="relative max-h-[90vh] w-full max-w-2xl overflow-y-auto rounded-lg bg-white shadow-lg">
            <button
              onClick={() => setApplyOpen(false)}
              className="sticky top-3 right-3 z-10 rounded-md p-1 text-zinc-500 hover:bg-zinc-100 hover:text-zinc-700"
            >
              <span className="text-xl">×</span>
            </button>
            <div className="p-6">
              <UploadResumeForm
                jobId={jobId}
                onUploaded={async () => {
                  await refreshApplicationsOnly();
                  setApplyOpen(false);
                }}
              />
            </div>
          </div>
        </div>
      )}

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
                  <th className="border-b border-zinc-200 py-2 pr-3">File</th>
                  <th className="border-b border-zinc-200 py-2 pr-3">Uploaded</th>
                  <th className="border-b border-zinc-200 py-2 pr-3 text-right">Match Score</th>
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
                        {a.candidate_email ? (
                          <a
                            href={`mailto:${a.candidate_email}`}
                            className="font-medium text-blue-600 hover:underline"
                          >
                            {a.candidate_email}
                          </a>
                        ) : (
                          "—"
                        )}
                      </td>
                      <td className="border-b border-zinc-100 py-3 pr-3 text-sm text-zinc-700">
                        {a.resume_filename ? (
                          <a
                            href={`/api/applications/${a.id}/resume`}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="font-medium text-blue-600 hover:underline"
                            title="View Resume"
                          >
                            {a.resume_filename}
                          </a>
                        ) : (
                          "—"
                        )}
                      </td>
                      <td className="border-b border-zinc-100 py-3 pr-3 text-sm text-zinc-700">
                        {formatDate(a.created_at)}
                      </td>
                      <td className="border-b border-zinc-100 py-3 pr-3 text-right">
                        <div className="flex items-center justify-end gap-2">
                          <button
                            type="button"
                            onClick={() => {
                              setSelectedAppId(a.id);
                              setHighlightModalOpen(true);
                            }}
                            className={`inline-flex items-center rounded-lg px-3 py-2 text-sm font-bold cursor-pointer transition-opacity hover:opacity-80 ${badge.className}`}
                            title="Click to see matching skills"
                          >
                            {badge.text}%
                          </button>
                          <button
                            type="button"
                            onClick={() => {
                              setSelectedAppId(a.id);
                              setHighlightModalOpen(true);
                            }}
                            className="inline-flex items-center rounded-md border border-zinc-300 bg-white px-3 py-2 text-sm font-medium text-zinc-700 hover:bg-zinc-50 transition-colors"
                            title="Analyze resume"
                          >
                            Analyze
                          </button>
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </section>

      <ResumeHighlightModal
        isOpen={highlightModalOpen}
        onClose={() => {
          setHighlightModalOpen(false);
          setSelectedAppId(null);
        }}
        applicationId={selectedAppId || 0}
        candidateName={
          applications.find((a) => a.id === selectedAppId)?.candidate_name ||
          "Candidate"
        }
        jobRequirements={Array.isArray(job?.requirements) ? job.requirements : []}
        score={applications.find((a) => a.id === selectedAppId)?.compatibility_score || 0}
      />
    </div>
  );
}
