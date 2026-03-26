"use client";

import type { FormEvent } from "react";
import { useEffect, useState } from "react";
import type { JobPosting, JobUpdateInput } from "@/lib/api/types";
import { updateJob } from "@/lib/api/jobs";

export default function JobEditForm({
  job,
  onUpdated,
}: {
  job: JobPosting;
  onUpdated: () => void | Promise<void>;
}) {
  const [title, setTitle] = useState(job.title);
  const [description, setDescription] = useState(job.description);
  const [requirements, setRequirements] = useState(job.requirements);
  const [company, setCompany] = useState(job.company);
  const [location, setLocation] = useState(job.location);

  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  useEffect(() => {
    setTitle(job.title);
    setDescription(job.description);
    setRequirements(job.requirements);
    setCompany(job.company);
    setLocation(job.location);
  }, [job]);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    setSuccess(null);

    if (!title.trim() || !description.trim()) {
      setError("`title` and `description` are required.");
      return;
    }

    setSubmitting(true);
    try {
      const payload: JobUpdateInput = {
        title: title.trim(),
        description: description.trim(),
        requirements: requirements.trim(),
        company: company.trim(),
        location: location.trim(),
      };
      await updateJob(job.id, payload);
      await onUpdated();
      setSuccess("Job updated.");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Update failed.");
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
        <h2 className="text-base font-semibold text-zinc-900">Edit Job</h2>
        <p className="text-sm text-zinc-600">Update title/description/metadata.</p>
      </div>

      {error ? <div className="mb-3 rounded bg-red-50 p-2 text-sm text-red-700">{error}</div> : null}
      {success ? <div className="mb-3 rounded bg-green-50 p-2 text-sm text-green-700">{success}</div> : null}

      <div className="grid grid-cols-1 gap-3">
        <label className="flex flex-col gap-1">
          <span className="text-sm font-medium text-zinc-800">Title *</span>
          <input
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            className="rounded-lg border border-zinc-200 bg-white px-3 py-2 text-sm outline-none focus:border-zinc-400"
          />
        </label>

        <label className="flex flex-col gap-1">
          <span className="text-sm font-medium text-zinc-800">Description *</span>
          <textarea
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            rows={3}
            className="rounded-lg border border-zinc-200 bg-white px-3 py-2 text-sm outline-none focus:border-zinc-400"
          />
        </label>

        <label className="flex flex-col gap-1">
          <span className="text-sm font-medium text-zinc-800">Requirements</span>
          <textarea
            value={requirements}
            onChange={(e) => setRequirements(e.target.value)}
            rows={2}
            className="rounded-lg border border-zinc-200 bg-white px-3 py-2 text-sm outline-none focus:border-zinc-400"
          />
        </label>

        <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
          <label className="flex flex-col gap-1">
            <span className="text-sm font-medium text-zinc-800">Company</span>
            <input
              value={company}
              onChange={(e) => setCompany(e.target.value)}
              className="rounded-lg border border-zinc-200 bg-white px-3 py-2 text-sm outline-none focus:border-zinc-400"
            />
          </label>

          <label className="flex flex-col gap-1">
            <span className="text-sm font-medium text-zinc-800">Location</span>
            <input
              value={location}
              onChange={(e) => setLocation(e.target.value)}
              className="rounded-lg border border-zinc-200 bg-white px-3 py-2 text-sm outline-none focus:border-zinc-400"
            />
          </label>
        </div>

        <button
          type="submit"
          disabled={submitting}
          className="mt-1 inline-flex h-10 items-center justify-center rounded-lg bg-zinc-900 px-4 text-sm font-semibold text-white hover:bg-zinc-800 disabled:cursor-not-allowed disabled:opacity-60"
        >
          {submitting ? "Saving..." : "Save Changes"}
        </button>
      </div>
    </form>
  );
}

