"use client";

import type { FormEvent } from "react";
import { useId, useState, useEffect } from "react";

export default function UploadResumeForm({
  jobId,
  onUploaded,
}: {
  jobId: number;
  onUploaded: () => void | Promise<void>;
}) {
  const fileInputId = useId();
  const [files, setFiles] = useState<File[]>([]);

  const [userId, setUserId] = useState<string | null>(null);
  const [savedCvs, setSavedCvs] = useState<{ id: number; filename: string }[]>([]);
  const [selectedCvId, setSelectedCvId] = useState<string>("");

  useEffect(() => {
    const uid = window.localStorage.getItem("sramp_user_id");
    if (uid) {
      setUserId(uid);
      fetch(`/api/users/${uid}/cvs`)
        .then(res => {
          if (!res.ok) throw new Error();
          return res.json();
        })
        .then(data => {
          if (Array.isArray(data)) setSavedCvs(data);
        })
        .catch(err => console.error("Failed to load CVs", err));
    }
  }, []);

  const [submitting, setSubmitting] = useState(false);
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState<string | null>(null);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);

    if (files.length === 0 && !selectedCvId) {
      setError("Please select a saved CV or upload at least one file.");
      return;
    }

    setSubmitting(true);
    setProgress(0);
    try {
      if (selectedCvId && userId) {
        const formData = new FormData();
        formData.append("cv_id", selectedCvId);
        formData.append("user_id", userId);

        const res = await fetch(`/api/applications/job/${jobId}/upload`, {
          method: "POST",
          body: formData,
        });

        if (!res.ok) {
          const data = await res.json();
          throw new Error(data.error || "Failed to apply with saved CV.");
        }
      } else {
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
        <h2 className="text-base font-semibold text-zinc-900">Submit Application</h2>
        <p className="text-sm text-zinc-600">Use a saved CV or upload new files.</p>
      </div>

      {error ? <div className="mb-3 rounded bg-red-50 p-2 text-sm text-red-700">{error}</div> : null}

      <div className="grid grid-cols-1 gap-3">
        {savedCvs.length > 0 && (
          <>
            <div className="flex flex-col gap-1">
              <span className="text-sm font-medium text-zinc-800">Use a Saved CV</span>
              <select
                value={selectedCvId}
                onChange={(e) => {
                  setSelectedCvId(e.target.value);
                  setFiles([]);
                }}
                className="rounded-md border border-zinc-300 px-3 py-2 text-sm outline-none focus:border-zinc-500 bg-white"
              >
                <option value="">-- Choose a saved CV --</option>
                {savedCvs.map(cv => (
                  <option key={cv.id} value={cv.id}>{cv.filename}</option>
                ))}
              </select>
            </div>
            <div className="text-center text-xs text-zinc-500 font-medium my-1">- OR -</div>
          </>
        )}

        <div className="flex flex-col gap-1">
          <span className="text-sm font-medium text-zinc-800">Select Resumes (PDF, DOCX, TXT)</span>
          <div className="flex items-center gap-3">
            <label
              htmlFor={fileInputId}
              className="inline-flex cursor-pointer items-center rounded-md bg-zinc-900 px-3 py-2 text-sm font-semibold text-white hover:bg-zinc-800"
            >
              Choose files
            </label>
            <span className="text-sm text-zinc-700">
              {files.length > 0 ? `${files.length} file(s) selected` : "No files selected"}
            </span>
          </div>
          <input
            id={fileInputId}
            type="file"
            multiple
            accept=".pdf,.docx,.txt"
            onChange={(e) => {
              setFiles(Array.from(e.target.files || []));
              setSelectedCvId("");
            }}
            className="sr-only"
          />
          <span className="text-xs text-zinc-500">
            Backend supports PDF, DOCX, and TXT.
          </span>
        </div>

        <button
          type="submit"
          disabled={submitting || (files.length === 0 && !selectedCvId)}
          className="mt-1 inline-flex h-10 items-center justify-center rounded-lg bg-zinc-900 px-4 text-sm font-semibold text-white hover:bg-zinc-800 disabled:cursor-not-allowed disabled:opacity-60"
        >
          {submitting ? (selectedCvId ? "Applying..." : `Uploading (${progress}/${files.length})...`) : "Submit Application"}
        </button>
      </div>
    </form>
  );
}
