import { apiFetch } from "./http";
import type { JobCreateInput, JobPosting, JobUpdateInput } from "./types";

export async function getJobs(): Promise<JobPosting[]> {
  return (await apiFetch<JobPosting[]>("/api/jobs", { method: "GET" })) ?? [];
}

export async function createJob(payload: JobCreateInput, userId: string) {
  const res = await fetch(`/api/jobs`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ ...payload, user_id: userId }), // Add user_id to the payload
  });

  if (!res.ok) {
    const data = await res.json();
    throw new Error(data.error || "Failed to create job");
  }

  return await res.json();
}

export async function getJob(jobId: number): Promise<JobPosting> {
  return (await apiFetch<JobPosting>(`/api/jobs/${jobId}`, { method: "GET" })) as JobPosting;
}

export async function updateJob(
  jobId: number,
  input: JobUpdateInput
): Promise<JobPosting> {
  return (await apiFetch<JobPosting>(`/api/jobs/${jobId}`, { method: "PUT", body: input })) as JobPosting;
}

export async function deleteJob(jobId: number, userId: string): Promise<void> {
  await apiFetch<unknown>(`/api/jobs/${jobId}?user_id=${userId}`, { method: "DELETE" });
}

// Applications endpoints live in a separate file for organization, but we keep types imported here if needed later.
