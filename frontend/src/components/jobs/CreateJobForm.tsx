"use client";

import type { FormEvent } from "react";
import { useState } from "react";
import type { JobCreateInput } from "@/lib/api/types";
import { createJob } from "@/lib/api/jobs";

export default function CreateJobForm({
  onCreated,
}: {
  onCreated: () => void | Promise<void>;
}) {
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [requirements, setRequirements] = useState("");
  const [company, setCompany] = useState("");
  const [location, setLocation] = useState("");

  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  function fillMockData() {
    setError(null);
    setTitle("Frontend Engineer (React)");
    setDescription(
      "Build accessible UI components, improve performance, and collaborate with design and backend teams.",
    );
    setRequirements("React, TypeScript, accessibility, performance tuning");
    setCompany("Acme Labs");
    setLocation("Remote");
  }

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);

    if (!title.trim() || !description.trim()) {
      setError("`title` and `description` are required.");
      return;
    }

    setSubmitting(true);
    try {
      const payload: JobCreateInput = {
        title: title.trim(),
        description: description.trim(),
        requirements: requirements.trim() || undefined,
        company: company.trim() || undefined,
        location: location.trim() || undefined,
      };
      await createJob(payload);
      setTitle("");
      setDescription("");
      setRequirements("");
      setCompany("");
      setLocation("");
      await onCreated();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to create job.");
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
        <h2 className="text-base font-semibold text-zinc-900">Create Job</h2>
        <p className="text-sm text-zinc-600">Add a job posting for candidates.</p>
      </div>

      {error ? <div className="mb-3 rounded bg-red-50 p-2 text-sm text-red-700">{error}</div> : null}

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

        <div className="mt-1 flex flex-col gap-2 sm:flex-row sm:items-center">
          <button
            type="button"
            onClick={fillMockData}
            disabled={submitting}
            className="inline-flex h-10 items-center justify-center rounded-lg bg-zinc-100 px-4 text-sm font-semibold text-zinc-900 hover:bg-zinc-200 disabled:cursor-not-allowed disabled:opacity-60"
          >
            Fill mock data
          </button>

          <button
            type="submit"
            disabled={submitting}
            className="inline-flex h-10 items-center justify-center rounded-lg bg-zinc-900 px-4 text-sm font-semibold text-white hover:bg-zinc-800 disabled:cursor-not-allowed disabled:opacity-60 sm:flex-1"
          >
            {submitting ? "Creating..." : "Create Job"}
          </button>
        </div>
      </div>
    </form>
  );
}

