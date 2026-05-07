"use client";

import type { FormEvent } from "react";
import { useState, useRef, useEffect } from "react";
import type { JobCreateInput } from "@/lib/api/types";
import { createJob } from "@/lib/api/jobs";

export default function CreateJobForm({
  onCreated,
}: {
  onCreated: () => void | Promise<void>;
}) {
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [requirements, setRequirements] = useState<string[]>([]);
  const [requirementInput, setRequirementInput] = useState("");
  const [company, setCompany] = useState("");
  const [location, setLocation] = useState("");
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  function fillMockData() {
    setError(null);
    setTitle("Frontend Engineer (React)");
    setDescription(
      "Build accessible UI components, improve performance, and collaborate with design and backend teams.",
    );
    setRequirements(["React", "TypeScript", "Accessibility", "Performance Tuning"]);
    setCompany("Acme Labs");
    setLocation("Remote");
  }

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
      textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`;
    }
  }, [description]);

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
        requirements: requirements.filter((r) => r.trim().length > 0) || undefined,
        company: company.trim() || undefined,
        location: location.trim() || undefined,
      };
      await createJob(payload);
      setTitle("");
      setDescription("");
      setRequirements([]);
      setRequirementInput("");
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
            ref={textareaRef}
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            rows={3}
            className="rounded-lg border border-zinc-200 bg-white px-3 py-2 text-sm outline-none focus:border-zinc-400 resize-none overflow-hidden"
          />
        </label>

        <div className="flex flex-col gap-1">
          <span className="text-sm font-medium text-zinc-800">Requirements</span>
          <div className="flex gap-2">
            <input
              value={requirementInput}
              onChange={(e) => setRequirementInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter") {
                  e.preventDefault();
                  if (requirementInput.trim()) {
                    setRequirements([...requirements, requirementInput.trim()]);
                    setRequirementInput("");
                  }
                }
              }}
              onPaste={(e) => {
                const pasteData = e.clipboardData.getData("text");
                if (pasteData.includes("\n")) {
                  e.preventDefault();
                  const splitReqs = pasteData
                    .split("\n")
                    .map((r) => r.replace(/^[•*-]\s*/, "").trim())
                    .filter(Boolean);
                  if (splitReqs.length > 0) {
                    setRequirements((prev) => [...prev, ...splitReqs]);
                    setRequirementInput("");
                  }
                }
              }}
              placeholder="Add a requirement and press Enter"
              className="flex-1 rounded-lg border border-zinc-200 bg-white px-3 py-2 text-sm outline-none focus:border-zinc-400"
            />
            <button
              type="button"
              onClick={() => {
                if (requirementInput.trim()) {
                  setRequirements([...requirements, requirementInput.trim()]);
                  setRequirementInput("");
                }
              }}
              className="rounded-lg bg-zinc-200 px-3 py-2 text-sm font-medium text-zinc-900 hover:bg-zinc-300"
            >
              Add
            </button>
          </div>
          {requirements.length > 0 && (
            <div className="mt-2 flex flex-wrap gap-2">
              {requirements.map((req, i) => (
                <span
                  key={i}
                  className="inline-flex items-center gap-2 rounded-full bg-zinc-100 px-3 py-1 text-sm text-zinc-900"
                >
                  <button
                    type="button"
                    onClick={() => setRequirements(requirements.filter((_, idx) => idx !== i))}
                    className="rounded-full hover:bg-zinc-200 w-5 h-5 flex items-center justify-center text-xs font-bold hover:text-red-600"
                    title="Remove requirement"
                  >
                    ×
                  </button>
                  {req}
                </span>
              ))}
            </div>
          )}
        </div>

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
