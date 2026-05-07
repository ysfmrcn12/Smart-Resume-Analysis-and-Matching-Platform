"use client";

import type { FormEvent } from "react";
import { useState } from "react";

export default function UploadResumeForm({
  jobId,
  onUploaded,
}: {
  jobId: number;
  onUploaded: () => void | Promise<void>;
}) {
  const [files, setFiles] = useState<File[]>([]);

  const [submitting, setSubmitting] = useState(false);
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState<string | null>(null);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);

    if (files.length === 0) {
      setError("Please select at least one file.");
      return;
    }

    setSubmitting(true);
    setProgress(0);
    try {
      let failureCount = 0;

      // Upload files sequentially to bypass Next.js proxy timeouts 
      for (let i = 0; i < files.length; i++) {
        setProgress(i + 1);
        const formData = new FormData();
        formData.append("file", files[i]);

        const res = await fetch(`/api/applications/job/${jobId}/upload`, {
          method: "POST",
          body: formData,
        });
        if (!res.ok) {
          failureCount++;
        }
      }

      if (failureCount > 0) {
        throw new Error(`${failureCount} file(s) failed. Check console for details.`);
      }

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
        <h2 className="text-base font-semibold text-zinc-900">Upload Resumes</h2>
        <p className="text-sm text-zinc-600">Select one or more files to batch upload.</p>
      </div>

      {error ? <div className="mb-3 rounded bg-red-50 p-2 text-sm text-red-700">{error}</div> : null}

      <div className="grid grid-cols-1 gap-3">
        <label className="flex flex-col gap-1">
          <span className="text-sm font-medium text-zinc-800">Select Resumes (PDF, DOCX, TXT)</span>
          <input
            type="file"
            multiple
            accept=".pdf,.docx,.txt"
            onChange={(e) => {
              setFiles(Array.from(e.target.files || []));
            }}
            className="rounded-lg border border-zinc-200 bg-white px-3 py-2 text-sm outline-none file:mr-3 file:rounded-md file:border-0 file:bg-zinc-900 file:px-3 file:py-2 file:text-sm file:font-semibold file:text-white"
          />
          <span className="text-xs text-zinc-500">
            Backend supports PDF, DOCX, and TXT.
          </span>
        </label>

        {files.length > 0 && (
          <div className="text-sm font-medium text-zinc-700">
            {files.length} file(s) selected
          </div>
        )}

        <button
          type="submit"
          disabled={submitting || files.length === 0}
          className="mt-1 inline-flex h-10 items-center justify-center rounded-lg bg-zinc-900 px-4 text-sm font-semibold text-white hover:bg-zinc-800 disabled:cursor-not-allowed disabled:opacity-60"
        >
          {submitting ? `Uploading (${progress}/${files.length})...` : "Upload All"}
        </button>
      </div>
    </form>
  );
}
