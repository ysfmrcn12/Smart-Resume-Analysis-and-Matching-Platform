"use client";

import type { FormEvent } from "react";
import { useState } from "react";
import { uploadResume } from "@/lib/api/applications";

export default function UploadResumeForm({
  jobId,
  onUploaded,
}: {
  jobId: number;
  onUploaded: () => void | Promise<void>;
}) {
  const [file, setFile] = useState<File | null>(null);
  const [candidateName, setCandidateName] = useState("");
  const [candidateEmail, setCandidateEmail] = useState("");

  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);

    if (!file) {
      setError("Please select a resume file.");
      return;
    }

    setSubmitting(true);
    try {
      await uploadResume(jobId, {
        file,
        candidateName: candidateName.trim() || undefined,
        candidateEmail: candidateEmail.trim() || undefined,
      });
      setFile(null);
      setCandidateName("");
      setCandidateEmail("");
      await onUploaded();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Upload failed.");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <form
      onSubmit={onSubmit}
      className="rounded-xl border border-zinc-200 bg-white p-4 shadow-sm"
    >
      <div className="mb-4">
        <h2 className="text-base font-semibold text-zinc-900">Upload Resume</h2>
        <p className="text-sm text-zinc-600">Upload a candidate resume for this job.</p>
      </div>

      {error ? <div className="mb-3 rounded bg-red-50 p-2 text-sm text-red-700">{error}</div> : null}

      <div className="grid grid-cols-1 gap-3">
        <label className="flex flex-col gap-1">
          <span className="text-sm font-medium text-zinc-800">Resume file</span>
          <input
            type="file"
            accept=".pdf,.docx,.txt"
            onChange={(e) => {
              const f = e.target.files?.[0] ?? null;
              setFile(f);
            }}
            className="rounded-lg border border-zinc-200 bg-white px-3 py-2 text-sm outline-none file:mr-3 file:rounded-md file:border-0 file:bg-zinc-900 file:px-3 file:py-2 file:text-sm file:font-semibold file:text-white"
          />
          <span className="text-xs text-zinc-500">
            Backend supports PDF, DOCX, and TXT.
          </span>
        </label>

        <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
          <label className="flex flex-col gap-1">
            <span className="text-sm font-medium text-zinc-800">Candidate name</span>
            <input
              value={candidateName}
              onChange={(e) => setCandidateName(e.target.value)}
              className="rounded-lg border border-zinc-200 bg-white px-3 py-2 text-sm outline-none focus:border-zinc-400"
            />
          </label>

          <label className="flex flex-col gap-1">
            <span className="text-sm font-medium text-zinc-800">Candidate email</span>
            <input
              value={candidateEmail}
              onChange={(e) => setCandidateEmail(e.target.value)}
              className="rounded-lg border border-zinc-200 bg-white px-3 py-2 text-sm outline-none focus:border-zinc-400"
            />
          </label>
        </div>

        <button
          type="submit"
          disabled={submitting}
          className="mt-1 inline-flex h-10 items-center justify-center rounded-lg bg-zinc-900 px-4 text-sm font-semibold text-white hover:bg-zinc-800 disabled:cursor-not-allowed disabled:opacity-60"
        >
          {submitting ? "Uploading..." : "Upload & Analyze"}
        </button>
      </div>
    </form>
  );
}

